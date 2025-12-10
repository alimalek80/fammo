#!/usr/bin/env python
"""Debug script to test if address changes trigger geocoding."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
sys.path.insert(0, '/d/fammo')
django.setup()

from vets.models import Clinic
import logging

# Enable all logging to see debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("Testing Address Change Detection and Geocoding")
print("="*60)

# Get a test clinic
clinic = Clinic.objects.filter(name='beges15249').first()

if not clinic:
    print("❌ Clinic 'beges15249' not found!")
    sys.exit(1)

print(f"\n=== Initial State ===")
print(f"Name: {clinic.name}")
print(f"Address: {clinic.address}")
print(f"City: {clinic.city}")
print(f"Latitude: {clinic.latitude}")
print(f"Longitude: {clinic.longitude}")

# Test 1: Change address via direct save
print(f"\n=== Test 1: Direct save() with address change ===")
old_address = clinic.address
clinic.address = "Test Address 1, Test City"
print(f"Changed address from: {old_address}")
print(f"Changed address to: {clinic.address}")
print("Calling clinic.save()...")
clinic.save()

# Refresh from database
clinic.refresh_from_db()
print(f"\nAfter save():")
print(f"Address: {clinic.address}")
print(f"Latitude: {clinic.latitude}")
print(f"Longitude: {clinic.longitude}")

if clinic.latitude and clinic.longitude:
    print("✅ Coordinates updated!")
else:
    print("❌ Coordinates NOT updated - still None")

# Test 2: Change address again
print(f"\n=== Test 2: Another address change ===")
clinic.address = "Another Test Street, Another City"
print(f"Changed address to: {clinic.address}")
print("Calling clinic.save()...")
clinic.save()

clinic.refresh_from_db()
print(f"\nAfter save():")
print(f"Address: {clinic.address}")
print(f"Latitude: {clinic.latitude}")
print(f"Longitude: {clinic.longitude}")

if clinic.latitude and clinic.longitude:
    print("✅ Coordinates updated!")
else:
    print("❌ Coordinates NOT updated - still None")

# Test 3: Force geocoding with print statements
print(f"\n=== Test 3: Direct geocoding function test ===")
from vets.utils import geocode_address

test_address = "Taksim Square, Istanbul"
test_city = "Istanbul"
print(f"Testing geocode_address('{test_address}', '{test_city}')")
coords = geocode_address(test_address, test_city)
if coords:
    print(f"✅ Geocoding works! Got: {coords}")
else:
    print(f"❌ Geocoding failed - returned None")

print("\n" + "="*60)
