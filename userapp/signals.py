from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile
from subscription.models import SubscriptionPlan  # ✅ new import

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        default_plan = SubscriptionPlan.objects.filter(name='free').first()
        Profile.objects.create(user=instance, subscription_plan=default_plan)
