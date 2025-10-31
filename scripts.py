"""
Sample User Creation Script for FAMMO
Run this script to add 7 sample users with Netherlands-based information.

Usage:
    python manage.py shell < scripts.py
    # OR
    python manage.py shell
    >>> exec(open('scripts.py').read())
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
django.setup()

from userapp.models import CustomUser, Profile
from django.utils import timezone

def create_sample_users():
    """Create 7 sample users with full Netherlands-based profiles"""
    
    users_data = [
        {
            'email': 'pieter.devries@example.nl',
            'password': 'TestPass123!',
            'first_name': 'Pieter',
            'last_name': 'de Vries',
            'phone': '+31 20 123 4567',
            'address': 'Prinsengracht 263',
            'city': 'Amsterdam',
            'zip_code': '1016 GV',
            'country': 'Netherlands',
        },
        {
            'email': 'anna.jansen@example.nl',
            'password': 'TestPass123!',
            'first_name': 'Anna',
            'last_name': 'Jansen',
            'phone': '+31 10 234 5678',
            'address': 'Witte de Withstraat 45',
            'city': 'Rotterdam',
            'zip_code': '3012 BM',
            'country': 'Netherlands',
        },
        {
            'email': 'hendrik.bakker@example.nl',
            'password': 'TestPass123!',
            'first_name': 'Hendrik',
            'last_name': 'Bakker',
            'phone': '+31 30 345 6789',
            'address': 'Oudegracht 234',
            'city': 'Utrecht',
            'zip_code': '3511 NR',
            'country': 'Netherlands',
        },
        {
            'email': 'sophie.vandenberg@example.nl',
            'password': 'TestPass123!',
            'first_name': 'Sophie',
            'last_name': 'van den Berg',
            'phone': '+31 70 456 7890',
            'address': 'Lange Voorhout 74',
            'city': 'The Hague',
            'zip_code': '2514 EH',
            'country': 'Netherlands',
        },
        {
            'email': 'lars.mulder@example.nl',
            'password': 'TestPass123!',
            'first_name': 'Lars',
            'last_name': 'Mulder',
            'phone': '+31 40 567 8901',
            'address': 'Stratumseind 12',
            'city': 'Eindhoven',
            'zip_code': '5611 NA',
            'country': 'Netherlands',
        },
        {
            'email': 'emma.visser@example.nl',
            'password': 'TestPass123!',
            'first_name': 'Emma',
            'last_name': 'Visser',
            'phone': '+31 50 678 9012',
            'address': 'Herestraat 89',
            'city': 'Groningen',
            'zip_code': '9711 LM',
            'country': 'Netherlands',
        },
        {
            'email': 'daan.dekker@example.nl',
            'password': 'TestPass123!',
            'first_name': 'Daan',
            'last_name': 'Dekker',
            'phone': '+31 24 789 0123',
            'address': 'Grote Markt 33',
            'city': 'Nijmegen',
            'zip_code': '6511 KB',
            'country': 'Netherlands',
        },
    ]
    
    created_count = 0
    skipped_count = 0
    
    for user_data in users_data:
        email = user_data['email']
        
        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            print(f"[X] User {email} already exists. Skipping...")
            skipped_count += 1
            continue
        
        try:
            # Create the user
            user = CustomUser.objects.create_user(
                email=email,
                password=user_data['password']
            )
            user.is_active = True
            user.save()
            
            # Create the profile
            profile = Profile.objects.create(
                user=user,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                address=user_data['address'],
                city=user_data['city'],
                zip_code=user_data['zip_code'],
                country=user_data['country'],
            )
            
            print(f"[OK] Created user: {user_data['first_name']} {user_data['last_name']} ({email})")
            created_count += 1
            
        except Exception as e:
            print(f"[ERROR] Error creating user {email}: {str(e)}")
            skipped_count += 1
    
    print("\n" + "="*60)
    print(f"[OK] Successfully created: {created_count} users")
    print(f"[WARN] Skipped: {skipped_count} users")
    print("="*60)
    print("\n[INFO] Login credentials for all users:")
    print("   Password: TestPass123!")
    print("   Emails: Check the list above")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("[START] Creating sample users for FAMMO...")
    print("="*60 + "\n")
    create_sample_users()
