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
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('export/users/', export_users_csv, name='export_users_csv'),
]
