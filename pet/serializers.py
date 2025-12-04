from rest_framework import serializers
from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    """
    Serializer for Pet model with absolute URLs for media files
    """
    # If you add a photo field later, uncomment this:
    # photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Pet
        fields = "__all__"
        read_only_fields = ['user']
    
    # def get_photo_url(self, obj):
    #     """Return absolute URL for pet photo"""
    #     if obj.photo:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri(obj.photo.url)
    #         return obj.photo.url
    #     return None
