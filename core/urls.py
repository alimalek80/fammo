from django.urls import path
from .views import home, manage_hero_section, manage_social_links, manage_faqs, edit_faq, delete_faq, contact
from django.views.generic import TemplateView

urlpatterns = [
    path('', home, name='home'),
    path("contact/", contact, name="contact"),
    path('dashboard/hero-section/', manage_hero_section, name='manage_hero_section'),
    path('dashboard/social-links/', manage_social_links, name='manage_social_links'),
    path("manage/faqs/", manage_faqs, name="manage_faqs"),
    path("manage/faqs/<int:pk>/edit/", edit_faq, name="edit_faq"),
    path("manage/faqs/<int:pk>/delete/", delete_faq, name="delete_faq"),
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path("how-it-works/", TemplateView.as_view(
        template_name="core/how_it_works.html"
    ), name="how_it_works"),
]