"""
Firebase Cloud Messaging (FCM) Service for FAMMO
Sends push notifications to mobile devices
"""
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_initialized = False


def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return True
    
    try:
        # Path to your service account key
        cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', 
                           os.path.join(settings.BASE_DIR, 'firebase-service-account.json'))
        
        if not os.path.exists(cred_path):
            logger.warning(f"Firebase credentials file not found at: {cred_path}")
            logger.warning("Push notifications will not work until Firebase is configured.")
            return False
        
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return False


def send_push_notification(token: str, title: str, body: str, data: dict = None) -> bool:
    """
    Send a push notification to a single device.
    
    Args:
        token: FCM device token
        title: Notification title
        body: Notification body text
        data: Optional data payload (dict)
    
    Returns:
        True if successful, False otherwise
    """
    if not initialize_firebase():
        logger.warning("Firebase not initialized, skipping push notification")
        return False
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#26B5A4',
                    sound='default',
                    channel_id='fammo_notifications',
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1,
                    ),
                ),
            ),
        )
        
        response = messaging.send(message)
        logger.info(f"FCM message sent successfully: {response}")
        return True
        
    except messaging.UnregisteredError:
        logger.warning(f"FCM token is no longer valid: {token[:20]}...")
        # Token is invalid, should be removed from database
        return False
    except Exception as e:
        logger.error(f"Failed to send FCM notification: {e}")
        return False


def send_push_to_multiple(tokens: list, title: str, body: str, data: dict = None) -> dict:
    """
    Send push notification to multiple devices.
    
    Args:
        tokens: List of FCM device tokens
        title: Notification title
        body: Notification body text
        data: Optional data payload
    
    Returns:
        Dict with success_count, failure_count, and failed_tokens
    """
    if not initialize_firebase():
        return {'success_count': 0, 'failure_count': len(tokens), 'failed_tokens': tokens}
    
    if not tokens:
        return {'success_count': 0, 'failure_count': 0, 'failed_tokens': []}
    
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#26B5A4',
                    sound='default',
                    channel_id='fammo_notifications',
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1,
                    ),
                ),
            ),
        )
        
        response = messaging.send_each_for_multicast(message)
        
        # Collect failed tokens
        failed_tokens = []
        for idx, send_response in enumerate(response.responses):
            if not send_response.success:
                failed_tokens.append(tokens[idx])
        
        return {
            'success_count': response.success_count,
            'failure_count': response.failure_count,
            'failed_tokens': failed_tokens,
        }
        
    except Exception as e:
        logger.error(f"Failed to send multicast FCM: {e}")
        return {'success_count': 0, 'failure_count': len(tokens), 'failed_tokens': tokens}


# ============================================
# Notification Helper Functions
# ============================================

def send_appointment_push_to_clinic(appointment):
    """Send push notification to clinic about new appointment"""
    from .models import DeviceToken
    
    clinic = appointment.clinic
    if not clinic.owner:
        return False
    
    # Get all device tokens for clinic owner
    tokens = DeviceToken.objects.filter(
        user=clinic.owner,
        is_active=True
    ).values_list('token', flat=True)
    
    if not tokens:
        logger.info(f"No FCM tokens for clinic owner {clinic.owner.email}")
        return False
    
    title = f"📅 New Appointment: {appointment.pet.name}"
    body = f"New appointment on {appointment.appointment_date.strftime('%b %d')} at {appointment.appointment_time.strftime('%H:%M')}"
    
    data = {
        'type': 'new_appointment',
        'appointment_id': str(appointment.id),
        'reference_code': appointment.reference_code,
    }
    
    result = send_push_to_multiple(list(tokens), title, body, data)
    
    # Clean up invalid tokens
    if result['failed_tokens']:
        DeviceToken.objects.filter(token__in=result['failed_tokens']).update(is_active=False)
    
    return result['success_count'] > 0


def send_appointment_status_push_to_user(appointment):
    """Send push notification to user about appointment status change"""
    from .models import DeviceToken
    from vets.models import AppointmentStatus
    
    # Get all device tokens for the user
    tokens = DeviceToken.objects.filter(
        user=appointment.user,
        is_active=True
    ).values_list('token', flat=True)
    
    if not tokens:
        logger.info(f"No FCM tokens for user {appointment.user.email}")
        return False
    
    # Customize message based on status
    if appointment.status == AppointmentStatus.CONFIRMED:
        title = "✅ Appointment Confirmed!"
        body = f"Your appointment for {appointment.pet.name} at {appointment.clinic.name} has been confirmed."
    elif appointment.status == AppointmentStatus.CANCELLED_BY_CLINIC:
        title = "❌ Appointment Cancelled"
        body = f"Your appointment at {appointment.clinic.name} has been cancelled by the clinic."
    elif appointment.status == AppointmentStatus.COMPLETED:
        title = "✓ Appointment Completed"
        body = f"Your appointment for {appointment.pet.name} has been marked as completed."
    else:
        title = "📋 Appointment Update"
        body = f"Your appointment for {appointment.pet.name} has been updated."
    
    data = {
        'type': 'appointment_update',
        'appointment_id': str(appointment.id),
        'status': appointment.status,
        'reference_code': appointment.reference_code,
    }
    
    result = send_push_to_multiple(list(tokens), title, body, data)
    
    # Clean up invalid tokens
    if result['failed_tokens']:
        DeviceToken.objects.filter(token__in=result['failed_tokens']).update(is_active=False)
    
    return result['success_count'] > 0


def send_appointment_cancelled_push_to_clinic(appointment):
    """Send push notification to clinic when user cancels"""
    from .models import DeviceToken
    
    clinic = appointment.clinic
    if not clinic.owner:
        return False
    
    tokens = DeviceToken.objects.filter(
        user=clinic.owner,
        is_active=True
    ).values_list('token', flat=True)
    
    if not tokens:
        return False
    
    title = "❌ Appointment Cancelled"
    body = f"{appointment.pet.name}'s appointment on {appointment.appointment_date.strftime('%b %d')} has been cancelled."
    
    data = {
        'type': 'appointment_cancelled',
        'appointment_id': str(appointment.id),
        'reference_code': appointment.reference_code,
    }
    
    result = send_push_to_multiple(list(tokens), title, body, data)
    
    if result['failed_tokens']:
        DeviceToken.objects.filter(token__in=result['failed_tokens']).update(is_active=False)
    
    return result['success_count'] > 0


def send_general_push_to_user(user, title: str, body: str, data: dict = None):
    """Send a general push notification to a user"""
    from .models import DeviceToken
    
    tokens = DeviceToken.objects.filter(
        user=user,
        is_active=True
    ).values_list('token', flat=True)
    
    if not tokens:
        logger.info(f"No FCM tokens for user {user.email}")
        return False
    
    result = send_push_to_multiple(list(tokens), title, body, data or {})
    
    # Clean up invalid tokens
    if result['failed_tokens']:
        DeviceToken.objects.filter(token__in=result['failed_tokens']).update(is_active=False)
    
    return result['success_count'] > 0
