from django.urls import path, include
from rest_framework.routers import DefaultRouter
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
    GoogleAuthView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView,
    ResendActivationEmailView,
    DeleteTestUserView,
    # Clinic views
    ClinicListCreateView,
    ClinicDetailView,
    MyClinicView,
    ConfirmClinicEmailView,
    SendClinicConfirmationEmailView,
    ClinicWorkingHoursView,
    ClinicVetProfileView,
    SearchClinicsView,
    CombinedClinicUserClinicRegistrationView,
    # Appointment views
    AppointmentReasonListView,
    MyAppointmentsListView,
    AppointmentCreateView,
    AppointmentDetailView,
    AppointmentCancelView,
    ClinicAvailableSlotsView,
    ClinicAvailableDatesView,
    ClinicAppointmentsListView,
    ClinicAppointmentDetailView,
    ClinicAppointmentUpdateView,
    ClinicNotificationsListView,
    ClinicNotificationMarkReadView,
    ClinicNotificationsMarkAllReadView,
    ClinicUnreadNotificationsCountView,
    # AI Hub views
    AIRecommendationViewSet,
    AIHealthReportViewSet,
    # User Notification & FCM views
    RegisterDeviceTokenView,
    UnregisterDeviceTokenView,
    UserNotificationsListView,
    UserNotificationMarkReadView,
    UserNotificationsMarkAllReadView,
    UserUnreadNotificationsCountView,
    DeleteUserNotificationView,
)
from core.legal_viewsets import (
    LegalDocumentViewSet,
    UserConsentViewSet,
    ClinicConsentViewSet,
    ConsentLogViewSet,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Initialize router for viewsets
router = DefaultRouter()
router.register(r'ai/recommendations', AIRecommendationViewSet, basename='ai-recommendations')
router.register(r'ai/health-reports', AIHealthReportViewSet, basename='ai-health-reports')
router.register(r'legal/documents', LegalDocumentViewSet, basename='legal-documents')
router.register(r'legal/consent/user', UserConsentViewSet, basename='legal-user-consent')
router.register(r'legal/consent/clinic', ClinicConsentViewSet, basename='legal-clinic-consent')
router.register(r'legal/logs', ConsentLogViewSet, basename='legal-consent-logs')


urlpatterns = [
    path('ping/', PingView.as_view(), name='api-ping'),
    path('config/', AppConfigView.as_view(), name='api-config'),
    path('onboarding/', OnboardingSlideListView.as_view(), name='api-onboarding'),

    # JWT auth
    path('auth/signup/', SignupView.as_view(), name='api-signup'),
    path('auth/google/', GoogleAuthView.as_view(), name='api-google-auth'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='api-forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='api-reset-password'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='api-change-password'),
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
    path("clinics/send-confirmation-email/", SendClinicConfirmationEmailView.as_view(), name="api-send-clinic-confirmation-email"),
    path("clinics/confirm-email/<str:token>/", ConfirmClinicEmailView.as_view(), name="api-clinic-confirm-email"),
    path("clinics/<int:pk>/", ClinicDetailView.as_view(), name="api-clinic-detail"),
    path("clinics/<int:clinic_id>/working-hours/", ClinicWorkingHoursView.as_view(), name="api-clinic-working-hours"),
    path("clinics/<int:clinic_id>/vet-profile/", ClinicVetProfileView.as_view(), name="api-clinic-vet-profile"),
    path("clinics/register/", CombinedClinicUserClinicRegistrationView.as_view(), name="api-clinic-user-register"),
    
    # Clinic Available Slots & Dates for Appointments
    path("clinics/<int:clinic_id>/available-slots/", ClinicAvailableSlotsView.as_view(), name="api-clinic-available-slots"),
    path("clinics/<int:clinic_id>/available-dates/", ClinicAvailableDatesView.as_view(), name="api-clinic-available-dates"),
    
    # Clinic Dashboard - Appointments Management
    path("clinics/my/appointments/", ClinicAppointmentsListView.as_view(), name="api-clinic-appointments"),
    path("clinics/my/appointments/<int:pk>/", ClinicAppointmentDetailView.as_view(), name="api-clinic-appointment-detail"),
    path("clinics/my/appointments/<int:pk>/update/", ClinicAppointmentUpdateView.as_view(), name="api-clinic-appointment-update"),
    
    # Clinic Dashboard - Notifications
    path("clinics/my/notifications/", ClinicNotificationsListView.as_view(), name="api-clinic-notifications"),
    path("clinics/my/notifications/unread-count/", ClinicUnreadNotificationsCountView.as_view(), name="api-clinic-notifications-unread-count"),
    path("clinics/my/notifications/mark-all-read/", ClinicNotificationsMarkAllReadView.as_view(), name="api-clinic-notifications-mark-all-read"),
    path("clinics/my/notifications/<int:pk>/read/", ClinicNotificationMarkReadView.as_view(), name="api-clinic-notification-mark-read"),
    
    # User Appointments
    path("appointments/", MyAppointmentsListView.as_view(), name="api-my-appointments"),
    path("appointments/create/", AppointmentCreateView.as_view(), name="api-appointment-create"),
    path("appointments/reasons/", AppointmentReasonListView.as_view(), name="api-appointment-reasons"),
    path("appointments/<int:pk>/", AppointmentDetailView.as_view(), name="api-appointment-detail"),
    path("appointments/<int:pk>/cancel/", AppointmentCancelView.as_view(), name="api-appointment-cancel"),
    
    # AI Hub endpoints (meal recommendations and health reports)
    path("", include(router.urls)),
    
    # AI Core endpoints (nutrition predictions, etc.)
    path("", include('ai_core.urls')),
    
    # Chat API endpoints
    path("chat/", include('chat.api_urls')),
    
    # Device Token Registration (FCM Push Notifications)
    path("notifications/device/register/", RegisterDeviceTokenView.as_view(), name="api-register-device"),
    path("notifications/device/unregister/", UnregisterDeviceTokenView.as_view(), name="api-unregister-device"),
    
    # User Notifications
    path("notifications/", UserNotificationsListView.as_view(), name="api-user-notifications"),
    path("notifications/unread-count/", UserUnreadNotificationsCountView.as_view(), name="api-user-notifications-unread-count"),
    path("notifications/mark-all-read/", UserNotificationsMarkAllReadView.as_view(), name="api-user-notifications-mark-all-read"),
    path("notifications/<int:pk>/read/", UserNotificationMarkReadView.as_view(), name="api-user-notification-mark-read"),
    path("notifications/<int:pk>/", DeleteUserNotificationView.as_view(), name="api-user-notification-delete"),
]
