# Generated migration to preserve existing data during translation setup

from django.db import migrations


def migrate_to_english(apps, schema_editor):
    """
    Copy existing 'name' field values to 'name_en' for all pet models.
    This preserves the original data when introducing django-modeltranslation.
    """
    models_to_migrate = [
        'PetType',
        'Gender',
        'AgeCategory',
        'Breed',
        'FoodType',
        'FoodFeeling',
        'FoodImportance',
        'BodyType',
        'ActivityLevel',
        'FoodAllergy',
        'HealthIssue',
        'TreatFrequency',
    ]
    
    for model_name in models_to_migrate:
        Model = apps.get_model('pet', model_name)
        
        # For models with 'description' field (FoodFeeling, BodyType, ActivityLevel, TreatFrequency)
        has_description = hasattr(Model, 'description')
        
        for obj in Model.objects.all():
            # Migrate 'name' to 'name_en'
            if hasattr(obj, 'name') and obj.name:
                obj.name_en = obj.name
            
            # Migrate 'description' to 'description_en' if it exists
            if has_description and hasattr(obj, 'description') and obj.description:
                obj.description_en = obj.description
            
            obj.save(update_fields=['name_en'] + (['description_en'] if has_description else []))


def reverse_migration(apps, schema_editor):
    """
    Reverse the migration by clearing the _en fields.
    Note: Original 'name' field data is preserved in the database.
    """
    models_to_migrate = [
        'PetType',
        'Gender',
        'AgeCategory',
        'Breed',
        'FoodType',
        'FoodFeeling',
        'FoodImportance',
        'BodyType',
        'ActivityLevel',
        'FoodAllergy',
        'HealthIssue',
        'TreatFrequency',
    ]
    
    for model_name in models_to_migrate:
        Model = apps.get_model('pet', model_name)
        
        # Clear the _en fields
        Model.objects.all().update(name_en=None)
        
        # Also clear description_en if it exists
        if hasattr(Model, 'description'):
            Model.objects.all().update(description_en=None)


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0024_add_pet_translations'),
    ]

    operations = [
        migrations.RunPython(migrate_to_english, reverse_migration),
    ]
