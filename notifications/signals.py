"""
Django signal receivers for Telegram notifications.
Imported once by NotificationsConfig.ready().
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.telegram import send_telegram_message
from notifications.models import NotificationLog


# ─────────────────────────────────────────────
# 1. New user registration
# ─────────────────────────────────────────────
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def notify_new_user(sender, instance, created, **kwargs):
    if not created:
        return

    text = (
        "👤 <b>New User Registered</b>\n"
        f"📧 Email: {instance.email}\n"
        f"🕐 Joined: {instance.date_joined.strftime('%Y-%m-%d %H:%M')}"
    )
    success = send_telegram_message(text)
    NotificationLog.objects.create(
        event='new_user',
        message=text,
        status='sent' if success else 'failed',
        error_detail='' if success else 'Telegram API call failed',
    )


# ─────────────────────────────────────────────
# 2. New forum question
# ─────────────────────────────────────────────
from forum.models import Question


@receiver(post_save, sender=Question)
def notify_new_forum_question(sender, instance, created, **kwargs):
    if not created:
        return

    author = getattr(instance, 'author', None)
    author_email = author.email if author else 'unknown'

    text = (
        "❓ <b>New Forum Question</b>\n"
        f"📝 Title: {instance.title}\n"
        f"🏷 Category: {instance.get_category_display()}\n"
        f"👤 Author: {author_email}\n"
        f"🕐 Posted: {instance.created_at.strftime('%Y-%m-%d %H:%M')}"
    )
    success = send_telegram_message(text)
    NotificationLog.objects.create(
        event='new_forum_question',
        message=text,
        status='sent' if success else 'failed',
        error_detail='' if success else 'Telegram API call failed',
    )


# ─────────────────────────────────────────────
# 3. New completed subscription transaction
# ─────────────────────────────────────────────
from subscription.models import SubscriptionTransaction


@receiver(post_save, sender=SubscriptionTransaction)
def notify_new_subscription(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.status != 'completed':
        return

    plan_name = instance.plan.get_name_display() if instance.plan else 'Unknown'
    text = (
        "💳 <b>New Subscription</b>\n"
        f"👤 User: {instance.user.email}\n"
        f"📦 Plan: {plan_name}\n"
        f"💶 Amount: €{instance.amount}\n"
        f"🕐 Date: {instance.created_at.strftime('%Y-%m-%d %H:%M')}"
    )
    success = send_telegram_message(text)
    NotificationLog.objects.create(
        event='new_subscription',
        message=text,
        status='sent' if success else 'failed',
        error_detail='' if success else 'Telegram API call failed',
    )


# ─────────────────────────────────────────────
# 4. New clinic / vet registered
# ─────────────────────────────────────────────
from vets.models import Clinic


@receiver(post_save, sender=Clinic)
def notify_new_clinic(sender, instance, created, **kwargs):
    if not created:
        return

    text = (
        "🏥 <b>New Clinic / Vet Registered</b>\n"
        f"🏷 Name: {instance.name}\n"
        f"📍 City: {instance.city or 'N/A'}\n"
        f"🕐 Registered: {instance.created_at.strftime('%Y-%m-%d %H:%M')}"
    )
    success = send_telegram_message(text)
    NotificationLog.objects.create(
        event='new_clinic',
        message=text,
        status='sent' if success else 'failed',
        error_detail='' if success else 'Telegram API call failed',
    )
