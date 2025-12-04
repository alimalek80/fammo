from django.urls import path, include
from .views import (
    PingView,
    MeProfileView,
    MyPetsListCreateView,
    MyPetDetailView,
    LanguageListView,
    SetUserLanguageView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('ping/', PingView.as_view(), name='api-ping'),

    # JWT auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Language management
    path('languages/', LanguageListView.as_view(), name='api-languages'),
    path('me/language/', SetUserLanguageView.as_view(), name='api-set-language'),

    # User profile
    path("me/", MeProfileView.as_view(), name="api-me"),

    #Pets
    path("pets/", MyPetsListCreateView.as_view(), name="api-my-pets"),
    path("pets/<int:pk>/", MyPetDetailView.as_view(), name="api-my-pet-detail"),
    
    # AI Core endpoints (nutrition predictions, etc.)
    path("", include('ai_core.urls')),
]
