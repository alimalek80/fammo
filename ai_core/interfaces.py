"""
FAMMO AI Core Interfaces

This module defines the core data structures and interfaces for FAMMO's nutrition AI engine.
These pure Python abstractions are used by both OpenAI-based implementations and future
proprietary ML models.

Data Structures:
- PetProfile: Input data representing a pet's complete profile
- ModelOutput: Structured prediction output from the AI engine

Interfaces:
- NutritionEngineInterface: Abstract base class for all nutrition prediction engines

Usage Example:
    from ai_core.interfaces import PetProfile, NutritionEngineInterface
    
    # Create a pet profile
    profile = PetProfile(
        species="dog",
        breed="Golden Retriever",
        age_years=3.5,
        weight_kg=29.0,
        health_goal="weight_loss"
    )
    
    # Use an engine implementation
    engine = SomeEngineImplementation()
    output = engine.predict(profile)
    print(f"Recommended calories: {output.calories_per_day}")
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PetProfile:
    """
    Complete pet profile input for nutrition AI predictions.
    
    This dataclass represents all the information needed by the AI engine to generate
    personalized nutrition recommendations and health risk assessments.
    
    Based on: ai_core/docs/ai_contracts.md - PetProfileInput Schema
    
    Required fields represent core identity and physical attributes.
    Optional fields with defaults allow partial profiles while maintaining type safety.
    """
    
    # Core Identity
    species: str  # "dog" or "cat"
    breed: str  # Specific breed name or "Mixed Breed" / "Unknown"
    breed_size_category: str  # "small", "medium", "large", "giant" (dogs); "small", "medium", "large" (cats)
    
    # Age & Life Stage
    age_years: float  # Age in years (e.g., 3.5 for 3 years 6 months)
    life_stage: str  # "puppy", "junior", "adult", "senior" (dogs); "kitten", "junior", "adult", "senior" (cats)
    
    # Physical Attributes
    weight_kg: float  # Current weight in kilograms
    body_condition_score: int  # 1=emaciated, 2=underweight, 3=ideal, 4=overweight, 5=obese
    sex: str  # "male" or "female"
    neutered: bool  # True if spayed/neutered
    
    # Activity & Lifestyle
    activity_level: str  # "sedentary", "low", "moderate", "high", "very_high"
    living_environment: str = "mixed"  # "indoor", "outdoor", "mixed"
    
    # Health & Medical History
    existing_conditions: list[str] = field(default_factory=list)  # List of condition identifiers (e.g., ["diabetes", "arthritis"])
    food_allergies: list[str] = field(default_factory=list)  # List of allergen identifiers (e.g., ["chicken", "dairy"])
    medications: list[str] = field(default_factory=list)  # List of current medications
    
    # Current Diet Information
    current_food_type: str = "dry"  # "dry", "wet", "raw", "homemade", "mixed"
    food_satisfaction: str = "satisfied"  # "always_hungry", "satisfied", "picky", "overeating"
    treat_frequency: str = "weekly"  # "never", "rarely", "weekly", "daily", "multiple_daily"
    
    # Goals & Preferences
    health_goal: str = "maintenance"  # "weight_loss", "weight_gain", "maintenance", "muscle_building", "joint_support", etc.
    dietary_preference: str = "no_preference"  # "no_preference", "grain_free", "high_protein", "low_fat", etc.
    
    # Geographic & Environmental Context
    climate_zone: str = "temperate"  # "cold", "temperate", "warm", "hot"
    country: str = "FI"  # ISO 3166-1 alpha-2 country code
    
    def __post_init__(self):
        """Validate critical fields after initialization."""
        if self.species not in ["dog", "cat"]:
            raise ValueError(f"Invalid species: {self.species}. Must be 'dog' or 'cat'.")
        
        if self.body_condition_score not in [1, 2, 3, 4, 5]:
            raise ValueError(f"Invalid body_condition_score: {self.body_condition_score}. Must be 1-5.")
        
        if self.age_years < 0 or self.age_years > 25:
            raise ValueError(f"Invalid age_years: {self.age_years}. Must be 0-25.")
        
        if self.weight_kg <= 0 or self.weight_kg > 100:
            raise ValueError(f"Invalid weight_kg: {self.weight_kg}. Must be 0.5-100.")


@dataclass
class RiskAssessment:
    """
    Health risk assessment across six preventive categories.
    
    Each risk level is classified as "low", "medium", or "high" based on
    the pet's profile, breed predispositions, and lifestyle factors.
    
    These are preventive health indicators, not medical diagnoses.
    """
    weight_risk: str  # Risk of obesity or unhealthy weight
    joint_risk: str  # Risk of arthritis, hip dysplasia, ligament injuries
    digestive_risk: str  # Risk of IBD, food sensitivities, digestive upset
    metabolic_risk: str  # Risk of diabetes, thyroid issues, Cushing's disease
    kidney_risk: str  # Risk of chronic kidney disease (especially cats)
    dental_risk: str  # Risk of periodontal disease, tooth decay
    
    def __post_init__(self):
        """Validate risk levels."""
        valid_levels = ["low", "medium", "high"]
        for field_name in ["weight_risk", "joint_risk", "digestive_risk", 
                          "metabolic_risk", "kidney_risk", "dental_risk"]:
            value = getattr(self, field_name)
            if value not in valid_levels:
                raise ValueError(f"Invalid {field_name}: {value}. Must be 'low', 'medium', or 'high'.")


@dataclass
class ModelOutput:
    """
    Structured output from the nutrition AI engine.
    
    Contains comprehensive recommendations including caloric needs, macronutrient targets,
    diet style classification, health risk assessment, and feeding guidelines.
    
    Based on: ai_core/docs/ai_contracts.md - ModelOutput Schema
    
    This structure is designed to be easily serialized to JSON for API responses
    and consumed by mobile/web frontends.
    """
    
    # Caloric Requirements
    calories_per_day: int  # Estimated daily energy requirement (DER) in kcal
    calorie_range_min: int  # Lower bound of safe caloric range (typically 90% of calories_per_day)
    calorie_range_max: int  # Upper bound of safe caloric range (typically 110% of calories_per_day)
    
    # Macronutrient Targets (percentages on dry matter basis)
    protein_percent: int  # Recommended protein percentage (18-50%)
    fat_percent: int  # Recommended fat percentage (8-35%)
    carbohydrate_percent: int  # Recommended carbohydrate percentage (5-50%)
    
    # Diet Style Recommendation
    diet_style: str  # One of 10 diet styles (e.g., "weight_loss", "senior_wellness", "growth_puppy")
    diet_style_confidence: float  # Model confidence score (0.0-1.0)
    
    # Risk Assessment
    risks: RiskAssessment  # Health risk scores across six categories
    
    # Feeding Recommendations
    meals_per_day: int  # Recommended number of meals per day (1-4)
    portion_size_grams: int  # Approximate portion size per meal in grams (for dry food reference)
    
    # Model Metadata
    model_version: str  # Version of the AI model used (e.g., "1.0.0")
    prediction_timestamp: str  # UTC timestamp when prediction was generated (ISO 8601 format)
    confidence_score: float  # Overall model confidence (0.0-1.0)
    
    # Alerts & Flags
    veterinary_consultation_recommended: bool  # True if vet consultation is advised
    alert_messages: list[str] = field(default_factory=list)  # Human-readable warnings and recommendations
    
    def __post_init__(self):
        """Validate output ranges."""
        if not (50 <= self.calories_per_day <= 5000):
            raise ValueError(f"Invalid calories_per_day: {self.calories_per_day}. Must be 50-5000.")
        
        if not (0.0 <= self.diet_style_confidence <= 1.0):
            raise ValueError(f"Invalid diet_style_confidence: {self.diet_style_confidence}. Must be 0.0-1.0.")
        
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError(f"Invalid confidence_score: {self.confidence_score}. Must be 0.0-1.0.")
        
        if not (1 <= self.meals_per_day <= 4):
            raise ValueError(f"Invalid meals_per_day: {self.meals_per_day}. Must be 1-4.")
    
    def to_dict(self) -> dict:
        """
        Convert ModelOutput to a dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation with nested RiskAssessment as dict.
        """
        return {
            "calories_per_day": self.calories_per_day,
            "calorie_range_min": self.calorie_range_min,
            "calorie_range_max": self.calorie_range_max,
            "protein_percent": self.protein_percent,
            "fat_percent": self.fat_percent,
            "carbohydrate_percent": self.carbohydrate_percent,
            "diet_style": self.diet_style,
            "diet_style_confidence": self.diet_style_confidence,
            "risks": {
                "weight_risk": self.risks.weight_risk,
                "joint_risk": self.risks.joint_risk,
                "digestive_risk": self.risks.digestive_risk,
                "metabolic_risk": self.risks.metabolic_risk,
                "kidney_risk": self.risks.kidney_risk,
                "dental_risk": self.risks.dental_risk,
            },
            "meals_per_day": self.meals_per_day,
            "portion_size_grams": self.portion_size_grams,
            "model_version": self.model_version,
            "prediction_timestamp": self.prediction_timestamp,
            "confidence_score": self.confidence_score,
            "veterinary_consultation_recommended": self.veterinary_consultation_recommended,
            "alert_messages": self.alert_messages,
        }


class NutritionEngineInterface(ABC):
    """
    Abstract base class for all nutrition prediction engines.
    
    This interface defines the contract that all AI engine implementations must follow,
    whether they use OpenAI APIs, proprietary ML models, or rule-based systems.
    
    Implementations should:
    1. Accept a PetProfile as input
    2. Perform prediction/inference using their specific method
    3. Return a structured ModelOutput with all required fields
    
    Example implementations:
    - OpenAINutritionEngine: Uses OpenAI GPT models with structured outputs
    - ProprietaryMLEngine: Uses trained scikit-learn/XGBoost models
    - RuleBasedEngine: Uses veterinary formulas and decision trees
    
    Usage:
        class MyEngine(NutritionEngineInterface):
            def predict(self, pet: PetProfile) -> ModelOutput:
                # Implementation here
                ...
        
        engine = MyEngine()
        profile = PetProfile(species="dog", breed="Beagle", ...)
        output = engine.predict(profile)
    """
    
    @abstractmethod
    def predict(self, pet: PetProfile) -> ModelOutput:
        """
        Generate nutrition recommendations and risk assessment for a pet.
        
        This method takes a complete pet profile and returns structured predictions
        including caloric requirements, macronutrient targets, diet style recommendations,
        and health risk assessments across six categories.
        
        Args:
            pet (PetProfile): Complete pet profile with all required attributes.
        
        Returns:
            ModelOutput: Structured prediction containing:
                - Daily calorie requirements with safe ranges
                - Macronutrient percentages (protein, fat, carbs)
                - Recommended diet style with confidence score
                - Risk assessment for six health categories
                - Feeding recommendations (meals per day, portion sizes)
                - Model metadata and confidence scores
                - Veterinary consultation flags and alert messages
        
        Raises:
            ValueError: If the pet profile contains invalid data.
            NotImplementedError: If the engine is not properly implemented.
        
        Example:
            >>> profile = PetProfile(
            ...     species="dog",
            ...     breed="Golden Retriever",
            ...     age_years=3.5,
            ...     weight_kg=29.0,
            ...     body_condition_score=4,
            ...     sex="male",
            ...     neutered=True,
            ...     activity_level="moderate",
            ...     health_goal="weight_loss"
            ... )
            >>> engine = SomeEngineImplementation()
            >>> output = engine.predict(profile)
            >>> print(f"Calories: {output.calories_per_day} kcal/day")
            >>> print(f"Diet style: {output.diet_style}")
            >>> print(f"Weight risk: {output.risks.weight_risk}")
        """
        raise NotImplementedError("Engine implementations must override the predict() method")
    
    def validate_output(self, output: ModelOutput) -> bool:
        """
        Validate that a ModelOutput meets basic sanity checks.
        
        This helper method can be used by implementations to verify their outputs
        before returning to callers. Checks include range validation, consistency
        between related fields, and required field presence.
        
        Args:
            output (ModelOutput): The output to validate.
        
        Returns:
            bool: True if valid, raises ValueError if invalid.
        
        Raises:
            ValueError: If validation fails with a descriptive message.
        """
        # Calorie ranges should be consistent
        if not (output.calorie_range_min <= output.calories_per_day <= output.calorie_range_max):
            raise ValueError(
                f"Calorie ranges inconsistent: {output.calorie_range_min} <= "
                f"{output.calories_per_day} <= {output.calorie_range_max}"
            )
        
        # Macronutrients should sum to approximately 100% (allow some flexibility)
        macro_sum = output.protein_percent + output.fat_percent + output.carbohydrate_percent
        if not (85 <= macro_sum <= 115):
            raise ValueError(
                f"Macronutrients sum to {macro_sum}%, expected ~100%. "
                f"P:{output.protein_percent} F:{output.fat_percent} C:{output.carbohydrate_percent}"
            )
        
        # Model version should be present
        if not output.model_version:
            raise ValueError("model_version must be specified")
        
        # Timestamp should be present
        if not output.prediction_timestamp:
            raise ValueError("prediction_timestamp must be specified")
        
        return True
