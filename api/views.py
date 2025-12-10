from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
import secrets
import string

from userapp.models import Profile, CustomUser
from userapp.serializers import ProfileSerializer, SignupSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from .serializers import CombinedClinicUserRegistrationSerializer


from pet.models import (
    Pet, PetType, Gender, AgeCategory, Breed,
    FoodType, FoodFeeling, FoodImportance, BodyType,
    ActivityLevel, FoodAllergy, HealthIssue, TreatFrequency
)
from pet.serializers import (
    PetSerializer, PetTypeSerializer, GenderSerializer,
    AgeCategorySerializer, BreedSerializer, FoodTypeSerializer,
    FoodFeelingSerializer, FoodImportanceSerializer, BodyTypeSerializer,
    ActivityLevelSerializer, FoodAllergySerializer, HealthIssueSerializer,
    TreatFrequencySerializer
)

from core.models import OnboardingSlide
from core.serializers import OnboardingSlideSerializer

from vets.models import Clinic, WorkingHours, VetProfile
from vets.serializers import (
    ClinicListSerializer, ClinicDetailSerializer, ClinicRegistrationSerializer,
    ClinicUpdateSerializer, WorkingHoursSerializer, WorkingHoursUpdateSerializer,
    VetProfileSerializer, VetProfileUpdateSerializer
)

class PingView(APIView):
    def get(self, request):
        return Response({"message": "pong from FAMMO API"})


class AppConfigView(APIView):
    """
    GET /api/v1/config/
    Returns app configuration including static asset URLs
    No authentication required - needed on app launch
    """
    permission_classes = []
    
    def get(self, request):
        # Build absolute URLs
        base_url = request.build_absolute_uri('/').rstrip('/')
        
        return Response({
            "base_url": base_url,
            "static_url": f"{base_url}{settings.STATIC_URL}",
            "media_url": f"{base_url}{settings.MEDIA_URL}",
            "assets": {
                "logo": f"{base_url}{settings.STATIC_URL}images/logo.png",
                "favicon": f"{base_url}{settings.STATIC_URL}images/favicon.png",
                "placeholder_pet": f"{base_url}{settings.STATIC_URL}images/pet-waiting.gif",
            },
            "api_version": "1.0.0",
        })


class LanguageListView(APIView):
    """
    GET /api/v1/languages/
    Returns list of available languages for mobile app language selection
    No authentication required - shown on first launch
    """
    permission_classes = []
    
    def get(self, request):
        languages = [
            {
                "code": code,
                "name": name,
                "native_name": name  # Same as name for now, can be customized
            }
            for code, name in settings.LANGUAGES
        ]
        return Response({"languages": languages})


