from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('session/<int:session_id>/', views.chat, name='chat_session'),
    path('session/<int:session_id>/delete/', views.delete_session, name='delete_chat_session'),
]