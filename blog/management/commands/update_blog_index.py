"""
Django management command to update the blog index JSON file.
Run this command daily via cron or scheduler.
"""
from django.core.management.base import BaseCommand
from blog.services.blog_index_generator import generate_blog_index


class Command(BaseCommand):
    help = 'Updates the blog index JSON file with all published blog posts'

    def handle(self, *args, **options):
        self.stdout.write('Generating blog index...')
        
        try:
            output_file = generate_blog_index()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully generated blog index at: {output_file}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to generate blog index: {e}')
            )
            raise
