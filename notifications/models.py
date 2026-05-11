from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationLog(models.Model):
    """Records every Telegram notification that was sent (or failed)."""

    EVENT_CHOICES = [
        ('new_user', 'New User Registered'),
        ('new_forum_question', 'New Forum Question'),
        ('new_subscription', 'New Subscription'),
        ('new_clinic', 'New Clinic / Vet Registered'),
    ]

    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    event = models.CharField(max_length=40, choices=EVENT_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    error_detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.get_event_display()} — {self.created_at.strftime('%Y-%m-%d %H:%M')}"
