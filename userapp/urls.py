from django.urls import path
from . import views
from .views import export_users_csv

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.update_profile, name='update_profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin/users/', views.users_admin_view, name='users_admin'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('set-password/', views.set_password_after_activation, name='set_password_after_activation'),
    path('app-redirect/', views.app_activation_redirect, name='app_activation_redirect'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_from_email, name='reset_password_from_email'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/chart-data/', views.admin_dashboard_chart_data, name='admin_dashboard_chart_data'),
    path('admin-dashboard/kpis/', views.admin_dashboard_kpis, name='admin_dashboard_kpis'),
    path('export/users/', export_users_csv, name='export_users_csv'),
    path('terms/', views.terms_and_conditions_view, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    # Translation Management
    path('translations/', views.translation_dashboard, name='translation_dashboard'),
    path('translations/update/', views.update_translation_ajax, name='update_translation'),
    path('translations/compile/', views.compile_translations_ajax, name='compile_translations'),
    path('translations/extract/', views.extract_translations_ajax, name='extract_translations'),
    path('translations/export-csv/', views.export_translations_csv, name='export_translations_csv'),
    path('translations/import-csv/', views.import_translations_csv, name='import_translations_csv'),
    # API
    path('api/save-location/', views.SaveUserLocationAPIView.as_view(), name='save_location_api'),
]
