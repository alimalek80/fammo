from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.pet_form_view, name='create_pet'),
    path('edit/<int:pk>/', views.pet_form_view, name='edit_pet'),
    path('my-pets/', views.my_pets_view, name='my_pets'),
    path('delete/<int:pk>/', views.delete_pet_view, name='delete_pet'),
    path('ajax/load-breeds/', views.load_breeds, name='ajax_load_breeds'),
    path('detail/<int:pk>/', views.pet_detail_view, name='pet_detail'),
]