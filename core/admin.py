from django.contrib import admin
from .models import HeroSection, SocialLinks, FAQ

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ("heading", "is_active")
    list_editable = ("is_active",)
    search_fields = ("heading", "subheading")

@admin.register(SocialLinks)
class SocialLinksAdmin(admin.ModelAdmin):
    list_display = ("instagram", "x", "facebook", "linkedin")

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "is_published", "sort_order", "updated_at")
    list_editable = ("is_published", "sort_order")
    search_fields = ("question", "answer")
    ordering = ("sort_order", "-updated_at")
