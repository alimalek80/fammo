from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from django.conf import settings

from userapp.models import Profile
from userapp.serializers import ProfileSerializer

from pet.models import Pet
from pet.serializers import PetSerializer

class PingView(APIView):
    def get(self, request):
        return Response({"message": "pong from FAMMO API"})


class AppConfigView(APIView):
    """
    GET /api/v1/config/
    Returns app configuration including static asset URLs
    No authentication required - needed on app launch
    """
    permission_classes = []
    
    def get(self, request):
        # Build absolute URLs
        base_url = request.build_absolute_uri('/').rstrip('/')
        
        return Response({
            "base_url": base_url,
            "static_url": f"{base_url}{settings.STATIC_URL}",
            "media_url": f"{base_url}{settings.MEDIA_URL}",
            "assets": {
                "logo": f"{base_url}{settings.STATIC_URL}images/logo.png",
                "favicon": f"{base_url}{settings.STATIC_URL}images/favicon.png",
                "placeholder_pet": f"{base_url}{settings.STATIC_URL}images/pet-waiting.gif",
            },
            "api_version": "1.0.0",
        })


class LanguageListView(APIView):
    """
    GET /api/v1/languages/
    Returns list of available languages for mobile app language selection
    No authentication required - shown on first launch
    """
    permission_classes = []
    
    def get(self, request):
        languages = [
            {
                "code": code,
                "name": name,
                "native_name": name  # Same as name for now, can be customized
            }
            for code, name in settings.LANGUAGES
        ]
        return Response({"languages": languages})


class SetUserLanguageView(APIView):
    """
    POST /api/v1/me/language/
    Set user's preferred language
    Request body: {"language": "en"} (or "tr", "nl", "fi")
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        language_code = request.data.get('language')
        
        if not language_code:
            return Response(
                {"error": "Language code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate language code
        valid_languages = [code for code, name in settings.LANGUAGES]
        if language_code not in valid_languages:
            return Response(
                {
                    "error": f"Invalid language code. Must be one of: {', '.join(valid_languages)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update user's profile
        profile = request.user.profile
        profile.preferred_language = language_code
        profile.save()
        
        return Response({
            "success": True,
            "language": language_code,
            "message": f"Language preference updated to {language_code}"
        })
    
    def get(self, request):
        """
        GET /api/v1/me/language/
        Returns user's current language preference
        """
        profile = request.user.profile
        return Response({
            "language": profile.preferred_language
        })
    
class MeProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)
    
class MyPetsListCreateView(generics.ListCreateAPIView):

    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MyPetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(user=self.request.user)