from __future__ import annotations
from django.db import models
import secrets
import string

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

# ---------- helpers ----------
def _rand_suffix(n: int = 5) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))

def _gen_ref_code(prefix: str = "vet") -> str:
    # e.g. vet-a1b2c
    return f"{prefix}-{_rand_suffix(5)}"

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ---------- core models ----------
class Clinic(TimeStampedModel):
    """
    A veterinarian or clinic with a public page on FAMMO.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_clinics",
        help_text="Account that manages this clinic page.",
    )
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=190, unique=True, blank=True)
    city = models.CharField(max_length=80, blank=True)
    address = models.CharField(max_length=220, blank=True)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Latitude coordinate for location"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Longitude coordinate for location"
    )
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=120, blank=True, help_text="Handle or URL")
    specializations = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated (e.g., Cats, Dogs, Nutrition)",
    )
    working_hours = models.CharField(
        max_length=160, blank=True, help_text="e.g., Mon–Sat 09:00–18:00"
    )
    bio = models.TextField(blank=True)
    logo = models.ImageField(upload_to="clinic_logos/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Email confirmation and approval fields
    email_confirmed = models.BooleanField(default=False, help_text="Email address has been confirmed")
    admin_approved = models.BooleanField(default=False, help_text="Approved by admin for public listing")
    email_confirmation_token = models.CharField(max_length=100, blank=True)
    email_confirmation_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Expression of Interest (EOI) for pilot program
    clinic_eoi = models.BooleanField(
        default=False,
        help_text="Indicates whether the clinic has expressed interest in participating in FAMMO's pilot program."
    )
    
    @property
    def is_active_clinic(self):
        """Clinic is active only if both email confirmed and admin approved"""
        return self.email_confirmed and self.admin_approved
    
    def get_formatted_working_hours(self):
        """Return formatted working hours for display"""
        hours_list = []
        schedule = self.working_hours_schedule.all().order_by('day_of_week')
        
        for hours in schedule:
            day_name = hours.get_day_of_week_display()
            if hours.is_closed:
                hours_list.append(f"{day_name}: Closed")
            elif hours.open_time and hours.close_time:
                hours_list.append(f"{day_name}: {hours.open_time.strftime('%H:%M')} - {hours.close_time.strftime('%H:%M')}")
            else:
                hours_list.append(f"{day_name}: Not set")
        
        return hours_list if hours_list else ["Working hours not set"]

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        # auto-generate a unique slug
        if not self.slug:
            base = slugify(self.name) or "clinic"
            slug_candidate = base
            i = 1
            while Clinic.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                i += 1
                slug_candidate = f"{base}-{i}"
            self.slug = slug_candidate
        
        # Check if we need to trigger geocoding (but don't do it here - do it after save)
        should_geocode = False
        
        if self.pk:
            try:
                existing = Clinic.objects.get(pk=self.pk)
                
                # Normalize for comparison (lowercase, stripped)
                old_addr = (existing.address or "").strip().lower()
                new_addr = (self.address or "").strip().lower()
                old_city = (existing.city or "").strip().lower()
                new_city = (self.city or "").strip().lower()
                
                # Check if anything changed
                if old_addr != new_addr or old_city != new_city:
                    logger.info(f"[CLINIC SAVE] Address/City changed for '{self.name}'")
                    logger.info(f"  OLD: {existing.address} | {existing.city}")
                    logger.info(f"  NEW: {self.address} | {self.city}")
                    
                    # Don't reset coordinates here - let geocoding task handle it
                    should_geocode = True
                    
            except Clinic.DoesNotExist:
                # New clinic
                pass
        
        # Check if coordinates are missing but address exists (also trigger geocoding)
        if not should_geocode and ((not self.latitude or not self.longitude) and (self.address or self.city)):
            should_geocode = True
        
        # Save the clinic first (don't block on geocoding)
        super().save(*args, **kwargs)
        
        # NOW trigger async geocoding if needed (non-blocking after save)
        if should_geocode:
            from .tasks import geocode_clinic_async
            try:
                # Try to use Celery if available
                geocode_clinic_async.delay(self.id)
                logger.info(f"[CLINIC SAVE] Scheduled async geocoding for clinic {self.id}")
            except Exception as e:
                # Fallback: try to geocode synchronously but with timeout protection
                logger.info(f"[CLINIC SAVE] Celery not available, attempting sync geocoding for clinic {self.id}")
                try:
                    from .utils import geocode_address
                    coords = geocode_address(self.address, self.city)
                    if coords:
                        # Update clinic with coordinates
                        self.latitude = coords['latitude']
                        self.longitude = coords['longitude']
                        # Save directly without triggering save() again
                        super().save(*args, **kwargs)
                        logger.info(f"[CLINIC SAVE] ✅ Geocoding complete: {self.latitude}, {self.longitude}")
                    else:
                        logger.warning(f"[CLINIC SAVE] ⚠️ Geocoding failed for clinic {self.id}")
                except Exception as geocode_error:
                    # Don't let geocoding errors crash the save
                    logger.error(f"[CLINIC SAVE] Geocoding error: {str(geocode_error)}", exc_info=True)

    def get_absolute_url(self):
        return reverse("vets:clinic_detail", kwargs={"slug": self.slug})
    
    def send_confirmation_email(self):
        """Send email confirmation link to clinic owner"""
        import uuid
        from django.core.mail import send_mail
        from django.conf import settings
        from django.utils import timezone
        
        # Generate token
        self.email_confirmation_token = str(uuid.uuid4())
        self.email_confirmation_sent_at = timezone.now()
        self.save(update_fields=['email_confirmation_token', 'email_confirmation_sent_at'])
        
        # Build confirmation URL
        confirmation_url = f"{settings.SITE_URL}/api/v1/clinics/confirm-email/{self.email_confirmation_token}/"
        
        # Send email
        subject = "Confirm your FAMMO Clinic Email"
        message = f"""
