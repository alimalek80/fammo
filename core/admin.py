from django.contrib import admin
from .models import HeroSection, SocialLinks, FAQ, ContactMessage
from modeltranslation.admin import TranslationAdmin

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
