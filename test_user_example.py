#!/usr/bin/env python
"""Test with the exact addresses from the user's example."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
sys.path.insert(0, '/d/fammo')
django.setup()

from vets.models import Clinic
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*80)
print("TEST: Address Change Detection - Using Exact User Example")
print("="*80)

# Get test clinic
clinic = Clinic.objects.filter(name='beges15249').first()

if not clinic:
    print("Creating test clinic...")
    clinic = Clinic.objects.create(
        name='beges15249',
        address='Hamidiye, Sena Sk. No:5, 34408 Kağıthane/İstanbul',
        city='Istanbul'
    )
else:
    # Reset to original address
    clinic.address = 'Hamidiye, Sena Sk. No:5, 34408 Kağıthane/İstanbul'
    clinic.city = 'Istanbul'
    clinic.save()

print(f"\n📍 ORIGINAL STATE:")
print(f"   Address: {clinic.address}")
print(f"   City: {clinic.city}")
print(f"   Latitude: {clinic.latitude}")
print(f"   Longitude: {clinic.longitude}")

# Now change to the new address
print(f"\n✏️  CHANGING ADDRESS TO NEW ADDRESS:")
old_addr = clinic.address
clinic.address = '62, Merkez, Kemerburgaz Cd. No:25, 34403 Kağıthane/İstanbul'
clinic.city = 'Istanbul'

print(f"   Old: {old_addr}")
print(f"   New: {clinic.address}")

print(f"\n⏳ SAVING WITH NEW ADDRESS...")
clinic.save()

# Refresh from database
clinic.refresh_from_db()

print(f"\n✅ AFTER SAVE:")
print(f"   Address: {clinic.address}")
print(f"   City: {clinic.city}")
print(f"   Latitude: {clinic.latitude}")
print(f"   Longitude: {clinic.longitude}")

if clinic.latitude and clinic.longitude:
    print(f"\n✅ SUCCESS: Coordinates CHANGED!")
    print(f"   Was: 41.006381, 28.975872")
    print(f"   Now: {clinic.latitude}, {clinic.longitude}")
else:
    print(f"\n❌ FAILED: Coordinates are still None!")

print("\n" + "="*80)
