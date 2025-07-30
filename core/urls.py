from django.urls import path
from .views import home, manage_hero_section, manage_social_links

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/hero-section/', manage_hero_section, name='manage_hero_section'),
    path('dashboard/social-links/', manage_social_links, name='manage_social_links'),
]