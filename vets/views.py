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
from core.models import LegalDocument, DocumentType
from .forms import (
    ClinicRegistrationForm, ClinicProfileForm, VetProfileForm, 
    ReferralCodeForm, ClinicSearchForm
)
from .utils import (
    send_clinic_confirmation_email, send_admin_notification_email,
    confirm_clinic_email, is_confirmation_token_valid
)
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from userapp.models import Profile

User = get_user_model()


class ClinicRegistrationView(CreateView):
    """Clinic registration view with email confirmation"""
    model = Clinic
    form_class = ClinicRegistrationForm
    template_name = 'vets/clinic_register.html'
    success_url = reverse_lazy('vets:clinic_register_success')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .forms import WorkingHoursFormSet
        from .models import WorkingHours
        
        if self.request.POST:
            context['working_hours_formset'] = WorkingHoursFormSet(self.request.POST)
        else:
            # Pre-populate with default working hours for registration
            import datetime
            initial_hours = []
            for day in range(7):
                initial_hours.append({
                    'day_of_week': day,
                    'is_closed': (day == 6),  # Sunday closed by default
                    'open_time': datetime.time(9, 0) if day != 6 else None,
                    'close_time': datetime.time(17, 0) if day != 6 else None,
                })
            context['working_hours_formset'] = WorkingHoursFormSet(initial=initial_hours, queryset=WorkingHours.objects.none())
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        
        from .forms import WorkingHoursFormSet
        working_hours_formset = WorkingHoursFormSet(self.request.POST)
        
        if form.is_valid() and working_hours_formset.is_valid():
            return self.form_valid(form, working_hours_formset)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form, working_hours_formset=None):
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
        
        # Save working hours from formset
        if working_hours_formset:
            for hours_form in working_hours_formset:
                if hours_form.cleaned_data and not hours_form.cleaned_data.get('DELETE', False):
                    working_hours = hours_form.save(commit=False)
                    working_hours.clinic = clinic
                    working_hours.save()
        
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
        # Show clinics that have confirmed email (public listing)
        # Badge will only show for admin_approved clinics
        queryset = Clinic.objects.filter(
            email_confirmed=True
        ).prefetch_related('working_hours_schedule').order_by('name')
        
        # Handle search within email-confirmed clinics
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
    """Public clinic profile page - show email-confirmed clinics"""
    model = Clinic
    template_name = 'vets/clinic_detail.html'
    context_object_name = 'clinic'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Show clinics that have confirmed email"""
        return Clinic.objects.filter(
            email_confirmed=True
        ).prefetch_related('working_hours_schedule')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.object
        
        # Add Google Maps API key
        from django.conf import settings
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        
        # Add current day of week (0=Monday, 6=Sunday)
        from datetime import datetime
        context['current_day'] = datetime.now().weekday()
        
        # Show referral functionality for email-confirmed clinics (even if not admin approved)
        if clinic.email_confirmed:
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
        from django.utils import timezone
        from .models import Appointment, AppointmentStatus, ClinicNotification
        
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
        
        # Appointment stats
        today = timezone.now().date()
        context['today_appointments'] = Appointment.objects.filter(
            clinic=clinic,
            appointment_date=today,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).count()
        context['pending_appointments'] = Appointment.objects.filter(
            clinic=clinic,
            status=AppointmentStatus.PENDING
        ).count()
        context['upcoming_appointments'] = Appointment.objects.filter(
            clinic=clinic,
            appointment_date__gte=today,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).count()
        
        # Unread notifications
        context['unread_notifications'] = ClinicNotification.objects.filter(
            clinic=clinic,
            is_read=False
        ).count()
        
        # Recent appointments
        context['recent_appointments'] = Appointment.objects.filter(
            clinic=clinic
        ).select_related('pet', 'user', 'reason').order_by('-created_at')[:5]
        
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
        
        # Add working hours formset
        from .forms import WorkingHoursFormSet
        from .models import WorkingHours
        
        if self.request.POST:
            context['working_hours_formset'] = WorkingHoursFormSet(
                self.request.POST,
                instance=self.clinic
            )
        else:
            # Initialize working hours if they don't exist
            existing_days = set(self.clinic.working_hours_schedule.values_list('day_of_week', flat=True))
            for day in range(7):
                if day not in existing_days:
                    WorkingHours.objects.create(
                        clinic=self.clinic,
                        day_of_week=day,
                        is_closed=(day == 6),  # Sunday closed by default
                        open_time='09:00' if day != 6 else None,
                        close_time='17:00' if day != 6 else None
                    )
            
            context['working_hours_formset'] = WorkingHoursFormSet(instance=self.clinic)
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        from .forms import WorkingHoursFormSet
        working_hours_formset = WorkingHoursFormSet(
            self.request.POST,
            instance=self.object
        )
        
        vet_form = VetProfileForm(
            self.request.POST,
            prefix='vet'
        )
        
        # Debug: Log formset data
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"POST data: {request.POST}")
        logger.info(f"Formset valid: {working_hours_formset.is_valid()}")
        if not working_hours_formset.is_valid():
            logger.error(f"Formset errors: {working_hours_formset.errors}")
            logger.error(f"Non-form errors: {working_hours_formset.non_form_errors()}")
        
        # Check if all forms are valid
        if form.is_valid() and working_hours_formset.is_valid():
            return self.form_valid(form, working_hours_formset, vet_form)
        else:
            if not working_hours_formset.is_valid():
                messages.error(request, f'Working hours validation failed: {working_hours_formset.errors}')
            return self.form_invalid(form)
    
    def form_valid(self, form, working_hours_formset, vet_form):
        # Check if address or city was modified
        clinic = self.object
        address_changed = (
            form.cleaned_data.get('address') != clinic.address or
            form.cleaned_data.get('city') != clinic.city
        )
        
        # Save the main form first
        response = super().form_valid(form)
        
        # If address changed, geocode to update coordinates
        if address_changed:
            from .utils import geocode_address
            geocoded_coords = geocode_address(
                address=clinic.address,
                city=clinic.city
            )
            if geocoded_coords:
                clinic.latitude = geocoded_coords['latitude']
                clinic.longitude = geocoded_coords['longitude']
                clinic.save()
        
        # Save working hours formset
        working_hours_formset.save()
        
        # Handle vet profile form
        if vet_form.is_valid():
            vet_data = vet_form.cleaned_data
            if any(vet_data.values()):  # If any vet data is provided
                try:
                    vet_profile = self.object.vet_profile
                    for field, value in vet_data.items():
                        setattr(vet_profile, field, value)
                    vet_profile.save()
                except VetProfile.DoesNotExist:
                    VetProfile.objects.create(
                        clinic=self.object,
                        **vet_data
                    )
        
        messages.success(self.request, 'Profile updated successfully!')
        return response


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
    """Landing page for referral links - available after email confirmation"""
    template_name = 'vets/referral_landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        code = kwargs.get('code')
        
        try:
            referral_code = ReferralCode.objects.select_related('clinic').get(
                code=code,
                is_active=True
            )
            
            # Check if the clinic has confirmed their email
            # No need to wait for admin approval to start accepting referrals
            clinic = referral_code.clinic
            if not clinic.email_confirmed:
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


def clinic_terms_and_conditions_view(request):
    """Display clinic terms and conditions from database"""
    document = get_object_or_404(
        LegalDocument,
        doc_type=DocumentType.CLINIC_TERMS_CONDITIONS,
        is_active=True
    )
    return render(request, 'vets/clinic_terms_and_conditions.html', {'document': document})


def clinic_partnership_agreement_view(request):
    """Display clinic partnership agreement from database"""
    document = get_object_or_404(
        LegalDocument,
        doc_type=DocumentType.CLINIC_PARTNERSHIP,
        is_active=True
    )
    return render(request, 'vets/clinic_partnership_agreement.html', {'document': document})


def eoi_terms(request):
    """Display Expression of Interest (EOI) terms from database"""
    document = get_object_or_404(
        LegalDocument,
        doc_type=DocumentType.CLINIC_EOI,
        is_active=True
    )
    return render(request, 'vets/eoi_terms.html', {'document': document})


# ========== Location & Nearby Clinics API ==========

class ClinicFinderView(TemplateView):
    """Main clinic finder page with location detection"""
    template_name = 'vets/clinic_finder.html'


class NearbyClinicAPIView(View):
    """API endpoint to find clinics near given coordinates"""
    
    def get(self, request, *args, **kwargs):
        try:
            # Get parameters
            lat = request.GET.get('lat')
            lng = request.GET.get('lng')
            radius = request.GET.get('radius', 50)  # Default 50km
            
            if not lat or not lng:
                return JsonResponse({
                    'error': 'Latitude and longitude are required'
                }, status=400)
            
            # Convert to float
            try:
                latitude = float(lat)
                longitude = float(lng)
                radius_km = float(radius)
            except ValueError:
                return JsonResponse({
                    'error': 'Invalid coordinate format'
                }, status=400)
            
            # Validate coordinates
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return JsonResponse({
                    'error': 'Invalid coordinates'
                }, status=400)
            
            # Get nearby clinics
            from .utils import get_clinics_within_radius
            clinics = get_clinics_within_radius(latitude, longitude, radius_km)
            
            # Serialize clinic data
            clinic_data = []
            for clinic in clinics:
                clinic_data.append({
                    'id': clinic.id,
                    'name': clinic.name,
                    'slug': clinic.slug,
                    'city': clinic.city,
                    'address': clinic.address,
                    'phone': clinic.phone,
                    'email': clinic.email,
                    'website': clinic.website,
                    'working_hours': clinic.working_hours,
                    'specializations': clinic.specializations,
                    'latitude': float(clinic.latitude) if clinic.latitude else None,
                    'longitude': float(clinic.longitude) if clinic.longitude else None,
                    'distance': clinic.distance,
                    'is_verified': clinic.is_verified,
                    'logo': clinic.logo.url if clinic.logo else None,
                })
            
            return JsonResponse({
                'success': True,
                'count': len(clinic_data),
                'clinics': clinic_data,
                'search_params': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius_km': radius_km
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)


class ClinicsByCityAPIView(View):
    """API endpoint to find clinics by city name"""
    
    def get(self, request, *args, **kwargs):
        try:
            city = request.GET.get('city', '').strip()
            radius = request.GET.get('radius', 10)
            
            if not city:
                return JsonResponse({
                    'error': 'City name is required'
                }, status=400)
            
            # Search for clinics in the city
            clinics = Clinic.objects.filter(
                city__icontains=city,
                email_confirmed=True,
                admin_approved=True
            ).order_by('name')
            
            # Serialize clinic data
            clinic_data = []
            for clinic in clinics:
                clinic_data.append({
                    'id': clinic.id,
                    'name': clinic.name,
                    'slug': clinic.slug,
                    'city': clinic.city,
                    'address': clinic.address,
                    'phone': clinic.phone,
                    'email': clinic.email,
                    'website': clinic.website,
                    'working_hours': clinic.working_hours,
                    'specializations': clinic.specializations,
                    'latitude': float(clinic.latitude) if clinic.latitude else None,
                    'longitude': float(clinic.longitude) if clinic.longitude else None,
                    'is_verified': clinic.is_verified,
                    'logo': clinic.logo.url if clinic.logo else None,
                })
            
            return JsonResponse({
                'success': True,
                'count': len(clinic_data),
                'clinics': clinic_data,
                'search_params': {
                    'city': city,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)


class IPLocationAPIView(View):
    """API endpoint to get location from user's IP address"""
    
    def get(self, request, *args, **kwargs):
        try:
            from .utils import get_client_ip, get_location_from_ip
            
            ip_address = get_client_ip(request)
            location = get_location_from_ip(ip_address)
            
            if location:
                return JsonResponse({
                    'success': True,
                    'location': location,
                    'ip': ip_address
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Unable to determine location from IP',
                    'ip': ip_address
                }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)


