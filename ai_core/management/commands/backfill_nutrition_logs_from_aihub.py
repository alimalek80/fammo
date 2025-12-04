"""
Django management command to backfill NutritionPredictionLog rows from aihub AIRecommendation data.

Usage:
    python manage.py backfill_nutrition_logs_from_aihub
    python manage.py backfill_nutrition_logs_from_aihub --limit=50
    python manage.py backfill_nutrition_logs_from_aihub --dry-run
"""

import json
from django.core.management.base import BaseCommand
from ai_core.models import NutritionPredictionLog
from aihub.models import AIRecommendation, RecommendationType
from pet.models import Pet


class Command(BaseCommand):
    help = 'Backfill NutritionPredictionLog records from aihub AIRecommendation meal plans'

    def add_arguments(self, parser):
        """Define command-line arguments."""
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of AIRecommendation records to process'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be created without writing to database'
        )

    def handle(self, *args, **options):
        """Execute the backfill command."""
        limit = options['limit']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY-RUN mode - no data will be written'))
        
        # Query AIRecommendation records that have content_json (meal plans AND health reports)
        queryset = AIRecommendation.objects.filter(
            type__in=[RecommendationType.MEAL, RecommendationType.HEALTH],
            content_json__isnull=False
        ).select_related('pet', 'pet__pet_type', 'pet__breed', 'pet__body_type', 'pet__activity_level')
        
        if limit:
            queryset = queryset[:limit]
        
        scanned_count = 0
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for recommendation in queryset:
            scanned_count += 1
            
            try:
                # Check if log already exists to avoid duplicates
                if self._log_exists(recommendation):
                    skipped_count += 1
                    if dry_run:
                        self.stdout.write(f"  [SKIP] Recommendation #{recommendation.id} - log already exists")
                    continue
                
                # Build input and output payloads
                input_payload = self._build_input_payload(recommendation)
                output_payload = self._build_output_payload(recommendation)
                
                if not input_payload or not output_payload:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"  [ERROR] Recommendation #{recommendation.id} - missing required data"))
                    continue
                
                if dry_run:
                    self.stdout.write(self.style.SUCCESS(
                        f"  [DRY-RUN] Would create log for {input_payload['species']} "
                        f"(health_goal={input_payload.get('health_goal', 'N/A')}, "
                        f"weight={input_payload.get('weight_kg', 'N/A')} kg)"
                    ))
                else:
                    # Determine model_version based on recommendation type
                    model_version = (
                        "aihub_mealplan_v1" if recommendation.type == RecommendationType.MEAL
                        else "aihub_healthreport_v1"
                    )
                    
                    # Create the log entry
                    NutritionPredictionLog.objects.create(
                        source="aihub",
                        backend="openai_responses",
                        model_version=model_version,
                        species=input_payload.get("species", ""),
                        life_stage=input_payload.get("life_stage", ""),
                        breed_size_category=input_payload.get("breed_size_category", ""),
                        health_goal=input_payload.get("health_goal", ""),
                        weight_kg=input_payload.get("weight_kg"),
                        age_years=input_payload.get("age_years"),
                        body_condition_score=input_payload.get("body_condition_score"),
                        input_payload=input_payload,
                        output_payload=output_payload,
                        notes=f"Backfilled from AIRecommendation #{recommendation.id} ({recommendation.get_type_display()})"
                    )
                    created_count += 1
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  [ERROR] Recommendation #{recommendation.id} - {str(e)}"))
        
        # Print summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"Summary:"))
        self.stdout.write(f"  AIRecommendation records scanned: {scanned_count}")
        self.stdout.write(f"  NutritionPredictionLog rows created: {created_count}")
        self.stdout.write(f"  Records skipped (duplicates): {skipped_count}")
        
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"  Errors encountered: {error_count}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY-RUN mode - no data was written to database"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✓ Backfill complete!"))

    def _log_exists(self, recommendation):
        """
        Check if a log already exists for this AIRecommendation.
        
        Uses a simple idempotency check based on source and the 
        recommendation ID stored in notes field (works for both meal and health types).
        """
        return NutritionPredictionLog.objects.filter(
            source="aihub",
            notes__contains=f"AIRecommendation #{recommendation.id}"
        ).exists()

    def _build_input_payload(self, recommendation):
        """
        Build the input_payload dict from pet data.
        
        Approximates the PetProfileSerializer structure with data from
        the Pet model.
        """
        pet = recommendation.pet
        
        if not pet:
            return None
        
        # Get current age
        age_data = pet.get_current_age()
        age_years = age_data.get('years', 0)
        age_months = age_data.get('months', 0)
        
        # Convert age to decimal years
        age_years_decimal = age_years + (age_months / 12.0)
        
        # Map body type to body condition score (rough approximation)
        body_condition_score = self._map_body_type_to_score(pet.body_type.name if pet.body_type else None)
        
        # Determine life stage from age category or age
        life_stage = self._determine_life_stage(pet)
        
        # Determine breed size category
        breed_size_category = self._determine_breed_size(pet)
        
        # Map food feeling or health issues to health goal
        health_goal = self._determine_health_goal(pet)
        
        input_payload = {
            "species": pet.pet_type.name.lower() if pet.pet_type else "dog",
            "life_stage": life_stage,
            "breed_size_category": breed_size_category,
            "health_goal": health_goal,
            "weight_kg": float(pet.weight) if pet.weight else None,
            "age_years": age_years_decimal,
            "body_condition_score": body_condition_score,
            "activity_level": pet.activity_level.name if pet.activity_level else None,
            "is_neutered": pet.neutered if pet.neutered is not None else False,
            "breed": pet.breed.name if pet.breed else None,
            "health_conditions": [hi.name for hi in pet.health_issues.all()],
            "allergies": [fa.name for fa in pet.food_allergies.all()],
            "current_food_types": [ft.name for ft in pet.food_types.all()],
            "pet_id": pet.id,
            "pet_name": pet.name,
        }
        
        return input_payload

    def _build_output_payload(self, recommendation):
        """
        Build the output_payload dict from AIRecommendation content_json.
        
        Extracts nutrition data from the meal plan JSON and structures it
        to match the ModelOutput format used by ai_core.
        """
        content_json = recommendation.content_json
        
        if not content_json:
            return None
        
        # Extract der_kcal
        der_kcal = content_json.get('der_kcal')
        if not der_kcal:
            return None
        
        # Extract nutrient targets
        nutrient_targets = content_json.get('nutrient_targets', {})
        protein_percent = self._parse_percent(nutrient_targets.get('protein_percent'))
        fat_percent = self._parse_percent(nutrient_targets.get('fat_percent'))
        carbs_percent = self._parse_percent(nutrient_targets.get('carbs_percent'))
        
        # Determine diet style from pet data
        pet = recommendation.pet
        diet_style = self._determine_diet_style(pet, der_kcal)
        
        output_payload = {
            "calories_per_day": der_kcal,
            "calorie_range_min": None,  # Not available in aihub data
            "calorie_range_max": None,  # Not available in aihub data
            "protein_percent": protein_percent,
            "fat_percent": fat_percent,
            "carbohydrate_percent": carbs_percent,
            "diet_style": diet_style,
            "diet_style_confidence": 0.9,  # Placeholder confidence
            "risks": {},  # Empty dict for now
            "model_version": "aihub_mealplan_v1",
            "recommendations": {
                "meal_options_count": len(content_json.get('options', [])),
                "feeding_schedule_count": len(content_json.get('feeding_schedule', [])),
                "safety_notes_count": len(content_json.get('safety_notes', [])),
            }
        }
        
        return output_payload

    def _parse_percent(self, value):
        """
        Parse percentage string to float.
        
        Handles formats like "35%", "35 %", "35", or numeric values.
        Returns None if parsing fails.
        """
        if value is None:
            return None
        
        # If already a number
        if isinstance(value, (int, float)):
            return float(value)
        
        # If string, strip whitespace and % sign
        if isinstance(value, str):
            value = value.strip().replace('%', '').strip()
            try:
                return float(value)
            except ValueError:
                return None
        
        return None

    def _map_body_type_to_score(self, body_type_name):
        """
        Map body type name to body condition score (1-9 scale).
        
        Returns approximate BCS based on common body type descriptions.
        """
        if not body_type_name:
            return 5  # Default to ideal
        
        body_type_lower = body_type_name.lower()
        
        if 'underweight' in body_type_lower or 'thin' in body_type_lower:
            return 3
        elif 'ideal' in body_type_lower or 'normal' in body_type_lower:
            return 5
        elif 'overweight' in body_type_lower:
            return 7
        elif 'obese' in body_type_lower:
            return 9
        else:
            return 5  # Default to ideal

    def _determine_life_stage(self, pet):
        """Determine life stage from age category or age."""
        if pet.age_category:
            age_cat_lower = pet.age_category.name.lower()
            if 'puppy' in age_cat_lower or 'kitten' in age_cat_lower:
                return 'puppy' if pet.pet_type and 'dog' in pet.pet_type.name.lower() else 'kitten'
            elif 'adult' in age_cat_lower:
                return 'adult'
            elif 'senior' in age_cat_lower:
                return 'senior'
        
        # Fallback to age-based determination
        age_data = pet.get_current_age()
        age_years = age_data.get('years', 0)
        
        if age_years < 1:
            return 'puppy' if pet.pet_type and 'dog' in pet.pet_type.name.lower() else 'kitten'
        elif age_years < 7:
            return 'adult'
        else:
            return 'senior'

    def _determine_breed_size(self, pet):
        """
        Determine breed size category.
        
        Returns 'small', 'medium', 'large', or 'giant' based on breed or weight.
        """
        # For dogs, use weight-based estimation if available
        if pet.pet_type and 'dog' in pet.pet_type.name.lower() and pet.weight:
            weight = float(pet.weight)
            if weight < 10:
                return 'small'
            elif weight < 25:
                return 'medium'
            elif weight < 45:
                return 'large'
            else:
                return 'giant'
        
        # For cats, typically small/medium
        if pet.pet_type and 'cat' in pet.pet_type.name.lower():
            return 'small'
        
        return 'medium'  # Default

    def _determine_health_goal(self, pet):
        """
        Determine health goal from pet data.
        
        Maps food feeling, body type, or health issues to a health goal.
        """
        # Check body type for weight-related goals
        if pet.body_type:
            body_type_lower = pet.body_type.name.lower()
            if 'underweight' in body_type_lower or 'thin' in body_type_lower:
                return 'weight_gain'
            elif 'overweight' in body_type_lower or 'obese' in body_type_lower:
                return 'weight_loss'
        
        # Check health issues for specific goals
        health_issues = pet.health_issues.all()
        if health_issues:
            health_names = [hi.name.lower() for hi in health_issues]
            if any('kidney' in name or 'renal' in name for name in health_names):
                return 'kidney_support'
            elif any('joint' in name or 'arthritis' in name for name in health_names):
                return 'joint_health'
            elif any('digestive' in name or 'stomach' in name for name in health_names):
                return 'digestive_health'
            elif any('skin' in name or 'allergy' in name for name in health_names):
                return 'skin_health'
        
        # Default to maintenance
        return 'maintenance'

    def _determine_diet_style(self, pet, der_kcal):
        """
        Determine diet style from pet data and calorie needs.
        
        Maps to one of the diet styles: balanced, high_protein, low_fat,
        weight_loss, weight_gain, senior, puppy, performance, etc.
        """
        # Check life stage first
        life_stage = self._determine_life_stage(pet)
        if life_stage == 'puppy' or life_stage == 'kitten':
            return 'puppy' if 'dog' in (pet.pet_type.name.lower() if pet.pet_type else '') else 'kitten'
        elif life_stage == 'senior':
            return 'senior'
        
        # Check health goal
        health_goal = self._determine_health_goal(pet)
        if health_goal == 'weight_loss':
            return 'weight_loss'
        elif health_goal == 'weight_gain':
            return 'weight_gain'
        
        # Check activity level
        if pet.activity_level:
            activity_lower = pet.activity_level.name.lower()
            if 'high' in activity_lower or 'very active' in activity_lower:
                return 'performance'
        
        # Default to balanced
        return 'balanced'
