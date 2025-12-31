from django.core.management.base import BaseCommand
from vets.models import AppointmentReason


class Command(BaseCommand):
    help = 'Seeds the database with default appointment reasons'

    def handle(self, *args, **options):
        reasons = [
            {
                'name': 'General Checkup',
                'description': 'Routine health examination and wellness check',
                'order': 1
            },
            {
                'name': 'Vaccination',
                'description': 'Vaccination and immunization appointments',
                'order': 2
            },
            {
                'name': 'Dental Care',
                'description': 'Dental checkup, cleaning, or treatment',
                'order': 3
            },
            {
                'name': 'Skin & Coat Issues',
                'description': 'Skin problems, allergies, or coat health concerns',
                'order': 4
            },
            {
                'name': 'Digestive Issues',
                'description': 'Vomiting, diarrhea, or eating problems',
                'order': 5
            },
            {
                'name': 'Injury or Wound',
                'description': 'Treatment for cuts, wounds, or injuries',
                'order': 6
            },
            {
                'name': 'Eye or Ear Problems',
                'description': 'Eye infections, ear problems, or related issues',
                'order': 7
            },
            {
                'name': 'Spay/Neuter Consultation',
                'description': 'Consultation for spaying or neutering procedure',
                'order': 8
            },
            {
                'name': 'Behavior Consultation',
                'description': 'Behavioral issues, anxiety, or training concerns',
                'order': 9
            },
            {
                'name': 'Nutrition Consultation',
                'description': 'Diet, weight management, or nutritional advice',
                'order': 10
            },
            {
                'name': 'Senior Pet Care',
                'description': 'Health checkup and care for senior pets',
                'order': 11
            },
            {
                'name': 'Puppy/Kitten Care',
                'description': 'New pet checkup and initial vaccinations',
                'order': 12
            },
            {
                'name': 'Follow-up Visit',
                'description': 'Follow-up appointment for previous treatment',
                'order': 13
            },
            {
                'name': 'Other',
                'description': 'Other reasons not listed above',
                'order': 99
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for reason_data in reasons:
            reason, created = AppointmentReason.objects.update_or_create(
                name=reason_data['name'],
                defaults={
                    'description': reason_data['description'],
                    'order': reason_data['order'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {reason.name}'))
            else:
                updated_count += 1
                self.stdout.write(f'Updated: {reason.name}')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {created_count}, Updated {updated_count} appointment reasons.'
        ))