@method_decorator(user_passes_test(lambda u: u.is_staff or u.is_superuser), name='dispatch')
class ClinicNearbyUsersReportView(TemplateView):
    """Admin-only report: users near a given clinic within a radius (km)."""
    template_name = 'vets/admin/nearby_users_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic_id = kwargs.get('clinic_id')
        clinic = get_object_or_404(Clinic, id=clinic_id)
        radius_km = self.request.GET.get('radius', '10')
        try:
            radius_km = float(radius_km)
        except ValueError:
            radius_km = 10.0

        users = []
        if clinic.latitude is not None and clinic.longitude is not None:
            from .utils import haversine_distance
            # Only profiles with consent and coordinates
            qs = Profile.objects.filter(
                location_consent=True,
                latitude__isnull=False,
                longitude__isnull=False,
            ).select_related('user')
            for prof in qs:
                try:
                    dist = haversine_distance(
                        float(clinic.latitude), float(clinic.longitude),
                        float(prof.latitude), float(prof.longitude)
                    )
                except Exception:
                    continue
                if dist <= radius_km:
                    users.append({
                        'profile': prof,
                        'email': getattr(prof.user, 'email', ''),
                        'first_name': prof.first_name,
                        'last_name': prof.last_name,
                        'city': prof.city,
                        'distance_km': round(dist, 1),
                        'location_updated_at': prof.location_updated_at,
                    })
            users.sort(key=lambda x: x['distance_km'])

        context.update({
            'clinic': clinic,
            'radius_km': radius_km,
            'users': users,
            'clinic_has_coords': clinic.latitude is not None and clinic.longitude is not None,
        })
        return context


