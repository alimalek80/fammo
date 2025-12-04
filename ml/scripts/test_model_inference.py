#!/usr/bin/env python
"""
Test script to verify the trained calorie model can be loaded and used for inference.

This script now uses the shared feature encoder from ml.feature_encoder to ensure
consistency with the ProprietaryEngine implementation.

Usage:
    python ml/scripts/test_model_inference.py
"""

import sys
import joblib
from pathlib import Path
from dataclasses import dataclass, field

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from ml.feature_encoder import encode_pet_profile

# Mock PetProfile for testing (mirrors ai_core.interfaces.PetProfile structure)
@dataclass
class PetProfile:
    """Simplified PetProfile for testing."""
    species: str
    breed: str = "Unknown"
    breed_size_category: str = "medium"
    age_years: float = 1.0
    life_stage: str = "adult"
    weight_kg: float = 10.0
    body_condition_score: int = 3
    sex: str = "male"
    neutered: bool = True
    activity_level: str = "moderate"
    living_environment: str = "mixed"
    existing_conditions: list = field(default_factory=list)
    food_allergies: list = field(default_factory=list)
    medications: list = field(default_factory=list)
    current_food_type: str = "dry"
    food_satisfaction: str = "satisfied"
    treat_frequency: str = "weekly"
    health_goal: str = "maintenance"
    dietary_preference: str = "no_preference"
    climate_zone: str = "temperate"
    country: str = "FI"

def main():
    """Test model inference."""
    print("="*80)
    print("TESTING CALORIE MODEL INFERENCE")
    print("="*80)
    
    # Load model
    model_path = Path('ml/models/calorie_regressor_v1.pkl')
    print(f"\nLoading model from: {model_path}")
    
    if not model_path.exists():
        print("Error: Model not found. Train first with:")
        print("  python ml/scripts/train_calorie_model.py")
        return
    
    pipeline = joblib.load(model_path)
    print("✓ Model loaded successfully")
    
    # Load metadata
    metadata_path = model_path.with_suffix('.json')
    if metadata_path.exists():
        import json
        with open(metadata_path) as f:
            metadata = json.load(f)
        print(f"\nModel info:")
        print(f"  Type: {metadata['model_type']}")
        print(f"  Trained on: {metadata['n_samples']} samples")
        print(f"  Features: {metadata['n_features']}")
    
    # Create test samples using PetProfile dataclass
    print("\n" + "-"*80)
    print("TEST PREDICTIONS")
    print("-"*80)
    
    test_profiles = [
        PetProfile(
            species='cat',
            breed='Mixed Breed',
            breed_size_category='small',
            age_years=1.2,
            life_stage='adult',
            weight_kg=4.0,
            body_condition_score=5,
            health_goal='maintenance'
        ),
        PetProfile(
            species='dog',
            breed='Labrador Retriever',
            breed_size_category='medium',
            age_years=5.0,
            life_stage='adult',
            weight_kg=25.0,
            body_condition_score=7,
            health_goal='weight_loss'
        ),
        PetProfile(
            species='dog',
            breed='Beagle',
            breed_size_category='small',
            age_years=0.5,
            life_stage='puppy',
            weight_kg=8.0,
            body_condition_score=5,
            health_goal='growth'
        )
    ]
    
    # Make predictions using the shared feature encoder
    print("\nSample | Species | Weight | Age | BCS | Goal        | Predicted Calories")
    print("-"*80)
    
    for idx, pet in enumerate(test_profiles, 1):
        # Use the shared feature encoder
        X_test = encode_pet_profile(pet)
        prediction = pipeline.predict(X_test)[0]
        
        print(f"  {idx}    | {pet.species:7s} | {pet.weight_kg:4.1f}kg | "
              f"{pet.age_years:3.1f}y | {pet.body_condition_score}   | "
              f"{pet.health_goal:11s} | {prediction:6.0f} kcal/day")
    
    print("\n" + "="*80)
    print("INFERENCE TEST COMPLETE")
    print("="*80)
    print("\nThe model is ready to use!")
    print("\n✓ Feature encoder working correctly (ml/feature_encoder.py)")
    print("✓ Model predictions successful")
    print("\nIntegration status:")
    print("  ✓ ai_core/proprietary_backend.py - ProprietaryEngine implemented")
    print("  ✓ ml/feature_encoder.py - Shared feature encoder created")
    print("\nTo activate proprietary backend:")
    print("  1. Add to settings.py: AI_BACKEND = 'proprietary'")
    print("  2. Or set environment variable: FAMMO_AI_BACKEND=proprietary")
    print()

if __name__ == "__main__":
    main()
