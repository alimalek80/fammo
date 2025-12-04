"""
Proprietary ML-based implementation of NutritionEngineInterface.

This module provides FAMMO's proprietary machine learning-powered nutrition
prediction engine. It uses trained scikit-learn models (Random Forest, XGBoost)
to generate predictions based on labeled pet nutrition data.

This engine can be activated via settings.AI_BACKEND = "proprietary".

Key differences from OpenAIEngine:
- Uses FAMMO's trained models instead of GPT APIs
- Faster inference (no API latency)
- No per-request API costs
- Predictable, deterministic outputs
- Can be retrained as more data becomes available

Model Architecture:
- Calorie prediction: Random Forest Regressor
- Risk assessment: Heuristic-based (future: multi-task classifier)
- Diet style: Derived from health_goal (future: dedicated classifier)
- Macronutrients: Heuristic-based (future: multi-output regressor)

Model Location:
- ml/models/calorie_regressor_v1.pkl (trained pipeline)
- ml/models/calorie_regressor_v1.json (metadata)

IMPORTANT NOTE - Model Training Status:
The baseline model is trained on a small initial dataset (~13 samples) and may
not show strong feature-target relationships. This is sufficient for Phase 9
integration testing but will improve significantly as more data is collected.

To improve model quality:
1. Use the OpenAI backend to collect more labeled data
2. Export logs: python manage.py export_nutrition_logs
3. Retrain: python ml/scripts/train_calorie_model.py
4. Switch to proprietary backend once confident in model performance
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import json

try:
    import joblib
    import pandas as pd
except ImportError as e:
    raise ImportError(
        f"Required ML dependencies not installed: {e}\n"
        "Install with: pip install pandas scikit-learn joblib"
    ) from e

from django.conf import settings

from ai_core.interfaces import (
    PetProfile,
    ModelOutput,
    RiskAssessment,
    NutritionEngineInterface,
)

# Import the shared feature encoder
from ml.feature_encoder import encode_pet_profile


class ProprietaryEngine(NutritionEngineInterface):
    """
    FAMMO's proprietary ML-based nutrition prediction engine.
    
    Uses trained machine learning models to generate predictions:
    - Calorie prediction from trained Random Forest model
    - Diet style derived from health_goal and predicted calories
    - Risk assessment using heuristics based on breed, age, weight, and BCS
    - Macronutrient ratios using veterinary guidelines
    
    The model is loaded once at initialization (lazy loading pattern) and
    cached for the lifetime of the engine instance.
    
    Configuration:
        In settings.py:
            AI_BACKEND = "proprietary"  # Activates this engine
            PROPRIETARY_MODEL_PATH = "ml/models/calorie_regressor_v1.pkl"  # Optional
    
    Usage:
        from ai_core.engine import get_engine
        from ai_core.interfaces import PetProfile
        
        engine = get_engine()  # Returns ProprietaryEngine if AI_BACKEND="proprietary"
        profile = PetProfile(species="dog", weight_kg=25.0, ...)
        output = engine.predict(profile)
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the proprietary engine.
        
        Args:
            model_path: Optional path to model file. If None, uses default location.
        """
        self.model_path = model_path or self._get_default_model_path()
        self.model = None
        self.metadata = None
        self._load_model()
    
    def _get_default_model_path(self) -> Path:
        """Get the default path to the trained model."""
        # Check if settings override exists
        if hasattr(settings, 'PROPRIETARY_MODEL_PATH'):
            return Path(settings.PROPRIETARY_MODEL_PATH)
        
        # Default to ml/models/calorie_regressor_v1.pkl relative to BASE_DIR
        base_dir = getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent.parent)
        return base_dir / 'ml' / 'models' / 'calorie_regressor_v1.pkl'
    
    def _load_model(self):
        """Load the trained model and metadata from disk."""
        model_path = Path(self.model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Trained model not found at: {model_path}\n"
                f"Train the model first with:\n"
                f"  python ml/scripts/train_calorie_model.py\n"
                f"Or switch back to OpenAI backend:\n"
                f"  AI_BACKEND='openai' in settings.py"
            )
        
        # Load the scikit-learn pipeline
        try:
            self.model = joblib.load(model_path)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load model from {model_path}: {e}"
            ) from e
        
        # Load metadata if available
        metadata_path = model_path.with_suffix('.json')
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                # Metadata is optional, continue without it
                self.metadata = {}
        else:
            self.metadata = {}
    
    def predict(self, pet: PetProfile) -> ModelOutput:
        """
        Generate nutrition prediction for a pet profile.
        
        This method:
        1. Encodes the pet profile into feature vector using ml.feature_encoder
        2. Predicts calories_per_day using the trained model
        3. Derives calorie range (±15%)
        4. Maps health_goal to diet_style
        5. Generates macronutrient ratios using veterinary guidelines
        6. Assesses health risks using heuristics
        7. Returns structured ModelOutput
        
        Args:
            pet: PetProfile dataclass with complete pet information
        
        Returns:
            ModelOutput: Structured prediction with all required fields
        
        Raises:
            ValueError: If pet profile contains invalid data
            RuntimeError: If model prediction fails
        """
        try:
            # Step 1: Encode pet profile to feature vector
            features_df = encode_pet_profile(pet)
            
            # Step 2: Predict calories using trained model
            calories_pred = self.model.predict(features_df)[0]
            
            # Ensure calories is a positive integer
            calories_per_day = int(max(50, round(calories_pred)))
            
            # Step 3: Calculate calorie range (±15%)
            delta = calories_per_day * 0.15
            calorie_range_min = int(max(50, calories_per_day - delta))
            calorie_range_max = int(calories_per_day + delta)
            
            # Step 4: Derive diet style from health_goal
            diet_style, diet_style_confidence = self._derive_diet_style(pet)
            
            # Step 5: Calculate macronutrient ratios
            protein_percent, fat_percent, carbohydrate_percent = self._calculate_macros(pet)
            
            # Step 6: Assess health risks
            risks = self._assess_risks(pet)
            
            # Step 7: Calculate feeding recommendations
            meals_per_day = self._calculate_meals_per_day(pet)
            portion_size_grams = self._calculate_portion_size(calories_per_day, meals_per_day)
            
            # Step 8: Generate alerts and veterinary consultation flag
            vet_consultation, alert_messages = self._generate_alerts(pet, calories_per_day)
            
            # Step 9: Build ModelOutput
            return ModelOutput(
                # Caloric requirements
                calories_per_day=calories_per_day,
                calorie_range_min=calorie_range_min,
                calorie_range_max=calorie_range_max,
                
                # Macronutrients
                protein_percent=protein_percent,
                fat_percent=fat_percent,
                carbohydrate_percent=carbohydrate_percent,
                
                # Diet style
                diet_style=diet_style,
                diet_style_confidence=diet_style_confidence,
                
                # Risk assessment
                risks=risks,
                
                # Feeding recommendations
                meals_per_day=meals_per_day,
                portion_size_grams=portion_size_grams,
                
                # Model metadata
                model_version="proprietary-v1.0.0",
                prediction_timestamp=datetime.now(timezone.utc).isoformat(),
                confidence_score=0.85,  # Overall confidence for proprietary model
                
                # Alerts
                veterinary_consultation_recommended=vet_consultation,
                alert_messages=alert_messages,
            )
            
        except Exception as e:
            raise RuntimeError(
                f"Proprietary engine prediction failed: {str(e)}"
            ) from e
    
    def _derive_diet_style(self, pet: PetProfile) -> tuple[str, float]:
        """
        Derive diet style from health goal and pet characteristics.
        
        Future: Replace with trained classifier.
        
        Args:
            pet: PetProfile instance
        
        Returns:
            Tuple of (diet_style, confidence)
        """
        goal = pet.health_goal.lower()
        
        # Map health goals to diet styles
        style_map = {
            'weight_loss': ('weight_loss', 0.85),
            'weight_gain': ('weight_gain', 0.85),
            'muscle_building': ('active', 0.80),
            'joint_support': ('senior_wellness', 0.75),
            'maintenance': ('balanced', 0.90),
        }
        
        # Check for life stage specific styles
        if pet.life_stage in ['puppy', 'kitten']:
            return ('growth_puppy' if pet.species == 'dog' else 'growth_kitten', 0.90)
        elif pet.life_stage == 'senior':
            return ('senior_wellness', 0.85)
        
        # Return mapped style or default
        return style_map.get(goal, ('balanced', 0.75))
    
    def _calculate_macros(self, pet: PetProfile) -> tuple[int, int, int]:
        """
        Calculate macronutrient percentages using veterinary guidelines.
        
        Future: Replace with trained multi-output regressor.
        
        Args:
            pet: PetProfile instance
        
        Returns:
            Tuple of (protein_percent, fat_percent, carbohydrate_percent)
        """
        # Base values
        protein = 25
        fat = 12
        carbs = 30
        
        # Adjust based on life stage
        if pet.life_stage in ['puppy', 'kitten']:
            protein = 32  # Higher protein for growth
            fat = 18  # Higher fat for energy
            carbs = 20
        elif pet.life_stage == 'senior':
            protein = 28  # Moderate protein
            fat = 10  # Lower fat
            carbs = 25
        
        # Adjust based on health goal
        if pet.health_goal == 'weight_loss':
            protein = 30  # Higher protein to preserve muscle
            fat = 9  # Lower fat
            carbs = 20  # Lower carbs
        elif pet.health_goal == 'muscle_building':
            protein = 35  # High protein
            fat = 15
            carbs = 25
        
        # Adjust based on activity level
        if pet.activity_level in ['high', 'very_high']:
            fat = min(fat + 3, 20)  # More fat for energy
        elif pet.activity_level == 'sedentary':
            fat = max(fat - 2, 8)  # Less fat for inactive pets
        
        return protein, fat, carbs
    
    def _assess_risks(self, pet: PetProfile) -> RiskAssessment:
        """
        Assess health risks using heuristics.
        
        Future: Replace with trained multi-task classifier.
        
        Args:
            pet: PetProfile instance
        
        Returns:
            RiskAssessment dataclass
        """
        # Weight risk (based on BCS)
        if pet.body_condition_score >= 4:
            weight_risk = "high"
        elif pet.body_condition_score == 3:
            weight_risk = "low"
        else:
            weight_risk = "medium"
        
        # Joint risk (based on breed size, age, weight)
        joint_risk = "low"
        if pet.breed_size_category in ['large', 'giant']:
            joint_risk = "medium"
        if pet.age_years >= 7:
            joint_risk = "medium" if joint_risk == "low" else "high"
        if pet.body_condition_score >= 4:
            joint_risk = "high"
        
        # Digestive risk (based on food allergies and current food satisfaction)
        digestive_risk = "low"
        if len(pet.food_allergies) > 0:
            digestive_risk = "medium"
        if pet.food_satisfaction in ['picky', 'overeating']:
            digestive_risk = "medium" if digestive_risk == "low" else "high"
        
        # Metabolic risk (based on age, BCS, breed)
        metabolic_risk = "low"
        if pet.body_condition_score >= 4:
            metabolic_risk = "medium"
        if pet.age_years >= 8:
            metabolic_risk = "medium" if metabolic_risk == "low" else "high"
        
        # Kidney risk (higher for cats, senior pets)
        kidney_risk = "low"
        if pet.species == "cat":
            kidney_risk = "medium"
        if pet.age_years >= 10:
            kidney_risk = "high"
        
        # Dental risk (based on age, diet type)
        dental_risk = "low"
        if pet.current_food_type == "wet":
            dental_risk = "medium"
        if pet.age_years >= 5:
            dental_risk = "medium" if dental_risk == "low" else "high"
        
        return RiskAssessment(
            weight_risk=weight_risk,
            joint_risk=joint_risk,
            digestive_risk=digestive_risk,
            metabolic_risk=metabolic_risk,
            kidney_risk=kidney_risk,
            dental_risk=dental_risk,
        )
    
    def _calculate_meals_per_day(self, pet: PetProfile) -> int:
        """Calculate recommended number of meals per day."""
        if pet.life_stage in ['puppy', 'kitten']:
            return 3 if pet.age_years < 0.5 else 2
        elif pet.species == 'cat':
            return 2  # Cats typically prefer 2 meals
        else:
            return 2  # Dogs typically 2 meals
    
    def _calculate_portion_size(self, calories: int, meals: int) -> int:
        """
        Calculate portion size in grams (dry food reference).
        
        Assumes ~350 kcal per 100g of dry food (typical kibble).
        """
        kcal_per_100g = 350
        total_grams = (calories / kcal_per_100g) * 100
        portion_grams = total_grams / meals
        return int(round(portion_grams))
    
    def _generate_alerts(self, pet: PetProfile, calories: int) -> tuple[bool, list[str]]:
        """
        Generate alert messages and veterinary consultation flag.
        
        Args:
            pet: PetProfile instance
            calories: Predicted daily calories
        
        Returns:
            Tuple of (vet_consultation_recommended, alert_messages)
        """
        alerts = []
        vet_consultation = False
        
        # Very low or high calorie needs
        if calories < 150 or calories > 3000:
            alerts.append("Unusual caloric requirements detected. Verify with veterinarian.")
            vet_consultation = True
        
        # Extreme body condition
        if pet.body_condition_score == 1:
            alerts.append("Severely underweight. Immediate veterinary consultation recommended.")
            vet_consultation = True
        elif pet.body_condition_score == 5:
            alerts.append("Severely obese. Veterinary-supervised weight loss recommended.")
            vet_consultation = True
        
        # Multiple health conditions
        if len(pet.existing_conditions) >= 3:
            alerts.append("Multiple health conditions detected. Consult veterinarian for tailored diet.")
            vet_consultation = True
        
        # Senior pets with low activity
        if pet.age_years >= 10 and pet.activity_level == 'sedentary':
            alerts.append("Senior pet with low activity. Monitor for age-related health issues.")
        
        # Food allergies with digestive issues
        if len(pet.food_allergies) > 0 and pet.food_satisfaction == 'picky':
            alerts.append("Food allergies detected. Consider hypoallergenic diet options.")
        
        return vet_consultation, alerts
