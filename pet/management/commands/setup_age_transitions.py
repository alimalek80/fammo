"""
Management command to set up age transition rules for existing age categories
This command creates the rules for when pets should transition between age categories
"""
from django.core.management.base import BaseCommand
from pet.models import PetType, AgeCategory, AgeTransitionRule

class Command(BaseCommand):
    help = 'Set up age transition rules for automatic pet age category updates based on existing age categories in database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing rules',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        created_count = 0
        updated_count = 0
        
        self.stdout.write(self.style.SUCCESS('Setting up age transition rules...'))
        
        try:
            # Get pet types
            dog_type = PetType.objects.filter(name__iexact='Dog').first()
            cat_type = PetType.objects.filter(name__iexact='Cat').first()
            
            if not dog_type:
                self.stdout.write(self.style.WARNING('Dog pet type not found in database'))
            if not cat_type:
                self.stdout.write(self.style.WARNING('Cat pet type not found in database'))
            
            # Set up DOG transition rules
            if dog_type:
                self.stdout.write(f'\\nSetting up rules for {dog_type.name}s...')
                
                # Get dog age categories (based on your database)
                puppy = AgeCategory.objects.filter(pet_type=dog_type, name__icontains='Puppy').first()
                mature = AgeCategory.objects.filter(pet_type=dog_type, name__icontains='Mature').first()
                senior = AgeCategory.objects.filter(pet_type=dog_type, name__icontains='Senior').first()
                
                if puppy and mature:
                    # Puppy to Mature Dog at 12 months (1 year)
                    rule, created = AgeTransitionRule.objects.get_or_create(
                        pet_type=dog_type,
                        from_category=puppy,
                        to_category=mature,
                        defaults={'transition_age_months': 12}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f'  ✓ Created: {puppy.name} → {mature.name} at 12 months')
                    elif force:
                        rule.transition_age_months = 12
                        rule.save()
                        updated_count += 1
                        self.stdout.write(f'  ↻ Updated: {puppy.name} → {mature.name} at 12 months')
                    else:
                        self.stdout.write(f'  - Exists: {puppy.name} → {mature.name} at {rule.transition_age_months} months')
                
                if mature and senior:
                    # Mature Dog to Senior Dog at 84 months (7 years)
                    rule, created = AgeTransitionRule.objects.get_or_create(
                        pet_type=dog_type,
                        from_category=mature,
                        to_category=senior,
                        defaults={'transition_age_months': 84}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f'  ✓ Created: {mature.name} → {senior.name} at 84 months (7 years)')
                    elif force:
                        rule.transition_age_months = 84
                        rule.save()
                        updated_count += 1
                        self.stdout.write(f'  ↻ Updated: {mature.name} → {senior.name} at 84 months')
                    else:
                        self.stdout.write(f'  - Exists: {mature.name} → {senior.name} at {rule.transition_age_months} months')
            
            # Set up CAT transition rules
            if cat_type:
                self.stdout.write(f'\\nSetting up rules for {cat_type.name}s...')
                
                # Get cat age categories (based on your database)
                kitten = AgeCategory.objects.filter(pet_type=cat_type, name__icontains='Kitten').first()
                adult = AgeCategory.objects.filter(pet_type=cat_type, name__icontains='Adult').first()
                aged = AgeCategory.objects.filter(pet_type=cat_type, name__icontains='Aged').first()
                
                if kitten and adult:
                    # Kitten to Adult Cat at 12 months (1 year)
                    rule, created = AgeTransitionRule.objects.get_or_create(
                        pet_type=cat_type,
                        from_category=kitten,
                        to_category=adult,
                        defaults={'transition_age_months': 12}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f'  ✓ Created: {kitten.name} → {adult.name} at 12 months')
                    elif force:
                        rule.transition_age_months = 12
                        rule.save()
                        updated_count += 1
                        self.stdout.write(f'  ↻ Updated: {kitten.name} → {adult.name} at 12 months')
                    else:
                        self.stdout.write(f'  - Exists: {kitten.name} → {adult.name} at {rule.transition_age_months} months')
                
                if adult and aged:
                    # Adult Cat to Aged Cat at 84 months (7 years)
                    rule, created = AgeTransitionRule.objects.get_or_create(
                        pet_type=cat_type,
                        from_category=adult,
                        to_category=aged,
                        defaults={'transition_age_months': 84}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f'  ✓ Created: {adult.name} → {aged.name} at 84 months (7 years)')
                    elif force:
                        rule.transition_age_months = 84
                        rule.save()
                        updated_count += 1
                        self.stdout.write(f'  ↻ Updated: {adult.name} → {aged.name} at 84 months')
                    else:
                        self.stdout.write(f'  - Exists: {adult.name} → {aged.name} at {rule.transition_age_months} months')
            
            # Summary
            self.stdout.write(f'\\n' + '='*50)
            self.stdout.write(self.style.SUCCESS(f'Age transition rules setup completed!'))
            self.stdout.write(f'Created: {created_count} new rules')
            self.stdout.write(f'Updated: {updated_count} existing rules')
            
            # Show current rules
            self.stdout.write(f'\\nCurrent transition rules:')
            rules = AgeTransitionRule.objects.all().order_by('pet_type__name', 'transition_age_months')
            for rule in rules:
                age_years = rule.transition_age_months // 12
                age_months_remainder = rule.transition_age_months % 12
                age_display = f"{age_years}y {age_months_remainder}m" if age_months_remainder else f"{age_years}y"
                self.stdout.write(f"  • {rule.pet_type.name}: {rule.from_category.name} → {rule.to_category.name} at {rule.transition_age_months}m ({age_display})")
            
            if created_count > 0 or updated_count > 0:
                self.stdout.write(f'\\n' + self.style.SUCCESS('✓ You can now run automatic age updates!'))
                self.stdout.write('Next steps:')
                self.stdout.write('  1. Initialize age history: python manage.py initialize_pet_histories')
                self.stdout.write('  2. Test age updates: python manage.py update_pet_ages')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up age transition rules: {str(e)}'))
            return
        
        self.stdout.write('\\n' + self.style.SUCCESS('Age transition rules setup completed successfully! ✓'))