from django.contrib import admin
from .models import (
    Clinic, VetProfile, ReferralCode, ReferredUser, ReferralStatus, WorkingHours,
    Appointment, AppointmentReason, AppointmentStatus, ClinicNotification
)


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 0
    ordering = ['day_of_week']
    fields = ['day_of_week', 'is_closed', 'open_time', 'close_time']


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = (
        "name", "city", "address", "owner", "email_status", "admin_status", 
        "public_status", "eoi_status", "latitude", "longitude", "created_at"
    )
    list_filter = (
        "email_confirmed", "admin_approved", "is_verified", "clinic_eoi",
        "city", "created_at"
    )
    search_fields = (
        "name", "city", "address", "email", 
        "owner__email", "owner__first_name", "owner__last_name"
    )
    readonly_fields = (
        "created_at", "updated_at", "slug", 
        "email_confirmation_token", "email_confirmation_sent_at"
    )
    prepopulated_fields = {}
    ordering = ("name",)
    inlines = [WorkingHoursInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'city', 'address', 'latitude', 'longitude', 'phone', 'email', 'website')
        }),
        ('Social & Professional', {
            'fields': ('instagram', 'specializations', 'working_hours', 'bio', 'logo')
        }),
        ('Owner & Management', {
            'fields': ('owner',)
        }),
        ('Verification Status', {
            'fields': ('email_confirmed', 'admin_approved', 'is_verified'),
            'description': 'Email confirmation is automatic. Admin approval and verification are manual.'
        }),
        ('Pilot Program Interest', {
            'fields': ('clinic_eoi',),
            'description': 'Expression of Interest for FAMMO pilot program'
        }),
        ('Email Confirmation Details', {
            'fields': ('email_confirmation_sent_at', 'email_confirmation_token'),
            'classes': ('collapse',),
            'description': 'Email confirmation tracking (automatic)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = [
        "mark_verified", "mark_unverified", "approve_clinics", 
        "disapprove_clinics", "create_or_refresh_referral_code", "report_nearby_users"
    ]

    def email_status(self, obj):
        if obj.email_confirmed:
            return "✅ Confirmed"
        else:
            return "❌ Pending"
    email_status.short_description = "Email Status"

    def admin_status(self, obj):
        if obj.admin_approved:
            return "✅ Approved"
        else:
            return "⏳ Pending"
    admin_status.short_description = "Admin Approval"

    def public_status(self, obj):
        if obj.email_confirmed and obj.admin_approved:
            return "🌐 Public + Verified"
        elif obj.email_confirmed:
            return "📋 Public (No Badge)"
        else:
            return "🔒 Hidden"
    public_status.short_description = "Public Listing"

    def eoi_status(self, obj):
        if obj.clinic_eoi:
            return "✅ Interested"
        else:
            return "➖ Not Indicated"
    eoi_status.short_description = "EOI (Pilot)"

    def save_model(self, request, obj, form, change):
        """
        Override save_model to ensure clinic.save() is always called,
        which triggers address change detection and auto-geocoding.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[ADMIN SAVE_MODEL] Saving clinic: {obj.name}, change={change}")
        if hasattr(form, 'changed_data'):
            logger.info(f"[ADMIN SAVE_MODEL] Changed fields: {form.changed_data}")
        logger.info(f"[ADMIN SAVE_MODEL] Current address: {obj.address}, city: {obj.city}")
        obj.save()
        logger.info(f"[ADMIN SAVE_MODEL] After save - lat: {obj.latitude}, lon: {obj.longitude}")

    @admin.action(description="Approve selected clinics (admin approval)")
    def approve_clinics(self, request, queryset):
        updated = 0
        for clinic in queryset:
            clinic.admin_approved = True
            clinic.save()
            updated += 1
        self.message_user(request, f"{updated} clinic(s) approved by admin.")

    @admin.action(description="Disapprove selected clinics")
    def disapprove_clinics(self, request, queryset):
        updated = queryset.update(admin_approved=False, is_verified=False)
        self.message_user(request, f"{updated} clinic(s) disapproved.")

    @admin.action(description="Mark selected clinics as Verified (public listing)")
    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} clinic(s) marked as verified.")

    @admin.action(description="Mark selected clinics as Unverified (hidden)")
    def mark_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} clinic(s) marked as unverified.")

    @admin.action(description="Create default referral code (if none) or refresh (add new active)")
    def create_or_refresh_referral_code(self, request, queryset):
        created = 0
        for clinic in queryset:
            # create a new active code (you may want to deactivate old ones)
            ReferralCode.create_default_for_clinic(clinic)
            created += 1
        self.message_user(request, f"Created new referral codes for {created} clinic(s).")

    @admin.action(description="Generate proximity user report for selected clinic (single)")
    def report_nearby_users(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one clinic to generate report", level='error')
            return
        clinic = queryset.first()
        from django.urls import reverse
        report_url = reverse('vets:clinic_nearby_users_report', kwargs={'clinic_id': clinic.id})
        self.message_user(request, f"Proximity report: {report_url}")


@admin.register(VetProfile)
class VetProfileAdmin(admin.ModelAdmin):
    list_display = ("vet_name", "clinic", "degrees")
    search_fields = ("vet_name", "clinic__name", "degrees", "certifications")


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "clinic", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("code", "clinic__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ReferredUser)
class ReferredUserAdmin(admin.ModelAdmin):
    list_display = ("__str__", "clinic", "status", "created_at")
    list_filter = ("status", "created_at", "clinic")
    search_fields = ("user__email", "email_capture", "clinic__name", "referral_code__code")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("clinic", "referral_code", "user")

    actions = ["mark_active", "mark_inactive"]

    @admin.action(description="Mark selected referrals as ACTIVE")
    def mark_active(self, request, queryset):
        updated = queryset.update(status=ReferralStatus.ACTIVE)
        self.message_user(request, f"{updated} referral(s) set to ACTIVE.")

    @admin.action(description="Mark selected referrals as INACTIVE")
    def mark_inactive(self, request, queryset):
        updated = queryset.update(status=ReferralStatus.INACTIVE)
        self.message_user(request, f"{updated} referral(s) set to INACTIVE.")


# ============================================================================
# APPOINTMENT ADMIN
# ============================================================================

@admin.register(AppointmentReason)
class AppointmentReasonAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("order", "name")
    list_editable = ("order", "is_active")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code", "pet_name", "clinic", "appointment_date", 
        "appointment_time", "status_badge", "user_email", "created_at"
    )
    list_filter = ("status", "appointment_date", "clinic", "created_at")
    search_fields = (
        "reference_code", "pet__name", "user__email", 
        "clinic__name", "reason_text"
    )
    readonly_fields = (
        "reference_code", "created_at", "updated_at", 
        "clinic_notified_at", "confirmed_at", "cancelled_at"
    )
    raw_id_fields = ("clinic", "user", "pet", "reason")
    date_hierarchy = "appointment_date"
    ordering = ("-appointment_date", "-appointment_time")
    
    fieldsets = (
        ('Appointment Info', {
            'fields': ('reference_code', 'clinic', 'user', 'pet', 'appointment_date', 'appointment_time', 'duration_minutes')
        }),
        ('Reason & Notes', {
            'fields': ('reason', 'reason_text', 'notes')
        }),
        ('Status', {
            'fields': ('status', 'confirmed_at', 'cancelled_at', 'cancellation_reason')
        }),
        ('Notifications', {
            'fields': ('clinic_notified_at',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ["confirm_appointments", "cancel_appointments", "mark_completed", "mark_no_show"]
    
    def pet_name(self, obj):
        return obj.pet.name
    pet_name.short_description = "Pet"
    pet_name.admin_order_field = "pet__name"
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User"
    user_email.admin_order_field = "user__email"
    
    def status_badge(self, obj):
        status_icons = {
            AppointmentStatus.PENDING: "⏳ Pending",
            AppointmentStatus.CONFIRMED: "✅ Confirmed",
            AppointmentStatus.CANCELLED_BY_USER: "❌ Cancelled (User)",
            AppointmentStatus.CANCELLED_BY_CLINIC: "❌ Cancelled (Clinic)",
            AppointmentStatus.COMPLETED: "✔️ Completed",
            AppointmentStatus.NO_SHOW: "🚫 No Show",
        }
        return status_icons.get(obj.status, obj.status)
    status_badge.short_description = "Status"
    
    @admin.action(description="Confirm selected appointments")
    def confirm_appointments(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for appointment in queryset.filter(status=AppointmentStatus.PENDING):
            appointment.status = AppointmentStatus.CONFIRMED
            appointment.confirmed_at = timezone.now()
            appointment.save()
            updated += 1
        self.message_user(request, f"{updated} appointment(s) confirmed.")
    
    @admin.action(description="Cancel selected appointments")
    def cancel_appointments(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for appointment in queryset.exclude(status__in=[
            AppointmentStatus.CANCELLED_BY_USER,
            AppointmentStatus.CANCELLED_BY_CLINIC,
            AppointmentStatus.COMPLETED
        ]):
            appointment.status = AppointmentStatus.CANCELLED_BY_CLINIC
            appointment.cancelled_at = timezone.now()
            appointment.cancellation_reason = "Cancelled by admin"
            appointment.save()
            updated += 1
        self.message_user(request, f"{updated} appointment(s) cancelled.")
    
    @admin.action(description="Mark selected as completed")
    def mark_completed(self, request, queryset):
        updated = queryset.filter(status=AppointmentStatus.CONFIRMED).update(
            status=AppointmentStatus.COMPLETED
        )
        self.message_user(request, f"{updated} appointment(s) marked as completed.")
    
    @admin.action(description="Mark selected as no-show")
    def mark_no_show(self, request, queryset):
        updated = queryset.filter(status=AppointmentStatus.CONFIRMED).update(
            status=AppointmentStatus.NO_SHOW
        )
        self.message_user(request, f"{updated} appointment(s) marked as no-show.")


@admin.register(ClinicNotification)
class ClinicNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "clinic", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "clinic", "created_at")
    search_fields = ("title", "message", "clinic__name")
    readonly_fields = ("created_at", "read_at")
    ordering = ("-created_at",)
    
    actions = ["mark_as_read", "mark_as_unread"]
    
    @admin.action(description="Mark selected as read")
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{updated} notification(s) marked as read.")
    
    @admin.action(description="Mark selected as unread")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{updated} notification(s) marked as unread.")
