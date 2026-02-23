#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/home/alex/projects/fammo-backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')

# Setup Django
django.setup()

from pet.models import PetType, AgeCategory

print("=== EXISTING AGE CATEGORIES ===")
for pet_type in PetType.objects.all():
    print(f"\n{pet_type.name.upper()}:")
    age_categories = AgeCategory.objects.filter(pet_type=pet_type).order_by('order')
    for i, category in enumerate(age_categories, 1):
        print(f"  {i}. {category.name} (ID: {category.id}, Order: {category.order})")