# ============================================================================
# APPOINTMENT VIEWS (Web Interface)
# ============================================================================

from .models import Appointment, AppointmentReason, AppointmentStatus, ClinicNotification, WorkingHours
from .utils import (
    send_appointment_notification_to_clinic, 
    send_appointment_cancellation_to_clinic,
    create_clinic_notification
)
from pet.models import Pet


class AppointmentBookingView(LoginRequiredMixin, View):
    """Book an appointment at a clinic"""
    template_name = 'vets/appointments/book_appointment.html'
    
    def get(self, request, slug):
        clinic = get_object_or_404(Clinic, slug=slug, email_confirmed=True)
        
        # Get user's pets
        pets = Pet.objects.filter(user=request.user)
        if not pets.exists():
            messages.warning(request, "Please add a pet first before booking an appointment.")
            return redirect('pet:pet_add')
        
        # Get appointment reasons
        reasons = AppointmentReason.objects.filter(is_active=True)
        
        # Get working hours
        working_hours = clinic.working_hours_schedule.all().order_by('day_of_week')
        
        context = {
            'clinic': clinic,
            'pets': pets,
            'reasons': reasons,
            'working_hours': working_hours,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, slug):
        from django.utils import timezone
        
        clinic = get_object_or_404(Clinic, slug=slug, email_confirmed=True)
        
        # Get form data
        pet_id = request.POST.get('pet')
        date_str = request.POST.get('appointment_date')
        time_str = request.POST.get('appointment_time')
        reason_id = request.POST.get('reason')
        reason_text = request.POST.get('reason_text', '')
        notes = request.POST.get('notes', '')
        
        # Validate
        errors = []
        
        # Validate pet
        try:
            pet = Pet.objects.get(pk=pet_id, user=request.user)
        except Pet.DoesNotExist:
            errors.append("Invalid pet selected.")
            pet = None
        
        # Validate date
        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if appointment_date < timezone.now().date():
                errors.append("Appointment date must be in the future.")
        except (ValueError, TypeError):
            errors.append("Invalid date format.")
            appointment_date = None
        
        # Validate time
        try:
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
        except (ValueError, TypeError):
            errors.append("Invalid time format.")
            appointment_time = None
        
        # Validate reason
        reason = None
        if reason_id:
            try:
                reason = AppointmentReason.objects.get(pk=reason_id, is_active=True)
            except AppointmentReason.DoesNotExist:
                pass
        
        if not reason and not reason_text:
            errors.append("Please select a reason or provide a description.")
        
        # Check working hours
        if appointment_date and appointment_time:
            day_of_week = appointment_date.weekday()
            try:
                working_hours = clinic.working_hours_schedule.get(day_of_week=day_of_week)
                if working_hours.is_closed:
                    errors.append(f"The clinic is closed on {working_hours.get_day_of_week_display()}.")
                elif working_hours.open_time and working_hours.close_time:
                    if appointment_time < working_hours.open_time:
                        errors.append(f"Clinic opens at {working_hours.open_time.strftime('%H:%M')}.")
                    if appointment_time >= working_hours.close_time:
                        errors.append(f"Clinic closes at {working_hours.close_time.strftime('%H:%M')}.")
            except WorkingHours.DoesNotExist:
                pass
            
            # Check for conflicting appointments
            existing = Appointment.objects.filter(
                clinic=clinic,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
            ).exists()
            if existing:
                errors.append("This time slot is already booked. Please choose another time.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('vets:book_appointment', slug=slug)
        
        # Create appointment
        appointment = Appointment.objects.create(
            clinic=clinic,
            user=request.user,
            pet=pet,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            reason_text=reason_text,
            notes=notes,
            status=AppointmentStatus.PENDING,
            clinic_notified_at=timezone.now()
        )
        
        # Create notification for clinic
        create_clinic_notification(
            clinic=clinic,
            notification_type='NEW_APPOINTMENT',
            title=f'New Appointment: {pet.name}',
            message=f'New appointment booked for {pet.name} on {appointment_date} at {appointment_time.strftime("%H:%M")}. Reference: {appointment.reference_code}',
            appointment=appointment
        )
        
        # Create notification for user (confirmation of booking)
        from core.models import UserNotification, NotificationType
        UserNotification.create_notification(
            user=request.user,
            notification_type=NotificationType.NEW_APPOINTMENT,
            title=f"Appointment Requested",
            message=f"Your appointment request for {pet.name} at {clinic.name} on {appointment_date.strftime('%B %d, %Y')} at {appointment_time.strftime('%H:%M')} has been submitted. The clinic will confirm shortly.",
            link=f"/en/vets/appointment/{appointment.pk}/",
            action_required=False
        )
        
        # Send email notification
        send_appointment_notification_to_clinic(appointment)
        
        messages.success(request, f"Appointment booked successfully! Reference: {appointment.reference_code}")
        return redirect('vets:my_appointments')


class MyAppointmentsView(LoginRequiredMixin, ListView):
    """User's appointments list"""
    template_name = 'vets/appointments/my_appointments.html'
    context_object_name = 'appointments'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Appointment.objects.filter(
            user=self.request.user
        ).select_related('clinic', 'pet', 'reason').order_by('-appointment_date', '-appointment_time')
        
        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = AppointmentStatus.choices
        context['current_status'] = self.request.GET.get('status', '')
        return context


class AppointmentDetailUserView(LoginRequiredMixin, DetailView):
    """User view of appointment details"""
    template_name = 'vets/appointments/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        return Appointment.objects.filter(
            user=self.request.user
        ).select_related('clinic', 'pet', 'reason')


