from django.contrib import admin
from .models import (
    HeroSection, SocialLinks, FAQ, ContactMessage, Lead, OnboardingSlide,
    LegalDocument, UserConsent, ClinicConsent, ConsentLog
)
from modeltranslation.admin import TranslationAdmin

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('email', 'pet_type', 'weight', 'source', 'created_at', 'processed')
    list_filter = ('pet_type', 'source', 'processed', 'created_at')
    search_fields = ('email', 'uuid')
    readonly_fields = ('uuid', 'created_at')

@admin.register(HeroSection)
class HeroSectionAdmin(TranslationAdmin):
    list_display = ("heading", "is_active")
    list_editable = ("is_active",)
    search_fields = ("heading", "subheading")

@admin.register(SocialLinks)
class SocialLinksAdmin(admin.ModelAdmin):
    list_display = ("instagram", "x", "facebook", "linkedin")

@admin.register(FAQ)
class FAQAdmin(TranslationAdmin):
    list_display = ("question", "is_published", "sort_order", "updated_at")
    list_editable = ("is_published", "sort_order")
    search_fields = ("question", "answer")
    ordering = ("sort_order", "-updated_at")

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_resolved", "created_at")
    list_filter = ("is_resolved", "created_at")
    search_fields = ("name", "email", "subject", "message")

@admin.register(OnboardingSlide)
class OnboardingSlidAdmin(TranslationAdmin):
    list_display = ("order", "title", "is_active", "updated_at")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    ordering = ("order",)


# ============================================
# Legal Document Admin
# ============================================

@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'doc_type', 'language', 'version', 'is_active', 'effective_date', 'updated_at')
    list_filter = ('doc_type', 'language', 'is_active', 'effective_date')
    search_fields = ('title', 'content', 'admin_notes')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Document Type', {
            'fields': ('doc_type', 'language', 'title', 'version')
        }),
        ('Content', {
            'fields': ('content', 'summary'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active', 'effective_date')
        }),
        ('Administration', {
            'fields': ('admin_notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-effective_date',)


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'accepted', 'accepted_at')
    list_filter = ('accepted', 'accepted_at', 'document__doc_type')
    search_fields = ('user__email', 'document__title')
    readonly_fields = ('user', 'document', 'accepted_at', 'ip_address', 'user_agent')
    
    fieldsets = (
        ('Consent Info', {
            'fields': ('user', 'document', 'accepted', 'accepted_at')
        }),
        ('Audit Trail', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    can_delete = False
    ordering = ('-accepted_at',)


@admin.register(ClinicConsent)
class ClinicConsentAdmin(admin.ModelAdmin):
    list_display = ('clinic_email', 'document', 'accepted', 'accepted_at')
    list_filter = ('accepted', 'accepted_at', 'document__doc_type')
    search_fields = ('clinic_email', 'document__title', 'user__email')
    readonly_fields = ('user', 'clinic_email', 'document', 'accepted_at', 'ip_address', 'user_agent')
    
    fieldsets = (
        ('Consent Info', {
            'fields': ('user', 'clinic_email', 'document', 'accepted', 'accepted_at')
        }),
        ('Audit Trail', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    can_delete = False
    ordering = ('-accepted_at',)


@admin.register(ConsentLog)
class ConsentLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'document', 'user', 'timestamp', 'admin_user')
    list_filter = ('action', 'timestamp', 'document__doc_type')
    search_fields = ('document__title', 'user__email', 'details', 'admin_user__email')
    readonly_fields = ('timestamp', 'document', 'user', 'admin_user')
    
    fieldsets = (
        ('Action', {
            'fields': ('action', 'timestamp')
        }),
        ('References', {
            'fields': ('document', 'user', 'admin_user')
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('wide',)
        }),
    )
    
    can_delete = False
    ordering = ('-timestamp',)

