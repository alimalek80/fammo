#!/usr/bin/env python
"""Test script to verify ProfileSerializer returns user type info"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
django.setup()

from userapp.models import Profile
from userapp.serializers import ProfileSerializer
import json

# Get first profile
profile = Profile.objects.first()
if profile:
    serializer = ProfileSerializer(profile)
    print("Sample API Response for GET /api/me/:")
    print(json.dumps(serializer.data, indent=2, default=str))
    print("\n✅ Key fields for Flutter routing:")
    print(f"  - is_clinic_owner: {serializer.data.get('is_clinic_owner')}")
    print(f"  - owned_clinics: {serializer.data.get('owned_clinics')}")
else:
    print("No profiles found in database")
