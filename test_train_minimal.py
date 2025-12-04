#!/usr/bin/env python
"""Minimal training test"""

import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

print("="*80)
print("MINIMAL TRAINING TEST")
print("="*80)

# Load data
input_path = Path('ml/data/nutrition_logs.jsonl')
print(f"\nLoading: {input_path}")
df = pd.read_json(input_path, lines=True)
print(f"Loaded {len(df)} records")

# Extract target
df['calories_per_day'] = df['output'].apply(lambda o: o.get('calories_per_day'))
print(f"Valid calories: {df['calories_per_day'].notna().sum()}")

# Prepare features  
X = df[['weight_kg', 'age_years', 'body_condition_score']].copy()
y = df['calories_per_day']

print(f"\nX shape: {X.shape}")
print(f"y shape: {y.shape}")

# Train simple model (no pipeline, just RF on numeric features)
print("\nTraining RandomForest...")
model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42, n_jobs=1)
model.fit(X, y)
print("✓ Training complete!")

# Predict
y_pred = model.predict(X)
mae = abs(y - y_pred).mean()
print(f"\nMAE: {mae:.2f} kcal/day")

# Save
output_path = Path('ml/models/test_model.pkl')
output_path.parent.mkdir(exist_ok=True)
joblib.dump(model, output_path)
print(f"\n✓ Saved to: {output_path}")

print("\nDONE!")
