#!/usr/bin/env python
"""Test clinic address update from user profile perspective (API level)."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
sys.path.insert(0, '/d/fammo')
django.setup()

from vets.models import Clinic
from vets.serializers import ClinicUpdateSerializer
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*80)
print("TEST: Clinic Update via API/Serializer")
print("="*80)

clinic = Clinic.objects.filter(name='beges15249').first()

if not clinic:
    print("❌ Clinic not found")
    sys.exit(1)

print(f"\n📍 BEFORE UPDATE:")
print(f"   Address: {clinic.address}")
print(f"   City: {clinic.city}")
print(f"   Latitude: {clinic.latitude}")
print(f"   Longitude: {clinic.longitude}")

# Simulate API update with serializer
data = {
    'address': 'Taksim Square, Istanbul',
    'city': 'Istanbul',
}

print(f"\n✏️  UPDATING via Serializer:")
print(f"   New Address: {data['address']}")
print(f"   New City: {data['city']}")

serializer = ClinicUpdateSerializer(clinic, data=data, partial=True)

if serializer.is_valid():
    print(f"\n⏳ SAVING WITH SERIALIZER...")
    serializer.save()
    
    # Refresh from database
    clinic.refresh_from_db()
    
    print(f"\n✅ AFTER SERIALIZER SAVE:")
    print(f"   Address: {clinic.address}")
    print(f"   City: {clinic.city}")
    print(f"   Latitude: {clinic.latitude}")
    print(f"   Longitude: {clinic.longitude}")
    
    if clinic.latitude and clinic.longitude:
        print(f"\n✅ SUCCESS: Coordinates AUTO-UPDATED via API!")
    else:
        print(f"\n❌ Coordinates are None")
else:
    print(f"❌ Serializer validation failed: {serializer.errors}")

print("\n" + "="*80)
