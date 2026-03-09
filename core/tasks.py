"""
Celery tasks for the core app - notifications and system maintenance
"""
from celery import shared_task
from django.utils import timezone
from django.urls import reverse
from .models import UserNotification, NotificationType
import logging

logger = logging.getLogger(__name__)

@shared_task
def create_weight_update_notifications():
    """
    Daily task to check pets and create weight update notifications when due.
    Prevents duplicate notifications by checking for existing unread notifications.
    """
    try:
        from pet.models import Pet
        
        created_count = 0
        checked_count = 0
        skipped_count = 0
        
        # Get all pets with proper setup (birth_date and pet_type required for reminder logic)
        pets = Pet.objects.filter(
            birth_date__isnull=False,
            pet_type__isnull=False
        ).select_related('user', 'pet_type').prefetch_related('weight_records')
        
        logger.info(f"Starting weight notification check for {pets.count()} pets")
        
        for pet in pets:
            checked_count += 1
            
            try:
                # Check if pet needs weight reminder
                reminder_info = pet.get_weight_reminder_info()
                
                if not reminder_info:
                    # No reminder needed
                    continue
                
                reminder_type = reminder_info['type']
                
                # Check for existing unread notifications to prevent duplicates
                notification_titles = []
                if reminder_type == 'first_weight':
                    notification_titles = [f"Add {pet.name}'s first weight record"]
                elif reminder_type == 'overdue':
                    notification_titles = [f"Update {pet.name}'s weight"]
                
                # Skip if there's already an unread notification for this pet's weight
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
                link = reverse('pet:add_weight_record', args=[pet.id])
                
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
                logger.info(f"Created weight notification for pet '{pet.name}' (ID: {pet.id}, Type: {reminder_type})")
                
            except Exception as e:
                logger.error(f"Error creating weight notification for pet '{pet.name}' (ID: {pet.id}): {str(e)}")
                continue
        
        logger.info(f"Weight notification check completed: {created_count} created, {skipped_count} skipped, {checked_count} total checked")
        
        return {
            'success': True,
            'checked_count': checked_count,
            'created_count': created_count,
            'skipped_count': skipped_count,
            'message': f"Created {created_count} weight notifications out of {checked_count} pets checked"
        }
        
    except Exception as e:
        error_msg = f"Error in create_weight_update_notifications task: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'checked_count': 0,
            'created_count': 0,
            'skipped_count': 0
        }


@shared_task
def resolve_weight_notifications_for_pet(pet_id):
    """
    Helper task to mark weight-related notifications as read when a pet's weight is updated.
    Called from the weight record creation process.
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
            logger.info(f"Resolved {resolved_count} weight notifications for pet '{pet.name}' (ID: {pet_id})")
        
        return {
            'success': True,
            'resolved_count': resolved_count
        }
        
    except Exception as e:
        logger.error(f"Error resolving weight notifications for pet {pet_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'resolved_count': 0
        }