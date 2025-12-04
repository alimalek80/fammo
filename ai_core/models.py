from django.db import models


class NutritionPredictionLog(models.Model):
    """
    Log of nutrition prediction API calls for training data collection.
    
    Stores both the input pet profile and the AI-generated output
    as JSON snapshots, along with key metadata fields for filtering
    and analysis.
    
    This model is self-contained and does not reference other Django models
    (no FKs to Pet or Profile). All data is captured in JSON payloads.
    """
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    source = models.CharField(
        max_length=50,
        default="api",
        help_text="Source of the prediction request (e.g., 'mobile', 'web', 'api')"
    )
    backend = models.CharField(
        max_length=50,
        default="openai",
        db_index=True,
        help_text="AI backend used (e.g., 'openai', 'proprietary', 'mock')"
    )
    model_version = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Version of the AI model that generated the prediction"
    )
    
    # Key pet metadata for quick filtering (denormalized from input_payload)
    species = models.CharField(max_length=20, db_index=True)
    life_stage = models.CharField(max_length=20, blank=True, db_index=True)
    breed_size_category = models.CharField(max_length=20, blank=True)
    health_goal = models.CharField(max_length=50, blank=True, db_index=True)
    weight_kg = models.FloatField(null=True, blank=True)
    age_years = models.FloatField(null=True, blank=True)
    body_condition_score = models.IntegerField(null=True, blank=True)
    
    # Full payload snapshots
    input_payload = models.JSONField(
        help_text="Complete validated pet profile input as JSON"
    )
    output_payload = models.JSONField(
        help_text="Complete AI prediction output as JSON"
    )
    
    # Optional annotation field for future labeling/training
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes for manual annotation or quality assessment"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Nutrition Prediction Log"
        verbose_name_plural = "Nutrition Prediction Logs"
        indexes = [
            models.Index(fields=['-created_at', 'species']),
            models.Index(fields=['backend', 'model_version']),
        ]
    
    def __str__(self):
        return f"{self.species} {self.health_goal} {self.created_at:%Y-%m-%d %H:%M}"
