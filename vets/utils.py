import secrets
import string
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