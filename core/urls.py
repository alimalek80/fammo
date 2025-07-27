from django.urls import path
from .views import home, manage_hero_section

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/hero-section/', manage_hero_section, name='manage_hero_section'),
]