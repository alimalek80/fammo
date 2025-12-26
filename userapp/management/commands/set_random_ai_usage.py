from django.core.management.base import BaseCommand
from userapp.models import CustomUser
from pet.models import Pet
from aihub.models import AIRecommendation, AIHealthReport
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Randomly create AI meal recommendations and health reports for sample users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-meals',
            type=int,
            default=3,
            help='Maximum meal recommendations per pet per month (default: 3)'
        )
        parser.add_argument(
            '--max-health',
            type=int,
            default=1,
            help='Maximum health reports per pet per month (default: 1)'
        )
        parser.add_argument(
            '--active-users-only',
            action='store_true',
            help='Only generate AI usage for users with last_login in last 30 days'
        )

    def handle(self, *args, **options):
        max_meals = options['max_meals']
        max_health = options['max_health']
        active_only = options['active_users_only']
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS('[START] Generating random AI usage'))
        self.stdout.write("="*60 + "\n")
        
        # Get users based on activity filter
        if active_only:
            cutoff_date = timezone.now() - timedelta(days=30)
            users = CustomUser.objects.filter(
                is_superuser=False,
                is_staff=False,
                last_login__gte=cutoff_date
            )
            self.stdout.write(self.style.NOTICE(f"Filtering to users active in last 30 days..."))
        else:
            users = CustomUser.objects.filter(is_superuser=False, is_staff=False)
        
        users_list = list(users)
        self.stdout.write(self.style.NOTICE(f"Found {len(users_list)} users to process\n"))
        
        processed_users = 0
        total_meals = 0
        total_health = 0
        
        for user in users_list:
            # Get user's pets
            pets = Pet.objects.filter(user=user)
            if not pets.exists():
                continue
            
            # Only generate AI usage for users who have logged in
            if not user.last_login:
                continue
            
            user_meals = 0
            user_health = 0
            
            # Calculate date range: from user registration to now
            now = timezone.now()
            start_date = user.date_joined
            
            # Calculate days between registration and now
            if start_date > now:
                continue
            
            days_since_registration = (now - start_date).days
            if days_since_registration < 0:
                days_since_registration = 0
            
            for pet in pets:
                # Random number of meal recommendations (0 to max_meals)
                # 70% chance of generating at least 1 meal
                if random.random() < 0.70:
                    meals_to_generate = random.randint(1, max_meals)
                else:
                    meals_to_generate = 0
                
                # Generate meal recommendations with random dates between registration and now
                for i in range(meals_to_generate):
                    # Random date between registration and now
                    random_days = random.randint(0, max(1, days_since_registration))
                    random_hours = random.randint(0, 23)
                    random_minutes = random.randint(0, 59)
                    
                    created_time = start_date + timedelta(
                        days=random_days,
                        hours=random_hours,
                        minutes=random_minutes
                    )
                    
                    # Make sure it doesn't exceed current time
                    if created_time > now:
                        created_time = now - timedelta(hours=random.randint(1, 24))
                    
                    # Create and update created_at (workaround for auto_now_add=True)
                    recommendation = AIRecommendation.objects.create(
                        pet=pet,
                        type='meal',
                        content=f"AI-generated meal recommendation for {pet.name}"
                    )
                    AIRecommendation.objects.filter(pk=recommendation.pk).update(created_at=created_time)
                    user_meals += 1
                
                # Random number of health reports (0 to max_health)
                # 40% chance of generating health report
                if random.random() < 0.40:
                    health_to_generate = random.randint(1, max_health)
                else:
                    health_to_generate = 0
                
                # Generate health reports with random dates between registration and now
                for i in range(health_to_generate):
                    # Random date between registration and now
                    random_days = random.randint(0, max(1, days_since_registration))
                    random_hours = random.randint(0, 23)
                    random_minutes = random.randint(0, 59)
                    
                    created_time = start_date + timedelta(
                        days=random_days,
                        hours=random_hours,
                        minutes=random_minutes
                    )
                    
                    # Make sure it doesn't exceed current time
                    if created_time > now:
                        created_time = now - timedelta(hours=random.randint(1, 24))
                    
                    # Create and update created_at (workaround for auto_now_add=True)
                    report = AIHealthReport.objects.create(
                        pet=pet,
                        summary=f"AI-generated health report for {pet.name}",
                        suggestions=f"Health suggestions for {pet.name}"
                    )
                    AIHealthReport.objects.filter(pk=report.pk).update(created_at=created_time)
                    user_health += 1
            
            if user_meals > 0 or user_health > 0:
                self.stdout.write(
                    f"  ✓ {user.email}: {user_meals} meal recs, {user_health} health reports"
                )
                processed_users += 1
                total_meals += user_meals
                total_health += user_health
        
        # Calculate averages
        avg_meals = total_meals / processed_users if processed_users > 0 else 0
        avg_health = total_health / processed_users if processed_users > 0 else 0
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"Users processed: {processed_users}"))
        self.stdout.write(self.style.SUCCESS(f"Total AI meal recommendations: {total_meals}"))
        self.stdout.write(self.style.SUCCESS(f"Total AI health reports: {total_health}"))
        self.stdout.write(self.style.SUCCESS(f"Average meals per user: {avg_meals:.2f}"))
        self.stdout.write(self.style.SUCCESS(f"Average health per user: {avg_health:.2f}"))
        self.stdout.write("="*60 + "\n")
