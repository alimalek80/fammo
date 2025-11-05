from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView, 
    TemplateView, View
)
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import Clinic, VetProfile, ReferralCode, ReferredUser, ReferralStatus
from .forms import (
    ClinicRegistrationForm, ClinicProfileForm, VetProfileForm, 
    ReferralCodeForm, ClinicSearchForm
)
from .utils import (
    send_clinic_confirmation_email, send_admin_notification_email,
    confirm_clinic_email, is_confirmation_token_valid
)

User = get_user_model()


class ClinicRegistrationView(CreateView):
    """Clinic registration view with email confirmation"""
    model = Clinic
    form_class = ClinicRegistrationForm
    template_name = 'vets/clinic_register.html'
    success_url = reverse_lazy('vets:clinic_register_success')
    
    def form_valid(self, form):
        # Create user account first
        user = User.objects.create_user(
            email=form.cleaned_data['owner_email'],
            password=form.cleaned_data['owner_password']
        )
        user.is_active = True
        user.save()
        
        # Create clinic and assign owner
        clinic = form.save(commit=False)
        clinic.owner = user
        # Set initial status - email not confirmed, admin not approved
        clinic.email_confirmed = False
        clinic.admin_approved = False
        clinic.is_verified = False  # Keep this False until both confirmations
        clinic.save()
        
        # Create vet profile if provided
        vet_name = form.cleaned_data.get('vet_name')
        if vet_name:
            VetProfile.objects.create(
                clinic=clinic,
                vet_name=vet_name,
                degrees=form.cleaned_data.get('degrees', ''),
                certifications=form.cleaned_data.get('certifications', '')
            )
        
        # Send confirmation email
        email_sent = send_clinic_confirmation_email(self.request, clinic)
        if email_sent:
            messages.success(
                self.request, 
                f'Registration successful! Please check your email to confirm your clinic registration.'
            )
        else:
            messages.warning(
                self.request,
                f'Registration successful, but there was an issue sending the confirmation email. Please contact support.'
            )
        
        # Log the user in with the correct backend
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        return super().form_valid(form)


class ClinicRegistrationSuccessView(TemplateView):
    """Success page after clinic registration"""
    template_name = 'vets/clinic_register_success.html'


class ClinicEmailConfirmationView(View):
    """Handle email confirmation for clinic registration"""
    
    def get(self, request, clinic_id, token):
        try:
            clinic = get_object_or_404(Clinic, id=clinic_id)
            
            # Check if email is already confirmed
            if clinic.email_confirmed:
                messages.info(request, 'Your email has already been confirmed.')
                return render(request, 'vets/email_confirmed.html', {'clinic': clinic})
            
            # Validate token and confirm email
            if confirm_clinic_email(clinic, token):
                # Send admin notification after successful email confirmation
                send_admin_notification_email(request, clinic)
                
                messages.success(
                    request, 
                    'Email confirmed successfully! Your clinic is now pending admin approval.'
                )
                return render(request, 'vets/email_confirmed.html', {'clinic': clinic})
            else:
                messages.error(
                    request,
                    'Invalid or expired confirmation link. Please contact support for assistance.'
                )
                return redirect('vets:partner_clinics')
                
        except Clinic.DoesNotExist:
            messages.error(request, 'Invalid confirmation link.')
            return redirect('vets:partner_clinics')


class PartnerClinicsListView(ListView):
    """Public list of partner clinics - only show fully approved clinics"""
    model = Clinic
    template_name = 'vets/partner_clinics.html'
    context_object_name = 'clinics'
    paginate_by = 12
    
    def get_queryset(self):
        # ALWAYS only show clinics that have completed BOTH steps:
        # 1. Email confirmed AND 2. Admin approved
        queryset = Clinic.objects.filter(
            email_confirmed=True,
            admin_approved=True,
            is_verified=True
        ).order_by('name')
        
        # Handle search within approved clinics only
        form = ClinicSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            city = form.cleaned_data.get('city')
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(city__icontains=search) |
                    Q(specializations__icontains=search)
                )
            
            if city:
                queryset = queryset.filter(city__icontains=city)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ClinicSearchForm(self.request.GET)
        context['total_clinics'] = self.get_queryset().count()
        return context


