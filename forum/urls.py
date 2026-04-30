from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('ask/', views.ask_question, name='ask_question'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('vote/<str:content_type>/<int:object_id>/<str:vote_type>/', views.vote, name='vote'),
    path('answer/<int:answer_id>/accept/', views.accept_answer, name='accept_answer'),
]
