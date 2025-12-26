from django.core.management.base import BaseCommand
from userapp.models import CustomUser, Profile
from pet.models import Pet, PetType, Gender, Breed, AgeCategory, BodyType, ActivityLevel, FoodType, FoodFeeling, FoodImportance, TreatFrequency
from aihub.models import AIRecommendation, AIHealthReport
from decimal import Decimal
from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone
import csv
import os
import random


class Command(BaseCommand):
    help = 'Create sample users with profiles and pet profiles from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='userapp/fammo_users_realistic_batch1_150.csv',
            help='Path to CSV file (relative to project root)'
        )
        parser.add_argument(
            '--generate-ai',
            action='store_true',
            help='Generate random AI meal and health reports for users'
        )
        parser.add_argument(
            '--max-meals',
            type=int,
            default=3,
            help='Maximum meal recommendations per pet (default: 3)'
        )
        parser.add_argument(
            '--max-health',
            type=int,
            default=1,
            help='Maximum health reports per pet (default: 1)'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        generate_ai = options['generate_ai']
        max_meals = options['max_meals']
        max_health = options['max_health']
        
        # Make path absolute if it's relative
        if not os.path.isabs(csv_path):
            from django.conf import settings
            csv_path = os.path.join(settings.BASE_DIR, csv_path)
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return
        
        created_count = 0
        skipped_count = 0
        pets_created = 0
        total_ai_meals = 0
        total_ai_health = 0
        users_with_ai = 0
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f'[START] Importing users from CSV: {csv_path}'))
        self.stdout.write("="*60 + "\n")
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    email = row['email']
                    
                    # Check if user already exists
                    if CustomUser.objects.filter(email=email).exists():
                        self.stdout.write(self.style.WARNING(f"[SKIP] User {email} already exists. Skipping..."))
                        skipped_count += 1
                        continue
                    
                    try:
                        with transaction.atomic():
                            # Parse date_joined
                            date_joined_str = row['date_joined']
                            date_joined = datetime.fromisoformat(date_joined_str.replace('Z', '+00:00'))
                            if timezone.is_naive(date_joined):
                                date_joined = timezone.make_aware(date_joined)
                            
                            # Create the user
                            user = CustomUser.objects.create_user(
                                email=email,
                                password=row['password'],
                                date_joined=date_joined,
                                is_active=True
                            )
                            
                            # Update the profile (created automatically by signal)
                            profile = user.profile
                            profile.first_name = row['first_name']
                            profile.last_name = row['last_name']
                            profile.phone = row['phone']
                            profile.address = row['address']
                            profile.city = row['city']
                            profile.zip_code = row['zip_code']
                            profile.country = row['country']
                            profile.save()
                            
                            self.stdout.write(self.style.SUCCESS(
                                f"[OK] Created user: {row['first_name']} {row['last_name']} ({email})"
                            ))
                            created_count += 1
                            
                            # Create pet profile if pet data exists
                            if row.get('pet_name') and row['pet_name'].strip():
                                try:
                                    # Get or create related objects
                                    pet_type, _ = PetType.objects.get_or_create(name=row['pet_type'])
                                    gender, _ = Gender.objects.get_or_create(name=row['pet_gender'])
                                    breed, _ = Breed.objects.get_or_create(
                                        name=row['pet_breed'],
                                        pet_type=pet_type
                                    )
                                    body_type, _ = BodyType.objects.get_or_create(
                                        name=row['pet_body_type'],
                                        defaults={'description': f'{row["pet_body_type"]} body type'}
                                    )
                                    activity_level, _ = ActivityLevel.objects.get_or_create(
                                        name=row['pet_activity_level'],
                                        defaults={'description': f'{row["pet_activity_level"]} activity level'}
                                    )
                                    food_feeling, _ = FoodFeeling.objects.get_or_create(
                                        name=row['pet_food_feeling'],
                                        defaults={'description': row['pet_food_feeling']}
                                    )
                                    food_importance, _ = FoodImportance.objects.get_or_create(
                                        name=row['pet_food_importance']
                                    )
                                    
                                    # Get age category if provided
                                    age_category = None
                                    if row.get('pet_age_category'):
                                        age_category, _ = AgeCategory.objects.get_or_create(
                                            name=row['pet_age_category'],
                                            pet_type=pet_type,
                                            defaults={'order': 0}
                                        )
                                    
                                    # Get treat frequency if provided
                                    treat_frequency = None
                                    if row.get('pet_treat_frequency'):
                                        treat_frequency, _ = TreatFrequency.objects.get_or_create(
                                            name=row['pet_treat_frequency'],
                                            defaults={'description': ''}
                                        )
                                    
                                    # Create the pet
                                    pet = Pet.objects.create(
                                        user=user,
                                        name=row['pet_name'],
                                        pet_type=pet_type,
                                        gender=gender,
                                        breed=breed,
                                        neutered=row['pet_neutered'].lower() in ['true', '1', 'yes'],
                                        age_category=age_category,
                                        age_years=int(float(row['pet_age_years'])) if row['pet_age_years'] else 0,
                                        age_months=int(float(row['pet_age_months'])) if row['pet_age_months'] else 0,
                                        age_weeks=int(float(row.get('pet_age_weeks', 0))) if row.get('pet_age_weeks') else 0,
                                        weight=Decimal(row['pet_weight']),
                                        body_type=body_type,
                                        activity_level=activity_level,
                                        food_feeling=food_feeling,
                                        food_importance=food_importance,
                                        treat_frequency=treat_frequency
                                    )
                                    
                                    # Add food types (can be comma-separated)
                                    food_types_str = row['pet_food_types']
                                    if food_types_str:
                                        food_type_names = [ft.strip() for ft in food_types_str.split(',')]
                                        for food_type_name in food_type_names:
                                            if food_type_name:
                                                food_type, _ = FoodType.objects.get_or_create(name=food_type_name)
                                                pet.food_types.add(food_type)
                                    
                                    # Add food allergies (can be comma-separated)
                                    food_allergies_str = row.get('pet_food_allergies', '')
                                    if food_allergies_str:
                                        allergy_names = [a.strip() for a in food_allergies_str.split(',')]
                                        for allergy_name in allergy_names:
                                            if allergy_name:
                                                from pet.models import FoodAllergy
                                                allergy, _ = FoodAllergy.objects.get_or_create(
                                                    name=allergy_name,
                                                    defaults={'order': 0}
                                                )
                                                pet.food_allergies.add(allergy)
                                    
                                    # Add health issues (can be comma-separated)
                                    health_issues_str = row.get('pet_health_issues', '')
                                    if health_issues_str:
                                        issue_names = [i.strip() for i in health_issues_str.split(',')]
                                        for issue_name in issue_names:
                                            if issue_name:
                                                from pet.models import HealthIssue
                                                issue, _ = HealthIssue.objects.get_or_create(
                                                    name=issue_name,
                                                    defaults={'order': 0}
                                                )
                                                pet.health_issues.add(issue)
                                    
                                    self.stdout.write(self.style.SUCCESS(
                                        f"  └─ Created pet: {row['pet_name']} ({row['pet_type']})"
                                    ))
                                    pets_created += 1
                                    
                                    # Generate AI usage if flag is set
                                    if generate_ai and user.last_login:
                                        user_meals, user_health = self.generate_ai_usage(
                                            pet, user.last_login, max_meals, max_health
                                        )
                                        if user_meals > 0 or user_health > 0:
                                            total_ai_meals += user_meals
                                            total_ai_health += user_health
                                            users_with_ai += 1
                                            self.stdout.write(self.style.NOTICE(
                                                f"     └─ Generated: {user_meals} meals, {user_health} health reports"
                                            ))
                                    
                                except Exception as pet_error:
                                    self.stdout.write(self.style.ERROR(
                                        f"  └─ [ERROR] Failed to create pet: {str(pet_error)}"
                                    ))
                                    raise  # Re-raise to rollback the transaction
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"[ERROR] Error creating user {email}: {str(e)}"))
                        skipped_count += 1
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading CSV file: {str(e)}"))
            return
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {created_count} users"))
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {pets_created} pets"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count} users"))
        
        if generate_ai:
            self.stdout.write(self.style.SUCCESS(f"AI meal recommendations: {total_ai_meals}"))
            self.stdout.write(self.style.SUCCESS(f"AI health reports: {total_ai_health}"))
            self.stdout.write(self.style.SUCCESS(f"Users with AI data: {users_with_ai}"))
            if users_with_ai > 0:
                avg_meals = total_ai_meals / users_with_ai
                avg_health = total_ai_health / users_with_ai
                self.stdout.write(self.style.NOTICE(f"Average per user: {avg_meals:.2f} meals, {avg_health:.2f} health"))
        
        self.stdout.write("="*60)
        self.stdout.write(self.style.NOTICE(f"\nImported from: {csv_path}\n"))
    
    def generate_ai_usage(self, pet, last_login, max_meals, max_health):
        """Generate random AI meal recommendations and health reports for a pet"""
        meals_created = 0
        health_created = 0
        
        now = timezone.now()
        
        # Calculate days between last_login and now
        if last_login > now:
            return 0, 0
        
        days_since_login = (now - last_login).days
        if days_since_login < 0:
            days_since_login = 0
        
        # Random number of meal recommendations (0 to max_meals)
        # 70% chance of generating at least 1 meal
        if random.random() < 0.70:
            meals_to_generate = random.randint(1, max_meals)
        else:
            meals_to_generate = 0
        
        # Generate meal recommendations with random dates between last_login and now
        for i in range(meals_to_generate):
            # Random date between last_login and now
            random_days = random.randint(0, max(1, days_since_login))
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            
            created_time = last_login + timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )
            
            # Make sure it doesn't exceed current time
            if created_time > now:
                created_time = now - timedelta(hours=random.randint(1, 24))
            
            AIRecommendation.objects.create(
                pet=pet,
                type='meal',
                content=f"AI-generated meal recommendation for {pet.name}",
                created_at=created_time
            )
            meals_created += 1
        
        # Random number of health reports (0 to max_health)
        # 40% chance of generating health report
        if random.random() < 0.40:
            health_to_generate = random.randint(1, max_health)
        else:
            health_to_generate = 0
        
        # Generate health reports with random dates between last_login and now
        for i in range(health_to_generate):
            # Random date between last_login and now
            random_days = random.randint(0, max(1, days_since_login))
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            
            created_time = last_login + timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )
            
            # Make sure it doesn't exceed current time
            if created_time > now:
                created_time = now - timedelta(hours=random.randint(1, 24))
            
            AIHealthReport.objects.create(
                pet=pet,
                summary=f"AI-generated health report for {pet.name}",
                suggestions=f"Health suggestions for {pet.name}",
                created_at=created_time
            )
            health_created += 1
        
        return meals_created, health_created