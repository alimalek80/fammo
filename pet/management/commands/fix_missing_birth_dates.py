"""
Management command to fix missing birth_dates for pets that have age information
This ensures all pets with age data have proper birth_date for age tracking
"""
from django.core.management.base import BaseCommand
from django.db import models
from pet.models import Pet

class Command(BaseCommand):
    help = 'Fix missing birth_dates for pets that have age_years, age_months, or age_weeks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write('Checking for pets with missing birth_dates...')
        
        try:
            # Find pets that have age data but no birth_date
            pets_to_fix = Pet.objects.filter(
                birth_date__isnull=True
            ).filter(
                models.Q(age_years__isnull=False) | 
                models.Q(age_months__isnull=False) | 
                models.Q(age_weeks__isnull=False)
            )
            
            total_pets = pets_to_fix.count()
            self.stdout.write(f'Found {total_pets} pets with age data but missing birth_date')
            
            if total_pets == 0:
                self.stdout.write(self.style.SUCCESS('✓ All pets with age data have birth_dates!'))
                return
            
            fixed_count = 0
            
            for i, pet in enumerate(pets_to_fix, 1):
                try:
                    self.stdout.write(f'[{i}/{total_pets}] Processing: {pet.name} (ID: {pet.id})')
                    self.stdout.write(f'  - Years: {pet.age_years}, Months: {pet.age_months}, Weeks: {pet.age_weeks}')
                    
                    # Calculate birth date
                    calculated_birth_date = pet.calculate_birth_date_from_age()
                    
                    if calculated_birth_date:
                        self.stdout.write(f'  - Calculated birth date: {calculated_birth_date}')
                        
                        if not dry_run:
                            pet.birth_date = calculated_birth_date
                            pet.save()
                            fixed_count += 1
                            self.stdout.write(f'  ✓ Updated birth_date')
                        else:
                            self.stdout.write(f'  → Would set birth_date to: {calculated_birth_date}')
                            fixed_count += 1
                    else:
                        self.stdout.write(f'  ⚠ Could not calculate birth date (no age data)')
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error processing pet {pet.name}: {str(e)}'))
                    continue
            
            # Summary
            self.stdout.write('\\n' + '='*50)
            if dry_run:
                self.stdout.write(self.style.SUCCESS('DRY RUN SUMMARY:'))
                self.stdout.write(f'Would fix birth_dates for {fixed_count} pets')
                self.stdout.write('\\nTo actually fix them, run without --dry-run flag')
            else:
                self.stdout.write(self.style.SUCCESS(f'Birth_date fix completed!'))
                self.stdout.write(f'Fixed: {fixed_count}/{total_pets} pets')
                
                if fixed_count > 0:
                    self.stdout.write('\\n' + self.style.SUCCESS('✓ Birth dates fixed successfully!'))
                    self.stdout.write('Next steps:')
                    self.stdout.write('  1. Initialize age history: python manage.py initialize_pet_histories')
                    self.stdout.write('  2. Update age categories: python manage.py update_pet_ages')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fixing birth dates: {str(e)}'))
            return
        
        if not dry_run and fixed_count > 0:
            self.stdout.write('\\n' + self.style.SUCCESS('Pets now have proper birth_dates for age tracking! ✓'))