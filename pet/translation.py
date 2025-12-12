"""
Multi-language translation configuration for Pet models.

Uses django-modeltranslation to provide translated fields for:
- PetType (name)
- Gender (name)
- AgeCategory (name)
- Breed (name)
- FoodType (name)
- FoodFeeling (name, description)
- FoodImportance (name)
- BodyType (name, description)
- ActivityLevel (name, description)
- FoodAllergy (name)
- HealthIssue (name)
- TreatFrequency (name, description)
"""

from modeltranslation.translator import register, TranslationOptions
from .models import (
    PetType,
    Gender,
    AgeCategory,
    Breed,
    FoodType,
    FoodFeeling,
    FoodImportance,
    BodyType,
    ActivityLevel,
    FoodAllergy,
    HealthIssue,
    TreatFrequency,
)


@register(PetType)
class PetTypeTranslationOptions(TranslationOptions):
    """Translatable fields for PetType (e.g., Dog, Cat)"""
    fields = ('name',)


@register(Gender)
class GenderTranslationOptions(TranslationOptions):
    """Translatable fields for Gender (e.g., Male, Female)"""
    fields = ('name',)


@register(AgeCategory)
class AgeCategoryTranslationOptions(TranslationOptions):
    """Translatable fields for AgeCategory (e.g., Puppy, Senior)"""
    fields = ('name',)


@register(Breed)
class BreedTranslationOptions(TranslationOptions):
    """Translatable fields for Breed"""
    fields = ('name',)


@register(FoodType)
class FoodTypeTranslationOptions(TranslationOptions):
    """Translatable fields for FoodType (e.g., Dry Food, Wet Food)"""
    fields = ('name',)


@register(FoodFeeling)
class FoodFeelingTranslationOptions(TranslationOptions):
    """Translatable fields for FoodFeeling (e.g., Loves it, Tolerates it)"""
    fields = ('name', 'description',)


@register(FoodImportance)
class FoodImportanceTranslationOptions(TranslationOptions):
    """Translatable fields for FoodImportance (e.g., Very Important, Not Important)"""
    fields = ('name',)


@register(BodyType)
class BodyTypeTranslationOptions(TranslationOptions):
    """Translatable fields for BodyType (e.g., Lean, Overweight)"""
    fields = ('name', 'description',)


@register(ActivityLevel)
class ActivityLevelTranslationOptions(TranslationOptions):
    """Translatable fields for ActivityLevel (e.g., Sedentary, Very Active)"""
    fields = ('name', 'description',)


@register(FoodAllergy)
class FoodAllergyTranslationOptions(TranslationOptions):
    """Translatable fields for FoodAllergy (e.g., Chicken, Dairy)"""
    fields = ('name',)


@register(HealthIssue)
class HealthIssueTranslationOptions(TranslationOptions):
    """Translatable fields for HealthIssue (e.g., Allergies, Diabetes)"""
    fields = ('name',)


@register(TreatFrequency)
class TreatFrequencyTranslationOptions(TranslationOptions):
    """Translatable fields for TreatFrequency (e.g., Daily, Weekly)"""
    fields = ('name', 'description',)
