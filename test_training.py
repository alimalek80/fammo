#!/usr/bin/env python
"""Quick test of training script components"""

import pandas as pd
from pathlib import Path

print("Testing training script components...")

# Test 1: Load data
input_path = Path('ml/data/nutrition_logs.jsonl')
print(f"\n1. Checking input file: {input_path}")
print(f"   Exists: {input_path.exists()}")

if input_path.exists():
    # Load data
    df = pd.read_json(input_path, lines=True)
    print(f"   Loaded {len(df)} records")
    
    # Test 2: Extract calories
    print("\n2. Extracting calories_per_day...")
    df['calories_per_day'] = df['output'].apply(
        lambda o: o.get('calories_per_day') if isinstance(o, dict) else None
    )
    df = df.dropna(subset=['calories_per_day'])
    print(f"   {len(df)} records with valid calories")
    
    # Test 3: Check features
    print("\n3. Checking features...")
    print(f"   Top-level columns: {list(df.columns)}")
    print(f"   Sample output keys: {list(df['output'].iloc[0].keys()) if len(df) > 0 else 'N/A'}")
    print(f"   Sample input keys: {list(df['input'].iloc[0].keys()) if len(df) > 0 else 'N/A'}")
    
    # Test 4: Extract features
    print("\n4. Testing feature extraction...")
    features = pd.DataFrame()
    features['weight_kg'] = df['weight_kg']
    features['age_years'] = df['age_years']  
    features['body_condition_score'] = df['body_condition_score']
    features['species'] = df['species']
    features['life_stage'] = df['life_stage']
    features['breed_size_category'] = df['breed_size_category']
    features['health_goal'] = df['health_goal']
    
    print(f"   Feature shape: {features.shape}")
    print(f"   Missing values:\n{features.isnull().sum()}")
    
    print("\n✓ All components working!")
else:
    print("   ERROR: File not found!")