class ClinicDetailView(DetailView):
    """Public clinic profile page - only show approved clinics"""
    model = Clinic
    template_name = 'vets/clinic_detail.html'
    context_object_name = 'clinic'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Only show clinics that are fully approved"""
        return Clinic.objects.filter(
            email_confirmed=True,
            admin_approved=True,
            is_verified=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.object
        
        # Only show referral functionality for approved clinics
        if clinic.is_active_clinic:
            # Get referral code for sharing
            context['referral_code'] = clinic.active_referral_code
            
            # Build referral URL
            if context['referral_code']:
                context['referral_url'] = self.request.build_absolute_uri(
                    reverse('vets:referral_landing', kwargs={'code': context['referral_code']})
                )
        
        return context


class ClinicOwnerRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user owns a clinic"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        try:
            self.clinic = request.user.owned_clinics.first()
            if not self.clinic:
                messages.error(request, "You don't have a registered clinic.")
                return redirect('vets:clinic_register')
        except:
            messages.error(request, "You don't have a registered clinic.")
            return redirect('vets:clinic_register')
        
        return super().dispatch(request, *args, **kwargs)


class ClinicDashboardView(ClinicOwnerRequiredMixin, TemplateView):
    """Clinic owner dashboard"""
    template_name = 'vets/dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.clinic
        
        # Basic stats
        context['clinic'] = clinic
        context['total_referrals'] = clinic.referred_users.count()
        context['active_referrals'] = clinic.referred_users.filter(
            status=ReferralStatus.ACTIVE
        ).count()
        context['new_referrals'] = clinic.referred_users.filter(
            status=ReferralStatus.NEW
        ).count()
        
        # Verification status
        context['verification_status'] = {
            'email_confirmed': clinic.email_confirmed,
            'admin_approved': clinic.admin_approved,
            'is_verified': clinic.is_verified,
            'is_public': clinic.is_active_clinic,
        }
        
        # Recent referrals
        context['recent_referrals'] = clinic.referred_users.select_related(
            'user', 'referral_code'
        ).order_by('-created_at')[:10]
        
        # Referral codes (only show if fully approved)
        if clinic.is_active_clinic:
            context['referral_codes'] = clinic.referral_codes.filter(
                is_active=True
            ).order_by('-created_at')
        else:
            context['referral_codes'] = []
        
        return context


class ClinicProfileUpdateView(ClinicOwnerRequiredMixin, UpdateView):
    """Update clinic profile"""
    model = Clinic
    form_class = ClinicProfileForm
    template_name = 'vets/dashboard/profile_update.html'
    success_url = reverse_lazy('vets:clinic_dashboard')
    
    def get_object(self):
        return self.clinic
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add vet profile form
        try:
            vet_profile = self.clinic.vet_profile
            context['vet_form'] = VetProfileForm(
                instance=vet_profile,
                prefix='vet'
            )
        except VetProfile.DoesNotExist:
            context['vet_form'] = VetProfileForm(prefix='vet')
        
        return context
    
    def form_valid(self, form):
        # Handle vet profile form
        vet_form = VetProfileForm(
            self.request.POST,
            prefix='vet'
        )
        
        if vet_form.is_valid():
            vet_data = vet_form.cleaned_data
            if any(vet_data.values()):  # If any vet data is provided
                try:
                    vet_profile = self.clinic.vet_profile
                    for field, value in vet_data.items():
                        setattr(vet_profile, field, value)
                    vet_profile.save()
                except VetProfile.DoesNotExist:
                    VetProfile.objects.create(
                        clinic=self.clinic,
                        **vet_data
                    )
        
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class ClinicReferralsView(ClinicOwnerRequiredMixin, TemplateView):
    """Clinic referrals management"""
    template_name = 'vets/dashboard/referrals.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.clinic
        
        # Referral statistics
        context['clinic'] = clinic
        context['total_referrals'] = clinic.referred_users.count()
        context['new_referrals'] = clinic.referred_users.filter(
            status=ReferralStatus.NEW
        ).count()
        context['active_referrals'] = clinic.referred_users.filter(
            status=ReferralStatus.ACTIVE
        ).count()
        
        # Referrals list with pagination
        referrals = clinic.referred_users.select_related(
            'user', 'referral_code'
        ).order_by('-created_at')
        
        paginator = Paginator(referrals, 20)
        page_number = self.request.GET.get('page')
        context['referrals'] = paginator.get_page(page_number)
        
        # Referral codes
        context['referral_codes'] = clinic.referral_codes.order_by('-created_at')
        context['referral_form'] = ReferralCodeForm(clinic=clinic)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle new referral code creation"""
        form = ReferralCodeForm(self.clinic, request.POST)
        
        if form.is_valid():
            code = form.cleaned_data.get('code')
            if not code:
                # Generate automatic code
                referral_code = ReferralCode.create_default_for_clinic(self.clinic)
            else:
                # Use custom code
                referral_code = ReferralCode.objects.create(
                    clinic=self.clinic,
                    code=code,
                    is_active=True
                )
            
            messages.success(
                request, 
                f'New referral code "{referral_code.code}" created successfully!'
            )
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return redirect('vets:clinic_referrals')