Hello {self.owner.get_full_name() or self.owner.username},

Thank you for registering your clinic "{self.name}" with FAMMO.

Please confirm your email address by clicking the link below:
{confirmation_url}

Once your email is confirmed, your clinic will be submitted for admin approval.

Best regards,
The FAMMO Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email or self.owner.email],
            fail_silently=False,
        )

    @property
    def active_referral_code(self) -> str | None:
        """Return referral code if clinic has confirmed email (even if not admin approved)"""
        if not self.email_confirmed:
            return None
        code = self.referral_codes.filter(is_active=True).order_by("created_at").first()
        return code.code if code else None


class VetProfile(TimeStampedModel):
    """
    Optional: lead veterinarian details tied to a Clinic.
    Keep if you want a person profile distinct from the clinic brand.
    """
    clinic = models.OneToOneField(Clinic, on_delete=models.CASCADE, related_name="vet_profile")
    vet_name = models.CharField(max_length=120)
    degrees = models.CharField(max_length=200, blank=True, help_text="e.g., DVM, MSc Nutrition")
    certifications = models.CharField(max_length=240, blank=True)

    def __str__(self) -> str:
        return f"{self.vet_name} @ {self.clinic.name}"


class ReferralCode(TimeStampedModel):
    """
    Unique referral code for a clinic. Used in signup URLs: /signup/?ref=<code>
    """
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="referral_codes")
    code = models.SlugField(max_length=40, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["code"])]

    def __str__(self) -> str:
        return f"{self.code} → {self.clinic.name}"

    @staticmethod
    def create_default_for_clinic(clinic: Clinic) -> "ReferralCode":
        """
        Create a readable, unique code based on clinic slug; fall back to random.
        """
        if clinic.slug:
            base = clinic.slug.replace("-", "")[:10]
            candidate = f"vet-{base or _rand_suffix(4)}"
        else:
            candidate = _gen_ref_code()
        # ensure uniqueness
        while ReferralCode.objects.filter(code=candidate).exists():
            candidate = _gen_ref_code()
        return ReferralCode.objects.create(clinic=clinic, code=candidate, is_active=True)


class WorkingHours(models.Model):
    """
    Structured working hours for each day of the week
    """
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="working_hours_schedule")
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    is_closed = models.BooleanField(default=False, help_text="Clinic is closed on this day")
    open_time = models.TimeField(null=True, blank=True, help_text="Opening time")
    close_time = models.TimeField(null=True, blank=True, help_text="Closing time")
    
    class Meta:
        ordering = ['day_of_week']
        unique_together = ['clinic', 'day_of_week']
        verbose_name_plural = "Working hours"
    
    def __str__(self):
        day_name = self.get_day_of_week_display()
        if self.is_closed:
            return f"{day_name}: Closed"
        elif self.open_time and self.close_time:
            return f"{day_name}: {self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')}"
        return f"{day_name}: Not set"


