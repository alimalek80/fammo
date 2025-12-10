from rest_framework import serializers
from .models import AIRecommendation, AIHealthReport


class AIRecommendationSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    recommendation_type = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = AIRecommendation
        fields = [
            'id',
            'pet',
            'pet_name',
            'type',
            'recommendation_type',
            'content',
            'content_json',
            'created_at',
        ]
        read_only_fields = ['id', 'pet_name', 'recommendation_type', 'created_at']


class AIHealthReportSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    
    class Meta:
        model = AIHealthReport
        fields = [
            'id',
            'pet',
            'pet_name',
            'summary',
            'suggestions',
            'summary_json',
            'created_at',
        ]
        read_only_fields = ['id', 'pet_name', 'created_at']
