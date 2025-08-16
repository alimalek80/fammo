from django.contrib import admin
from .models import SubscriptionPlan, AIUsage
from markdownx.admin import MarkdownxModelAdmin

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(MarkdownxModelAdmin):
    list_display = ('name', 'monthly_meal_limit', 'monthly_health_limit', 'price_eur')
    fields = ('name', 'price_eur', 'monthly_meal_limit', 'monthly_health_limit', 'description')
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'meal_used', 'health_used')
    list_filter = ('month', 'user')
    search_fields = ('user__email',)
