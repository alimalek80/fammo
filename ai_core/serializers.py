"""
FAMMO AI Core DRF Serializers

This module provides Django REST Framework serializers for the AI layer.
These serializers validate JSON from mobile apps and serialize AI engine outputs.

Serializers:
- PetProfileSerializer: Validates and deserializes JSON into PetProfile dataclass
- RiskAssessmentSerializer: Nested serializer for health risk scores
- ModelOutputSerializer: Serializes ModelOutput dataclass into JSON responses

These are pure API serializers - they do not interact with Django models.
They bridge between JSON (API) and Python dataclasses (AI engine).

Usage in DRF Views:
    # Input: JSON -> PetProfile
    serializer = PetProfileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    pet_profile = serializer.to_pet_profile()
    
    # AI prediction
    engine = get_engine()
    output = engine.predict(pet_profile)
    
    # Output: ModelOutput -> JSON
    response_serializer = ModelOutputSerializer(output)
    return Response(response_serializer.data)
"""

from rest_framework import serializers

from ai_core.interfaces import PetProfile, ModelOutput, RiskAssessment


class PetProfileSerializer(serializers.Serializer):
    """
    Serializer for pet profile input to the AI nutrition engine.
    
    Validates JSON data from mobile apps or internal calls and converts it
    into a PetProfile dataclass instance that can be passed to the AI engine.
    
    Based on: ai_core/docs/ai_contracts.md - PetProfileInput Schema
    
    All enum choices are defined according to the AI contracts specification.
    Optional fields have sensible defaults to minimize required input.
    
    Example:
        data = {
            "species": "dog",
            "breed": "Golden Retriever",
            "breed_size_category": "large",
            "age_years": 3.5,
            "life_stage": "adult",
            "weight_kg": 29.0,
            "body_condition_score": 4,
            "sex": "male",
            "neutered": true,
            "activity_level": "moderate",
            "health_goal": "weight_loss"
        }
        serializer = PetProfileSerializer(data=data)
        if serializer.is_valid():
            pet_profile = serializer.to_pet_profile()
    """
    
    # Core Identity Fields
    species = serializers.ChoiceField(
        choices=['dog', 'cat'],
        required=True,
        help_text="Pet species: 'dog' or 'cat'"
    )
    
    breed = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Specific breed name or 'Mixed Breed' / 'Unknown'"
    )
    
    breed_size_category = serializers.ChoiceField(
        choices=['small', 'medium', 'large', 'giant'],
        required=True,
        help_text="Size category: 'small', 'medium', 'large', 'giant' (dogs); 'small', 'medium', 'large' (cats)"
    )
    
    # Age & Life Stage
    age_years = serializers.FloatField(
        min_value=0.0,
        max_value=25.0,
        required=True,
        help_text="Pet's age in years (e.g., 3.5 for 3 years 6 months)"
    )
    
    life_stage = serializers.ChoiceField(
        choices=['puppy', 'kitten', 'junior', 'adult', 'senior'],
        required=True,
        help_text="Life stage: puppy/kitten, junior, adult, or senior"
    )
    
    # Physical Attributes
    weight_kg = serializers.FloatField(
        min_value=0.5,
        max_value=100.0,
        required=True,
        help_text="Current weight in kilograms"
    )
    
    body_condition_score = serializers.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        help_text="Body condition: 1=emaciated, 2=underweight, 3=ideal, 4=overweight, 5=obese"
    )
    
    sex = serializers.ChoiceField(
        choices=['male', 'female'],
        required=True,
        help_text="Biological sex: 'male' or 'female'"
    )
    
    neutered = serializers.BooleanField(
        required=True,
        help_text="Whether the pet is spayed/neutered"
    )
    
    # Activity & Lifestyle
    activity_level = serializers.ChoiceField(
        choices=['sedentary', 'low', 'moderate', 'high', 'very_high'],
        required=True,
        help_text="Daily activity intensity"
    )
    
    living_environment = serializers.ChoiceField(
        choices=['indoor', 'outdoor', 'mixed'],
        default='mixed',
        required=False,
        help_text="Primary living environment"
    )
    
    # Health & Medical History
    existing_conditions = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list,
        required=False,
        help_text="List of existing health conditions (e.g., ['diabetes', 'arthritis'])"
    )
    
    food_allergies = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list,
        required=False,
        help_text="List of known food allergens (e.g., ['chicken', 'dairy'])"
    )
    
    medications = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list,
        required=False,
        help_text="List of current medications"
    )
    
    # Current Diet Information
    current_food_type = serializers.ChoiceField(
        choices=['dry', 'wet', 'raw', 'homemade', 'mixed'],
        default='dry',
        required=False,
        help_text="Current primary food type"
    )
    
    food_satisfaction = serializers.ChoiceField(
        choices=['always_hungry', 'satisfied', 'picky', 'overeating'],
        default='satisfied',
        required=False,
        help_text="Owner's assessment of pet's eating behavior"
    )
    
    treat_frequency = serializers.ChoiceField(
        choices=['never', 'rarely', 'weekly', 'daily', 'multiple_daily'],
        default='weekly',
        required=False,
        help_text="Frequency of treats"
    )
    
    # Goals & Preferences
    health_goal = serializers.ChoiceField(
        choices=[
            'weight_loss',
            'weight_gain',
            'maintenance',
            'muscle_building',
            'joint_support',
            'digestive_health',
            'skin_coat_health',
            'senior_wellness'
        ],
        default='maintenance',
        required=False,
        help_text="Primary health goal"
    )
    
    dietary_preference = serializers.ChoiceField(
        choices=[
            'no_preference',
            'grain_free',
            'high_protein',
            'low_fat',
            'limited_ingredient',
            'raw',
            'holistic'
        ],
        default='no_preference',
        required=False,
        help_text="Owner's dietary philosophy preference"
    )
    
    # Geographic & Environmental Context
    climate_zone = serializers.ChoiceField(
        choices=['cold', 'temperate', 'warm', 'hot'],
        default='temperate',
        required=False,
        help_text="Climate where the pet lives"
    )
    
    country = serializers.CharField(
        max_length=2,
        default='FI',
        required=False,
        help_text="ISO 3166-1 alpha-2 country code (e.g., 'FI', 'US', 'TR')"
    )
    
    def to_pet_profile(self) -> PetProfile:
        """
        Convert validated serializer data to a PetProfile dataclass instance.
        
        This method should be called after is_valid() to obtain a PetProfile
        object that can be passed to the AI engine's predict() method.
        
        Returns:
            PetProfile: Dataclass instance ready for AI prediction.
        
        Raises:
            AssertionError: If called before is_valid() or validation failed.
        
        Example:
            serializer = PetProfileSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                pet_profile = serializer.to_pet_profile()
                output = engine.predict(pet_profile)
        """
        if not hasattr(self, '_validated_data'):
            raise AssertionError(
                "to_pet_profile() called before is_valid(). "
                "Ensure you call is_valid() first."
            )
        
        # Create PetProfile from validated data
        # Field names match exactly, so we can pass directly
        return PetProfile(**self.validated_data)


