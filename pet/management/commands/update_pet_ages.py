"""
Management command to manually update pet age categories
This command checks all pets and updates their age categories if needed
"""
from django.core.management.base import BaseCommand
from pet.models import Pet
from django.utils import timezone

class Command(BaseCommand):
    help = 'Manually check and update pet age categories based on current age and transition rules'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pet-id',
            type=int,
            help='Update age category for specific pet ID only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for all pets checked',
        )
    
    def handle(self, *args, **options):
        pet_id = options.get('pet_id')
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write('Checking pets for age category updates...')
        
        try:
            # Get pets to check
            if pet_id:
                pets = Pet.objects.filter(id=pet_id)
                if not pets.exists():
                    self.stdout.write(self.style.ERROR(f'Pet with ID {pet_id} not found'))
                    return
            else:
                # Get all pets with proper age tracking setup
                pets = Pet.objects.filter(
                    birth_date__isnull=False,
                    age_category__isnull=False,
                    pet_type__isnull=False
                ).select_related('age_category', 'pet_type', 'user')
            
            total_pets = pets.count()
            self.stdout.write(f'Checking {total_pets} pets for age category updates')
            
            if total_pets == 0:
                self.stdout.write(self.style.WARNING('No pets found with proper age tracking setup'))
                self.stdout.write('Make sure pets have:')
                self.stdout.write('  - Birth date set')
                self.stdout.write('  - Age category assigned')
                self.stdout.write('  - Pet type specified')
                return
            
            updated_count = 0
            checked_count = 0
            errors = []
            
            for i, pet in enumerate(pets, 1):
                try:
                    checked_count += 1
                    
                    # Get current age info
                    current_age = pet.get_current_age()
                    current_age_months = (current_age['years'] * 12) + current_age['months']
                    
                    # Check if pet should transition
                    new_category = pet.should_transition_age_category()
                    
                    if verbose or new_category:
                        self.stdout.write(f'\\n[{i}/{total_pets}] {pet.name} (ID: {pet.id})')
                        self.stdout.write(f'  - Owner: {pet.user.email}')
                        self.stdout.write(f'  - Type: {pet.pet_type.name}')
                        self.stdout.write(f'  - Current age: {current_age["years"]}y {current_age["months"]}m ({current_age_months} total months)')
                        self.stdout.write(f'  - Current category: {pet.age_category.name}')
                        self.stdout.write(f'  - Birth date: {pet.birth_date}')
                    
                    if new_category:
                        if not dry_run:
                            # Perform the transition
                            old_category_name = pet.age_category.name
                            success = pet.transition_to_age_category(new_category, "manual_update")
                            if success:
                                updated_count += 1
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Updated: {new_category.name} (was {old_category_name})'))
                            else:
                                errors.append(f'Failed to update {pet.name} (ID: {pet.id})')
                                self.stdout.write(self.style.ERROR(f'  ✗ Failed to update age category'))
                        else:
                            updated_count += 1
                            self.stdout.write(f'  → Would update to: {new_category.name}')
                    else:
                        if verbose:
                            self.stdout.write(f'  - No update needed')
                    
                except Exception as e:
                    error_msg = f'Error processing pet {pet.name} (ID: {pet.id}): {str(e)}'
                    errors.append(error_msg)
                    self.stdout.write(self.style.ERROR(f'  ✗ {error_msg}'))
                    continue
            
            # Summary
            self.stdout.write('\\n' + '='*60)
            if dry_run:
                self.stdout.write(self.style.SUCCESS('DRY RUN SUMMARY:'))
                self.stdout.write(f'Checked: {checked_count} pets')
                self.stdout.write(f'Would update: {updated_count} pets')
                self.stdout.write(f'Errors: {len(errors)}')
                
                if updated_count > 0:
                    self.stdout.write('\\nTo actually perform these updates, run without --dry-run flag')
            else:
                self.stdout.write(self.style.SUCCESS(f'Age category update completed!'))
                self.stdout.write(f'Checked: {checked_count} pets')
                self.stdout.write(f'Updated: {updated_count} pets')
                self.stdout.write(f'Errors: {len(errors)}')
                
                if updated_count > 0:
                    self.stdout.write('\\n' + self.style.SUCCESS('✓ Age categories updated successfully!'))
            
            # Show errors if any
            if errors:
                self.stdout.write('\\n' + self.style.ERROR('Errors encountered:'))
                for error in errors:
                    self.stdout.write(f'  • {error}')
            
            # Show transition rules
            from pet.models import AgeTransitionRule
            rules = AgeTransitionRule.objects.all().order_by('pet_type__name', 'transition_age_months')
            if rules.exists():
                self.stdout.write('\\nCurrent age transition rules:')
                for rule in rules:
                    age_years = rule.transition_age_months // 12
                    age_months_remainder = rule.transition_age_months % 12
                    age_display = f"{age_years}y {age_months_remainder}m" if age_months_remainder else f"{age_years}y"
                    self.stdout.write(f"  • {rule.pet_type.name}: {rule.from_category.name} → {rule.to_category.name} at {rule.transition_age_months}m ({age_display})")
            else:
                self.stdout.write('\\n' + self.style.WARNING('⚠ No age transition rules found!'))
                self.stdout.write('Run: python manage.py setup_age_transitions')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating pet ages: {str(e)}'))
            return
        
        if not dry_run and updated_count > 0:
            self.stdout.write('\\n' + self.style.SUCCESS('Pet age categories are now up to date! ✓'))