class SetUserLanguageView(APIView):
    """
    POST /api/v1/me/language/
    Set user's preferred language
    Request body: {"language": "en"} (or "tr", "nl", "fi")
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        language_code = request.data.get('language')
        
        if not language_code:
            return Response(
                {"error": "Language code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate language code
        valid_languages = [code for code, name in settings.LANGUAGES]
        if language_code not in valid_languages:
            return Response(
                {
                    "error": f"Invalid language code. Must be one of: {', '.join(valid_languages)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update user's profile
        profile = request.user.profile
        profile.preferred_language = language_code
        profile.save()
        
        return Response({
            "success": True,
            "language": language_code,
            "message": f"Language preference updated to {language_code}"
        })
    
    def get(self, request):
        """
        GET /api/v1/me/language/
        Returns user's current language preference
        """
        profile = request.user.profile
        return Response({
            "language": profile.preferred_language
        })
    
class MeProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)
    
class MyPetsListCreateView(generics.ListCreateAPIView):

    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyPetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(user=self.request.user)


# Pet Form Options Views
class PetTypeListView(generics.ListAPIView):
    """GET /api/v1/pet-types/ - List all pet types (Cat, Dog, etc.)"""
    serializer_class = PetTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PetType.objects.all()


class GenderListView(generics.ListAPIView):
    """GET /api/v1/genders/ - List all genders"""
    serializer_class = GenderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Gender.objects.all()


class AgeCategoryListView(generics.ListAPIView):
    """GET /api/v1/age-categories/ - List all age categories, optionally filtered by pet_type"""
    serializer_class = AgeCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AgeCategory.objects.all().order_by('order')
        pet_type_id = self.request.query_params.get('pet_type', None)
        if pet_type_id:
            queryset = queryset.filter(pet_type_id=pet_type_id)
        return queryset


class BreedListView(generics.ListAPIView):
    """GET /api/v1/breeds/ - List all breeds, optionally filtered by pet_type"""
    serializer_class = BreedSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Breed.objects.all().order_by('name')
        pet_type_id = self.request.query_params.get('pet_type', None)
        if pet_type_id:
            queryset = queryset.filter(pet_type_id=pet_type_id)
        return queryset


class FoodTypeListView(generics.ListAPIView):
    """GET /api/v1/food-types/ - List all food types"""
    serializer_class = FoodTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FoodType.objects.all()


class FoodFeelingListView(generics.ListAPIView):
    """GET /api/v1/food-feelings/ - List all food feelings"""
    serializer_class = FoodFeelingSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FoodFeeling.objects.all()


class FoodImportanceListView(generics.ListAPIView):
    """GET /api/v1/food-importance/ - List all food importance levels"""
    serializer_class = FoodImportanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FoodImportance.objects.all()


class BodyTypeListView(generics.ListAPIView):
    """GET /api/v1/body-types/ - List all body types"""
    serializer_class = BodyTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BodyType.objects.all()


class ActivityLevelListView(generics.ListAPIView):
    """GET /api/v1/activity-levels/ - List all activity levels"""
    serializer_class = ActivityLevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ActivityLevel.objects.all().order_by('order')


class FoodAllergyListView(generics.ListAPIView):
    """GET /api/v1/food-allergies/ - List all food allergies"""
    serializer_class = FoodAllergySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FoodAllergy.objects.all().order_by('order')


class HealthIssueListView(generics.ListAPIView):
    """GET /api/v1/health-issues/ - List all health issues"""
    serializer_class = HealthIssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = HealthIssue.objects.all().order_by('order')


class TreatFrequencyListView(generics.ListAPIView):
    """GET /api/v1/treat-frequencies/ - List all treat frequency options"""
    serializer_class = TreatFrequencySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = TreatFrequency.objects.all()


class OnboardingSlideListView(generics.ListAPIView):
    """
    GET /api/v1/onboarding/
    Returns active onboarding slides ordered by 'order' field
    No authentication required - shown on first app launch
    Supports language headers for localized content
    """
    serializer_class = OnboardingSlideSerializer
    permission_classes = []
    
    def get_queryset(self):
        return OnboardingSlide.objects.filter(is_active=True).order_by('order')


class SignupView(generics.CreateAPIView):
    """
    POST /api/auth/signup/
    Register a new user account
    Request body: {"email": "user@example.com", "password": "...", "password_confirm": "..."}
    """
    serializer_class = SignupSerializer
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Set user inactive until email confirmation
            user.is_active = False
            user.save()
            
            # Ensure profile exists (should be created by signal, but double-check)
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)
            
            # Send activation email (same as website registration)
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Add source=app parameter so activation knows user came from mobile app
            activation_url = f"http://{current_site.domain}/en/users/activate/{uid}/{token}/?source=app"
            
            subject = "Activate your Fammo account"
            html_message = render_to_string('userapp/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
                'from_app': True,  # Flag to show app-specific messaging in template
            })
            
            # Create plain text version as fallback
            plain_message = f"""
Hello {user.email},

Thank you for joining Fammo! We're thrilled to have you as part of our community.

To activate your account, please visit:
{activation_url}

This activation link will expire in 24 hours.

Best regards,
The Fammo Team
            """.strip()
            
            # Send email with HTML
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            return Response({
                "success": True,
                "message": "Registration successful. Please check your email to activate your account.",
                "user": {
                    "id": user.id,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "error": f"Registration failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/
    Request password reset email
    Request body: {"email": "user@example.com"}
    """
    permission_classes = []
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset link
            base_url = request.build_absolute_uri('/').rstrip('/')
            reset_link = f"{base_url}/reset-password/{uid}/{token}/"
            
            # Send email
            subject = "Password Reset Request"
            message = f"Click the link below to reset your password:\n\n{reset_link}\n\nIf you didn't request this, please ignore this email."
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
        except CustomUser.DoesNotExist:
            # Don't reveal if email exists or not for security
            pass
        
        return Response({
            "success": True,
            "message": "If an account with this email exists, a password reset link has been sent."
        })


