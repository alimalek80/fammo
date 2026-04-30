from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from subscription.models import SubscriptionPlan
from datetime import timedelta

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        try:
            p = self.profile
            name = f"{p.first_name} {p.last_name}".strip()
            if name:
                return name
        except Exception:
            pass
        return self.email.split('@')[0]
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    phone = models.CharField(_("Phone Number"), max_length=20)
    address = models.TextField(_("Address"))
    city = models.CharField(_("City"), max_length=100)
    zip_code = models.CharField(_("ZIP Code"), max_length=20)
    country = models.CharField(_("Country"), max_length=100)

    # Optional location fields for proximity features
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_consent = models.BooleanField(default=False, help_text="User consented to store approximate location")
    location_updated_at = models.DateTimeField(null=True, blank=True)

    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='profiles'
    )

    is_writer = models.BooleanField(default=False, verbose_name="Writer")
    
    # Language preference for mobile app
    preferred_language = models.CharField(
        _("Preferred Language"),
        max_length=7,
        choices=settings.LANGUAGES,
        default='en',
        help_text="User's preferred language for the mobile app"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.user.email}"


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