class CancelAppointmentView(LoginRequiredMixin, View):
    """Cancel an appointment"""
    
    def post(self, request, pk):
        from django.utils import timezone
        
        appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
        
        if not appointment.can_cancel:
            messages.error(request, "This appointment cannot be cancelled. Cancellations must be made at least 24 hours before the appointment.")
            return redirect('vets:appointment_detail', pk=pk)
        
        cancellation_reason = request.POST.get('cancellation_reason', '')
        
        appointment.status = AppointmentStatus.CANCELLED_BY_USER
        appointment.cancelled_at = timezone.now()
        appointment.cancellation_reason = cancellation_reason
        appointment.save()
        
        # Create notification for clinic
        create_clinic_notification(
            clinic=appointment.clinic,
            notification_type='CANCELLED_APPOINTMENT',
            title=f'Appointment Cancelled: {appointment.pet.name}',
            message=f'The appointment for {appointment.pet.name} on {appointment.appointment_date} has been cancelled.',
            appointment=appointment
        )
        
        # Send email
        send_appointment_cancellation_to_clinic(appointment)
        
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('vets:my_appointments')


class ClinicAvailableSlotsAPIView(LoginRequiredMixin, View):
    """AJAX endpoint to get available slots for a date"""
    
    def get(self, request, slug):
        from django.utils import timezone
        
        clinic = get_object_or_404(Clinic, slug=slug, email_confirmed=True)
        date_str = request.GET.get('date')
        
        if not date_str:
            return JsonResponse({'error': 'Date required'}, status=400)
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        if target_date < timezone.now().date():
            return JsonResponse({'error': 'Cannot book in the past'}, status=400)
        
        # Get working hours
        day_of_week = target_date.weekday()
        try:
            working_hours = clinic.working_hours_schedule.get(day_of_week=day_of_week)
        except WorkingHours.DoesNotExist:
            return JsonResponse({
                'is_open': False,
                'slots': [],
                'message': 'Working hours not set'
            })
        
        if working_hours.is_closed or not working_hours.open_time or not working_hours.close_time:
            return JsonResponse({
                'is_open': False,
                'slots': [],
                'message': 'Clinic closed on this day'
            })
        
        # Generate slots
        slots = []
        duration = 30  # minutes
        current_time = datetime.combine(target_date, working_hours.open_time)
        end_time = datetime.combine(target_date, working_hours.close_time)
        
        # If today, start from now + 1 hour
        if target_date == timezone.now().date():
            min_time = timezone.now() + timedelta(hours=1)
            if current_time < min_time:
                minutes = (min_time.minute // duration + 1) * duration
                current_time = min_time.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)
        
        # Get booked slots
        booked = set(Appointment.objects.filter(
            clinic=clinic,
            appointment_date=target_date,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).values_list('appointment_time', flat=True))
        
        while current_time + timedelta(minutes=duration) <= end_time:
            slot_time = current_time.time()
            if slot_time not in booked:
                slots.append(slot_time.strftime('%H:%M'))
            current_time += timedelta(minutes=duration)
        
        return JsonResponse({
            'is_open': True,
            'slots': slots,
            'open_time': working_hours.open_time.strftime('%H:%M'),
            'close_time': working_hours.close_time.strftime('%H:%M')
        })


