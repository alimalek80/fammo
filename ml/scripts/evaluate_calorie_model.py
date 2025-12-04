#!/usr/bin/env python
"""
Calorie Prediction Model Evaluation Script

This script evaluates the trained regression model by comparing its predictions
against the original calorie values from OpenAI/aihub stored in nutrition logs.

The purpose is to assess model quality and understand how well the offline ML model
can approximate the current AI-generated calorie predictions before integrating
a proprietary engine into the ai_core Django backend.

Usage:
    python ml/scripts/evaluate_calorie_model.py
    python ml/scripts/evaluate_calorie_model.py --input=ml/data/nutrition_logs.jsonl
    python ml/scripts/evaluate_calorie_model.py --model=ml/models/my_model.pkl

Metrics computed:
    - MAE (Mean Absolute Error): Average absolute difference in calories
    - RMSE (Root Mean Squared Error): Penalizes larger errors more
    - R² (Coefficient of Determination): How well the model explains variance
    - MAPE (Mean Absolute Percentage Error): Average percentage error

The script also shows example predictions to help understand model behavior.
"""

import argparse
import sys
from pathlib import Path

try:
    import pandas as pd
    import joblib
    import numpy as np
    from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    print("\nInstall dependencies with:")
    print("  pip install pandas scikit-learn joblib")
    sys.exit(1)


def load_model(model_path):
    """
    Load trained model from disk.
    
    Args:
        model_path: Path to saved model (.pkl file)
        
    Returns:
        Loaded sklearn Pipeline
    """
    print(f"\nLoading model from: {model_path}")
    
    if not model_path.exists():
        print(f"Error: Model file not found: {model_path}")
        print("\nTrain a model first with:")
        print("  python ml/scripts/train_calorie_model.py")
        sys.exit(1)
    
    pipeline = joblib.load(model_path)
    print("✓ Model loaded successfully")
    
    # Try to load metadata
    metadata_path = model_path.with_suffix('.json')
    if metadata_path.exists():
        import json
        with open(metadata_path) as f:
            metadata = json.load(f)
        print(f"\nModel metadata:")
        print(f"  Type: {metadata.get('model_type', 'unknown')}")
        print(f"  Trained on: {metadata.get('n_samples', 'unknown')} samples")
        print(f"  Features: {metadata.get('n_features', 'unknown')}")
    
    return pipeline


def load_nutrition_data(input_path):
    """
    Load nutrition logs from JSONL file.
    
    Args:
        input_path: Path to JSONL file
        
    Returns:
        pandas DataFrame with nutrition data
    """
    print(f"\nLoading data from: {input_path}")
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("\nExport data from Django first with:")
        print("  python manage.py export_nutrition_logs --output=ml/data/nutrition_logs.jsonl")
        sys.exit(1)
    
    # Load JSONL file
    df = pd.read_json(input_path, lines=True)
    
    print(f"Loaded {len(df)} records")
    
    return df


def extract_features_and_target(df):
    """
    Extract features and target variable from DataFrame.
    
    Uses the same feature extraction logic as train_calorie_model.py
    to ensure consistency.
    
    Args:
        df: DataFrame with nutrition data
        
    Returns:
        Tuple of (X, y, feature_info) where feature_info contains metadata
    """
    # Extract target from output payload
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
    
    if len(df) == 0:
        print("\nError: No valid data found with calories_per_day")
        sys.exit(1)
    
    print(f"Valid samples: {len(df)}")
    
    # Define feature columns (must match training script)
    numeric_features = ['weight_kg', 'age_years', 'body_condition_score']
    categorical_features = ['species', 'life_stage', 'breed_size_category', 'health_goal']
    
    # Create features dataframe
    features_df = pd.DataFrame()
    
    # Extract numeric features
    for col in numeric_features:
        if col in df.columns:
            features_df[col] = df[col]
        elif 'input' in df.columns:
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
    
    # Get target values for the same indices
    y = df.loc[features_df.index, 'calories_per_day']
    
    # Also extract metadata for display
    metadata_df = df.loc[features_df.index, ['species', 'weight_kg', 'age_years', 
                                              'life_stage', 'health_goal', 'source', 
                                              'backend', 'model_version']].copy()
    
    feature_info = {
        'numeric': numeric_features,
        'categorical': categorical_features,
        'metadata': metadata_df
    }
    
    return features_df, y, feature_info


