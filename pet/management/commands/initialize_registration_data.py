from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from pet.models import Pet
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Initialize registration data for existing pets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Initializing registration data for existing pets...'))
        
        try:
            # Find pets without registration_date OR without current age tracking
            pets_to_update = Pet.objects.filter(
                models.Q(registration_date__isnull=True) |
                models.Q(
                    current_age_years__isnull=True,
                    current_age_months__isnull=True,
                    current_age_weeks__isnull=True
                ) |
                models.Q(
                    age_at_registration_years__isnull=True,
                    age_at_registration_months__isnull=True,
                    age_at_registration_weeks__isnull=True
                )
            )
            
            if not pets_to_update.exists():
                self.stdout.write(self.style.SUCCESS('No pets need registration data initialization.'))
                return
                
            updated_count = 0
            
            for pet in pets_to_update:
                try:
                    # Set registration_date to use actual creation time (if available)
                    if hasattr(pet, 'created_at') and pet.created_at:
                        pet.registration_date = pet.created_at
                        self.stdout.write(f'  ⚡ Setting registration_date to created_at: {pet.created_at}')
                    elif not pet.registration_date:
                        # No created_at or registration_date, use current time as fallback
                        pet.registration_date = timezone.now()
                        self.stdout.write(f'  ⚠ No timestamp found, using current time')
                    
                    # Ensure registration age fields are set from main age fields
                    if not any([pet.age_at_registration_years, pet.age_at_registration_months, pet.age_at_registration_weeks]):
                        pet.age_at_registration_years = pet.age_years
                        pet.age_at_registration_months = pet.age_months
                        pet.age_at_registration_weeks = pet.age_weeks
                    
                    # Make sure main age fields represent registration age (they should now)
                    # If they're different from registration fields, sync them
                    if (pet.age_years != pet.age_at_registration_years or 
                        pet.age_months != pet.age_at_registration_months or
                        pet.age_weeks != pet.age_at_registration_weeks):
                        pet.age_years = pet.age_at_registration_years
                        pet.age_months = pet.age_at_registration_months 
                        pet.age_weeks = pet.age_at_registration_weeks
                        self.stdout.write(f'  🔄 Synced main age fields with registration age')
                    
                    # Save to trigger birth_date calculation and current age update
                    pet.save()
                    
                    updated_count += 1
                    self.stdout.write(f'  ✓ Updated {pet.name} (ID: {pet.id})')
                    self.stdout.write(f'    Registration: {pet.get_age_at_registration_display()}, Current: {pet.get_age_display()}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Failed to update {pet.name} (ID: {pet.id}): {str(e)}')
                    )
            
            self.stdout.write('')
            self.stdout.write('=' * 50)
            self.stdout.write(self.style.SUCCESS(f'Registration data initialization completed!'))
            self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count} pets'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to initialize registration data: {str(e)}'))