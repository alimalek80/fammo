from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class AccountDeletionRequest(models.Model):
    """Track user account deletion requests"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved - Awaiting Deletion'),
        ('cancelled', 'Cancelled by User'),
        ('completed', 'Deletion Completed'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deletion_request'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, help_text="Optional reason for deletion")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin review
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_deletions'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Deletion schedule
    scheduled_deletion_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Track what was deleted
    had_pets = models.BooleanField(default=False)
    had_clinic = models.BooleanField(default=False)
    pets_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Account Deletion Request'
        verbose_name_plural = 'Account Deletion Requests'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_status_display()}"
    
    def days_until_deletion(self):
        """Calculate days remaining until deletion"""
        if self.scheduled_deletion_date and self.status == 'approved':
            delta = self.scheduled_deletion_date - timezone.now()
            return max(0, delta.days)
        return None
    
    def can_cancel(self):
        """Check if user can still cancel the request"""
        return self.status in ['pending', 'approved']
    
    def is_ready_for_deletion(self):
        """Check if the deletion date has passed"""
        if self.status == 'approved' and self.scheduled_deletion_date:
            return timezone.now() >= self.scheduled_deletion_date
        return False
