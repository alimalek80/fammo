"""
AI Core URL Configuration

Defines URL patterns for AI-powered prediction endpoints.
Currently includes:
- POST /ai/nutrition/ - Generate nutrition predictions

Mount this in your main urls.py:
    path('api/v1/', include('ai_core.urls'))
"""

from django.urls import path
from ai_core.views import NutritionPredictionView

app_name = 'ai_core'

urlpatterns = [
    path('ai/nutrition/', NutritionPredictionView.as_view(), name='nutrition-prediction'),
]
