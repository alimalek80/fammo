from django.urls import path
from . import views

app_name = 'evidence'

urlpatterns = [
    path('', views.evidence_dashboard, name='dashboard'),
]
