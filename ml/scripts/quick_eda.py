#!/usr/bin/env python
"""
Quick EDA script for FAMMO Nutrition Logs (Simplified version)

This is a lightweight version that focuses on essential analysis
without complex plotting that may cause issues.

Usage:
    python ml/scripts/quick_eda.py
"""

import json
import sys
from pathlib import Path
from collections import Counter

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas")
    sys.exit(1)


def load_jsonl(file_path):
    """Load JSONL file into pandas DataFrame."""
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return pd.DataFrame(records)


def extract_output_fields(df):
    """Extract nested fields from output payload."""
    if 'output' in df.columns:
        df['calories_per_day'] = df['output'].apply(
            lambda x: x.get('calories_per_day') if isinstance(x, dict) else None
        )
        df['protein_percent'] = df['output'].apply(
            lambda x: x.get('protein_percent') if isinstance(x, dict) else None
        )
        df['fat_percent'] = df['output'].apply(
            lambda x: x.get('fat_percent') if isinstance(x, dict) else None
        )
        df['carbohydrate_percent'] = df['output'].apply(
            lambda x: x.get('carbohydrate_percent') if isinstance(x, dict) else None
        )
        df['diet_style'] = df['output'].apply(
            lambda x: x.get('diet_style') if isinstance(x, dict) else None
        )
    return df


def main():
    """Main execution function."""
    # Input path
    input_path = Path('ml/data/nutrition_logs.jsonl')
    
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        print("\nExport data first with:")
        print("  python manage.py export_nutrition_logs --output=ml/data/nutrition_logs.jsonl")
        sys.exit(1)
    
    # Load data
    print(f"\n{'='*80}")
    print("FAMMO NUTRITION LOGS - QUICK EDA")
    print(f"{'='*80}")
    print(f"\nLoading: {input_path}")
    
    df = load_jsonl(input_path)
    df = extract_output_fields(df)
    
    print(f"Total records: {len(df)}")
    
    # Summary by categorical fields
    categorical_fields = [
        'source', 'backend', 'model_version', 'species', 
        'life_stage', 'health_goal', 'diet_style'
    ]
    
    for field in categorical_fields:
        if field in df.columns:
            print(f"\n--- {field.replace('_', ' ').title()} ---")
            counts = df[field].value_counts()
            for value, count in counts.items():
                print(f"  {value}: {count}")
    
    # Numeric statistics
    numeric_fields = [
        'weight_kg', 'age_years', 'body_condition_score',
        'calories_per_day', 'protein_percent', 'fat_percent', 
        'carbohydrate_percent'
    ]
    
    print(f"\n{'='*80}")
    print("NUMERIC STATISTICS")
    print(f"{'='*80}")
    
    for field in numeric_fields:
        if field in df.columns:
            series = df[field].dropna()
            if len(series) > 0:
                print(f"\n{field.replace('_', ' ').title()}:")
                print(f"  Count: {len(series)}")
                print(f"  Mean:  {series.mean():.2f}")
                print(f"  Std:   {series.std():.2f}")
                print(f"  Min:   {series.min():.2f}")
                print(f"  Max:   {series.max():.2f}")
    
    # Export summary to CSV
    summary_path = input_path.parent / 'eda_summary.csv'
    df_summary = df[[c for c in df.columns if c not in ['input', 'output']]]
    df_summary.to_csv(summary_path, index=False)
    print(f"\n{'='*80}")
    print(f"Summary exported to: {summary_path}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
