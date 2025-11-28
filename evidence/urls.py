from django.urls import path
from . import views

app_name = 'evidence'

urlpatterns = [
    path('', views.evidence_dashboard, name='dashboard'),
    path('download-pdf/', views.download_pdf_report, name='download_pdf'),
]
