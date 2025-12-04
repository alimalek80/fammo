from django.contrib import admin
from .models import NutritionPredictionLog


@admin.register(NutritionPredictionLog)
class NutritionPredictionLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing and analyzing nutrition prediction logs.
    
    Provides filtering, searching, and detailed view of prediction data
    for training data collection and quality assessment.
    """
    
    list_display = [
        'created_at',
        'species',
        'health_goal',
        'backend',
        'model_version',
        'source',
        'body_condition_score',
        'weight_kg',
    ]
    
    list_filter = [
        'species',
        'backend',
        'health_goal',
        'model_version',
        'source',
        'life_stage',
        'body_condition_score',
    ]
    
    search_fields = [
        'health_goal',
        'notes',
        'model_version',
    ]
    
    readonly_fields = [
        'created_at',
        'source',
        'backend',
        'model_version',
        'species',
        'life_stage',
        'breed_size_category',
        'health_goal',
        'weight_kg',
        'age_years',
        'body_condition_score',
        'input_payload',
        'output_payload',
    ]
    
    fieldsets = (
        ('Metadata', {
            'fields': ('created_at', 'source', 'backend', 'model_version')
        }),
        ('Pet Profile Summary', {
            'fields': (
                'species',
                'life_stage',
                'breed_size_category',
                'health_goal',
                'weight_kg',
                'age_years',
                'body_condition_score',
            )
        }),
        ('Full Payloads', {
            'fields': ('input_payload', 'output_payload'),
            'classes': ('collapse',),
        }),
        ('Notes', {
            'fields': ('notes',),
        }),
    )
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Prevent manual creation - logs are auto-generated."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for data management."""
        return request.user.is_superuser
