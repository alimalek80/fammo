import secrets
import string
from math import radians, cos, sin, asin, sqrt
from typing import Tuple, Optional
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.conf import settings
from .models import Clinic


def generate_email_confirmation_token():
    """Generate a secure random token for email confirmation"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))


def send_clinic_confirmation_email(request, clinic):
    """Send email confirmation to clinic"""
    # Generate token
    token = generate_email_confirmation_token()
    clinic.email_confirmation_token = token
    clinic.email_confirmation_sent_at = timezone.now()
    clinic.save()
    
    # Build confirmation URL
    current_site = get_current_site(request)
    confirmation_url = request.build_absolute_uri(
        reverse('vets:confirm_email', kwargs={
            'clinic_id': clinic.id,
            'token': token
        })
    )
    
    # Prepare email context
    context = {
        'clinic': clinic,
        'confirmation_url': confirmation_url,
        'site_name': 'FAMMO',
        'domain': current_site.domain,
    }
    
    # Render email content
    subject = 'Confirm Your Clinic Email - FAMMO'
    html_message = render_to_string('vets/emails/clinic_email_confirmation.html', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message='',  # Plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[clinic.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False


def send_admin_notification_email(request, clinic):
    """Send notification to admin about new clinic registration"""
    current_site = get_current_site(request)
    
    # Build admin URL
    admin_url = request.build_absolute_uri(
        f'/admin/vets/clinic/{clinic.id}/change/'
    )
    
    # Prepare email context
    context = {
        'clinic': clinic,
        'admin_url': admin_url,
        'site_name': 'FAMMO',
        'domain': current_site.domain,
    }
    
    # Render email content
    subject = f'New Clinic Pending Approval - {clinic.name}'
    html_message = render_to_string('vets/emails/admin_clinic_notification.html', context)
    
    # Get admin emails from settings
    admin_emails = [email for name, email in settings.ADMINS]
    if not admin_emails:
        admin_emails = [settings.DEFAULT_FROM_EMAIL]  # Fallback
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message='',  # Plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending admin notification: {e}")
        return False


def is_confirmation_token_valid(clinic, token):
    """Check if the confirmation token is valid and not expired"""
    if not clinic.email_confirmation_token or clinic.email_confirmation_token != token:
        return False
    
    # Check if token is expired (24 hours)
    if clinic.email_confirmation_sent_at:
        expiry_time = clinic.email_confirmation_sent_at + timezone.timedelta(hours=24)
        if timezone.now() > expiry_time:
            return False
    
    return True


def confirm_clinic_email(clinic, token):
    """Confirm clinic email if token is valid"""
    if not is_confirmation_token_valid(clinic, token):
        return False
    
    # Mark email as confirmed
    clinic.email_confirmed = True
    clinic.email_confirmation_token = ''  # Clear token after use
    clinic.save()
    
    return True


# ========== Location & Geocoding Utilities ==========

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def get_clinics_within_radius(latitude: float, longitude: float, radius_km: float = 50):
    """
    Get all clinics within a certain radius of given coordinates.
    Uses Haversine formula for distance calculation.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        radius_km: Search radius in kilometers (default: 50)
    
    Returns:
        QuerySet of clinics with distance annotation, ordered by distance
    """
    from django.db.models import F
    
    # Get all clinics with coordinates that are active
    clinics = Clinic.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        email_confirmed=True,
        admin_approved=True
    )
    
    # Calculate distance for each clinic
    clinics_with_distance = []
    for clinic in clinics:
        distance = haversine_distance(
            latitude, longitude,
            float(clinic.latitude), float(clinic.longitude)
        )
        
        if distance <= radius_km:
            clinic.distance = round(distance, 1)
            clinics_with_distance.append(clinic)
    
    # Sort by distance
    clinics_with_distance.sort(key=lambda x: x.distance)
    
    return clinics_with_distance


def get_location_from_ip(ip_address: str) -> Optional[dict]:
    """
    Get approximate location from IP address.
    This is a placeholder - integrate with IP geolocation service.
    
    Args:
        ip_address: User's IP address
    
    Returns:
        Dictionary with latitude, longitude, city, country or None
    """
    # TODO: Implement IP geolocation
    # Options:
    # 1. MaxMind GeoIP2 (you already have GeoLite2-Country.mmdb)
    # 2. ip-api.com (free tier available)
    # 3. ipinfo.io
    
    try:
        # Example using MaxMind GeoLite2:
        # import geoip2.database
        # reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        # response = reader.city(ip_address)
        # return {
        #     'latitude': response.location.latitude,
        #     'longitude': response.location.longitude,
        #     'city': response.city.name,
        #     'country': response.country.name
        # }
        pass
    except Exception as e:
        print(f"IP geolocation error: {e}")
    
    return None


def geocode_address(address: str = '', city: str = '') -> Optional[dict]:
    """
    Convert address and city to latitude and longitude using Google Geocoding API.
    
    Args:
        address: Street address
        city: City name
        
    Returns:
        dict with 'latitude' and 'longitude' keys, or None if geocoding fails
        (non-blocking - returns None gracefully on any error)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Check if geopy is available
        try:
            from geopy.geocoders import GoogleV3
            from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        except ImportError:
            logger.warning("[GEOCODING] geopy not installed - skipping geocoding")
            return None
        
        # Build full address
        full_address = f"{address}, {city}".strip(', ')
        
        if not full_address:
            logger.debug("[GEOCODING] Empty address - skipping")
            return None
        
        # Get Google Maps API key
        google_api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        if not google_api_key:
            logger.warning("[GEOCODING] GOOGLE_MAPS_API_KEY not configured - skipping")
            return None
        
        # Initialize geocoder
        geolocator = GoogleV3(api_key=google_api_key, timeout=5)
        
        # Geocode address
        location = geolocator.geocode(full_address)
        
        if location:
            logger.info(f"[GEOCODING] ✅ Success for '{full_address}': ({location.latitude}, {location.longitude})")
            return {
                'latitude': location.latitude,
                'longitude': location.longitude
            }
        else:
            logger.warning(f"[GEOCODING] No location found for '{full_address}'")
            return None
        
    except ImportError as e:
        logger.warning(f"[GEOCODING] Missing dependency: {str(e)}")
        return None
    except Exception as e:
        # Don't let geocoding errors crash the admin
        logger.error(f"[GEOCODING] Unexpected error: {str(e)}", exc_info=True)
        return None


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    Handles proxies and load balancers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ========== Appointment Notification Utilities ==========

