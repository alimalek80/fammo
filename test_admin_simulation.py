#!/usr/bin/env python
"""Simulate Django admin form submission to test real-world admin scenario."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
sys.path.insert(0, '/d/fammo')
django.setup()

from vets.models import Clinic
import logging

logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

print("\n" + "="*70)
print("Simulating Django Admin Form Submission")
print("="*70)

# Get the clinic
clinic = Clinic.objects.get(name='beges15249')

print(f"\n=== Before Admin Edit ===")
print(f"Address: {clinic.address}")
print(f"City: {clinic.city}")
print(f"Latitude: {clinic.latitude}")
print(f"Longitude: {clinic.longitude}")

# Simulate admin form submission - create a NEW instance with same pk but changed data
# This is what Django does internally
print(f"\n=== Simulating Admin Form Submission ===")
print("Creating new instance from form data (like Django admin does)...")

# This simulates what happens when admin form is submitted
clinic_from_form = Clinic.objects.get(pk=clinic.pk)
print(f"Initial from_form address: {clinic_from_form.address}")

clinic_from_form.address = "REAL CHANGED ADDRESS FROM ADMIN"
print(f"Changed from_form address to: {clinic_from_form.address}")

print("\nCalling clinic_from_form.save()...")
clinic_from_form.save()

# Refresh and check
clinic_from_form.refresh_from_db()
print(f"\n=== After save_model() call ===")
print(f"Address: {clinic_from_form.address}")
print(f"Latitude: {clinic_from_form.latitude}")
print(f"Longitude: {clinic_from_form.longitude}")

if clinic_from_form.latitude and clinic_from_form.longitude:
    print("✅ Coordinates were updated by admin save!")
else:
    print("❌ Coordinates were NOT updated - still None or original value")

print("\n" + "="*70)
