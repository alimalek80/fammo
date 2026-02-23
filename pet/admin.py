from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (Pet, PetType, Gender, AgeCategory, Breed, FoodType, FoodFeeling, 
                     FoodImportance, BodyType, ActivityLevel, FoodAllergy, HealthIssue, 
                     TreatFrequency, AgeTransitionRule, PetAgeHistory, PetConditionSnapshot,
                     PetConditionSnapshotFoodTypes, PetConditionSnapshotFoodAllergies,
                     PetConditionSnapshotHealthIssues)

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


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'pet_type', 'breed', 'age_at_registration_display', 'current_age_display', 'age_category', 'weight', 'registration_date')
    list_filter = ('pet_type', 'age_category', 'gender', 'neutered', 'registration_date')
    search_fields = ('name', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('registration_date', 'birth_date', 'current_age_years', 'current_age_months', 'current_age_weeks')
    ordering = ('-registration_date',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'user', 'pet_type', 'breed', 'gender', 'neutered', 'image')
        }),
        ('Age Information', {
            'fields': (
                'registration_date',
                ('age_years', 'age_months', 'age_weeks'),
                ('current_age_years', 'current_age_months', 'current_age_weeks'),
                'birth_date',
                'age_category'
            ),
            'description': 'Age fields (years/months/weeks) represent age at registration. Current age is automatically calculated.'
        }),
        ('Physical Details', {
            'fields': ('weight', 'body_type', 'activity_level')
        }),
        ('Food & Health', {
            'fields': ('food_types', 'food_feeling', 'food_importance', 'food_allergies', 'food_allergy_other', 'health_issues', 'treat_frequency')
        }),
    )
    
    def age_at_registration_display(self, obj):
        return obj.get_age_at_registration_display()
    age_at_registration_display.short_description = 'Age at Registration'
    
    def current_age_display(self, obj):
        return obj.get_age_display()
    current_age_display.short_description = 'Current Age'


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


# Age Transition and History Admin
@admin.register(AgeTransitionRule)
class AgeTransitionRuleAdmin(admin.ModelAdmin):
    list_display = ('pet_type', 'from_category', 'to_category', 'transition_age_months', 'age_display', 'created_at')
    list_filter = ('pet_type', 'created_at')
    list_editable = ('transition_age_months',)
    ordering = ('pet_type', 'transition_age_months')
    search_fields = ('pet_type__name', 'from_category__name', 'to_category__name')
    
    def age_display(self, obj):
        years = obj.transition_age_months // 12
        months = obj.transition_age_months % 12
        if months:
            return f"{years}y {months}m"
        return f"{years}y"
    age_display.short_description = 'Age'


@admin.register(PetAgeHistory)
class PetAgeHistoryAdmin(admin.ModelAdmin):
    list_display = ('pet', 'age_category', 'started_at', 'ended_at', 'age_months_at_start', 'transition_reason', 'is_current')
    list_filter = ('age_category', 'transition_reason', 'started_at')
    readonly_fields = ('started_at', 'ended_at')
    search_fields = ('pet__name', 'pet__user__email')
    ordering = ('-started_at',)
    
    def is_current(self, obj):
        return obj.ended_at is None
    is_current.boolean = True
    is_current.short_description = 'Current'


class PetConditionSnapshotFoodTypesInline(admin.TabularInline):
    model = PetConditionSnapshotFoodTypes
    extra = 0
    readonly_fields = ('added_at',)


class PetConditionSnapshotFoodAllergiesInline(admin.TabularInline):
    model = PetConditionSnapshotFoodAllergies
    extra = 0
    readonly_fields = ('added_at',)


class PetConditionSnapshotHealthIssuesInline(admin.TabularInline):
    model = PetConditionSnapshotHealthIssues
    extra = 0
    readonly_fields = ('added_at',)


@admin.register(PetConditionSnapshot)
class PetConditionSnapshotAdmin(admin.ModelAdmin):
    list_display = ('pet', 'age_category', 'weight', 'snapshot_date', 'transition_reason', 'food_types_count', 'allergies_count', 'health_issues_count')
    list_filter = ('age_category', 'transition_reason', 'snapshot_date')
    readonly_fields = ('snapshot_date',)
    search_fields = ('pet__name', 'pet__user__email', 'notes')
    ordering = ('-snapshot_date',)
    inlines = [PetConditionSnapshotFoodTypesInline, PetConditionSnapshotFoodAllergiesInline, PetConditionSnapshotHealthIssuesInline]
    
    def food_types_count(self, obj):
        return obj.food_type_snapshots.count()
    food_types_count.short_description = 'Food Types'
    
    def allergies_count(self, obj):
        return obj.food_allergy_snapshots.count()
    allergies_count.short_description = 'Allergies'
    
    def health_issues_count(self, obj):
        return obj.health_issue_snapshots.count()
    health_issues_count.short_description = 'Health Issues'




