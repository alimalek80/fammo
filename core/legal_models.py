"""
Legal Documents and Consent Models for User and Clinic Registration

This module contains models for managing:
1. Terms of Service and Conditions
2. Privacy Policies
3. Partnership Agreements
4. User and Clinic Consent Tracking
5. Expression of Interest (EOI) Terms

These models allow backend admins to:
- Create/edit legal documents via API
- Track version history
- Monitor user/clinic acceptance
- Generate audit reports
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class DocumentType(models.TextChoices):
    """Types of legal documents"""
    USER_TERMS_CONDITIONS = 'user_terms', _('User Terms and Conditions')
    USER_PRIVACY_POLICY = 'user_privacy', _('User Privacy Policy')
    CLINIC_TERMS_CONDITIONS = 'clinic_terms', _('Clinic Terms and Conditions')
    CLINIC_PARTNERSHIP = 'clinic_partnership', _('Clinic Partnership Agreement')
    CLINIC_EOI = 'clinic_eoi', _('Expression of Interest (EOI) Terms')


class LegalDocument(models.Model):
    """
    Stores legal documents (Terms, Privacy Policy, Agreements, etc.)
    Supports versioning and multi-language content.
    """
    doc_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        help_text="Type of legal document"
    )
    
    # Content in multiple languages
    language = models.CharField(
        max_length=10,
        default='en',
        help_text="Language code (e.g., 'en', 'fi', 'nl', 'tr')"
    )
    
    # Document metadata
    title = models.CharField(
        max_length=255,
        help_text="Document title (e.g., 'Terms and Conditions v2.0')"
    )
    version = models.CharField(
        max_length=20,
        help_text="Version identifier (e.g., '1.0', '2.1', 'v2021-11-01')"
    )
    
    # Document content
    content = models.TextField(
        help_text="Full legal document content (HTML allowed)"
    )
    
    # Metadata
    summary = models.TextField(
        blank=True,
        help_text="Brief summary of document (optional)"
    )
    
    # Status and dates
    is_active = models.BooleanField(
        default=True,
        help_text="Is this the active version? Only one version per doc_type/language should be active"
    )
    effective_date = models.DateTimeField(
        default=timezone.now,
        help_text="When this version becomes effective"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes about changes"
    )
    
    class Meta:
        verbose_name = "Legal Document"
        verbose_name_plural = "Legal Documents"
        # Ensure only one active version per doc type and language
        unique_together = ('doc_type', 'language', 'is_active')
        indexes = [
            models.Index(fields=['doc_type', 'language', 'is_active']),
            models.Index(fields=['doc_type', 'effective_date']),
        ]
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.get_doc_type_display()} ({self.language}) v{self.version}"


class UserConsent(models.Model):
    """
    Tracks when users accept Terms and Privacy Policy during registration.
    Provides audit trail for compliance.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='legal_consents'
    )
    
    # Document reference
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.PROTECT,
        help_text="The legal document accepted"
    )
    
    # Consent details
    accepted = models.BooleanField(
        default=True,
        help_text="Whether user accepted (true) or revoked (false)"
    )
    
    # Metadata
    accepted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When consent was given"
    )
    
    # Optional: track IP and user agent for security audit
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address when consent was given"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent (browser info) when consent was given"
    )
    
    class Meta:
        verbose_name = "User Consent"
        verbose_name_plural = "User Consents"
        unique_together = ('user', 'document')
        indexes = [
            models.Index(fields=['user', 'accepted_at']),
            models.Index(fields=['document', 'accepted_at']),
        ]
        ordering = ['-accepted_at']
    
    def __str__(self):
        status = "Accepted" if self.accepted else "Revoked"
        return f"{self.user.email} - {self.document.get_doc_type_display()} - {status}"


class ClinicConsent(models.Model):
    """
    Tracks when clinics accept Terms, Partnership Agreement, and EOI during registration.
    Similar to UserConsent but for clinic accounts.
    """
    # Clinic reference - can be stored as user who owns clinic or direct clinic reference
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clinic_legal_consents'
    )
    
    clinic_email = models.EmailField(
        help_text="Email of clinic being registered (for audit trail)"
    )
    
    # Document reference
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.PROTECT,
        help_text="The legal document accepted"
    )
    
    # Consent details
    accepted = models.BooleanField(
        default=True,
        help_text="Whether clinic accepted (true) or revoked (false)"
    )
    
    # Metadata
    accepted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When consent was given"
    )
    
    # Optional: track IP and user agent
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address when consent was given"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent (browser info) when consent was given"
    )
    
    class Meta:
        verbose_name = "Clinic Consent"
        verbose_name_plural = "Clinic Consents"
        unique_together = ('user', 'document', 'clinic_email')
        indexes = [
            models.Index(fields=['user', 'accepted_at']),
            models.Index(fields=['document', 'accepted_at']),
            models.Index(fields=['clinic_email', 'accepted_at']),
        ]
        ordering = ['-accepted_at']
    
    def __str__(self):
        status = "Accepted" if self.accepted else "Revoked"
        return f"{self.clinic_email} - {self.document.get_doc_type_display()} - {status}"


class ConsentLog(models.Model):
    """
    Audit log for all consent-related activities (acceptance, updates, revocations).
    Provides detailed compliance tracking.
    """
    ACTION_CHOICES = [
        ('created', 'Document Created'),
        ('updated', 'Document Updated'),
        ('accepted', 'Consent Accepted'),
        ('revoked', 'Consent Revoked'),
        ('reminded', 'User Reminded'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Document reference
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.CASCADE,
        related_name='consent_logs'
    )
    
    # User reference (can be null for document creation by admin)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Details
    details = models.TextField(
        blank=True,
        help_text="Additional information about the action"
    )
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Admin info (who made the change)
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consent_log_actions'
    )
    
    class Meta:
        verbose_name = "Consent Log"
        verbose_name_plural = "Consent Logs"
        indexes = [
            models.Index(fields=['document', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.document} - {self.timestamp}"