def create_clinic_notification(clinic, notification_type, title, message, appointment=None):
    """Create an in-app notification for a clinic"""
    from .models import ClinicNotification
    
    return ClinicNotification.objects.create(
        clinic=clinic,
        notification_type=notification_type,
        title=title,
        message=message,
        appointment=appointment
    )


def send_appointment_notification_to_clinic(appointment):
    """Send email notification to clinic about new appointment"""
    try:
        # Get user profile info
        user_name = "Unknown User"
        user_phone = ""
        if hasattr(appointment.user, 'profile'):
            profile = appointment.user.profile
            user_name = f"{profile.first_name} {profile.last_name}".strip() or appointment.user.email
            user_phone = profile.phone or ""
        
        # Prepare email context
        context = {
            'clinic': appointment.clinic,
            'appointment': appointment,
            'pet': appointment.pet,
            'user_name': user_name,
            'user_email': appointment.user.email,
            'user_phone': user_phone,
            'reason': appointment.reason.name if appointment.reason else appointment.reason_text,
            'site_name': 'FAMMO',
        }
        
        # Render email content
        subject = f'New Appointment Booking - {appointment.pet.name} ({appointment.reference_code})'
        html_message = render_to_string('vets/emails/appointment_new_notification.html', context)
        
        # Send email to clinic
        recipient_email = appointment.clinic.email or (appointment.clinic.owner.email if appointment.clinic.owner else None)
        if not recipient_email:
            print(f"No email address for clinic {appointment.clinic.name}")
            return False
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending appointment notification to clinic: {e}")
        return False


