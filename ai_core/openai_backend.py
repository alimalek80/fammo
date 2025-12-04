"""
OpenAI-based implementation of NutritionEngineInterface.

This module provides the OpenAI GPT-powered nutrition prediction engine
for FAMMO's /api/v1/ai/nutrition/ endpoint. It uses OpenAI's Responses API
with structured outputs (Pydantic models) to generate consistent, parseable
predictions.

This engine can be swapped out for a ProprietaryEngine via settings.AI_BACKEND.

Key differences from aihub/views.py:
- This generates NutritionPrediction (calories + diet_style + risks) for API consumption
- aihub/views.py generates MealPlan and HealthReport for web template rendering
- This uses the new AI contracts specification (ai_core/docs/ai_contracts.md)
"""

from datetime import datetime
from openai import OpenAI
from pydantic import BaseModel
from django.conf import settings

from ai_core.interfaces import (
    PetProfile,
    ModelOutput,
    RiskAssessment,
    NutritionEngineInterface,
)


# Initialize OpenAI client at module level (same pattern as aihub/views.py)
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ==============================================================================
# Pydantic Models for Structured Output Parsing
# ==============================================================================

class NutritionRisks(BaseModel):
    """
    Health risk assessment structure for OpenAI structured outputs.
    
    Maps to RiskAssessment dataclass in ai_core.interfaces.
    Each risk level must be "low", "medium", or "high".
    """
    weight_risk: str  # Risk of obesity or unhealthy weight
    joint_risk: str  # Risk of arthritis, hip dysplasia, joint issues
    digestive_risk: str  # Risk of IBD, food sensitivities, digestive upset
    metabolic_risk: str  # Risk of diabetes, thyroid issues, metabolic disorders
    kidney_risk: str  # Risk of chronic kidney disease
    dental_risk: str  # Risk of periodontal disease, tooth decay


class NutritionPrediction(BaseModel):
    """
    Complete nutrition prediction structure for OpenAI structured outputs.
    
    This Pydantic model defines the schema that OpenAI will generate.
    Maps to ModelOutput dataclass in ai_core.interfaces.
    
    Based on: ai_core/docs/ai_contracts.md - ModelOutput Schema
    """
    # Caloric Requirements
    calories_per_day: int
    calorie_range_min: int
    calorie_range_max: int
    
    # Macronutrient Targets
    protein_percent: int
    fat_percent: int
    carbohydrate_percent: int
    
    # Diet Style Recommendation
    diet_style: str
    diet_style_confidence: float
    
    # Risk Assessment
    risks: NutritionRisks
    
    # Feeding Recommendations
    meals_per_day: int
    portion_size_grams: int
    
    # Model Metadata
    model_version: str
    confidence_score: float
    
    # Alerts & Flags
    veterinary_consultation_recommended: bool
    alert_messages: list[str]


# ==============================================================================
# OpenAI Engine Implementation
# ==============================================================================

