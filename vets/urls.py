from django.urls import path
from . import views

app_name = 'vets'

urlpatterns = [
    # Clinic registration
    path('register/', views.ClinicRegistrationView.as_view(), name='clinic_register'),
    path('register/success/', views.ClinicRegistrationSuccessView.as_view(), name='clinic_register_success'),
    path('confirm-email/<int:clinic_id>/<str:token>/', views.ClinicEmailConfirmationView.as_view(), name='confirm_email'),
    
    # Public clinic profiles
    path('clinics/', views.PartnerClinicsListView.as_view(), name='partner_clinics'),
    path('clinic/<slug:slug>/', views.ClinicDetailView.as_view(), name='clinic_detail'),
    
    # Appointment booking (user-facing)
    path('clinic/<slug:slug>/book/', views.AppointmentBookingView.as_view(), name='book_appointment'),
    path('clinic/<slug:slug>/available-slots/', views.ClinicAvailableSlotsAPIView.as_view(), name='clinic_available_slots'),
    path('my-appointments/', views.MyAppointmentsView.as_view(), name='my_appointments'),
    path('appointment/<int:pk>/', views.AppointmentDetailUserView.as_view(), name='appointment_detail'),
    path('appointment/<int:pk>/cancel/', views.CancelAppointmentView.as_view(), name='cancel_appointment'),
    
    # Clinic dashboard (requires owner permissions)
    path('dashboard/', views.ClinicDashboardView.as_view(), name='clinic_dashboard'),
    path('dashboard/profile/', views.ClinicProfileUpdateView.as_view(), name='clinic_profile_update'),
    path('dashboard/referrals/', views.ClinicReferralsView.as_view(), name='clinic_referrals'),
    path('dashboard/analytics/', views.ClinicAnalyticsView.as_view(), name='clinic_analytics'),
    
    # Clinic dashboard - Appointments management
    path('dashboard/appointments/', views.ClinicAppointmentsDashboardView.as_view(), name='clinic_appointments'),
    path('dashboard/appointments/<int:pk>/', views.ClinicAppointmentDetailView.as_view(), name='clinic_appointment_detail'),
    path('dashboard/appointments/<int:pk>/update/', views.ClinicUpdateAppointmentView.as_view(), name='clinic_update_appointment'),
    
    # Clinic dashboard - Notifications
    path('dashboard/notifications/', views.ClinicNotificationsView.as_view(), name='clinic_notifications'),
    path('dashboard/notifications/<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('dashboard/notifications/mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
    
    # Referral handling
    path('ref/<str:code>/', views.ReferralLandingView.as_view(), name='referral_landing'),
    path('api/track-referral/', views.TrackReferralAPIView.as_view(), name='track_referral_api'),
    
    # Legal documents
    path('clinic-terms/', views.clinic_terms_and_conditions_view, name='clinic_terms_and_conditions'),
    path('clinic-partnership/', views.clinic_partnership_agreement_view, name='clinic_partnership_agreement'),
    path('eoi-terms/', views.eoi_terms, name='eoi_terms'),
    
    # Location & Clinic Finder
    path('find/', views.ClinicFinderView.as_view(), name='clinic_finder'),
    path('api/nearby-clinics/', views.NearbyClinicAPIView.as_view(), name='nearby_clinics_api'),
    path('api/clinics-by-city/', views.ClinicsByCityAPIView.as_view(), name='clinics_by_city_api'),
    path('api/location/ip/', views.IPLocationAPIView.as_view(), name='ip_location_api'),
    path('admin/clinic/<int:clinic_id>/nearby-users/', views.ClinicNearbyUsersReportView.as_view(), name='clinic_nearby_users_report'),
]