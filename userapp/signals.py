from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from .models import CustomUser, Profile
from subscription.models import SubscriptionPlan  # ✅ new import
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            # Get or create default free plan
            default_plan, _ = SubscriptionPlan.objects.get_or_create(
                name='free',
                defaults={
                    'price': 0,
                    'daily_ai_limit': 10,
                    'is_active': True
                }
            )
            Profile.objects.get_or_create(
                user=instance,
                defaults={'subscription_plan': default_plan}
            )
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.email}: {str(e)}")
            # Create profile without subscription plan as fallback
            try:
                Profile.objects.get_or_create(user=instance)
            except Exception as e2:
                logger.error(f"Critical error creating profile: {str(e2)}")

@receiver(post_save, sender=User)
def notify_admin_on_signup(sender, instance, created, **kwargs):
    if created:
        try:
            send_mail(
                subject="New User Signup",
                message=f"A new user has signed up: {instance.email}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # or your admin email
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Error sending admin notification: {str(e)}")
