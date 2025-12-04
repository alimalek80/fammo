#!/usr/bin/env python
"""
Exploratory Data Analysis (EDA) for FAMMO Nutrition Prediction Logs

This script loads exported nutrition logs from JSONL format and performs
basic statistical analysis and visualization.

Usage:
    python ml/scripts/eda_nutrition_logs.py
    python ml/scripts/eda_nutrition_logs.py --input=ml/data/dog_logs.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend


def load_jsonl(file_path):
    """
    Load JSONL file into a pandas DataFrame.
    
    Args:
        file_path: Path to JSONL file
        
    Returns:
        pandas DataFrame
    """
    records = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    return pd.DataFrame(records)


def extract_output_fields(df):
    """
    Extract nested fields from output payload into top-level columns.
    
    Args:
        df: DataFrame with 'output' column containing dicts
        
    Returns:
        DataFrame with extracted fields
    """
    # Extract commonly used fields from output payload
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


def print_summary_statistics(df):
    """
    Print summary statistics for the dataset.
    
    Args:
        df: pandas DataFrame
    """
    print("\n" + "=" * 80)
    print("NUTRITION LOGS - EXPLORATORY DATA ANALYSIS")
    print("=" * 80)
    
    print(f"\nTotal Records: {len(df)}")
    
    # Distribution by source
    if 'source' in df.columns:
        print("\n--- Distribution by Source ---")
        print(df['source'].value_counts())
    
    # Distribution by species
    if 'species' in df.columns:
        print("\n--- Distribution by Species ---")
        print(df['species'].value_counts())
    
    # Distribution by backend
    if 'backend' in df.columns:
        print("\n--- Distribution by Backend ---")
        print(df['backend'].value_counts())
    
    # Distribution by model version
    if 'model_version' in df.columns:
        print("\n--- Distribution by Model Version ---")
        print(df['model_version'].value_counts())
    
    # Distribution by life stage
    if 'life_stage' in df.columns:
        print("\n--- Distribution by Life Stage ---")
        print(df['life_stage'].value_counts())
    
    # Distribution by health goal
    if 'health_goal' in df.columns:
        print("\n--- Distribution by Health Goal ---")
        print(df['health_goal'].value_counts())
    
    # Distribution by diet style
    if 'diet_style' in df.columns:
        print("\n--- Distribution by Diet Style ---")
        print(df['diet_style'].value_counts())
    
    # Numeric statistics
    numeric_cols = ['weight_kg', 'age_years', 'body_condition_score', 
                    'calories_per_day', 'protein_percent', 'fat_percent', 
                    'carbohydrate_percent']
    
    available_numeric = [col for col in numeric_cols if col in df.columns]
    
    if available_numeric:
        print("\n--- Numeric Field Statistics ---")
        print(df[available_numeric].describe())
    
    # Check for missing values
    print("\n--- Missing Values ---")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        print(missing)
    else:
        print("No missing values in main columns")
    
    print("\n" + "=" * 80)


def plot_weight_distribution(df, output_dir):
    """
    Create histogram of weight distribution by species.
    
    Args:
        df: pandas DataFrame
        output_dir: Directory to save plot
    """
    if 'weight_kg' not in df.columns or 'species' not in df.columns:
        print("Skipping weight distribution plot - missing required columns")
        return
    
    # Filter out null weights
    df_filtered = df[df['weight_kg'].notna()]
    
    if len(df_filtered) == 0:
        print("No weight data available for plotting")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get unique species
    species_list = df_filtered['species'].unique()
    
    # Create histogram for each species
    for species in species_list:
        species_data = df_filtered[df_filtered['species'] == species]['weight_kg']
        ax.hist(species_data, alpha=0.6, label=species, bins=20)
    
    ax.set_xlabel('Weight (kg)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Weight Distribution by Species', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Save plot
    output_path = output_dir / 'weight_distribution_by_species.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {output_path}")
    plt.close()


def plot_calories_distribution(df, output_dir):
    """
    Create histogram of calorie distribution.
    
    Args:
        df: pandas DataFrame
        output_dir: Directory to save plot
    """
    if 'calories_per_day' not in df.columns:
        print("Skipping calories distribution plot - missing required column")
        return
    
    # Filter out null calories
    df_filtered = df[df['calories_per_day'].notna()]
    
    if len(df_filtered) == 0:
        print("No calorie data available for plotting")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create histogram
    ax.hist(df_filtered['calories_per_day'], bins=30, color='skyblue', 
            edgecolor='black', alpha=0.7)
    
    ax.set_xlabel('Calories per Day', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Daily Calorie Distribution', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add mean line
    mean_calories = df_filtered['calories_per_day'].mean()
    ax.axvline(mean_calories, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_calories:.0f} kcal')
    ax.legend()
    
    # Save plot
    output_path = output_dir / 'calories_distribution.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_macronutrient_distribution(df, output_dir):
    """
    Create box plot of macronutrient percentages by species.
    
    Args:
        df: pandas DataFrame
        output_dir: Directory to save plot
    """
    macro_cols = ['protein_percent', 'fat_percent', 'carbohydrate_percent']
    
    # Check if all macro columns exist
    if not all(col in df.columns for col in macro_cols):
        print("Skipping macronutrient plot - missing required columns")
        return
    
    # Filter to rows with all macro data
    df_filtered = df[df[macro_cols].notna().all(axis=1)]
    
    if len(df_filtered) == 0:
        print("No macronutrient data available for plotting")
        return
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, (col, ax) in enumerate(zip(macro_cols, axes)):
        if 'species' in df.columns:
            species_list = df_filtered['species'].unique()
            data_by_species = [df_filtered[df_filtered['species'] == s][col].dropna() 
                               for s in species_list]
            ax.boxplot(data_by_species, labels=species_list)
        else:
            ax.boxplot(df_filtered[col].dropna())
        
        # Format title
        title = col.replace('_', ' ').title()
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel('Percentage (%)', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Macronutrient Distribution by Species', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save plot
    output_path = output_dir / 'macronutrient_distribution.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def plot_age_vs_weight(df, output_dir):
    """
    Create scatter plot of age vs weight by species.
    
    Args:
        df: pandas DataFrame
        output_dir: Directory to save plot
    """
    if 'age_years' not in df.columns or 'weight_kg' not in df.columns:
        print("Skipping age vs weight plot - missing required columns")
        return
    
    # Filter out null values
    df_filtered = df[df[['age_years', 'weight_kg']].notna().all(axis=1)]
    
    if len(df_filtered) == 0:
        print("No age/weight data available for plotting")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get unique species
    if 'species' in df.columns:
        species_list = df_filtered['species'].unique()
        
        for species in species_list:
            species_data = df_filtered[df_filtered['species'] == species]
            ax.scatter(species_data['age_years'], species_data['weight_kg'], 
                      alpha=0.6, label=species, s=50)
    else:
        ax.scatter(df_filtered['age_years'], df_filtered['weight_kg'], 
                  alpha=0.6, s=50)
    
    ax.set_xlabel('Age (years)', fontsize=12)
    ax.set_ylabel('Weight (kg)', fontsize=12)
    ax.set_title('Age vs Weight by Species', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Save plot
    output_path = output_dir / 'age_vs_weight.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Exploratory Data Analysis for FAMMO Nutrition Logs'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='ml/data/nutrition_logs.jsonl',
        help='Path to input JSONL file (default: ml/data/nutrition_logs.jsonl)'
    )
    
    args = parser.parse_args()
    
    # Resolve input path
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("\nTo export data from Django, run:")
        print("  python manage.py export_nutrition_logs --output=ml/data/nutrition_logs.jsonl")
        sys.exit(1)
    
    # Load data
    print(f"\nLoading data from: {input_path}")
    df = load_jsonl(input_path)
    
    # Extract output fields
    df = extract_output_fields(df)
    
    # Print summary statistics
    print_summary_statistics(df)
    
    # Create visualizations
    output_dir = input_path.parent
    
    print("\n" + "=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    
    plot_weight_distribution(df, output_dir)
    plot_calories_distribution(df, output_dir)
    plot_macronutrient_distribution(df, output_dir)
    plot_age_vs_weight(df, output_dir)
    
    print("\n" + "=" * 80)
    print("EDA COMPLETE")
    print("=" * 80)
    print(f"\nAll plots saved to: {output_dir}")
    print("\n")


if __name__ == "__main__":
    main()
