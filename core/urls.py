from django.urls import path
from . import views
from django.views.generic import TemplateView

# Import specific views
from .views import (
    home, manage_hero_section, manage_social_links, manage_faqs, edit_faq, delete_faq, contact,
    UserNotificationsView, MarkNotificationReadView, MarkAllNotificationsReadView, DeleteNotificationView
)

urlpatterns = [
    path('', home, name='home'),
    path("contact/", contact, name="contact"),
    path('dashboard/hero-section/', manage_hero_section, name='manage_hero_section'),
    path('dashboard/social-links/', manage_social_links, name='manage_social_links'),
    path("manage/faqs/", manage_faqs, name="manage_faqs"),
    path("manage/faqs/<int:pk>/edit/", edit_faq, name="edit_faq"),
    path("manage/faqs/<int:pk>/delete/", delete_faq, name="delete_faq"),
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path("how-it-works/user-guide/", TemplateView.as_view(
        template_name="core/how_it_works.html"
    ), name="how_it_works"),
    path("how-it-works/ai-engine/", TemplateView.as_view(
        template_name="core/how_fammo_works.html"
    ), name="how_fammo_works"),
    path('collect-lead/', views.collect_lead, name='collect_lead'),
    path('start/lead/<str:uuid>/', views.start_from_lead, name='start_from_lead'),
    
    # User Notifications
    path('notifications/', UserNotificationsView.as_view(), name='user_notifications'),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('notifications/mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
    path('notifications/<int:pk>/delete/', DeleteNotificationView.as_view(), name='delete_notification'),
]