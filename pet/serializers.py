from rest_framework import serializers
from .models import (
    Pet, PetType, Gender, AgeCategory, Breed, 
    FoodType, FoodFeeling, FoodImportance, BodyType, 
    ActivityLevel, FoodAllergy, HealthIssue, TreatFrequency,
    AgeTransitionRule, PetAgeHistory, PetConditionSnapshot
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
    
    # Computed fields for age and tracking
    age_display = serializers.SerializerMethodField()
    current_age = serializers.SerializerMethodField()
    should_transition_age = serializers.SerializerMethodField()
    age_progression_timeline = serializers.SerializerMethodField()
    
    def get_age_display(self, obj):
        """Safely get age display, return empty string if error"""
        try:
            return obj.get_age_display()
        except:
            return ""
    
    def get_current_age(self, obj):
        """Get current age breakdown"""
        try:
            return obj.get_current_age()
        except:
            return {"years": 0, "months": 0, "weeks": 0, "days": 0, "total_days": 0}
    
    def get_should_transition_age(self, obj):
        """Check if pet should transition to next age category"""
        try:
            new_category = obj.should_transition_age_category()
            return {
                'should_transition': new_category is not None,
                'next_category': new_category.name if new_category else None,
                'next_category_id': new_category.id if new_category else None
            }
        except:
            return {'should_transition': False, 'next_category': None, 'next_category_id': None}
    
    def get_age_progression_timeline(self, obj):
        """Get brief age progression timeline (last 3 periods)"""
        try:
            timeline = obj.get_age_progression_timeline()
            # Return only last 3 periods for mobile app (keep response size reasonable)
            return timeline[:3] if timeline else []
        except:
            return []
    
    class Meta:
        model = Pet
        fields = [
            'id', 'image', 'name', 'neutered', 'birth_date',
            'age_years', 'age_months', 'age_weeks', 'age_display', 'current_age',
            'unknown_breed', 'weight', 'food_allergy_other', 'user',
            # Age tracking fields
            'should_transition_age', 'age_progression_timeline',
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
        read_only_fields = ['user', 'age_display', 'current_age', 'should_transition_age', 'age_progression_timeline']


# Age Tracking System Serializers
class AgeTransitionRuleSerializer(serializers.ModelSerializer):
    """Serializer for age transition rules"""
    pet_type_detail = PetTypeSerializer(source='pet_type', read_only=True)
    from_category_detail = AgeCategorySerializer(source='from_category', read_only=True)
    to_category_detail = AgeCategorySerializer(source='to_category', read_only=True)
    age_display = serializers.SerializerMethodField()
    
    def get_age_display(self, obj):
        years = obj.transition_age_months // 12
        months = obj.transition_age_months % 12
        if months:
            return f"{years}y {months}m"
        return f"{years}y"
    
    class Meta:
        model = AgeTransitionRule
        fields = [
            'id', 'transition_age_months', 'age_display', 'created_at', 'updated_at',
            'pet_type', 'from_category', 'to_category',
            'pet_type_detail', 'from_category_detail', 'to_category_detail'
        ]


class PetAgeHistorySerializer(serializers.ModelSerializer):
    """Serializer for pet age history"""
    age_category_detail = AgeCategorySerializer(source='age_category', read_only=True)
    is_current = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    
    def get_is_current(self, obj):
        return obj.ended_at is None
    
    def get_duration_days(self, obj):
        if obj.ended_at:
            return (obj.ended_at - obj.started_at).days
        else:
            from django.utils import timezone
            return (timezone.now() - obj.started_at).days
    
    class Meta:
        model = PetAgeHistory
        fields = [
            'id', 'started_at', 'ended_at', 'age_months_at_start', 
            'transition_reason', 'is_current', 'duration_days',
            'age_category', 'age_category_detail'
        ]


class PetConditionSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for pet condition snapshots"""
    age_category_detail = AgeCategorySerializer(source='age_category', read_only=True)
    activity_level_detail = ActivityLevelSerializer(source='activity_level', read_only=True, allow_null=True)
    food_feeling_detail = FoodFeelingSerializer(source='food_feeling', read_only=True, allow_null=True)
    food_importance_detail = FoodImportanceSerializer(source='food_importance', read_only=True, allow_null=True)
    body_type_detail = BodyTypeSerializer(source='body_type', read_only=True, allow_null=True)
    treat_frequency_detail = TreatFrequencySerializer(source='treat_frequency', read_only=True, allow_null=True)
    
    # Get related many-to-many data from intermediate models
    food_types = serializers.SerializerMethodField()
    food_allergies = serializers.SerializerMethodField()
    health_issues = serializers.SerializerMethodField()
    
    def get_food_types(self, obj):
        food_type_snapshots = obj.food_type_snapshots.all()
        return [FoodTypeSerializer(ft.food_type).data for ft in food_type_snapshots]
    
    def get_food_allergies(self, obj):
        allergy_snapshots = obj.food_allergy_snapshots.all()
        return [FoodAllergySerializer(fa.food_allergy).data for fa in allergy_snapshots]
    
    def get_health_issues(self, obj):
        health_snapshots = obj.health_issue_snapshots.all()
        return [HealthIssueSerializer(hi.health_issue).data for hi in health_snapshots]
    
    class Meta:
        model = PetConditionSnapshot
        fields = [
            'id', 'weight', 'snapshot_date', 'transition_reason', 'notes',
            'food_allergy_other',
            # ID fields
            'age_category', 'activity_level', 'food_feeling', 'food_importance',
            'body_type', 'treat_frequency',
            # Detail fields
            'age_category_detail', 'activity_level_detail', 'food_feeling_detail',
            'food_importance_detail', 'body_type_detail', 'treat_frequency_detail',
            # Many-to-many snapshot data
            'food_types', 'food_allergies', 'health_issues'
        ]


class PetDetailedSerializer(PetSerializer):
    """Extended Pet serializer with full age tracking history for detailed views"""
    complete_age_history = PetAgeHistorySerializer(source='age_history', many=True, read_only=True)
    recent_snapshots = serializers.SerializerMethodField()
    
    def get_recent_snapshots(self, obj):
        """Get last 5 condition snapshots"""
        try:
            recent = obj.condition_snapshots.all()[:5]
            return PetConditionSnapshotSerializer(recent, many=True).data
        except:
            return []
    
    class Meta(PetSerializer.Meta):
        fields = PetSerializer.Meta.fields + ['complete_age_history', 'recent_snapshots']
