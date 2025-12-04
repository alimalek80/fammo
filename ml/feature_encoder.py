"""
Feature Encoder for FAMMO Calorie Prediction Model

This module provides a shared feature encoding function that is used by both:
1. Training scripts (ml/scripts/train_calorie_model.py)
2. ProprietaryEngine (ai_core/proprietary_backend.py)

This ensures consistency between training and inference, preventing feature
mismatch errors and ensuring reproducible predictions.

The feature encoder converts a PetProfile dataclass into a pandas DataFrame
with the exact feature set expected by the trained calorie regression model.

Feature Set:
    Numeric features (3):
        - weight_kg
        - age_years
        - body_condition_score
    
    Categorical features (4):
        - species
        - life_stage
        - breed_size_category
        - health_goal

Usage:
    from ai_core.interfaces import PetProfile
    from ml.feature_encoder import encode_pet_profile
    
    pet = PetProfile(
        species="dog",
        breed="Golden Retriever",
        age_years=3.5,
        weight_kg=29.0,
        body_condition_score=4,
        sex="male",
        neutered=True,
        activity_level="moderate",
        health_goal="weight_loss",
        ...
    )
    
    features_df = encode_pet_profile(pet)
    # Returns DataFrame with one row and 7 columns
"""

import pandas as pd
from typing import Union


def encode_pet_profile(pet: 'PetProfile') -> pd.DataFrame:
    """
    Convert a PetProfile dataclass into a DataFrame for model inference.
    
    This function extracts the exact features used during model training
    and returns them in the correct order and format expected by the
    scikit-learn pipeline.
    
    Args:
        pet: PetProfile dataclass instance with pet information
    
    Returns:
        pandas.DataFrame: Single-row DataFrame with 7 feature columns:
            - weight_kg (float)
            - age_years (float)
            - body_condition_score (int)
            - species (str)
            - life_stage (str)
            - breed_size_category (str)
            - health_goal (str)
    
    Raises:
        AttributeError: If pet is missing required attributes
        ValueError: If feature values are invalid
    
    Example:
        >>> pet = PetProfile(species="dog", weight_kg=25.0, ...)
        >>> features = encode_pet_profile(pet)
        >>> print(features.columns.tolist())
        ['weight_kg', 'age_years', 'body_condition_score', 'species', 
         'life_stage', 'breed_size_category', 'health_goal']
    """
    # Define feature columns in the exact order used during training
    numeric_features = ['weight_kg', 'age_years', 'body_condition_score']
    categorical_features = ['species', 'life_stage', 'breed_size_category', 'health_goal']
    
    # Extract features from PetProfile
    feature_dict = {
        # Numeric features
        'weight_kg': float(pet.weight_kg),
        'age_years': float(pet.age_years),
        'body_condition_score': int(pet.body_condition_score),
        
        # Categorical features
        'species': str(pet.species),
        'life_stage': str(pet.life_stage),
        'breed_size_category': str(pet.breed_size_category),
        'health_goal': str(pet.health_goal),
    }
    
    # Create DataFrame with single row
    features_df = pd.DataFrame([feature_dict])
    
    # Ensure column order matches training
    all_features = numeric_features + categorical_features
    features_df = features_df[all_features]
    
    return features_df


def get_feature_metadata():
    """
    Get metadata about the features used in the calorie model.
    
    Returns:
        dict: Feature metadata with keys:
            - numeric_features: List of numeric feature names
            - categorical_features: List of categorical feature names
            - all_features: Ordered list of all feature names
            - feature_count: Total number of features (7)
    
    Example:
        >>> metadata = get_feature_metadata()
        >>> print(metadata['feature_count'])
        7
    """
    numeric_features = ['weight_kg', 'age_years', 'body_condition_score']
    categorical_features = ['species', 'life_stage', 'breed_size_category', 'health_goal']
    all_features = numeric_features + categorical_features
    
    return {
        'numeric_features': numeric_features,
        'categorical_features': categorical_features,
        'all_features': all_features,
        'feature_count': len(all_features)
    }