# ============================================================================
# CLINIC DASHBOARD - APPOINTMENTS MANAGEMENT
# ============================================================================

class ClinicAppointmentsDashboardView(ClinicOwnerRequiredMixin, ListView):
    """Clinic dashboard appointments list"""
    template_name = 'vets/dashboard/appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Appointment.objects.filter(
            clinic=self.clinic
        ).select_related('pet', 'user', 'reason')
        
        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date
        date_filter = self.request.GET.get('date')
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date=filter_date)
            except ValueError:
                pass
        
        # Default ordering
        return queryset.order_by('appointment_date', 'appointment_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic'] = self.clinic
        context['status_choices'] = AppointmentStatus.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['current_date'] = self.request.GET.get('date', '')
        
        # Get today's and upcoming counts
        from django.utils import timezone
        today = timezone.now().date()
        
        context['today_count'] = Appointment.objects.filter(
            clinic=self.clinic,
            appointment_date=today,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).count()
        
        context['pending_count'] = Appointment.objects.filter(
            clinic=self.clinic,
            status=AppointmentStatus.PENDING
        ).count()
        
        return context


class ClinicAppointmentDetailView(ClinicOwnerRequiredMixin, DetailView):
    """Clinic view of appointment details"""
    template_name = 'vets/dashboard/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        return Appointment.objects.filter(
            clinic=self.clinic
        ).select_related('pet', 'user', 'reason')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic'] = self.clinic
        
        # Get user profile info
        appointment = self.object
        if hasattr(appointment.user, 'profile'):
            context['user_profile'] = appointment.user.profile
        
        return context