class RiskAssessmentSerializer(serializers.Serializer):
    """
    Serializer for health risk assessment output.
    
    Represents the six preventive health risk categories predicted by the AI engine.
    Each risk is classified as 'low', 'medium', or 'high'.
    
    These are preventive health indicators, not medical diagnoses.
    
    Risk Categories:
    - weight_risk: Risk of obesity or unhealthy weight
    - joint_risk: Risk of arthritis, hip dysplasia, ligament injuries
    - digestive_risk: Risk of IBD, food sensitivities, digestive upset
    - metabolic_risk: Risk of diabetes, thyroid issues, metabolic disorders
    - kidney_risk: Risk of chronic kidney disease (especially cats)
    - dental_risk: Risk of periodontal disease, tooth decay
    
    Example:
        {
            "weight_risk": "high",
            "joint_risk": "medium",
            "digestive_risk": "low",
            "metabolic_risk": "medium",
            "kidney_risk": "low",
            "dental_risk": "low"
        }
    """
    
    RISK_LEVEL_CHOICES = ['low', 'medium', 'high']
    
    weight_risk = serializers.ChoiceField(
        choices=RISK_LEVEL_CHOICES,
        help_text="Risk of obesity or unhealthy weight"
    )
    
    joint_risk = serializers.ChoiceField(
        choices=RISK_LEVEL_CHOICES,
        help_text="Risk of arthritis, hip dysplasia, ligament injuries"
    )
    
    digestive_risk = serializers.ChoiceField(
        choices=RISK_LEVEL_CHOICES,
        help_text="Risk of IBD, food sensitivities, digestive upset"
    )
    
    metabolic_risk = serializers.ChoiceField(
        choices=RISK_LEVEL_CHOICES,
        help_text="Risk of diabetes, thyroid issues, metabolic disorders"
    )
    
    kidney_risk = serializers.ChoiceField(
        choices=RISK_LEVEL_CHOICES,
        help_text="Risk of chronic kidney disease (especially cats)"
    )
    
    dental_risk = serializers.ChoiceField(
        choices=RISK_LEVEL_CHOICES,
        help_text="Risk of periodontal disease, tooth decay"
    )


