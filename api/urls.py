from django.urls import path, include
from .views import (
    PingView,
    AppConfigView,
    MeProfileView,
    MyPetsListCreateView,
    MyPetDetailView,
    LanguageListView,
    SetUserLanguageView,
    OnboardingSlideListView,
    SignupView,
    ForgotPasswordView,
    ResetPasswordView,
    ResendActivationEmailView,
    DeleteTestUserView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('ping/', PingView.as_view(), name='api-ping'),
    path('config/', AppConfigView.as_view(), name='api-config'),
    path('onboarding/', OnboardingSlideListView.as_view(), name='api-onboarding'),

    # JWT auth
    path('auth/signup/', SignupView.as_view(), name='api-signup'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='api-forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='api-reset-password'),
    path('auth/resend-activation/', ResendActivationEmailView.as_view(), name='api-resend-activation'),
    path('auth/delete-test-user/', DeleteTestUserView.as_view(), name='api-delete-test-user'),

    # Language management
    path('languages/', LanguageListView.as_view(), name='api-languages'),
    path('me/language/', SetUserLanguageView.as_view(), name='api-set-language'),

    # User profile
    path("me/", MeProfileView.as_view(), name="api-me"),

    #Pets
    path("pets/", MyPetsListCreateView.as_view(), name="api-my-pets"),
    path("pets/<int:pk>/", MyPetDetailView.as_view(), name="api-my-pet-detail"),
    
    # AI Core endpoints (nutrition predictions, etc.)
    path("", include('ai_core.urls')),
]
