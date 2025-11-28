"""
Management command to generate screenshots locally for uploading to cPanel.
Usage: python manage.py generate_screenshots
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from aihub.models import AIRecommendation, AIHealthReport
from evidence.screenshot_generator import generate_section_screenshots_from_data
import os


class Command(BaseCommand):
    help = 'Generate screenshots from latest meal plan and health report data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting screenshot generation...'))
        
        try:
            # Get latest meal plan
            latest_meal_plan = AIRecommendation.objects.order_by('-created_at').first()
            if not latest_meal_plan:
                self.stdout.write(self.style.ERROR('No meal plan data found in database'))
                return
            
            self.stdout.write(f'Found meal plan: {latest_meal_plan.id}')
            
            # Get latest health report
            latest_health_report = AIHealthReport.objects.order_by('-created_at').first()
            if not latest_health_report:
                self.stdout.write(self.style.ERROR('No health report data found in database'))
                return
            
            self.stdout.write(f'Found health report: {latest_health_report.id}')
            
            # Generate screenshots
            meal_plan_path, health_report_path = generate_section_screenshots_from_data(
                latest_meal_plan.content_json,
                latest_health_report.summary_json
            )
            
            if meal_plan_path and health_report_path:
                self.stdout.write(self.style.SUCCESS(f'✓ Meal plan screenshot: {meal_plan_path}'))
                self.stdout.write(self.style.SUCCESS(f'✓ Health report screenshot: {health_report_path}'))
                self.stdout.write(self.style.SUCCESS('\nScreenshots generated successfully!'))
                self.stdout.write(self.style.WARNING('\nTo use on cPanel:'))
                self.stdout.write('1. Upload these files to: ~/public_html/fammo/fammo/media/evidence_screenshots/')
                self.stdout.write('2. Make sure file permissions are 644')
                self.stdout.write('3. Set ENABLE_PLAYWRIGHT_SCREENSHOTS=False in cPanel environment')
            else:
                self.stdout.write(self.style.ERROR('Screenshot generation failed'))
                self.stdout.write(self.style.WARNING('Check console output for errors'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            import traceback
            traceback.print_exc()