class ModelOutputSerializer(serializers.Serializer):
    """
    Serializer for AI engine prediction output.
    
    Converts a ModelOutput dataclass instance into JSON for API responses.
    Contains comprehensive nutrition recommendations and health risk assessments.
    
    Based on: ai_core/docs/ai_contracts.md - ModelOutput Schema
    
    This serializer is designed to work with the to_representation() method
    to accept ModelOutput dataclass instances directly.
    
    Output includes:
    - Caloric requirements (daily calories with safe ranges)
    - Macronutrient targets (protein, fat, carbohydrate percentages)
    - Diet style recommendation with confidence score
    - Health risk assessment across six categories
    - Feeding recommendations (meals per day, portion sizes)
    - Model metadata (version, timestamp, confidence)
    - Veterinary consultation flags and alert messages
    
    Example:
        output = engine.predict(pet_profile)
        serializer = ModelOutputSerializer(output)
        return Response(serializer.data)
    """
    
    # Diet style choices (10 diet styles from AI contracts)
    DIET_STYLE_CHOICES = [
        'maintenance_standard',
        'weight_loss',
        'weight_gain',
        'high_protein_performance',
        'senior_wellness',
        'senior_wellness_kidney',
        'growth_puppy',
        'growth_kitten',
        'digestive_sensitive',
        'grain_free_high_protein'
    ]
    
    # Caloric Requirements
    calories_per_day = serializers.IntegerField(
        min_value=50,
        max_value=5000,
        help_text="Estimated daily energy requirement (DER) in kcal"
    )
    
    calorie_range_min = serializers.IntegerField(
        min_value=40,
        max_value=4500,
        help_text="Lower bound of safe caloric range"
    )
    
    calorie_range_max = serializers.IntegerField(
        min_value=60,
        max_value=5500,
        help_text="Upper bound of safe caloric range"
    )
    
    # Macronutrient Targets
    protein_percent = serializers.IntegerField(
        min_value=18,
        max_value=50,
        help_text="Recommended protein percentage (dry matter basis)"
    )
    
    fat_percent = serializers.IntegerField(
        min_value=8,
        max_value=35,
        help_text="Recommended fat percentage (dry matter basis)"
    )
    
    carbohydrate_percent = serializers.IntegerField(
        min_value=5,
        max_value=50,
        help_text="Recommended carbohydrate percentage (dry matter basis)"
    )
    
    # Diet Style Recommendation
    diet_style = serializers.ChoiceField(
        choices=DIET_STYLE_CHOICES,
        help_text="Recommended diet style category"
    )
    
    diet_style_confidence = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        help_text="Model confidence score for diet style (0.0-1.0)"
    )
    
    # Risk Assessment (nested serializer)
    risks = RiskAssessmentSerializer(
        help_text="Health risk scores across six categories"
    )
    
    # Feeding Recommendations
    meals_per_day = serializers.IntegerField(
        min_value=1,
        max_value=4,
        help_text="Recommended number of meals per day"
    )
    
    portion_size_grams = serializers.IntegerField(
        min_value=20,
        max_value=1000,
        help_text="Approximate portion size per meal in grams (dry food reference)"
    )
    
    # Model Metadata
    model_version = serializers.CharField(
        max_length=20,
        help_text="Version of the AI model used (e.g., '1.0.0')"
    )
    
    prediction_timestamp = serializers.CharField(
        max_length=30,
        help_text="UTC timestamp when prediction was generated (ISO 8601)"
    )
    
    confidence_score = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        help_text="Overall model confidence (0.0-1.0)"
    )
    
    # Alerts & Flags
    veterinary_consultation_recommended = serializers.BooleanField(
        help_text="Whether veterinary consultation is advised before implementing diet"
    )
    
    alert_messages = serializers.ListField(
        child=serializers.CharField(),
        default=list,
        help_text="Human-readable warnings and recommendations"
    )
    
    def to_representation(self, instance: ModelOutput) -> dict:
        """
        Convert a ModelOutput dataclass instance to a JSON-serializable dict.
        
        This method handles the conversion from the AI engine's ModelOutput
        dataclass to the JSON format expected by API consumers.
        
        Args:
            instance (ModelOutput): The AI engine output to serialize.
        
        Returns:
            dict: JSON-serializable representation of the prediction.
        
        Example:
            output = engine.predict(pet_profile)
            serializer = ModelOutputSerializer(output)
            json_data = serializer.data  # Calls to_representation internally
        """
        # Convert RiskAssessment dataclass to dict for nested serializer
        risks_dict = {
            'weight_risk': instance.risks.weight_risk,
            'joint_risk': instance.risks.joint_risk,
            'digestive_risk': instance.risks.digestive_risk,
            'metabolic_risk': instance.risks.metabolic_risk,
            'kidney_risk': instance.risks.kidney_risk,
            'dental_risk': instance.risks.dental_risk,
        }
        
        # Build complete representation
        representation = {
            'calories_per_day': instance.calories_per_day,
            'calorie_range_min': instance.calorie_range_min,
            'calorie_range_max': instance.calorie_range_max,
            'protein_percent': instance.protein_percent,
            'fat_percent': instance.fat_percent,
            'carbohydrate_percent': instance.carbohydrate_percent,
            'diet_style': instance.diet_style,
            'diet_style_confidence': instance.diet_style_confidence,
            'risks': risks_dict,
            'meals_per_day': instance.meals_per_day,
            'portion_size_grams': instance.portion_size_grams,
            'model_version': instance.model_version,
            'prediction_timestamp': instance.prediction_timestamp,
            'confidence_score': instance.confidence_score,
            'veterinary_consultation_recommended': instance.veterinary_consultation_recommended,
            'alert_messages': instance.alert_messages,
        }
        
        return representation