class OpenAIEngine(NutritionEngineInterface):
    """
    OpenAI GPT-powered nutrition prediction engine.
    
    Uses OpenAI's Responses API with structured outputs to generate
    personalized pet nutrition recommendations and health risk assessments.
    
    This implementation:
    1. Converts PetProfile dataclass to a structured prompt
    2. Calls OpenAI GPT-4o with text_format=NutritionPrediction
    3. Parses the structured Pydantic output
    4. Converts to ModelOutput dataclass for API response
    
    Configuration:
    - Model: Configurable via settings.OPENAI_MODEL (default: gpt-4o-2024-08-06)
    - API Key: Read from settings.OPENAI_API_KEY
    
    Error Handling:
    - Raises RuntimeError on OpenAI API errors
    - Raises ValueError if output parsing fails
    - All exceptions are caught by NutritionPredictionView and returned as 500/503 responses
    """
    
    def __init__(self):
        """Initialize the OpenAI engine with model configuration."""
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-4o-2024-08-06")
    
    def predict(self, pet: PetProfile) -> ModelOutput:
        """
        Generate nutrition prediction for a pet profile.
        
        Args:
            pet: PetProfile dataclass with complete pet information
        
        Returns:
            ModelOutput: Structured prediction with calories, diet style, risks, etc.
        
        Raises:
            RuntimeError: If OpenAI API call fails
            ValueError: If output parsing or validation fails
        """
        try:
            # Step 1: Build prompt from pet profile
            prompt = self._build_prompt(pet)
            
            # Step 2: Call OpenAI with structured output
            parsed = self._call_openai(prompt)
            
            # Step 3: Convert Pydantic model to dataclass
            return self._convert_to_model_output(parsed)
            
        except Exception as e:
            # Re-raise with context for debugging
            raise RuntimeError(f"OpenAI engine prediction failed: {str(e)}") from e
    
    def _build_prompt(self, pet: PetProfile) -> str:
        """
        Build structured prompt for OpenAI from pet profile.
        
        The prompt:
        - Explains FAMMO's role and purpose
        - Provides complete pet profile data
        - Specifies exact output format requirements
        - Lists valid enum values (diet styles, risk levels)
        - Emphasizes safety and veterinary consultation guidelines
        
        Args:
            pet: PetProfile dataclass
        
        Returns:
            str: Complete prompt for OpenAI
        """
        # Format lists as comma-separated strings for readability
        conditions_str = ", ".join(pet.existing_conditions) if pet.existing_conditions else "None"
        allergies_str = ", ".join(pet.food_allergies) if pet.food_allergies else "None"
        medications_str = ", ".join(pet.medications) if pet.medications else "None"
        
        prompt = f"""You are a professional pet nutrition and preventive health assistant for FAMMO, an AI-powered pet wellness platform.

Your task is to generate a comprehensive nutrition prediction and health risk assessment for the pet described below.

**Important Guidelines:**
- Provide realistic, safe, evidence-based recommendations
- Base calorie calculations on standard RER formulas with activity multipliers
- Consider breed-specific risks and predispositions
- Flag any concerns that warrant veterinary consultation
- Be conservative with risk assessments - when in doubt, recommend professional consultation

**Pet Profile:**

**Identity & Basics:**
- Species: {pet.species}
- Breed: {pet.breed}
- Breed Size: {pet.breed_size_category}
- Age: {pet.age_years} years
- Life Stage: {pet.life_stage}

**Physical Attributes:**
- Current Weight: {pet.weight_kg} kg
- Body Condition Score: {pet.body_condition_score}/5 (1=emaciated, 3=ideal, 5=obese)
- Sex: {pet.sex}
- Neutered: {"Yes" if pet.neutered else "No"}

**Activity & Lifestyle:**
- Activity Level: {pet.activity_level}
- Living Environment: {pet.living_environment}

**Health & Medical:**
- Existing Conditions: {conditions_str}
- Food Allergies: {allergies_str}
- Current Medications: {medications_str}

**Current Diet:**
- Food Type: {pet.current_food_type}
- Food Satisfaction: {pet.food_satisfaction}
- Treat Frequency: {pet.treat_frequency}

**Goals & Preferences:**
- Health Goal: {pet.health_goal}
- Dietary Preference: {pet.dietary_preference}

**Environment:**
- Climate Zone: {pet.climate_zone}
- Country: {pet.country}

---

**Output Requirements:**

Generate a structured prediction with the following fields:

1. **Caloric Requirements:**
   - calories_per_day (int): Daily energy requirement in kcal (realistic range: 50-5000)
   - calorie_range_min (int): Lower safe range (typically 90% of calories_per_day)
   - calorie_range_max (int): Upper safe range (typically 110% of calories_per_day)

2. **Macronutrient Targets (as percentages of dry matter):**
   - protein_percent (int): 18-50%
   - fat_percent (int): 8-35%
   - carbohydrate_percent (int): 5-50%

3. **Diet Style Recommendation:**
   - diet_style (str): Choose ONE from:
     * "maintenance" - Standard balanced diet for healthy adults
     * "weight_loss" - Calorie-restricted for overweight/obese pets
     * "weight_gain" - Calorie-dense for underweight pets
     * "high_protein_performance" - For highly active/working dogs
     * "senior_wellness" - For healthy senior pets
     * "senior_wellness_kidney" - For seniors with kidney concerns
     * "growth_puppy" - For puppies (dogs)
     * "growth_kitten" - For kittens (cats)
     * "digestive_support" - For sensitive stomachs/allergies
     * "joint_support" - For joint health emphasis
   - diet_style_confidence (float): 0.0-1.0 (your confidence in this recommendation)

4. **Risk Assessment (each must be "low", "medium", or "high"):**
   - weight_risk: Risk of obesity or unhealthy weight
   - joint_risk: Risk of arthritis, hip dysplasia, joint issues
   - digestive_risk: Risk of IBD, food sensitivities
   - metabolic_risk: Risk of diabetes, thyroid issues
   - kidney_risk: Risk of chronic kidney disease
   - dental_risk: Risk of dental disease

5. **Feeding Recommendations:**
   - meals_per_day (int): 1-4 meals (puppies/kittens need 3-4, adults typically 2)
   - portion_size_grams (int): Approximate grams per meal for dry food reference

6. **Metadata:**
   - model_version (str): Use "1.0.0-openai"
   - confidence_score (float): 0.0-1.0 (overall prediction confidence)

7. **Alerts:**
   - veterinary_consultation_recommended (bool): True if vet should be consulted
   - alert_messages (list[str]): 0-5 concise alert/warning messages

**Risk Assessment Logic:**
- Weight risk: Base on body_condition_score and breed obesity predisposition
- Joint risk: Consider breed size, weight, age, existing conditions
- Digestive risk: Consider allergies, conditions, food satisfaction
- Metabolic risk: Consider age, weight, neutered status, breed
- Kidney risk: Consider age (especially senior cats), breed, conditions
- Dental risk: Consider age, breed size, food type

Generate safe, actionable recommendations that pet owners can implement with confidence."""

        return prompt
    
    def _call_openai(self, prompt: str) -> NutritionPrediction:
        """
        Call OpenAI Responses API with structured output parsing.
        
        Uses the same pattern as aihub/views.py but with NutritionPrediction schema.
        
        Args:
            prompt: Complete prompt string
        
        Returns:
            NutritionPrediction: Parsed Pydantic model from OpenAI
        
        Raises:
            RuntimeError: If API call fails or parsing fails
        """
        try:
            response = client.responses.parse(
                model=self.model,
                input=prompt,
                text_format=NutritionPrediction,
            )
            
            # Get parsed output
            parsed = response.output_parsed
            
            if parsed is None:
                raise ValueError("OpenAI returned None for output_parsed - response may have been filtered or failed")
            
            return parsed
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}") from e
    
    def _convert_to_model_output(self, parsed: NutritionPrediction) -> ModelOutput:
        """
        Convert Pydantic NutritionPrediction to ModelOutput dataclass.
        
        Args:
            parsed: NutritionPrediction Pydantic model from OpenAI
        
        Returns:
            ModelOutput: Dataclass instance for API serialization
        
        Raises:
            ValueError: If risk level validation fails
        """
        # Convert Pydantic model to dict
        data = parsed.model_dump()
        
        # Extract and validate risk data
        risks_data = data["risks"]
        risks = RiskAssessment(
            weight_risk=risks_data["weight_risk"],
            joint_risk=risks_data["joint_risk"],
            digestive_risk=risks_data["digestive_risk"],
            metabolic_risk=risks_data["metabolic_risk"],
            kidney_risk=risks_data["kidney_risk"],
            dental_risk=risks_data["dental_risk"],
        )
        
        # Add current timestamp
        prediction_timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Create ModelOutput dataclass
        return ModelOutput(
            calories_per_day=data["calories_per_day"],
            calorie_range_min=data["calorie_range_min"],
            calorie_range_max=data["calorie_range_max"],
            protein_percent=data["protein_percent"],
            fat_percent=data["fat_percent"],
            carbohydrate_percent=data["carbohydrate_percent"],
            diet_style=data["diet_style"],
            diet_style_confidence=data["diet_style_confidence"],
            risks=risks,
            meals_per_day=data["meals_per_day"],
            portion_size_grams=data["portion_size_grams"],
            model_version=data["model_version"],
            prediction_timestamp=prediction_timestamp,
            confidence_score=data["confidence_score"],
            veterinary_consultation_recommended=data["veterinary_consultation_recommended"],
            alert_messages=data["alert_messages"],
        )
