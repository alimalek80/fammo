from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Pet, PetType, Gender, AgeCategory, Breed, FoodType, FoodFeeling, FoodImportance, BodyType, ActivityLevel, FoodAllergy, HealthIssue, TreatFrequency

class ActivityLevelAdmin(TranslationAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    ordering = ('order', 'name')

class FoodAllergyAdmin(TranslationAdmin):
    list_display = ('id', 'name_en', 'name_fi', 'name_nl', 'name_tr', 'order')
    list_editable = ('name_en', 'name_fi', 'name_nl', 'name_tr', 'order')
    ordering = ('order', 'name')

class HealthIssueAdmin(TranslationAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    ordering = ('order', 'name')

class AgeCategoryAdmin(TranslationAdmin):
    list_display = ('id', 'name_en', 'name_fi', 'name_nl', 'name_tr', 'pet_type', 'order')
    list_editable = ('name_en', 'name_fi', 'name_nl', 'name_tr', 'order')
    ordering = ('pet_type', 'order', 'name')

class PetTypeAdmin(TranslationAdmin):
    list_display = ('name',)

class GenderAdmin(TranslationAdmin):
    list_display = ('name',)

class BreedAdmin(TranslationAdmin):
    list_display = ('id', 'name_en', 'name_fi', 'name_nl', 'name_tr', 'pet_type')
    list_editable = ('name_en', 'name_fi', 'name_nl', 'name_tr')

class FoodTypeAdmin(TranslationAdmin):
    list_display = ('name',)

class FoodFeelingAdmin(TranslationAdmin):
    list_display = ('name', 'description')

class FoodImportanceAdmin(TranslationAdmin):
    list_display = ('name',)

class BodyTypeAdmin(TranslationAdmin):
    list_display = ('name', 'description')

class TreatFrequencyAdmin(TranslationAdmin):
    list_display = ('name', 'description')

admin.site.register(Pet)
admin.site.register(PetType, PetTypeAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(AgeCategory, AgeCategoryAdmin)
admin.site.register(Breed, BreedAdmin)
admin.site.register(FoodType, FoodTypeAdmin)
admin.site.register(FoodFeeling, FoodFeelingAdmin)
admin.site.register(FoodImportance, FoodImportanceAdmin)
admin.site.register(BodyType, BodyTypeAdmin)
admin.site.register(ActivityLevel, ActivityLevelAdmin)
admin.site.register(FoodAllergy, FoodAllergyAdmin)
admin.site.register(HealthIssue, HealthIssueAdmin)
admin.site.register(TreatFrequency, TreatFrequencyAdmin)