class ClinicAnalyticsView(ClinicOwnerRequiredMixin, TemplateView):
    """Clinic analytics and statistics"""
    template_name = 'vets/dashboard/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.clinic
        
        # Time-based analytics
        now = datetime.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        context['clinic'] = clinic
        
        # Referral statistics
        context['stats'] = {
            'total_referrals': clinic.referred_users.count(),
            'referrals_30_days': clinic.referred_users.filter(
                created_at__gte=last_30_days
            ).count(),
            'referrals_7_days': clinic.referred_users.filter(
                created_at__gte=last_7_days
            ).count(),
            'conversion_rate': self._calculate_conversion_rate(clinic),
        }
        
        # Referral code performance
        code_stats = []
        for code in clinic.referral_codes.all():
            referrals_count = code.referreduser_set.count()
            code_stats.append({
                'code': code.code,
                'referrals': referrals_count,
                'is_active': code.is_active,
            })
        
        context['code_stats'] = sorted(
            code_stats, 
            key=lambda x: x['referrals'], 
            reverse=True
        )
        
        return context
    
    def _calculate_conversion_rate(self, clinic):
        """Calculate conversion rate from referrals to active users"""
        total_referrals = clinic.referred_users.count()
        if total_referrals == 0:
            return 0
        
        active_users = clinic.referred_users.filter(
            status=ReferralStatus.ACTIVE
        ).count()
        
        return round((active_users / total_referrals) * 100, 1)


class ReferralLandingView(TemplateView):
    """Landing page for referral links - only for approved clinics"""
    template_name = 'vets/referral_landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        code = kwargs.get('code')
        
        try:
            referral_code = ReferralCode.objects.select_related('clinic').get(
                code=code,
                is_active=True
            )
            
            # Check if the clinic is fully approved
            clinic = referral_code.clinic
            if not (clinic.email_confirmed and clinic.admin_approved and clinic.is_verified):
                raise Http404("This clinic is not currently accepting referrals")
            
            context['referral_code'] = referral_code
            context['clinic'] = clinic
            
            # Store referral code in session for later use
            self.request.session['referral_code'] = code
            
        except ReferralCode.DoesNotExist:
            raise Http404("Referral code not found or inactive")
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class TrackReferralAPIView(View):
    """API endpoint to track referral conversions"""
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            referral_code = data.get('referral_code')
            
            if not email or not referral_code:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Get referral code object
            try:
                ref_code_obj = ReferralCode.objects.get(
                    code=referral_code,
                    is_active=True
                )
            except ReferralCode.DoesNotExist:
                return JsonResponse({'error': 'Invalid referral code'}, status=400)
            
            # Check if user exists
            try:
                user = User.objects.get(email=email)
                user_exists = True
            except User.DoesNotExist:
                user = None
                user_exists = False
            
            # Create or update referred user record
            referred_user, created = ReferredUser.objects.get_or_create(
                clinic=ref_code_obj.clinic,
                referral_code=ref_code_obj,
                user=user,
                defaults={
                    'email_capture': email if not user_exists else '',
                    'status': ReferralStatus.ACTIVE if user_exists else ReferralStatus.NEW
                }
            )
            
            if not created and user_exists and not referred_user.user:
                # Update existing record with user
                referred_user.user = user
                referred_user.status = ReferralStatus.ACTIVE
                referred_user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Referral tracked successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