class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/
    Reset password using token from email
    Request body: {"token": "...", "uid": "...", "password": "...", "password_confirm": "..."}
    """
    permission_classes = []
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        
        if not uid or not token:
            return Response({
                "error": "Both uid and token are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=user_id)
            
            if not default_token_generator.check_token(user, token):
                return Response({
                    "error": "Invalid or expired token"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = ResetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user.set_password(serializer.validated_data['password'])
            user.save()
            
            return Response({
                "success": True,
                "message": "Password has been reset successfully"
            })
            
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({
                "error": "Invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)


class ResendActivationEmailView(APIView):
    """
    POST /api/auth/resend-activation/
    Resend activation email for testing purposes
    Request body: {"email": "user@example.com"}
    """
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                "error": "Email is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Only resend if user is inactive
            if user.is_active:
                return Response({
                    "error": "This account is already activated"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Resend activation email
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Add source=app parameter for mobile app users
            activation_url = f"http://{current_site.domain}/en/users/activate/{uid}/{token}/?source=app"
            
            subject = "Activate your Fammo account"
            html_message = render_to_string('userapp/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
                'from_app': True,  # Flag to show app-specific messaging
            })
            
            # Create plain text version as fallback
            plain_message = f"""
Hello {user.email},

To activate your account, please visit:
{activation_url}

This activation link will expire in 24 hours.

Best regards,
The Fammo Team
            """.strip()
            
            # Send email with HTML
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            return Response({
                "success": True,
                "message": "Activation email has been resent successfully"
            })
            
        except CustomUser.DoesNotExist:
            return Response({
                "error": "No account found with this email"
            }, status=status.HTTP_404_NOT_FOUND)


class DeleteTestUserView(APIView):
    """
    DELETE /api/auth/delete-test-user/
    Delete a test user account (only in DEBUG mode)
    Request body: {"email": "user@example.com"}
    WARNING: Only enable this in development/testing environments
    """
    permission_classes = []
    
    def delete(self, request):
        # Only allow in DEBUG mode for security
        if not settings.DEBUG:
            return Response({
                "error": "This endpoint is only available in DEBUG mode"
            }, status=status.HTTP_403_FORBIDDEN)
        
        email = request.data.get('email')
        
        if not email:
            return Response({
                "error": "Email is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
            user_email = user.email
            
            # Delete user (this will cascade delete Profile and related objects)
            user.delete()
            
            return Response({
                "success": True,
                "message": f"User {user_email} has been deleted successfully"
            })
            
        except CustomUser.DoesNotExist:
            return Response({
                "error": "No account found with this email"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": f"Error deleting user: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# CLINIC API ENDPOINTS
# ============================================================================

class ClinicListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/clinics/
    List all active clinics (email confirmed and admin approved)
    
    Query parameters:
    - ?show_all=true : Show all clinics (including unconfirmed/unapproved)
    - ?verified_email=true : Show all clinics with email confirmed (regardless of admin approval)
    - ?city=Paris : Filter by city
    - ?eoi=true : Filter by Expression of Interest
    
    POST /api/v1/clinics/
    Create a new clinic (requires authentication)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClinicRegistrationSerializer
        return ClinicListSerializer
    
    def get_queryset(self):
        queryset = Clinic.objects.all()
        
        # Filter by status
        show_all = self.request.query_params.get('show_all', 'false').lower() == 'true'
        verified_email = self.request.query_params.get('verified_email', 'false').lower() == 'true'
        
        if verified_email:
            # Show all clinics with email confirmed (regardless of admin approval)
            queryset = queryset.filter(email_confirmed=True)
        elif not show_all:
            # Default: show only active clinics (email confirmed AND admin approved)
            queryset = queryset.filter(email_confirmed=True, admin_approved=True)
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by EOI status
        eoi = self.request.query_params.get('eoi')
        if eoi:
            queryset = queryset.filter(clinic_eoi=eoi.lower() == 'true')
        
        return queryset.select_related('owner').order_by('-created_at')
    
    def perform_create(self, serializer):
        clinic = serializer.save(owner=self.request.user)
        # Send confirmation email
        clinic.send_confirmation_email()


class ClinicDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/v1/clinics/<id>/
    Retrieve clinic details
    
    PUT/PATCH /api/v1/clinics/<id>/
    Update clinic (owner only)
    
    DELETE /api/v1/clinics/<id>/
    Delete clinic (owner only)
    """
    queryset = Clinic.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ClinicUpdateSerializer
        return ClinicDetailSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_update(self, serializer):
        # Only owner can update
        if self.get_object().owner != self.request.user:
            raise permissions.PermissionDenied("You don't have permission to edit this clinic")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only owner can delete
        if instance.owner != self.request.user:
            raise permissions.PermissionDenied("You don't have permission to delete this clinic")
        instance.delete()


