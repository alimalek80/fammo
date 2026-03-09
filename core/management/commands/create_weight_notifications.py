"""
Management command to manually trigger weight notification creation for testing
"""
from django.core.management.base import BaseCommand
from core.tasks import create_weight_update_notifications


class Command(BaseCommand):
    help = 'Manually create weight update notifications for pets (for testing)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating notifications'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write("DRY RUN MODE - No notifications will be created")
        
        self.stdout.write("Checking pets for weight update notifications...")
        
        try:
            if dry_run:
                # For dry run, we'll just call the logic without actually creating notifications
                from pet.models import Pet
                from core.models import UserNotification, NotificationType
                
                pets = Pet.objects.filter(
                    birth_date__isnull=False,
                    pet_type__isnull=False
                ).select_related('user', 'pet_type').prefetch_related('weight_records')
                
                self.stdout.write(f"Found {pets.count()} pets to check")
                
                notifications_to_create = 0
                notifications_to_skip = 0
                
                for pet in pets:
                    reminder_info = pet.get_weight_reminder_info()
                    
                    if not reminder_info:
                        continue
                    
                    # Check for existing notifications
                    notification_titles = []
                    reminder_type = reminder_info['type']
                    if reminder_type == 'first_weight':
                        notification_titles = [f"Add {pet.name}'s first weight record"]
                    elif reminder_type == 'overdue':
                        notification_titles = [f"Update {pet.name}'s weight"]
                    
                    existing = UserNotification.objects.filter(
                        user=pet.user,
                        is_read=False,
                        notification_type=NotificationType.PET_REMINDER,
                        title__in=notification_titles
                    ).exists()
                    
                    if existing:
                        notifications_to_skip += 1
                        self.stdout.write(f"  SKIP: {pet.name} ({pet.user.email}) - notification exists")
                    else:
                        notifications_to_create += 1
                        self.stdout.write(f"  CREATE: {pet.name} ({pet.user.email}) - {reminder_type}")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nDRY RUN SUMMARY: Would create {notifications_to_create} notifications, "
                        f"skip {notifications_to_skip} existing ones"
                    )
                )
                
            else:
                # Actually run the task
                result = create_weight_update_notifications()
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully created {result['created_count']} notifications, "
                            f"skipped {result['skipped_count']} duplicates out of "
                            f"{result['checked_count']} pets checked"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Task failed: {result.get('error', 'Unknown error')}")
                    )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error running weight notification check: {str(e)}")
            )