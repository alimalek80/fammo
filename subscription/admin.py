from django.contrib import admin
from .models import SubscriptionPlan, AIUsage

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_meal_limit', 'monthly_health_limit', 'price_eur')
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(AIUsage)
class AIUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'meal_used', 'health_used')
    list_filter = ('month', 'user')
    search_fields = ('user__email',)