class ReferralStatus(models.TextChoices):
    NEW = "NEW", "New"
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class ReferredUser(TimeStampedModel):
    """
    Tracks users who arrive via a clinic's referral link.
    If signup hasn't completed yet, keep email_capture until the account is created.
    """
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="referred_users")
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clinic_referrals",
    )
    email_capture = models.EmailField(blank=True)
    status = models.CharField(max_length=10, choices=ReferralStatus.choices, default=ReferralStatus.NEW)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["clinic", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        who = getattr(self.user, "email", None) if self.user_id else (self.email_capture or "anonymous")
        return f"{who} via {self.clinic.name} ({self.status})"


class AppointmentReason(models.Model):
    """
    Predefined appointment reasons/types for better categorization
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Controls display order")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Appointment Reason"
        verbose_name_plural = "Appointment Reasons"
    
    def __str__(self):
        return self.name


class AppointmentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    CANCELLED_BY_USER = "CANCELLED_USER", "Cancelled by User"
    CANCELLED_BY_CLINIC = "CANCELLED_CLINIC", "Cancelled by Clinic"
    COMPLETED = "COMPLETED", "Completed"
    NO_SHOW = "NO_SHOW", "No Show"


class Appointment(TimeStampedModel):
    """
    Appointment booking for a user's pet at a clinic
    """
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text="The clinic where the appointment is booked"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text="The user who booked the appointment"
    )
    pet = models.ForeignKey(
        'pet.Pet',
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text="The pet for this appointment"
    )
    
    # Date and time
    appointment_date = models.DateField(
        db_index=True,
        help_text="The date of the appointment"
    )
    appointment_time = models.TimeField(
        help_text="The time of the appointment"
    )
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Expected duration in minutes"
    )
    
    # Appointment details
    reason = models.ForeignKey(
        AppointmentReason,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
        help_text="Predefined reason for the appointment"
    )
    reason_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom reason or additional details"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes from the user"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        db_index=True
    )
    
    # Confirmation and notification tracking
    clinic_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the clinic was notified"
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the clinic confirmed the appointment"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the appointment was cancelled"
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Reason for cancellation"
    )
    
    # Reference code for easy lookup
    reference_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Unique reference code for the appointment"
    )
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['clinic', 'appointment_date']),
            models.Index(fields=['user', 'appointment_date']),
            models.Index(fields=['status', 'appointment_date']),
        ]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
    
    def __str__(self):
        return f"{self.pet.name} @ {self.clinic.name} on {self.appointment_date} at {self.appointment_time}"
    
    def save(self, *args, **kwargs):
        # Generate reference code if not set
        if not self.reference_code:
            self.reference_code = self._generate_reference_code()
        super().save(*args, **kwargs)
    
    def _generate_reference_code(self):
        """Generate a unique reference code"""
        import secrets
        import string
        prefix = "APT"
        suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        code = f"{prefix}-{suffix}"
        # Ensure uniqueness
        while Appointment.objects.filter(reference_code=code).exists():
            suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            code = f"{prefix}-{suffix}"
        return code
    
    @property
    def is_upcoming(self):
        """Check if appointment is in the future"""
        from django.utils import timezone
        from datetime import datetime
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return timezone.make_aware(appointment_datetime) > timezone.now()
    
    @property
    def can_cancel(self):
        """Check if appointment can be cancelled (at least 24 hours before)"""
        from django.utils import timezone
        from datetime import datetime, timedelta
        if self.status in [AppointmentStatus.CANCELLED_BY_USER, 
                          AppointmentStatus.CANCELLED_BY_CLINIC,
                          AppointmentStatus.COMPLETED,
                          AppointmentStatus.NO_SHOW]:
            return False
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        return timezone.make_aware(appointment_datetime) > timezone.now() + timedelta(hours=24)


class ClinicNotification(TimeStampedModel):
    """
    Notifications for clinic owners/managers
    """
    NOTIFICATION_TYPES = [
        ('NEW_APPOINTMENT', 'New Appointment'),
        ('CANCELLED_APPOINTMENT', 'Cancelled Appointment'),
        ('APPOINTMENT_REMINDER', 'Appointment Reminder'),
        ('REFERRAL', 'New Referral'),
        ('SYSTEM', 'System Notification'),
    ]
    
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional link to related appointment
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    
    # Read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Clinic Notification"
        verbose_name_plural = "Clinic Notifications"
    
    def __str__(self):
        return f"{self.title} - {self.clinic.name}"
    
    def mark_as_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
