"""
Management command to initialize age history for existing pets
This creates initial age history records for pets that don't have them
"""
from django.core.management.base import BaseCommand
from pet.models import Pet, PetAgeHistory
from django.utils import timezone

class Command(BaseCommand):
    help = 'Initialize age history records for existing pets without losing current data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pet-id',
            type=int,
            help='Initialize age history for specific pet ID only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating records',
        )
    
    def handle(self, *args, **options):
        pet_id = options.get('pet_id')
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write('Initializing age history for existing pets...')
        
        try:
            # Get pets that need age history initialization
            if pet_id:
                pets = Pet.objects.filter(id=pet_id)
                if not pets.exists():
                    self.stdout.write(self.style.ERROR(f'Pet with ID {pet_id} not found'))
                    return
            else:
                # Get pets without age history that have the required data
                pets = Pet.objects.filter(
                    birth_date__isnull=False,
                    age_category__isnull=False,
                    age_history__isnull=True  # No age history records
                ).distinct().select_related('age_category', 'user', 'pet_type')
            
            total_pets = pets.count()
            self.stdout.write(f'Found {total_pets} pets that need age history initialization')
            
            if total_pets == 0:
                self.stdout.write(self.style.WARNING('No pets found that need age history initialization'))
                return
            
            created_count = 0
            snapshot_count = 0
            
            for i, pet in enumerate(pets, 1):
                try:
                    self.stdout.write(f'[{i}/{total_pets}] Processing: {pet.name} (ID: {pet.id})')
                    
                    # Calculate current age
                    current_age = pet.get_current_age()
                    current_age_months = (current_age['years'] * 12) + current_age['months']
                    
                    # Show pet details
                    self.stdout.write(f'  - Type: {pet.pet_type.name if pet.pet_type else "Unknown"}')
                    self.stdout.write(f'  - Current age: {current_age["years"]}y {current_age["months"]}m {current_age["weeks"]}w')
                    self.stdout.write(f'  - Age category: {pet.age_category.name}')
                    self.stdout.write(f'  - Birth date: {pet.birth_date}')
                    
                    if not dry_run:
                        # Create initial age history record
                        age_history = PetAgeHistory.objects.create(
                            pet=pet,
                            age_category=pet.age_category,
                            age_months_at_start=max(0, current_age_months),  # Don't allow negative ages
                            transition_reason='initial_setup'
                        )
                        created_count += 1
                        self.stdout.write(f'  ✓ Created age history record')
                        
                        # Create initial condition snapshot
                        snapshot = pet._save_condition_snapshot('initial_setup')
                        if snapshot:
                            snapshot_count += 1
                            self.stdout.write(f'  ✓ Created condition snapshot')
                        else:
                            self.stdout.write(f'  ⚠ Failed to create condition snapshot')
                    else:
                        self.stdout.write(f'  → Would create age history record and condition snapshot')
                        created_count += 1  # Count for dry run
                        snapshot_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error processing pet {pet.name} (ID: {pet.id}): {str(e)}'))
                    continue
            
            # Summary
            self.stdout.write('\\n' + '='*50)
            if dry_run:
                self.stdout.write(self.style.SUCCESS('DRY RUN SUMMARY:'))
                self.stdout.write(f'Would initialize age history for {created_count} pets')
                self.stdout.write(f'Would create {snapshot_count} condition snapshots')
                self.stdout.write('\\nTo actually perform these changes, run without --dry-run flag')
            else:
                self.stdout.write(self.style.SUCCESS(f'Age history initialization completed!'))
                self.stdout.write(f'Processed: {total_pets} pets')
                self.stdout.write(f'Created: {created_count} age history records')
                self.stdout.write(f'Created: {snapshot_count} condition snapshots')
                
                if created_count > 0:
                    self.stdout.write('\\n' + self.style.SUCCESS('✓ Age history initialized successfully!'))
                    self.stdout.write('Next steps:')
                    self.stdout.write('  1. Run age updates: python manage.py update_pet_ages')
                    self.stdout.write('  2. Set up automatic scheduling with Celery')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error initializing age history: {str(e)}'))
            return
        
        if not dry_run and created_count > 0:
            self.stdout.write('\\n' + self.style.SUCCESS('Pets now have age history tracking enabled! ✓'))