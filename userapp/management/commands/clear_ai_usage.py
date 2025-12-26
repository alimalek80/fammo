from django.core.management.base import BaseCommand
from aihub.models import AIRecommendation, AIHealthReport
from django.utils import timezone


class Command(BaseCommand):
    help = 'Clear sample AI meal recommendations and health reports created by set_random_ai_usage script'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting'
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        
        # Count sample records (created by set_random_ai_usage script)
        meal_count = AIRecommendation.objects.filter(
            type='meal',
            content__icontains='Sample AI meal recommendation'
        ).count()
        
        health_count = AIHealthReport.objects.filter(
            summary__icontains='Sample AI health report'
        ).count()
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.WARNING('[WARNING] Clear Sample AI Usage Data'))
        self.stdout.write("="*60 + "\n")
        self.stdout.write(f"Found {meal_count} sample AI meal recommendations")
        self.stdout.write(f"Found {health_count} sample AI health reports")
        self.stdout.write(f"Total sample records to delete: {meal_count + health_count}\n")
        
        if meal_count == 0 and health_count == 0:
            self.stdout.write(self.style.NOTICE("No sample records found."))
            return
        
        if not confirm:
            self.stdout.write(self.style.ERROR(f"This will DELETE {meal_count + health_count} sample AI records!"))
            self.stdout.write(self.style.NOTICE("(Only records with 'Sample' in content will be deleted)"))
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.NOTICE("Operation cancelled."))
                return
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.NOTICE("Deleting sample AI meal recommendations..."))
        deleted_meals = AIRecommendation.objects.filter(
            type='meal',
            content__icontains='Sample AI meal recommendation'
        ).delete()
        self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted_meals[0]} meal recommendations"))
        
        self.stdout.write(self.style.NOTICE("Deleting sample AI health reports..."))
        deleted_health = AIHealthReport.objects.filter(
            summary__icontains='Sample AI health report'
        ).delete()
        self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted_health[0]} health reports"))
        
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS(f"Total deleted: {deleted_meals[0] + deleted_health[0]} records"))
        self.stdout.write(self.style.NOTICE("Real user-generated AI data was preserved."))
        self.stdout.write("="*60 + "\n")