class ClinicUpdateAppointmentView(ClinicOwnerRequiredMixin, View):
    """Update appointment status from clinic dashboard"""
    
    def post(self, request, pk):
        from django.utils import timezone
        from .utils import send_appointment_status_update_to_user
        
        appointment = get_object_or_404(Appointment, pk=pk, clinic=self.clinic)
        
        new_status = request.POST.get('status')
        cancellation_reason = request.POST.get('cancellation_reason', '')
        
        if new_status not in [s[0] for s in AppointmentStatus.choices]:
            messages.error(request, "Invalid status.")
            return redirect('vets:clinic_appointment_detail', pk=pk)
        
        appointment.status = new_status
        
        if new_status == AppointmentStatus.CONFIRMED:
            appointment.confirmed_at = timezone.now()
            messages.success(request, "Appointment confirmed.")
        elif new_status == AppointmentStatus.CANCELLED_BY_CLINIC:
            appointment.cancelled_at = timezone.now()
            appointment.cancellation_reason = cancellation_reason
            messages.success(request, "Appointment cancelled.")
        elif new_status == AppointmentStatus.COMPLETED:
            messages.success(request, "Appointment marked as completed.")
        elif new_status == AppointmentStatus.NO_SHOW:
            messages.success(request, "Appointment marked as no-show.")
        
        appointment.save()
        
        # Send notification to user
        send_appointment_status_update_to_user(appointment)
        
        return redirect('vets:clinic_appointments')


class ClinicNotificationsView(ClinicOwnerRequiredMixin, ListView):
    """Clinic notifications list"""
    template_name = 'vets/dashboard/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return ClinicNotification.objects.filter(
            clinic=self.clinic
        ).select_related('appointment').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic'] = self.clinic
        context['unread_count'] = ClinicNotification.objects.filter(
            clinic=self.clinic,
            is_read=False
        ).count()
        return context


class MarkNotificationReadView(ClinicOwnerRequiredMixin, View):
    """Mark a notification as read"""
    
    def post(self, request, pk):
        notification = get_object_or_404(ClinicNotification, pk=pk, clinic=self.clinic)
        notification.mark_as_read()
        
        # If AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('vets:clinic_notifications')


class MarkAllNotificationsReadView(ClinicOwnerRequiredMixin, View):
    """Mark all notifications as read"""
    
    def post(self, request):
        from django.utils import timezone
        
        ClinicNotification.objects.filter(
            clinic=self.clinic,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        messages.success(request, "All notifications marked as read.")
        return redirect('vets:clinic_notifications')