def send_appointment_cancellation_to_clinic(appointment):
    """Send email notification to clinic about cancelled appointment"""
    try:
        # Get user profile info
        user_name = "Unknown User"
        if hasattr(appointment.user, 'profile'):
            profile = appointment.user.profile
            user_name = f"{profile.first_name} {profile.last_name}".strip() or appointment.user.email
        
        # Prepare email context
        context = {
            'clinic': appointment.clinic,
            'appointment': appointment,
            'pet': appointment.pet,
            'user_name': user_name,
            'cancellation_reason': appointment.cancellation_reason,
            'site_name': 'FAMMO',
        }
        
        # Render email content
        subject = f'Appointment Cancelled - {appointment.pet.name} ({appointment.reference_code})'
        html_message = render_to_string('vets/emails/appointment_cancelled_notification.html', context)
        
        # Send email to clinic
        recipient_email = appointment.clinic.email or (appointment.clinic.owner.email if appointment.clinic.owner else None)
        if not recipient_email:
            return False
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending cancellation notification to clinic: {e}")
        return False


def send_appointment_status_update_to_user(appointment):
    """Send email notification to user about appointment status change and create UserNotification"""
    try:
        # Get user profile info
        user_name = "User"
        if hasattr(appointment.user, 'profile'):
            user_name = appointment.user.profile.first_name or "User"
        
        # Prepare email context
        context = {
            'clinic': appointment.clinic,
            'appointment': appointment,
            'pet': appointment.pet,
            'user_name': user_name,
            'status_display': appointment.get_status_display(),
            'site_name': 'FAMMO',
        }
        
        # Determine subject based on status
        from .models import AppointmentStatus
        from core.models import UserNotification, NotificationType
        
        if appointment.status == AppointmentStatus.CONFIRMED:
            subject = f'Appointment Confirmed - {appointment.pet.name} at {appointment.clinic.name}'
            template = 'vets/emails/appointment_confirmed_user.html'
            notification_type = NotificationType.APPOINTMENT_CONFIRMED
            notification_title = f"Appointment Confirmed"
            notification_message = f"Your appointment for {appointment.pet.name} at {appointment.clinic.name} on {appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.appointment_time.strftime('%H:%M')} has been confirmed."
        elif appointment.status == AppointmentStatus.CANCELLED_BY_CLINIC:
            subject = f'Appointment Cancelled by Clinic - {appointment.pet.name}'
            template = 'vets/emails/appointment_cancelled_by_clinic_user.html'
            notification_type = NotificationType.APPOINTMENT_CANCELLED
            notification_title = f"Appointment Cancelled"
            notification_message = f"Your appointment for {appointment.pet.name} at {appointment.clinic.name} on {appointment.appointment_date.strftime('%B %d, %Y')} has been cancelled by the clinic."
            if appointment.cancellation_reason:
                notification_message += f" Reason: {appointment.cancellation_reason}"
        else:
            subject = f'Appointment Update - {appointment.pet.name}'
            template = 'vets/emails/appointment_status_update_user.html'
            notification_type = NotificationType.SYSTEM
            notification_title = f"Appointment Update"
            notification_message = f"Your appointment for {appointment.pet.name} has been updated. Status: {appointment.get_status_display()}"
        
        # Create UserNotification
        UserNotification.create_notification(
            user=appointment.user,
            notification_type=notification_type,
            title=notification_title,
            message=notification_message,
            link=f"/en/vets/appointments/{appointment.pk}/",
            is_important=(appointment.status == AppointmentStatus.CANCELLED_BY_CLINIC),
            action_required=False
        )
        
        html_message = render_to_string(template, context)
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending appointment status update to user: {e}")
        return False


def send_appointment_reminder(appointment):
    """Send appointment reminder to user (typically 24 hours before)"""
    try:
        # Get user profile info
        user_name = "User"
        if hasattr(appointment.user, 'profile'):
            user_name = appointment.user.profile.first_name or "User"
        
        # Prepare email context
        context = {
            'clinic': appointment.clinic,
            'appointment': appointment,
            'pet': appointment.pet,
            'user_name': user_name,
            'site_name': 'FAMMO',
        }
        
        subject = f'Reminder: Appointment Tomorrow - {appointment.pet.name} at {appointment.clinic.name}'
        html_message = render_to_string('vets/emails/appointment_reminder_user.html', context)
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.user.email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending appointment reminder: {e}")
        return False
