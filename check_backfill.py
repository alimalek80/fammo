#!/usr/bin/env python
"""Quick script to check backfilled nutrition logs."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
django.setup()

from ai_core.models import NutritionPredictionLog

# Query backfilled records
backfilled = NutritionPredictionLog.objects.filter(
    source='aihub',
    model_version='aihub_mealplan_v1'
)

print(f"\n{'='*60}")
print(f"Backfilled Nutrition Logs Summary")
print(f"{'='*60}")
print(f"Total backfilled records: {backfilled.count()}")

if backfilled.exists():
    first = backfilled.first()
    print(f"\nFirst record details:")
    print(f"  ID: {first.id}")
    print(f"  Species: {first.species}")
    print(f"  Life stage: {first.life_stage}")
    print(f"  Health goal: {first.health_goal}")
    print(f"  Weight: {first.weight_kg} kg")
    print(f"  Age: {first.age_years} years")
    print(f"  Body condition score: {first.body_condition_score}")
    print(f"  Calories per day: {first.output_payload.get('calories_per_day')}")
    print(f"  Protein %: {first.output_payload.get('protein_percent')}")
    print(f"  Fat %: {first.output_payload.get('fat_percent')}")
    print(f"  Carbs %: {first.output_payload.get('carbohydrate_percent')}")
    print(f"  Diet style: {first.output_payload.get('diet_style')}")
    print(f"  Notes: {first.notes}")
    
    # Show distribution by species
    print(f"\nDistribution by species:")
    for species in backfilled.values_list('species', flat=True).distinct():
        count = backfilled.filter(species=species).count()
        print(f"  {species}: {count} records")
    
    # Show distribution by health goal
    print(f"\nDistribution by health goal:")
    for goal in backfilled.values_list('health_goal', flat=True).distinct():
        count = backfilled.filter(health_goal=goal).count()
        print(f"  {goal}: {count} records")
else:
    print("\n⚠ No backfilled records found")

print(f"\n{'='*60}\n")
