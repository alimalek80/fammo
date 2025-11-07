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
    
    # Clinic dashboard (requires owner permissions)
    path('dashboard/', views.ClinicDashboardView.as_view(), name='clinic_dashboard'),
    path('dashboard/profile/', views.ClinicProfileUpdateView.as_view(), name='clinic_profile_update'),
    path('dashboard/referrals/', views.ClinicReferralsView.as_view(), name='clinic_referrals'),
    path('dashboard/analytics/', views.ClinicAnalyticsView.as_view(), name='clinic_analytics'),
    
    # Referral handling
    path('ref/<str:code>/', views.ReferralLandingView.as_view(), name='referral_landing'),
    path('api/track-referral/', views.TrackReferralAPIView.as_view(), name='track_referral_api'),
    
    # Legal documents
    path('clinic-terms/', views.clinic_terms_and_conditions_view, name='clinic_terms_and_conditions'),
    path('clinic-partnership/', views.clinic_partnership_agreement_view, name='clinic_partnership_agreement'),
]