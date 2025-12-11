#!/usr/bin/env python
"""Test script to verify ProfileSerializer returns user type info for different users"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
django.setup()

from userapp.models import Profile
from userapp.serializers import ProfileSerializer

# Get all profiles
profiles = Profile.objects.all()
print(f"Testing {profiles.count()} profiles:\n")

for i, profile in enumerate(profiles[:3], 1):
    serializer = ProfileSerializer(profile)
    print(f"Profile {i}: {profile.user.email}")
    print(f"  is_clinic_owner: {serializer.data.get('is_clinic_owner')}")
    print(f"  owned_clinics: {serializer.data.get('owned_clinics')}")
    print()
