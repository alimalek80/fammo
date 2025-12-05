from rest_framework import serializers
from .models import OnboardingSlide


class OnboardingSlideSerializer(serializers.ModelSerializer):
    """Serializer for onboarding slides with localized fields."""
    
    icon_url = serializers.SerializerMethodField()
    
    class Meta:
        model = OnboardingSlide
        fields = ['id', 'title', 'description', 'icon_url', 'order', 'button_text']
    
    def get_icon_url(self, obj):
        """Return absolute URL for the icon."""
        request = self.context.get('request')
        if obj.icon and hasattr(obj.icon, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None
