from django.urls import path
from . import api_views

app_name = 'chat_api'

urlpatterns = [
    # Sessions
    path('sessions/', api_views.ChatSessionListView.as_view(), name='session-list'),
    path('sessions/new/', api_views.ChatSessionCreateView.as_view(), name='session-create'),
    path('sessions/<int:pk>/', api_views.ChatSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<int:session_id>/messages/', api_views.ChatHistoryView.as_view(), name='session-messages'),
    path('sessions/<int:session_id>/clear/', api_views.ClearSessionView.as_view(), name='session-clear'),
    
    # Messages
    path('send/', api_views.SendMessageView.as_view(), name='send-message'),
    path('messages/<int:pk>/', api_views.DeleteMessageView.as_view(), name='message-delete'),
    
    # Active session
    path('active/', api_views.ActiveSessionView.as_view(), name='active-session'),
]