class MyClinicView(APIView):
    """
    GET /api/v1/clinics/my/
    Get current user's clinic
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            clinic = Clinic.objects.get(owner=request.user)
            serializer = ClinicDetailSerializer(clinic)
            return Response(serializer.data)
        except Clinic.DoesNotExist:
            return Response(
                {"error": "You don't have a clinic registered"},
                status=status.HTTP_404_NOT_FOUND
            )


class ConfirmClinicEmailView(APIView):
    """
    GET /api/v1/clinics/confirm-email/<token>/
    Confirm clinic email address AND activate user account in one action.
    This replaces separate user activation and clinic confirmation.
    
    For web browsers: Shows confirmation page
    For API calls: Returns JSON response
    """
    permission_classes = []
    
    def get(self, request, token):
        try:
            clinic = Clinic.objects.get(email_confirmation_token=token)
            user = clinic.owner
            
            # Check if already confirmed
            if clinic.email_confirmed and user.is_active:
                # If browser, show confirmation page
                if 'text/html' in request.headers.get('Accept', ''):
                    from django.shortcuts import render
                    return render(request, 'vets/email_confirmed.html', {
                        'clinic': clinic,
                        'message': 'Your email has already been confirmed.'
                    })
                
                # If API call, return JSON
                return Response({
                    "message": "Email already confirmed and account already activated",
                    "clinic_id": clinic.id,
                    "user_id": user.id
                })
            
            # Confirm clinic email
            clinic.email_confirmed = True
            clinic.email_confirmation_token = ''
            clinic.save()
            
            # Activate user account
            user.is_active = True
            user.save()
            
            # Check if request is from browser (has Accept: text/html header)
            if 'text/html' in request.headers.get('Accept', ''):
                # Show confirmation page directly
                from django.shortcuts import render
                return render(request, 'vets/email_confirmed.html', {
                    'clinic': clinic,
                    'message': 'Email confirmed and account activated successfully! Your clinic is now pending admin approval.'
                })
            
            # Return JSON for API calls
            return Response({
                "message": "Email confirmed and account activated successfully. Your clinic is now pending admin approval.",
                "clinic_id": clinic.id,
                "user_id": user.id,
                "user_email": user.email,
                "admin_approved": clinic.admin_approved
            })
            
        except Clinic.DoesNotExist:
            # If browser, show error page
            if 'text/html' in request.headers.get('Accept', ''):
                from django.shortcuts import render
                return render(request, 'vets/email_confirmation_error.html', {
                    'error': 'Invalid or expired confirmation link. Please contact support.'
                }, status=404)
            
            # If API call, return JSON error
            return Response(
                {"error": "Invalid confirmation token"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        except Clinic.DoesNotExist:
            return Response(
                {"error": "Invalid confirmation token"},
                status=status.HTTP_404_NOT_FOUND
            )


class SendClinicConfirmationEmailView(APIView):
    """
    POST /api/v1/clinics/send-confirmation-email/
    Send/Resend clinic confirmation email to clinic owner
    
    Request body: {"clinic_id": <int>}
    
    Used by Flutter app after clinic registration to ensure clinic gets
    the clinic confirmation email (not user activation email)
    """
    permission_classes = []
    
    def post(self, request):
        clinic_id = request.data.get('clinic_id')
        
        if not clinic_id:
            return Response(
                {'error': 'clinic_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            clinic = Clinic.objects.get(id=clinic_id)
            
            if not clinic.email:
                return Response(
                    {'error': 'Clinic does not have an email address'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate new token if needed
            if not clinic.email_confirmation_token:
                clinic.email_confirmation_token = secrets.token_urlsafe(32)
                clinic.save()
            
            # Send clinic confirmation email
            current_site = get_current_site(request)
            clinic_confirmation_url = f"http://{current_site.domain}/api/v1/clinics/confirm-email/{clinic.email_confirmation_token}/?source=app"
            
            clinic_subject = "Confirm your clinic email address on Fammo"
            clinic_html_message = render_to_string('vets/clinic_confirmation_email.html', {
                'clinic': clinic,
                'domain': current_site.domain,
                'confirmation_url': clinic_confirmation_url,
                'token': clinic.email_confirmation_token,
                'from_app': True,
            }) if 'vets/clinic_confirmation_email.html' in str(settings.TEMPLATES) else None
            
            clinic_plain_message = f"""
