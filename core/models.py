from django.db import models
from django.utils.crypto import get_random_string
from django.conf import settings

# Import legal document models
from .legal_models import (
    LegalDocument,
    DocumentType,
    UserConsent,
    ClinicConsent,
    ConsentLog,
)

# Create your models here.

class HeroSection(models.Model):
    """Model to store the content for the homepage hero section."""
    heading = models.CharField(max_length=200, help_text="The main title, e.g., 'Healthy Meals, Happy Pets!'")
    subheading = models.TextField(help_text="The paragraph text below the main title.")
    subheading_secondary = models.CharField(max_length=200, blank=True, help_text="An extra line under the main subheading, e.g., in red.")
    button_text = models.CharField(max_length=50, help_text="The text for the call-to-action button.")
    button_url = models.CharField(max_length=200, help_text="The URL the button links to. Can be a full URL or a Django URL name like '/pets/create/'.")
    background_image = models.ImageField(upload_to='hero_backgrounds/', help_text="Background image. Recommended size: 1920x1080px.")
    is_active = models.BooleanField(default=True, help_text="Only one hero section can be active at a time.")

    def save(self, *args, **kwargs):
        # Ensure only one instance is active
        if self.is_active:
            HeroSection.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Homepage Hero Section - {self.heading}"

    class Meta:
        verbose_name = "Homepage Hero Section"
        verbose_name_plural = "Homepage Hero Sections"

class Lead(models.Model):
    PET_TYPES = (("cat","Cat"),("dog","Dog"))
    uuid = models.CharField(max_length=22, unique=True)
    pet_type = models.CharField(max_length=10, choices=PET_TYPES)
    weight = models.DecimalField(max_digits=5, decimal_places=1)
    email = models.EmailField()
    source = models.CharField(max_length=50, blank=True, default="instagram")
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = get_random_string(22)
        super().save(*args, **kwargs)

    def __str__(self): 
        return f"{self.email} • {self.pet_type} • {self.weight}kg"

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ["-created_at"]

class SocialLinks(models.Model):
    instagram = models.URLField(blank=True, null=True)
    x = models.URLField("X (Twitter)", blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Social Links"
        verbose_name_plural = "Social Links"

    def __str__(self):
        return "Social Media Links"


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    sort_order = models.PositiveIntegerField(default=0, help_text="Lower appears first")
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-updated_at"]

    def __str__(self):
        return self.question

class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=180, blank=True)
    message = models.TextField()
    consent = models.BooleanField(default=False, help_text="User consented to be contacted")
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject or 'No subject'}"


class OnboardingSlide(models.Model):
    """Model for app onboarding slides with multilanguage support."""
    title = models.CharField(max_length=200, help_text="Slide title")
    description = models.TextField(help_text="Slide description text")
    icon = models.ImageField(upload_to='onboarding_icons/', help_text="Icon/image for the slide. Recommended size: 200x200px.")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Show this slide in the app")
    button_text = models.CharField(max_length=50, default="Next", help_text="Button text for this slide")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Onboarding Slide"
        verbose_name_plural = "Onboarding Slides"

    def __str__(self):
        return f"{self.order}. {self.title}"


class NotificationType(models.TextChoices):
    """Types of notifications that can be sent to users"""
    # Appointment related
    APPOINTMENT_CONFIRMED = 'APPOINTMENT_CONFIRMED', 'Appointment Confirmed'
    APPOINTMENT_CANCELLED = 'APPOINTMENT_CANCELLED', 'Appointment Cancelled'
    APPOINTMENT_REMINDER = 'APPOINTMENT_REMINDER', 'Appointment Reminder'
    NEW_APPOINTMENT = 'NEW_APPOINTMENT', 'New Appointment'
    
    # Account related
    EMAIL_CONFIRMATION = 'EMAIL_CONFIRMATION', 'Email Confirmation Needed'
    ACCOUNT_VERIFIED = 'ACCOUNT_VERIFIED', 'Account Verified'
    
    # System messages
    ADMIN_MESSAGE = 'ADMIN_MESSAGE', 'Message from Admin'
    SYSTEM = 'SYSTEM', 'System Notification'
    
    # Pet related
    PET_REMINDER = 'PET_REMINDER', 'Pet Care Reminder'
    
    # Referral related
    NEW_REFERRAL = 'NEW_REFERRAL', 'New Referral'


class UserNotification(models.Model):
    """
    Universal notifications for all users (both regular users and clinic owners).
    This is the central notification system for the platform.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional link to related objects
    link = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL to redirect when notification is clicked"
    )
    
    # For admin messages, track who sent it
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        help_text="Admin who sent this notification (for admin messages)"
    )
    
    # Read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Priority for sorting
    is_important = models.BooleanField(
        default=False,
        help_text="Important notifications appear at the top"
    )
    
    # Action required flag
    action_required = models.BooleanField(
        default=False,
        help_text="Notification requires user action"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_important', '-created_at']
        verbose_name = "User Notification"
        verbose_name_plural = "User Notifications"
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, 
                          link='', is_important=False, action_required=False,
                          sent_by=None):
        """Helper method to create notifications"""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            is_important=is_important,
            action_required=action_required,
            sent_by=sent_by
        )
    
    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for a user"""
        return cls.objects.filter(user=user, is_read=False).count()
