from django.urls import path
from .views import home, manage_hero_section, manage_social_links
from django.views.generic import TemplateView

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/hero-section/', manage_hero_section, name='manage_hero_section'),
    path('dashboard/social-links/', manage_social_links, name='manage_social_links'),
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
]