Hello,

Thank you for registering your clinic on Fammo. To verify your clinic email address and make your clinic visible in the directory, please click the link below:

{clinic_confirmation_url}

After you confirm your email, your clinic will be pending admin review for public listing.

Best regards,
The Fammo Team
            """.strip()
            
            clinic_email = EmailMultiAlternatives(
                subject=clinic_subject,
                body=clinic_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[clinic.email]
            )
            if clinic_html_message:
                clinic_email.attach_alternative(clinic_html_message, "text/html")
            clinic_email.send()
            
            return Response({
                "success": True,
                "message": "Clinic confirmation email sent successfully",
                "clinic_id": clinic.id,
                "confirmation_url": clinic_confirmation_url,
                "email_sent_to": clinic.email
            }, status=status.HTTP_200_OK)
            
        except Clinic.DoesNotExist:
            return Response(
                {'error': 'Clinic not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to send confirmation email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClinicWorkingHoursView(APIView):
    """
    GET /api/v1/clinics/<clinic_id>/working-hours/
    Get working hours for a clinic
    
    POST /api/v1/clinics/<clinic_id>/working-hours/
    Create/Update working hours (bulk operation)
    """
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get(self, request, clinic_id):
        try:
            clinic = Clinic.objects.get(id=clinic_id)
            working_hours = WorkingHours.objects.filter(clinic=clinic).order_by('day_of_week')
            serializer = WorkingHoursSerializer(working_hours, many=True)
            return Response(serializer.data)
        except Clinic.DoesNotExist:
            return Response(
                {"error": "Clinic not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request, clinic_id):
        try:
            clinic = Clinic.objects.get(id=clinic_id)
            
            # Check permission
            if clinic.owner != request.user:
                return Response(
                    {"error": "You don't have permission to edit this clinic's working hours"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Expect array of working hours data
            hours_data = request.data if isinstance(request.data, list) else [request.data]
            
            created_hours = []
            errors = []
            
            for hour_data in hours_data:
                serializer = WorkingHoursUpdateSerializer(data=hour_data)
                if serializer.is_valid():
                    # Update or create
                    day = serializer.validated_data['day_of_week']
                    obj, created = WorkingHours.objects.update_or_create(
                        clinic=clinic,
                        day_of_week=day,
                        defaults=serializer.validated_data
                    )
                    created_hours.append(WorkingHoursSerializer(obj).data)
                else:
                    errors.append({
                        "day": hour_data.get('day_of_week'),
                        "errors": serializer.errors
                    })
            
            if errors:
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                "success": True,
                "working_hours": created_hours
            }, status=status.HTTP_201_CREATED)
            
        except Clinic.DoesNotExist:
            return Response(
                {"error": "Clinic not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ClinicVetProfileView(APIView):
    """
    GET /api/v1/clinics/<clinic_id>/vet-profile/
    Get vet profile for a clinic
    
    PUT/PATCH /api/v1/clinics/<clinic_id>/vet-profile/
    Update vet profile (owner only)
    """
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get(self, request, clinic_id):
        try:
            clinic = Clinic.objects.get(id=clinic_id)
            try:
                vet_profile = clinic.vet_profile
                serializer = VetProfileSerializer(vet_profile)
                return Response(serializer.data)
            except VetProfile.DoesNotExist:
                return Response(
                    {"error": "No vet profile found for this clinic"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Clinic.DoesNotExist:
            return Response(
                {"error": "Clinic not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def put(self, request, clinic_id):
        return self._update(request, clinic_id)
    
    def patch(self, request, clinic_id):
        return self._update(request, clinic_id, partial=True)
    
    def _update(self, request, clinic_id, partial=False):
        try:
            clinic = Clinic.objects.get(id=clinic_id)
            
            # Check permission
            if clinic.owner != request.user:
                return Response(
                    {"error": "You don't have permission to edit this vet profile"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get or create vet profile
            vet_profile, created = VetProfile.objects.get_or_create(clinic=clinic)
            
            serializer = VetProfileUpdateSerializer(
                vet_profile,
                data=request.data,
                partial=partial
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(VetProfileSerializer(vet_profile).data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Clinic.DoesNotExist:
            return Response(
                {"error": "Clinic not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class SearchClinicsView(APIView):
    """
    POST /api/v1/clinics/search/
    Search clinics by location, specialization, etc.
    """
    permission_classes = []
    
    def post(self, request):
        queryset = Clinic.objects.filter(email_confirmed=True, admin_approved=True)
        
        # Search by text (name, city, specializations)
        search_text = request.data.get('search')
        if search_text:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=search_text) |
                Q(city__icontains=search_text) |
                Q(specializations__icontains=search_text)
            )
        
        # Filter by location (radius search)
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        radius_km = request.data.get('radius', 50)  # Default 50km
        
        if latitude and longitude:
            # Simple bounding box filter
            # For production, consider using PostGIS for accurate distance calculations
            lat_range = float(radius_km) / 111  # Rough conversion: 1 degree ≈ 111 km
            lon_range = float(radius_km) / (111 * abs(float(latitude)))
            
            queryset = queryset.filter(
                latitude__range=(float(latitude) - lat_range, float(latitude) + lat_range),
                longitude__range=(float(longitude) - lon_range, float(longitude) + lon_range)
            )
        
        # Filter by EOI
        eoi = request.data.get('eoi')
        if eoi is not None:
            queryset = queryset.filter(clinic_eoi=eoi)
        
        serializer = ClinicListSerializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        })
    

class CombinedClinicUserClinicRegistrationView(APIView):
    """
    POST /api/v1/clinics/register/
    Register a new user and clinic in one request (unauthenticated)
    """
    permission_classes = []

    def post(self, request):
        serializer = CombinedClinicUserRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data

        # Create user
        user = CustomUser.objects.create_user(
            email=data['email'],
            password=data['password']
        )
        user.is_active = False  # Require email confirmation
        user.save()
        profile, created = Profile.objects.get_or_create(user=user)
        profile.first_name = data.get('first_name', '')
        profile.last_name = data.get('last_name', '')
        profile.save()

        # Create clinic
        try:
            clinic = Clinic.objects.create(
                owner=user,
                name=data['clinic_name'],
                address=data.get('address', ''),
                city=data.get('city', ''),
                phone=data.get('phone', ''),
                email=data.get('email_clinic', ''),
                website=data.get('website', ''),
                instagram=data.get('instagram', ''),
                specializations=data.get('specializations', ''),
                bio=data.get('bio', ''),
                clinic_eoi=data.get('clinic_eoi', False),
                latitude=data.get('latitude', None),
                longitude=data.get('longitude', None),
            )
            # Generate clinic email confirmation token
            clinic.email_confirmation_token = secrets.token_urlsafe(32)
            clinic.save()
        except IntegrityError:
            # Clean up the user that was just created
            user.delete()
            return Response(
                {"clinic_name": "A clinic with this name already exists. Please choose a different name."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Optionally create vet profile
        if data.get('vet_name'):
            from vets.models import VetProfile
            VetProfile.objects.create(
                clinic=clinic,
                vet_name=data['vet_name'],
                degrees=data.get('degrees', ''),
                certifications=data.get('certifications', '')
            )
        # Create working hours
        wh_data = data.get('working_hours', [])
        from vets.models import WorkingHours
        for wh in wh_data:
            try:
                WorkingHours.objects.create(
                    clinic=clinic,
                    day_of_week=wh.get('day_of_week') or wh.get('day'),
                    is_closed=wh.get('is_closed', False),
                    open_time=wh.get('open_time') or wh.get('start_time'),
                    close_time=wh.get('close_time') or wh.get('end_time')
                )
            except Exception as e:
                # Log the error but don't fail the registration
                print(f"[WORKING HOURS ERROR] {str(e)}")
        
        # Keep user inactive until clinic email is confirmed
        user.is_active = False
        user.save()
        
        # Send SINGLE combined confirmation email to clinic email
        # This email confirms BOTH the clinic and the user account
        current_site = get_current_site(request)
        clinic_confirmation_url = f"http://{current_site.domain}/api/v1/clinics/confirm-email/{clinic.email_confirmation_token}/?source=app"
        
        # Send confirmation email to user's email (the login email)
        # This email confirms both the clinic and activates the user account
        confirmation_email = user.email
        
        subject = f"Confirm your clinic email - {clinic.name}"
        
        # Create a combined confirmation message
        plain_message = f"""
