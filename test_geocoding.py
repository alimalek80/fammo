#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
django.setup()

from vets.models import Clinic
import logging

# Set up logging to see our debug output
logging.basicConfig(level=logging.INFO)

# Get a clinic to test
clinic = Clinic.objects.first()

if clinic:
    print(f"\n=== Testing Clinic: {clinic.name} ===")
    print(f"Current Address: {clinic.address}")
    print(f"Current City: {clinic.city}")
    print(f"Current Latitude: {clinic.latitude}")
    print(f"Current Longitude: {clinic.longitude}")
    
    # Change the address
    old_address = clinic.address
    clinic.address = "123 New Test Street, Test City"
    
    print(f"\n--- Changing address ---")
    print(f"Old: {old_address}")
    print(f"New: {clinic.address}")
    
    # Save (this should trigger geocoding)
    clinic.save()
    
    print(f"\n--- After Save ---")
    print(f"Address: {clinic.address}")
    print(f"Latitude: {clinic.latitude}")
    print(f"Longitude: {clinic.longitude}")
else:
    print("No clinics found in database")