def calculate_mape(y_true, y_pred):
    """
    Calculate Mean Absolute Percentage Error (MAPE).
    
    Safely handles zero values by skipping them.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        MAPE as a percentage
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Avoid division by zero
    mask = y_true != 0
    
    if not mask.any():
        return np.nan
    
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    return mape


def evaluate_model(pipeline, X, y, feature_info):
    """
    Evaluate the model and print metrics.
    
    Args:
        pipeline: Trained sklearn Pipeline
        X: Feature matrix
        y: Target vector
        feature_info: Dictionary with feature metadata
    """
    print("\n" + "="*80)
    print("MODEL EVALUATION RESULTS")
    print("="*80)
    
    # Make predictions
    print("\nGenerating predictions...")
    y_pred = pipeline.predict(X)
    
    # Calculate metrics
    mae = mean_absolute_error(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    rmse = mse ** 0.5
    r2 = r2_score(y, y_pred)
    mape = calculate_mape(y, y_pred)
    
    # Print metrics
    print("\nPrediction Metrics:")
    print("-" * 80)
    print(f"  MAE (Mean Absolute Error):       {mae:8.2f} kcal/day")
    print(f"  RMSE (Root Mean Squared Error):  {rmse:8.2f} kcal/day")
    print(f"  R² (Coefficient of Determination): {r2:8.4f}")
    
    if not np.isnan(mape):
        print(f"  MAPE (Mean Absolute % Error):    {mape:8.2f}%")
    else:
        print(f"  MAPE: N/A (division by zero)")
    
    print("\nInterpretation:")
    print(f"  - On average, predictions are off by {mae:.0f} calories per day")
    print(f"  - The model explains {r2*100:.1f}% of the variance in calorie predictions")
    
    if r2 < 0:
        print("  ⚠ R² is negative - model performs worse than predicting the mean")
    elif r2 < 0.3:
        print("  ⚠ R² is low - model has limited predictive power")
    elif r2 < 0.7:
        print("  ⚠ R² is moderate - model captures some patterns but has room for improvement")
    else:
        print("  ✓ R² is good - model captures most of the variance")
    
    # Calculate residuals
    residuals = y - y_pred
    
    print("\nResidual Statistics:")
    print("-" * 80)
    print(f"  Mean residual:     {residuals.mean():8.2f} kcal/day")
    print(f"  Std residual:      {residuals.std():8.2f} kcal/day")
    print(f"  Min residual:      {residuals.min():8.2f} kcal/day")
    print(f"  Max residual:      {residuals.max():8.2f} kcal/day")
    
    # Show prediction distribution
    print("\nPrediction Range:")
    print("-" * 80)
    print(f"  True values:       {y.min():.0f} - {y.max():.0f} kcal/day")
    print(f"  Predicted values:  {y_pred.min():.0f} - {y_pred.max():.0f} kcal/day")
    
    return y_pred, mae, rmse, r2, mape


def show_prediction_examples(X, y, y_pred, feature_info, n_examples=10):
    """
    Display sample predictions for inspection.
    
    Args:
        X: Feature matrix
        y: True target values
        y_pred: Predicted values
        feature_info: Dictionary with feature metadata
        n_examples: Number of examples to show
    """
    print("\n" + "="*80)
    print("SAMPLE PREDICTIONS")
    print("="*80)
    
    # Create results dataframe
    metadata = feature_info['metadata']
    results_df = metadata.copy()
    results_df['true_calories'] = y.values
    results_df['pred_calories'] = y_pred
    results_df['difference'] = y.values - y_pred
    results_df['abs_error'] = np.abs(results_df['difference'])
    results_df['pct_error'] = (results_df['abs_error'] / results_df['true_calories']) * 100
    
    # Show first n examples
    n = min(n_examples, len(results_df))
    
    print(f"\nFirst {n} predictions:")
    print("-" * 80)
    print(f"{'#':<3} {'Species':<8} {'Weight':<7} {'Age':<6} {'Source':<8} "
          f"{'True':<7} {'Pred':<7} {'Error':<7} {'%Err':<6}")
    print("-" * 80)
    
    for idx, (i, row) in enumerate(results_df.head(n).iterrows(), 1):
        print(f"{idx:<3} {row['species']:<8} {row['weight_kg']:>5.1f}kg "
              f"{row['age_years']:>4.1f}y {row['source']:<8} "
              f"{row['true_calories']:>6.0f} {row['pred_calories']:>6.0f} "
              f"{row['difference']:>6.0f} {row['pct_error']:>5.1f}%")
    
    # Show worst predictions
    print(f"\nWorst {min(5, n)} predictions (largest errors):")
    print("-" * 80)
    print(f"{'#':<3} {'Species':<8} {'Weight':<7} {'Age':<6} {'Source':<8} "
          f"{'True':<7} {'Pred':<7} {'Error':<7} {'%Err':<6}")
    print("-" * 80)
    
    worst = results_df.nlargest(min(5, n), 'abs_error')
    for idx, (i, row) in enumerate(worst.iterrows(), 1):
        print(f"{idx:<3} {row['species']:<8} {row['weight_kg']:>5.1f}kg "
              f"{row['age_years']:>4.1f}y {row['source']:<8} "
              f"{row['true_calories']:>6.0f} {row['pred_calories']:>6.0f} "
              f"{row['difference']:>6.0f} {row['pct_error']:>5.1f}%")
    
    # Group by source
    print("\nPerformance by Data Source:")
    print("-" * 80)
    for source in results_df['source'].unique():
        source_df = results_df[results_df['source'] == source]
        source_mae = source_df['abs_error'].mean()
        source_mape = (source_df['abs_error'] / source_df['true_calories']).mean() * 100
        print(f"  {source:15s} - MAE: {source_mae:6.2f} kcal/day, "
              f"MAPE: {source_mape:5.2f}%, n={len(source_df)}")
    
    print("\n" + "="*80)


def main():
    """Main execution function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Evaluate trained calorie prediction model against original data'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='ml/data/nutrition_logs.jsonl',
        help='Path to input JSONL file (default: ml/data/nutrition_logs.jsonl)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='ml/models/calorie_regressor_v1.pkl',
        help='Path to trained model (default: ml/models/calorie_regressor_v1.pkl)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    input_path = Path(args.input)
    model_path = Path(args.model)
    
    print("="*80)
    print("CALORIE MODEL EVALUATION")
    print("="*80)
    
    # Load model
    pipeline = load_model(model_path)
    
    # Load data
    df = load_nutrition_data(input_path)
    
    # Extract features and target
    X, y, feature_info = extract_features_and_target(df)
    
    print(f"\nEvaluation dataset:")
    print(f"  Samples: {len(X)}")
    print(f"  Features: {len(feature_info['numeric']) + len(feature_info['categorical'])}")
    print(f"    Numeric: {', '.join(feature_info['numeric'])}")
    print(f"    Categorical: {', '.join(feature_info['categorical'])}")
    
    # Evaluate model
    y_pred, mae, rmse, r2, mape = evaluate_model(pipeline, X, y, feature_info)
    
    # Show examples
    show_prediction_examples(X, y, y_pred, feature_info)
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)
    print("\nSummary:")
    print(f"  • Model evaluated on {len(X)} samples")
    print(f"  • MAE: {mae:.2f} kcal/day")
    print(f"  • R²: {r2:.4f}")
    
    if r2 < 0.5:
        print("\n⚠ Consider:")
        print("  - Collecting more diverse training data")
        print("  - Adding more features (breed, activity level, health conditions)")
        print("  - Trying different model architectures")
        print("  - Feature engineering (e.g., weight * activity level)")
    else:
        print("\n✓ Model performance is reasonable for baseline")
    
    print("\nNext steps:")
    print("  1. If satisfied, integrate into ai_core/proprietary_backend.py")
    print("  2. Otherwise, retrain with more data or different features")
    print("  3. Compare cost: OpenAI API vs. self-hosted inference")
    print()


if __name__ == "__main__":
    main()
