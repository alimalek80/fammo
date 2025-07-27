from django.contrib import admin
from .models import AIRecommendation, AIHealthReport

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('pet', 'type', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('pet__name', 'content')

@admin.register(AIHealthReport)
class AIHealthReportAdmin(admin.ModelAdmin):
    list_display = ('pet', 'created_at')
    search_fields = ('pet__name', 'summary')
