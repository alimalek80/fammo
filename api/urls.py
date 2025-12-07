from django.urls import path, include
from .views import (
    PingView,
    AppConfigView,
    MeProfileView,
    MyPetsListCreateView,
    MyPetDetailView,
    PetTypeListView,
    GenderListView,
    AgeCategoryListView,
    BreedListView,
    FoodTypeListView,
    FoodFeelingListView,
    FoodImportanceListView,
    BodyTypeListView,
    ActivityLevelListView,
    FoodAllergyListView,
    HealthIssueListView,
    TreatFrequencyListView,
    LanguageListView,
    SetUserLanguageView,
    OnboardingSlideListView,
    SignupView,
    ForgotPasswordView,
    ResetPasswordView,
    ResendActivationEmailView,
    DeleteTestUserView,
    # Clinic views
    ClinicListCreateView,
    ClinicDetailView,
    MyClinicView,
    ConfirmClinicEmailView,
    ClinicWorkingHoursView,
    ClinicVetProfileView,
    SearchClinicsView,
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
    
    # Pet Form Options
    path("pet-types/", PetTypeListView.as_view(), name="api-pet-types"),
    path("genders/", GenderListView.as_view(), name="api-genders"),
    path("age-categories/", AgeCategoryListView.as_view(), name="api-age-categories"),
    path("breeds/", BreedListView.as_view(), name="api-breeds"),
    path("food-types/", FoodTypeListView.as_view(), name="api-food-types"),
    path("food-feelings/", FoodFeelingListView.as_view(), name="api-food-feelings"),
    path("food-importance/", FoodImportanceListView.as_view(), name="api-food-importance"),
    path("body-types/", BodyTypeListView.as_view(), name="api-body-types"),
    path("activity-levels/", ActivityLevelListView.as_view(), name="api-activity-levels"),
    path("food-allergies/", FoodAllergyListView.as_view(), name="api-food-allergies"),
    path("health-issues/", HealthIssueListView.as_view(), name="api-health-issues"),
    path("treat-frequencies/", TreatFrequencyListView.as_view(), name="api-treat-frequencies"),
    
    # Clinics
    path("clinics/", ClinicListCreateView.as_view(), name="api-clinics-list-create"),
    path("clinics/my/", MyClinicView.as_view(), name="api-my-clinic"),
    path("clinics/search/", SearchClinicsView.as_view(), name="api-clinics-search"),
    path("clinics/confirm-email/<str:token>/", ConfirmClinicEmailView.as_view(), name="api-clinic-confirm-email"),
    path("clinics/<int:pk>/", ClinicDetailView.as_view(), name="api-clinic-detail"),
    path("clinics/<int:clinic_id>/working-hours/", ClinicWorkingHoursView.as_view(), name="api-clinic-working-hours"),
    path("clinics/<int:clinic_id>/vet-profile/", ClinicVetProfileView.as_view(), name="api-clinic-vet-profile"),
    
    # AI Core endpoints (nutrition predictions, etc.)
    path("", include('ai_core.urls')),
]
