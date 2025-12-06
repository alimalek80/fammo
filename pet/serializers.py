from rest_framework import serializers
from .models import (
    Pet, PetType, Gender, AgeCategory, Breed, 
    FoodType, FoodFeeling, FoodImportance, BodyType, 
    ActivityLevel, FoodAllergy, HealthIssue, TreatFrequency
)


# Nested serializers for related models
class PetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetType
        fields = ['id', 'name']


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['id', 'name']


class AgeCategorySerializer(serializers.ModelSerializer):
    pet_type = PetTypeSerializer(read_only=True)
    
    class Meta:
        model = AgeCategory
        fields = ['id', 'name', 'pet_type', 'order']


class BreedSerializer(serializers.ModelSerializer):
    pet_type = PetTypeSerializer(read_only=True)
    
    class Meta:
        model = Breed
        fields = ['id', 'name', 'pet_type']


class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = ['id', 'name']


class FoodFeelingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodFeeling
        fields = ['id', 'name', 'description']


class FoodImportanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodImportance
        fields = ['id', 'name']


class BodyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyType
        fields = ['id', 'name', 'description']


class ActivityLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLevel
        fields = ['id', 'name', 'description']


class FoodAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAllergy
        fields = ['id', 'name']


class HealthIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthIssue
        fields = ['id', 'name']


class TreatFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatFrequency
        fields = ['id', 'name', 'description']


class PetSerializer(serializers.ModelSerializer):
    """
    Serializer for Pet model with nested related objects
    Returns full object details instead of just IDs for better frontend integration
    """
    # Read-only nested serializers for GET requests (allow_null handles None values)
    pet_type_detail = PetTypeSerializer(source='pet_type', read_only=True, allow_null=True)
    gender_detail = GenderSerializer(source='gender', read_only=True, allow_null=True)
    age_category_detail = AgeCategorySerializer(source='age_category', read_only=True, allow_null=True)
    breed_detail = BreedSerializer(source='breed', read_only=True, allow_null=True)
    food_feeling_detail = FoodFeelingSerializer(source='food_feeling', read_only=True, allow_null=True)
    food_importance_detail = FoodImportanceSerializer(source='food_importance', read_only=True, allow_null=True)
    body_type_detail = BodyTypeSerializer(source='body_type', read_only=True, allow_null=True)
    activity_level_detail = ActivityLevelSerializer(source='activity_level', read_only=True, allow_null=True)
    treat_frequency_detail = TreatFrequencySerializer(source='treat_frequency', read_only=True, allow_null=True)
    
    # Many-to-many relationships
    food_types_detail = FoodTypeSerializer(source='food_types', many=True, read_only=True)
    food_allergies_detail = FoodAllergySerializer(source='food_allergies', many=True, read_only=True)
    health_issues_detail = HealthIssueSerializer(source='health_issues', many=True, read_only=True)
    
    # Computed field for age display
    age_display = serializers.SerializerMethodField()
    
    def get_age_display(self, obj):
        """Safely get age display, return empty string if error"""
        try:
            return obj.get_age_display()
        except:
            return ""
    
    class Meta:
        model = Pet
        fields = [
            'id', 'image', 'name', 'neutered', 'birth_date',
            'age_years', 'age_months', 'age_weeks', 'age_display',
            'unknown_breed', 'weight', 'food_allergy_other', 'user',
            # ID fields for write operations
            'pet_type', 'gender', 'age_category', 'breed',
            'food_feeling', 'food_importance', 'body_type',
            'activity_level', 'treat_frequency',
            'food_types', 'food_allergies', 'health_issues',
            # Detail fields for read operations
            'pet_type_detail', 'gender_detail', 'age_category_detail',
            'breed_detail', 'food_feeling_detail', 'food_importance_detail',
            'body_type_detail', 'activity_level_detail', 'treat_frequency_detail',
            'food_types_detail', 'food_allergies_detail', 'health_issues_detail',
        ]
        read_only_fields = ['user', 'age_display']
