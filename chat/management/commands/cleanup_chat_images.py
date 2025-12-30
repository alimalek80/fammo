from django.core.management.base import BaseCommand
from chat.models import ChatMessage


class Command(BaseCommand):
    help = 'Delete chat images older than specified days to save storage space'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete images older than this many days (default: 7)'
        )

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(f'Cleaning up chat images older than {days} days...')
        
        deleted_count = ChatMessage.cleanup_old_images(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} old chat images')
        )
