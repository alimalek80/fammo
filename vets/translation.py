"""
Multi-language translation configuration for Vets/Clinic models.

Uses django-modeltranslation to provide translated fields for:
- AppointmentReason (name, description)
- WorkingHours (day name display via choices - handled separately)

Note: ClinicNotification and Appointment have dynamic content (titles/messages)
that are generated in code, so they use gettext_lazy for translation.
The Clinic model contains user-generated content that doesn't need translation.
"""

from modeltranslation.translator import register, TranslationOptions
from .models import AppointmentReason


@register(AppointmentReason)
class AppointmentReasonTranslationOptions(TranslationOptions):
    """Translatable fields for AppointmentReason (e.g., General Checkup, Vaccination)"""
    fields = ('name', 'description',)
