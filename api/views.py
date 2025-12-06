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

from userapp.models import Profile, CustomUser
from userapp.serializers import ProfileSerializer, SignupSerializer, ForgotPasswordSerializer, ResetPasswordSerializer

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
