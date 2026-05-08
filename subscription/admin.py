from django.contrib import admin
from .models import SubscriptionPlan, AIUsage, SubscriptionTransaction
from markdownx.admin import MarkdownxModelAdmin

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(MarkdownxModelAdmin):
    list_display = ('name', 'monthly_meal_limit', 'monthly_health_limit', 'price_eur', 'unlimited_meals', 'unlimited_health')
    fields = ('name', 'price_eur', 'monthly_meal_limit', 'unlimited_meals', 'monthly_health_limit', 'unlimited_health', 'description')
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'meal_used', 'health_used')
    list_filter = ('month', 'user')
    search_fields = ('user__email',)

@admin.register(SubscriptionTransaction)
class SubscriptionTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'status', 'card_last4', 'created_at')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('user__email', 'gateway_transaction_id')
    readonly_fields = ('user', 'plan', 'amount', 'card_last4', 'gateway_transaction_id', 'created_at')
    ordering = ('-created_at',)
