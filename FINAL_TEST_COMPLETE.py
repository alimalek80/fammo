#!/usr/bin/env python
"""
Complete test simulating exact Django admin behavior for clinic address changes.
This will show you exactly what should happen when you edit a clinic in admin.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
sys.path.insert(0, '/d/fammo')
django.setup()

from vets.models import Clinic
import logging

# Setup logging to show all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("\n" + "="*80)
print("COMPLETE DJANGO ADMIN ADDRESS CHANGE TEST")
print("="*80)

# Get all clinics with coordinates
clinics = Clinic.objects.filter(latitude__isnull=False).order_by('-updated_at')[:3]

if not clinics:
    print("❌ No clinics with coordinates found!")
    sys.exit(1)

print(f"\nFound {clinics.count()} clinics to test:\n")

for clinic in clinics:
    print(f"\n{'='*80}")
    print(f"Testing Clinic: {clinic.name}")
    print(f"{'='*80}")
    
    print(f"\n📍 BEFORE:")
    print(f"   Address: {clinic.address}")
    print(f"   City: {clinic.city}")
    print(f"   Latitude: {clinic.latitude}")
    print(f"   Longitude: {clinic.longitude}")
    
    # Simulate admin form: reload clinic and change address
    clinic = Clinic.objects.get(pk=clinic.pk)  # Fresh instance like Django form
    
    # Change to a real address
    new_address = "Kizilay Street, Ankara"
    clinic.address = new_address
    
    print(f"\n✏️  CHANGING ADDRESS:")
    print(f"   New Address: {clinic.address}")
    print(f"   City: {clinic.city}")
    
    print(f"\n⏳ SAVING (calling clinic.save())...")
    clinic.save()
    
    # Refresh from database
    clinic.refresh_from_db()
    
    print(f"\n✅ AFTER SAVE:")
    print(f"   Address: {clinic.address}")
    print(f"   City: {clinic.city}")
    print(f"   Latitude: {clinic.latitude}")
    print(f"   Longitude: {clinic.longitude}")
    
    if clinic.latitude and clinic.longitude:
        print(f"\n   ✅ SUCCESS: Coordinates were AUTO-UPDATED!")
    else:
        print(f"\n   ❌ FAILURE: Coordinates were NOT updated!")

print(f"\n{'='*80}")
print("TEST COMPLETE")
print("="*80)
print("\nSUMMARY: If all clinics show updated coordinates, the system is working.")
print("If coordinates are NOT updated, check Django logs for [CLINIC SAVE] messages.")
