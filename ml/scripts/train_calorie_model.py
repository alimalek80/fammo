#!/usr/bin/env python
"""
Calorie Prediction Model Training Script

This script trains a baseline regression model to predict daily calorie requirements
(calories_per_day) from pet nutrition data exported from the FAMMO Django backend.

The model uses pet features like species, weight, age, life stage, and health goals
to predict appropriate calorie intake. This is a first baseline model that should be
retrained as more NutritionPredictionLog data becomes available.

Usage:
    python ml/scripts/train_calorie_model.py
    python ml/scripts/train_calorie_model.py --input=ml/data/nutrition_logs.jsonl
    python ml/scripts/train_calorie_model.py --output-model=ml/models/my_model.pkl

Requirements:
    - pandas
    - scikit-learn
    - joblib

The trained model will be saved as a scikit-learn Pipeline that can be loaded
and used for inference in the ai_core proprietary backend.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import pandas as pd
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    print("\nInstall dependencies with:")
    print("  pip install pandas scikit-learn joblib")
    sys.exit(1)


def load_nutrition_data(input_path):
    """
    Load nutrition logs from JSONL file.
    
    Args:
        input_path: Path to JSONL file
        
    Returns:
        pandas DataFrame with nutrition data
    """
    print(f"\nLoading data from: {input_path}")
    
    # Load JSONL file
    df = pd.read_json(input_path, lines=True)
    
    print(f"Loaded {len(df)} records")
    
    return df


def extract_target_variable(df):
    """
    Extract calories_per_day from output payload.
    
    Args:
        df: DataFrame with 'output' column
        
    Returns:
        DataFrame with extracted 'calories_per_day' column
    """
    # Extract calories_per_day from output dict
    if 'output' in df.columns:
        df['calories_per_day'] = df['output'].apply(
            lambda o: o.get('calories_per_day') if isinstance(o, dict) else None
        )
    
    # Drop rows with missing target
    initial_count = len(df)
    df = df.dropna(subset=['calories_per_day'])
    dropped = initial_count - len(df)
    
    if dropped > 0:
        print(f"Dropped {dropped} rows with missing calories_per_day")
    
    print(f"Final dataset size: {len(df)} records")
    
    return df


def prepare_features(df):
    """
    Prepare feature matrix from DataFrame.
    
    Extracts relevant features from top-level columns and input payload.
    Falls back to input dict if top-level columns are missing.
    
    Args:
        df: DataFrame with nutrition data
        
    Returns:
        DataFrame with selected features
    """
    # Define feature columns
    numeric_features = ['weight_kg', 'age_years', 'body_condition_score']
    categorical_features = ['species', 'life_stage', 'breed_size_category', 'health_goal']
    
    # Create features dataframe
    features_df = pd.DataFrame()
    
    # Extract numeric features
    for col in numeric_features:
        if col in df.columns:
            features_df[col] = df[col]
        elif 'input' in df.columns:
            # Try to extract from input payload
            features_df[col] = df['input'].apply(
                lambda x: x.get(col) if isinstance(x, dict) else None
            )
        else:
            features_df[col] = None
    
    # Extract categorical features
    for col in categorical_features:
        if col in df.columns:
            features_df[col] = df[col]
        elif 'input' in df.columns:
            # Try to extract from input payload
            features_df[col] = df['input'].apply(
                lambda x: x.get(col) if isinstance(x, dict) else None
            )
        else:
            features_df[col] = None
    
    # Fill missing categorical values with 'unknown'
    for col in categorical_features:
        features_df[col] = features_df[col].fillna('unknown')
    
    # Drop rows with missing numeric features
    initial_count = len(features_df)
    features_df = features_df.dropna(subset=numeric_features)
    dropped = initial_count - len(features_df)
    
    if dropped > 0:
        print(f"Dropped {dropped} rows with missing numeric features")
    
    return features_df, numeric_features, categorical_features


def build_pipeline(numeric_features, categorical_features):
    """
    Build scikit-learn pipeline for calorie prediction.
    
    Args:
        numeric_features: List of numeric feature names
        categorical_features: List of categorical feature names
        
    Returns:
        sklearn Pipeline
    """
    # Define preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )
    
    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=1  # Use single thread for shared hosting compatibility
        ))
    ])
    
    return pipeline


def train_model(X, y, test_size=0.2, random_state=42):
    """
    Train the calorie prediction model.
    
    Args:
        X: Feature matrix
        y: Target vector
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (trained_pipeline, X_test, y_test, X_train, y_train)
        If dataset is too small, returns (trained_pipeline, None, None, X, y)
    """
    # Check if dataset is large enough for train/test split
    if len(X) < 20:
        print(f"\n⚠ Warning: Dataset has only {len(X)} samples")
        print("Training on all data without test split (metrics will be unreliable)")
        
        # Get feature lists
        _, numeric_features, categorical_features = prepare_features(pd.DataFrame())
        
        # Build and train pipeline on all data
        pipeline = build_pipeline(numeric_features, categorical_features)
        pipeline.fit(X, y)
        
        return pipeline, None, None, X, y
    
    # Perform train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set:  {len(X_test)} samples")
    
    # Get feature lists from X columns
    numeric_features = ['weight_kg', 'age_years', 'body_condition_score']
    categorical_features = ['species', 'life_stage', 'breed_size_category', 'health_goal']
    
    # Build pipeline
    pipeline = build_pipeline(numeric_features, categorical_features)
    
    # Train model
    print("\nTraining Random Forest Regressor...")
    pipeline.fit(X_train, y_train)
    print("✓ Training complete")
    
    return pipeline, X_test, y_test, X_train, y_train


def evaluate_model(pipeline, X_train, y_train, X_test=None, y_test=None):
    """
    Evaluate the trained model and print metrics.
    
    Args:
        pipeline: Trained sklearn Pipeline
        X_train: Training features
        y_train: Training targets
        X_test: Test features (optional)
        y_test: Test targets (optional)
    """
    print("\n" + "="*80)
    print("MODEL EVALUATION")
    print("="*80)
    
    # Training metrics
    y_train_pred = pipeline.predict(X_train)
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_mse = mean_squared_error(y_train, y_train_pred)
    train_rmse = train_mse ** 0.5
    train_r2 = r2_score(y_train, y_train_pred)
    
    print("\nTraining Set Metrics:")
    print(f"  MAE:  {train_mae:.2f} kcal/day")
    print(f"  RMSE: {train_rmse:.2f} kcal/day")
    print(f"  R²:   {train_r2:.4f}")
    
    # Test metrics (if available)
    if X_test is not None and y_test is not None:
        y_test_pred = pipeline.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        test_rmse = test_mse ** 0.5
        test_r2 = r2_score(y_test, y_test_pred)
        
        print("\nTest Set Metrics:")
        print(f"  MAE:  {test_mae:.2f} kcal/day")
        print(f"  RMSE: {test_rmse:.2f} kcal/day")
        print(f"  R²:   {test_r2:.4f}")
        
        # Show some example predictions
        print("\nSample Predictions (first 5 test examples):")
        print("  Actual  | Predicted | Error")
        print("  " + "-"*35)
        for i in range(min(5, len(y_test))):
            actual = y_test.iloc[i] if hasattr(y_test, 'iloc') else y_test[i]
            predicted = y_test_pred[i]
            error = abs(actual - predicted)
            print(f"  {actual:6.0f}  | {predicted:9.0f} | {error:5.0f}")
    else:
        print("\n⚠ No test set available - metrics are based on training data only")
    
    print("\n" + "="*80)


def print_feature_importance(pipeline, feature_names):
    """
    Print feature importance from the trained Random Forest model.
    
    Args:
        pipeline: Trained sklearn Pipeline
        feature_names: List of original feature names
    """
    # Get the regressor from pipeline
    regressor = pipeline.named_steps['regressor']
    
    # Get feature names after preprocessing
    preprocessor = pipeline.named_steps['preprocessor']
    
    # Extract feature names from transformers
    feature_names_out = []
    
    # Numeric features (3 features: weight_kg, age_years, body_condition_score)
    numeric_features = ['weight_kg', 'age_years', 'body_condition_score']
    feature_names_out.extend(numeric_features)
    
    # Categorical features (after one-hot encoding)
    categorical_transformer = preprocessor.named_transformers_['cat']
    if hasattr(categorical_transformer, 'get_feature_names_out'):
        cat_features = categorical_transformer.get_feature_names_out()
        feature_names_out.extend(cat_features)
    
    # Get feature importances
    importances = regressor.feature_importances_
    
    # Create feature importance dataframe
    importance_df = pd.DataFrame({
        'feature': feature_names_out[:len(importances)],
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print("  " + "-"*50)
    for idx, row in importance_df.head(10).iterrows():
        print(f"  {row['feature']:40s} {row['importance']:.4f}")


def save_model(pipeline, output_path, metadata=None):
    """
    Save the trained pipeline to disk.
    
    Args:
        pipeline: Trained sklearn Pipeline
        output_path: Path to save the model
        metadata: Optional dict with model metadata
    """
    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save pipeline
    joblib.dump(pipeline, output_path)
    
    print(f"\n✓ Model saved to: {output_path.absolute()}")
    
    # Save metadata if provided
    if metadata:
        metadata_path = output_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved to: {metadata_path.absolute()}")


def main():
    """Main execution function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Train a calorie prediction model from FAMMO nutrition logs'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='ml/data/nutrition_logs.jsonl',
        help='Path to input JSONL file (default: ml/data/nutrition_logs.jsonl)'
    )
    parser.add_argument(
        '--output-model',
        type=str,
        default='ml/models/calorie_regressor_v1.pkl',
        help='Path to save trained model (default: ml/models/calorie_regressor_v1.pkl)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    input_path = Path(args.input)
    output_model_path = Path(args.output_model)
    
    # Check if input file exists
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("\nTo export data from Django, run:")
        print("  python manage.py export_nutrition_logs --output=ml/data/nutrition_logs.jsonl")
        sys.exit(1)
    
    print("="*80)
    print("FAMMO CALORIE PREDICTION MODEL TRAINING")
    print("="*80)
    
    # Load data
    df = load_nutrition_data(input_path)
    
    # Extract target variable
    df = extract_target_variable(df)
    
    if len(df) == 0:
        print("\nError: No valid data found with calories_per_day")
        print("Ensure the exported data contains output payloads with calorie predictions")
        sys.exit(1)
    
    # Prepare features
    X, numeric_features, categorical_features = prepare_features(df)
    
    # Ensure we have matching indices
    y = df.loc[X.index, 'calories_per_day']
    
    if len(X) == 0:
        print("\nError: No valid samples after feature extraction")
        print("Check that the data contains required features:")
        print(f"  Numeric: {numeric_features}")
        print(f"  Categorical: {categorical_features}")
        sys.exit(1)
    
    print(f"\nFeatures used:")
    print(f"  Numeric: {', '.join(numeric_features)}")
    print(f"  Categorical: {', '.join(categorical_features)}")
    print(f"  Total samples: {len(X)}")
    
    # Train model
    pipeline, X_test, y_test, X_train, y_train = train_model(X, y)
    
    # Evaluate model
    evaluate_model(pipeline, X_train, y_train, X_test, y_test)
    
    # Print feature importance
    try:
        print_feature_importance(pipeline, numeric_features + categorical_features)
    except Exception as e:
        print(f"\n⚠ Could not extract feature importance: {e}")
    
    # Save model
    metadata = {
        'model_type': 'RandomForestRegressor',
        'n_samples': len(X),
        'n_features': len(numeric_features) + len(categorical_features),
        'numeric_features': numeric_features,
        'categorical_features': categorical_features,
        'target': 'calories_per_day',
        'description': 'Baseline calorie prediction model for FAMMO pet nutrition'
    }
    
    save_model(pipeline, output_model_path, metadata)
    
    print("\n" + "="*80)
    print("TRAINING COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("  1. Review the metrics above to assess model quality")
    print("  2. Collect more training data through the API")
    print("  3. Retrain periodically as more data becomes available")
    print("  4. Integrate this model into ai_core/proprietary_backend.py")
    print("\n")


if __name__ == "__main__":
    main()