Hello,

Thank you for registering {clinic.name} on Fammo!

To complete your registration and activate your account, please click the confirmation link below:

{clinic_confirmation_url}

This link will:
- Confirm your clinic registration
- Activate your user account
- Allow you to log in and manage your clinic

After you confirm, your clinic will be pending admin review for public listing in the directory.

If you have any questions, please contact us at support@fammo.ai

Best regards,
The Fammo Team
        """.strip()
        
        # Send to user's email with plain text message
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[confirmation_email]
        )
        email.send()
        
        return Response({
            "success": True,
            "message": "Registration successful. Please check your email to confirm your registration and activate your account.",
            "user": {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active
            },
            "clinic": {
                "id": clinic.id,
                "name": clinic.name,
                "email": clinic.email,
                "email_confirmation_token": clinic.email_confirmation_token,
                "confirmation_url": f"http://{get_current_site(request).domain}/vets/confirm-email/{clinic.email_confirmation_token}/?source=app"
            }
        }, status=status.HTTP_201_CREATED)


# AI Hub API Views
import json
import openai
from openai import OpenAI
from rest_framework import viewsets
from rest_framework.decorators import action
from datetime import datetime

from aihub.models import AIRecommendation, AIHealthReport, RecommendationType
from aihub.serializers import AIRecommendationSerializer, AIHealthReportSerializer
from aihub.views import MealPlan, HealthReport, get_client_ip
from subscription.models import AIUsage, first_day_of_current_month

openai.api_key = settings.OPENAI_API_KEY


class AIRecommendationViewSet(viewsets.ModelViewSet):
    """
    API endpoints for AI meal recommendations.
    
    - GET /api/v1/ai/recommendations/ - List all recommendations for current user's pets
    - POST /api/v1/ai/recommendations/generate-meal/ - Generate new meal recommendation
    - GET /api/v1/ai/recommendations/{id}/ - Get a specific recommendation
    """
    serializer_class = AIRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get all recommendations for current user's pets"""
        user_pets = self.request.user.pets.all()
        return AIRecommendation.objects.filter(pet__in=user_pets).order_by('-created_at')
    
    @action(detail=False, methods=['post'], url_path='generate-meal')
    def generate_meal(self, request):
        """
        Generate an AI meal recommendation for a specific pet.
        
        Request body:
        {
            "pet_id": <int>
        }
        
        Returns:
            - New AIRecommendation object with meal plan
            - Or error if monthly limit reached
        """
        pet_id = request.data.get('pet_id')
        
        if not pet_id:
            return Response(
                {'error': 'pet_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get pet and verify ownership
        pet = get_object_or_404(Pet, id=pet_id, user=request.user)
        
        # Check monthly limit
        start_of_month = datetime(now().year, now().month, 1)
        used_count = AIRecommendation.objects.filter(
            pet__user=request.user,
            type=RecommendationType.MEAL,
            created_at__gte=start_of_month
        ).count()
        
        user_profile = request.user.profile
        meal_limit = user_profile.subscription_plan.monthly_meal_limit if user_profile.subscription_plan else 3
        
        if not request.user.is_superuser and used_count >= meal_limit:
            return Response(
                {
                    'error': f'Monthly limit reached. You have used {used_count}/{meal_limit} meal recommendations this month.',
                    'used': used_count,
                    'limit': meal_limit
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        try:
            # Get pet profile
            pet_profile = pet.get_full_profile_for_ai()
            
            # Create prompt
            prompt = (
                "You are a professional pet nutritionist. Based on the pet profile below, generate a detailed one-day meal plan. "
                "Provide practical, safe, and nutritionally appropriate recommendations.\n\n"
                f"Pet Profile:\n{pet_profile}"
            )
            
            # Generate meal plan using OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=prompt,
                text_format=MealPlan,
            )
            
            meal_plan = response.output_parsed
            content_json = meal_plan.model_dump() if meal_plan else None
            content = json.dumps(content_json, indent=2) if content_json else ""
            
            # Save recommendation
            ip_address = get_client_ip(request)
            recommendation = AIRecommendation.objects.create(
                pet=pet,
                type=RecommendationType.MEAL,
                content=content,
                content_json=content_json,
                ip_address=ip_address
            )
            
            # Track usage
            if not request.user.is_superuser:
                usage, created = AIUsage.objects.get_or_create(
                    user=request.user,
                    month=first_day_of_current_month()
                )
                usage.meal_used += 1
                usage.save()
            
            serializer = AIRecommendationSerializer(recommendation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate meal recommendation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIHealthReportViewSet(viewsets.ModelViewSet):
    """
    API endpoints for AI health reports.
    
    - GET /api/v1/ai/health-reports/ - List all health reports for current user's pets
    - POST /api/v1/ai/health-reports/generate-report/ - Generate new health report
    - GET /api/v1/ai/health-reports/{id}/ - Get a specific health report
    """
    serializer_class = AIHealthReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get all health reports for current user's pets"""
        user_pets = self.request.user.pets.all()
        return AIHealthReport.objects.filter(pet__in=user_pets).order_by('-created_at')
    
    @action(detail=False, methods=['post'], url_path='generate-report')
    def generate_report(self, request):
        """
        Generate an AI health report for a specific pet.
        
        Request body:
        {
            "pet_id": <int>
        }
        
        Returns:
            - New AIHealthReport object with health insights
            - Or error if monthly limit reached
        """
        pet_id = request.data.get('pet_id')
        
        if not pet_id:
            return Response(
                {'error': 'pet_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get pet and verify ownership
        pet = get_object_or_404(Pet, id=pet_id, user=request.user)
        
        # Check monthly limit
        start_of_month = datetime(now().year, now().month, 1)
        used_count = AIHealthReport.objects.filter(
            pet__user=request.user,
            created_at__gte=start_of_month
        ).count()
        
        user_profile = request.user.profile
        health_limit = user_profile.subscription_plan.monthly_health_limit if user_profile.subscription_plan else 1
        
        if not request.user.is_superuser and used_count >= health_limit:
            return Response(
                {
                    'error': f'Monthly limit reached. You have used {used_count}/{health_limit} health reports this month.',
                    'used': used_count,
                    'limit': health_limit
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        try:
            # Get pet profile
            pet_profile = pet.get_full_profile_for_ai()
            
            # Create prompt
            prompt = (
                "You are a professional pet health consultant. Based on the pet profile below, generate a comprehensive health insight report. "
                "Be informative, concise, and provide actionable recommendations.\n\n"
                f"Pet Profile:\n{pet_profile}"
            )
            
            # Generate health report using OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=prompt,
                text_format=HealthReport,
            )
            
            health_data = response.output_parsed
            summary_json = health_data.model_dump() if health_data else None
            summary = json.dumps(summary_json, indent=2) if summary_json else ""
            
            # Save report
            ip_address = get_client_ip(request)
            report = AIHealthReport.objects.create(
                pet=pet,
                summary=summary,
                summary_json=summary_json,
                ip_address=ip_address
            )
            
            # Track usage
            if not request.user.is_superuser:
                usage, created = AIUsage.objects.get_or_create(
                    user=request.user,
                    month=first_day_of_current_month()
                )
                usage.health_used += 1
                usage.save()
            
            serializer = AIHealthReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate health report: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

