#!/usr/bin/env python
"""
Cron job script for weight notifications on shared hosting
Run this script via cPanel cron jobs every 6 hours
"""
import os
import sys
import django
from datetime import datetime
import logging

# Setup paths - CONFIGURED FOR YOUR CPANEL
PROJECT_PATH = '/home/fammkoqw/public_html/fammo'
LOG_PATH = '/home/fammkoqw/public_html/fammo/logs'

# Add project to Python path
sys.path.insert(0, PROJECT_PATH)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
django.setup()

from pet.models import Pet
from core.models import UserNotification, NotificationType
from django.urls import reverse
from django.utils import timezone

# Setup logging
os.makedirs(LOG_PATH, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_PATH, 'weight_notifications.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_and_create_notifications():
    """
    Check pets and create weight notifications
    This replicates the functionality of the Celery task
    """
    try:
        created_count = 0
        checked_count = 0
        skipped_count = 0
        
        # Get all pets with proper setup
        pets = Pet.objects.filter(
            birth_date__isnull=False,
            pet_type__isnull=False
        ).select_related('user', 'pet_type').prefetch_related('weight_records')
        
        logging.info(f"Starting weight notification check for {pets.count()} pets")
        
        for pet in pets:
            checked_count += 1
            
            try:
                # Check if pet needs weight reminder
                reminder_info = pet.get_weight_reminder_info()
                
                if not reminder_info:
                    continue
                
                reminder_type = reminder_info['type']
                
                # Check for existing unread notifications to prevent duplicates
                notification_titles = []
                if reminder_type == 'first_weight':
                    notification_titles = [f"Add {pet.name}'s first weight record"]
                elif reminder_type == 'overdue':
                    notification_titles = [f"Update {pet.name}'s weight"]
                
                existing_notification = UserNotification.objects.filter(
                    user=pet.user,
                    is_read=False,
                    notification_type=NotificationType.PET_REMINDER,
                    title__in=notification_titles
                ).exists()
                
                if existing_notification:
                    skipped_count += 1
                    continue
                
                # Create notification based on reminder type
                if reminder_type == 'first_weight':
                    title = f"Add {pet.name}'s first weight record"
                    message = f"Tracking weight helps detect health changes early. Add the first weight record for {pet.name}."
                    action_required = True
                    
                elif reminder_type == 'overdue':
                    days_overdue = reminder_info.get('days_overdue', 0)
                    total_days = days_overdue + reminder_info['reminder_days']
                    title = f"Update {pet.name}'s weight"
                    message = f"It has been {total_days} days since {pet.name}'s last weight update. Regular tracking helps catch health changes early."
                    action_required = False
                
                # Generate link to add weight record
                try:
                    link = reverse('pet:add_weight_record', args=[pet.id])
                except:
                    link = f'/en/pets/{pet.id}/weight/add/'  # Fallback URL
                
                # Create the notification
                UserNotification.create_notification(
                    user=pet.user,
                    notification_type=NotificationType.PET_REMINDER,
                    title=title,
                    message=message,
                    link=link,
                    action_required=action_required,
                    is_important=False
                )
                
                created_count += 1
                logging.info(f"Created weight notification for pet '{pet.name}' (ID: {pet.id}, Type: {reminder_type})")
                
            except Exception as e:
                logging.error(f"Error creating weight notification for pet '{pet.name}' (ID: {pet.id}): {str(e)}")
                continue
        
        logging.info(f"Weight notification check completed: {created_count} created, {skipped_count} skipped, {checked_count} total checked")
        
        return {
            'success': True,
            'checked_count': checked_count,
            'created_count': created_count,
            'skipped_count': skipped_count,
            'message': f"Created {created_count} weight notifications out of {checked_count} pets checked"
        }
        
    except Exception as e:
        error_msg = f"Error in weight notification check: {str(e)}"
        logging.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'checked_count': 0,
            'created_count': 0,
            'skipped_count': 0
        }

def resolve_weight_notifications(pet_id):
    """
    Mark weight-related notifications as read
    Called when user adds weight record
    """
    try:
        from pet.models import Pet
        
        # Get the pet
        pet = Pet.objects.select_related('user').get(id=pet_id)
        
        # Find unread weight-related notifications for this pet
        weight_notification_titles = [
            f"Add {pet.name}'s first weight record",
            f"Update {pet.name}'s weight"
        ]
        
        notifications = UserNotification.objects.filter(
            user=pet.user,
            is_read=False,
            notification_type=NotificationType.PET_REMINDER,
            title__in=weight_notification_titles
        )
        
        resolved_count = 0
        for notification in notifications:
            notification.mark_as_read()
            resolved_count += 1
        
        if resolved_count > 0:
            logging.info(f"Resolved {resolved_count} weight notifications for pet '{pet.name}' (ID: {pet_id})")
        
        return resolved_count
        
    except Exception as e:
        logging.error(f"Error resolving weight notifications for pet {pet_id}: {str(e)}")
        return 0

if __name__ == "__main__":
    print(f"FAMMO Weight Notification Check - {datetime.now()}")
    result = check_and_create_notifications()
    
    if result['success']:
        print(f"✅ Success: Created {result['created_count']} notifications, "
              f"skipped {result['skipped_count']} duplicates, "
              f"checked {result['checked_count']} pets total")
        logging.info(f"Cron job completed successfully: {result}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        logging.error(f"Cron job failed: {result}")
    
    print("Check logs at:", os.path.join(LOG_PATH, 'weight_notifications.log'))