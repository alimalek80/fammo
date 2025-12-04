"""
Tests for FAMMO AI Core Serializers

This module tests the DRF serializers that bridge between JSON and AI dataclasses.
Tests cover validation, data conversion, and serialization for:
- PetProfileSerializer (JSON -> PetProfile dataclass)
- ModelOutputSerializer (ModelOutput dataclass -> JSON)

Run tests with:
    python manage.py test ai_core.tests.test_ai_serializers
    # or
    pytest ai_core/tests/test_ai_serializers.py
"""

from datetime import datetime
from django.test import TestCase

from ai_core.serializers import (
    PetProfileSerializer,
    RiskAssessmentSerializer,
    ModelOutputSerializer
)
from ai_core.interfaces import PetProfile, ModelOutput, RiskAssessment


class PetProfileSerializerTestCase(TestCase):
    """Tests for PetProfileSerializer - validates JSON input and converts to PetProfile."""
    
    def setUp(self):
        """Set up common test data."""
        self.valid_minimal_data = {
            "species": "dog",
            "breed": "Golden Retriever",
            "breed_size_category": "large",
            "age_years": 3.5,
            "life_stage": "adult",
            "weight_kg": 29.0,
            "body_condition_score": 4,
            "sex": "male",
            "neutered": True,
            "activity_level": "moderate",
        }
        
        self.valid_complete_data = {
            "species": "dog",
            "breed": "Golden Retriever",
            "breed_size_category": "large",
            "age_years": 3.5,
            "life_stage": "adult",
            "weight_kg": 29.0,
            "body_condition_score": 4,
            "sex": "male",
            "neutered": True,
            "activity_level": "moderate",
            "living_environment": "mixed",
            "existing_conditions": ["hip_dysplasia", "food_sensitivity"],
            "food_allergies": ["chicken", "dairy"],
            "medications": [],
            "current_food_type": "dry",
            "food_satisfaction": "always_hungry",
            "treat_frequency": "daily",
            "health_goal": "weight_loss",
            "dietary_preference": "grain_free",
            "climate_zone": "temperate",
            "country": "FI"
        }
    
    def test_valid_minimal_pet_profile_serialization(self):
        """Test that minimal valid data is accepted and converts to PetProfile correctly."""
        serializer = PetProfileSerializer(data=self.valid_minimal_data)
        
        # Should be valid
        self.assertTrue(serializer.is_valid(), f"Serializer errors: {serializer.errors}")
        
        # Convert to dataclass
        pet_profile = serializer.to_pet_profile()
        
        # Assert it's a PetProfile instance
        self.assertIsInstance(pet_profile, PetProfile)
        
        # Assert required fields match
        self.assertEqual(pet_profile.species, "dog")
        self.assertEqual(pet_profile.breed, "Golden Retriever")
        self.assertEqual(pet_profile.breed_size_category, "large")
        self.assertEqual(pet_profile.age_years, 3.5)
        self.assertEqual(pet_profile.life_stage, "adult")
        self.assertEqual(pet_profile.weight_kg, 29.0)
        self.assertEqual(pet_profile.body_condition_score, 4)
        self.assertEqual(pet_profile.sex, "male")
        self.assertTrue(pet_profile.neutered)
        self.assertEqual(pet_profile.activity_level, "moderate")
        
        # Assert optional fields have defaults
        self.assertEqual(pet_profile.living_environment, "mixed")
        self.assertEqual(pet_profile.existing_conditions, [])
        self.assertEqual(pet_profile.food_allergies, [])
        self.assertEqual(pet_profile.medications, [])
        self.assertEqual(pet_profile.current_food_type, "dry")
        self.assertEqual(pet_profile.food_satisfaction, "satisfied")
        self.assertEqual(pet_profile.treat_frequency, "weekly")
        self.assertEqual(pet_profile.health_goal, "maintenance")
        self.assertEqual(pet_profile.dietary_preference, "no_preference")
        self.assertEqual(pet_profile.climate_zone, "temperate")
        self.assertEqual(pet_profile.country, "FI")
    
    def test_valid_complete_pet_profile_serialization(self):
        """Test that complete valid data with all optional fields is accepted."""
        serializer = PetProfileSerializer(data=self.valid_complete_data)
        
        # Should be valid
        self.assertTrue(serializer.is_valid(), f"Serializer errors: {serializer.errors}")
        
        # Convert to dataclass
        pet_profile = serializer.to_pet_profile()
        
        # Assert lists are correctly parsed
        self.assertEqual(pet_profile.existing_conditions, ["hip_dysplasia", "food_sensitivity"])
        self.assertEqual(pet_profile.food_allergies, ["chicken", "dairy"])
        self.assertEqual(pet_profile.medications, [])
        
        # Assert optional enums are correct
        self.assertEqual(pet_profile.health_goal, "weight_loss")
        self.assertEqual(pet_profile.dietary_preference, "grain_free")
        self.assertEqual(pet_profile.food_satisfaction, "always_hungry")
        self.assertEqual(pet_profile.treat_frequency, "daily")
    
    def test_missing_required_species_field_fails(self):
        """Test that missing 'species' field causes validation error."""
        data = self.valid_minimal_data.copy()
        del data["species"]
        
        serializer = PetProfileSerializer(data=data)
        
        # Should be invalid
        self.assertFalse(serializer.is_valid())
        
        # Error should mention 'species'
        self.assertIn("species", serializer.errors)
    
    def test_missing_required_weight_field_fails(self):
        """Test that missing 'weight_kg' field causes validation error."""
        data = self.valid_minimal_data.copy()
        del data["weight_kg"]
        
        serializer = PetProfileSerializer(data=data)
        
        # Should be invalid
        self.assertFalse(serializer.is_valid())
        
        # Error should mention 'weight_kg'
        self.assertIn("weight_kg", serializer.errors)
    
    def test_invalid_species_value_fails(self):
        """Test that invalid species value causes validation error."""
        data = self.valid_minimal_data.copy()
        data["species"] = "hamster"  # Not in choices
        
        serializer = PetProfileSerializer(data=data)
        
        # Should be invalid
        self.assertFalse(serializer.is_valid())
        
        # Error should mention 'species'
        self.assertIn("species", serializer.errors)
    
    def test_invalid_body_condition_score_fails(self):
        """Test that body_condition_score outside 1-5 range fails."""
        data = self.valid_minimal_data.copy()
        data["body_condition_score"] = 6  # Max is 5
        
        serializer = PetProfileSerializer(data=data)
        
        # Should be invalid
        self.assertFalse(serializer.is_valid())
        
        # Error should mention 'body_condition_score'
        self.assertIn("body_condition_score", serializer.errors)
    
    def test_age_years_out_of_range_fails(self):
        """Test that age_years > 25 causes validation error."""
        data = self.valid_minimal_data.copy()
        data["age_years"] = 30.0  # Max is 25.0
        
        serializer = PetProfileSerializer(data=data)
        
        # Should be invalid
        self.assertFalse(serializer.is_valid())
        
        # Error should mention 'age_years'
        self.assertIn("age_years", serializer.errors)
    
    def test_weight_kg_out_of_range_fails(self):
        """Test that weight_kg > 100 causes validation error."""
        data = self.valid_minimal_data.copy()
        data["weight_kg"] = 150.0  # Max is 100.0
        
        serializer = PetProfileSerializer(data=data)
        
        # Should be invalid
        self.assertFalse(serializer.is_valid())
        
        # Error should mention 'weight_kg'
        self.assertIn("weight_kg", serializer.errors)
    
    def test_invalid_activity_level_fails(self):
        """Test that invalid activity_level value fails."""
        data = self.valid_minimal_data.copy()
        data["activity_level"] = "extreme"  # Not in choices
        
        serializer = PetProfileSerializer(data=data)
        
        # Should be invalid
        self.assertFalse(serializer.is_valid())
        
        # Error should mention 'activity_level'
        self.assertIn("activity_level", serializer.errors)
    
    def test_to_pet_profile_before_validation_raises_error(self):
        """Test that calling to_pet_profile() before is_valid() raises AssertionError."""
        serializer = PetProfileSerializer(data=self.valid_minimal_data)
        
        # Don't call is_valid()
        with self.assertRaises(AssertionError) as context:
            serializer.to_pet_profile()
        
        # Error message should mention is_valid()
        self.assertIn("is_valid()", str(context.exception))
    
    def test_cat_profile_with_kitten_life_stage(self):
        """Test that a valid cat profile is accepted."""
        data = {
            "species": "cat",
            "breed": "Siamese",
            "breed_size_category": "medium",
            "age_years": 0.5,
            "life_stage": "kitten",
            "weight_kg": 2.5,
            "body_condition_score": 3,
            "sex": "female",
            "neutered": False,
            "activity_level": "high",
        }
        
        serializer = PetProfileSerializer(data=data)
        
        # Should be valid
        self.assertTrue(serializer.is_valid(), f"Serializer errors: {serializer.errors}")
        
        # Convert to dataclass
        pet_profile = serializer.to_pet_profile()
        
        # Assert cat-specific values
        self.assertEqual(pet_profile.species, "cat")
        self.assertEqual(pet_profile.life_stage, "kitten")
        self.assertFalse(pet_profile.neutered)


class RiskAssessmentSerializerTestCase(TestCase):
    """Tests for RiskAssessmentSerializer - validates risk scores."""
    
    def test_valid_risk_assessment(self):
        """Test that valid risk assessment data is accepted."""
        data = {
            "weight_risk": "high",
            "joint_risk": "medium",
            "digestive_risk": "low",
            "metabolic_risk": "medium",
            "kidney_risk": "low",
            "dental_risk": "low"
        }
        
        serializer = RiskAssessmentSerializer(data=data)
        
        # Should be valid
        self.assertTrue(serializer.is_valid(), f"Serializer errors: {serializer.errors}")
        
        # Check data matches
        self.assertEqual(serializer.validated_data["weight_risk"], "high")
        self.assertEqual(serializer.validated_data["joint_risk"], "medium")
        self.assertEqual(serializer.validated_data["digestive_risk"], "low")
    
    def test_invalid_risk_level_fails(self):
        """Test that invalid risk level causes validation error."""
        data = {
            "weight_risk": "critical",  # Not in choices (low/medium/high)
            "joint_risk": "medium",
            "digestive_risk": "low",
            "metabolic_risk": "low",
            "kidney_risk": "low",
            "dental_risk": "low"
        }
        
        serializer = RiskAssessmentSerializer(data=data)
        
        # Should be invalid
        self.assertFalse(serializer.is_valid())
        
        # Error should mention 'weight_risk'
        self.assertIn("weight_risk", serializer.errors)


class ModelOutputSerializerTestCase(TestCase):
    """Tests for ModelOutputSerializer - serializes ModelOutput dataclass to JSON."""
    
    def setUp(self):
        """Set up common test data."""
        self.sample_risks = RiskAssessment(
            weight_risk="high",
            joint_risk="medium",
            digestive_risk="low",
            metabolic_risk="medium",
            kidney_risk="low",
            dental_risk="low"
        )
        
        self.sample_output = ModelOutput(
            calories_per_day=780,
            calorie_range_min=702,
            calorie_range_max=858,
            protein_percent=28,
            fat_percent=12,
            carbohydrate_percent=40,
            diet_style="weight_loss",
            diet_style_confidence=0.87,
            risks=self.sample_risks,
            meals_per_day=2,
            portion_size_grams=195,
            model_version="1.0.0",
            prediction_timestamp="2025-12-01T14:32:15Z",
            confidence_score=0.85,
            veterinary_consultation_recommended=False,
            alert_messages=[
                "Weight loss target detected - reduce calories by 15-20% from maintenance",
                "Monitor weight weekly and adjust portions as needed"
            ]
        )
    
    def test_model_output_serialization(self):
        """Test that ModelOutput instance is correctly serialized to JSON dict."""
        serializer = ModelOutputSerializer(self.sample_output)
        data = serializer.data
        
        # Assert caloric fields
        self.assertEqual(data["calories_per_day"], 780)
        self.assertEqual(data["calorie_range_min"], 702)
        self.assertEqual(data["calorie_range_max"], 858)
        
        # Assert macronutrient fields
        self.assertEqual(data["protein_percent"], 28)
        self.assertEqual(data["fat_percent"], 12)
        self.assertEqual(data["carbohydrate_percent"], 40)
        
        # Assert diet style
        self.assertEqual(data["diet_style"], "weight_loss")
        self.assertEqual(data["diet_style_confidence"], 0.87)
        
        # Assert nested risks
        self.assertIn("risks", data)
        self.assertEqual(data["risks"]["weight_risk"], "high")
        self.assertEqual(data["risks"]["joint_risk"], "medium")
        self.assertEqual(data["risks"]["digestive_risk"], "low")
        self.assertEqual(data["risks"]["metabolic_risk"], "medium")
        self.assertEqual(data["risks"]["kidney_risk"], "low")
        self.assertEqual(data["risks"]["dental_risk"], "low")
        
        # Assert feeding recommendations
        self.assertEqual(data["meals_per_day"], 2)
        self.assertEqual(data["portion_size_grams"], 195)
        
        # Assert metadata
        self.assertEqual(data["model_version"], "1.0.0")
        self.assertEqual(data["prediction_timestamp"], "2025-12-01T14:32:15Z")
        self.assertEqual(data["confidence_score"], 0.85)
        
        # Assert alerts
        self.assertFalse(data["veterinary_consultation_recommended"])
        self.assertEqual(len(data["alert_messages"]), 2)
        self.assertIn("Weight loss target detected", data["alert_messages"][0])
    
    def test_senior_cat_output_serialization(self):
        """Test serialization of senior cat with kidney disease output."""
        risks = RiskAssessment(
            weight_risk="medium",
            joint_risk="low",
            digestive_risk="low",
            metabolic_risk="low",
            kidney_risk="high",
            dental_risk="high"
        )
        
        output = ModelOutput(
            calories_per_day=185,
            calorie_range_min=167,
            calorie_range_max=204,
            protein_percent=26,
            fat_percent=18,
            carbohydrate_percent=35,
            diet_style="senior_wellness_kidney",
            diet_style_confidence=0.92,
            risks=risks,
            meals_per_day=3,
            portion_size_grams=45,
            model_version="1.0.0",
            prediction_timestamp="2025-12-01T14:35:22Z",
            confidence_score=0.89,
            veterinary_consultation_recommended=True,
            alert_messages=[
                "Chronic kidney disease detected - veterinary-prescribed diet recommended",
                "Protein restriction may be necessary - consult vet before changes"
            ]
        )
        
        serializer = ModelOutputSerializer(output)
        data = serializer.data
        
        # Assert cat-specific values
        self.assertEqual(data["calories_per_day"], 185)
        self.assertEqual(data["diet_style"], "senior_wellness_kidney")
        self.assertEqual(data["risks"]["kidney_risk"], "high")
        self.assertTrue(data["veterinary_consultation_recommended"])
        self.assertEqual(data["meals_per_day"], 3)
    
    def test_active_puppy_output_serialization(self):
        """Test serialization of active puppy output."""
        risks = RiskAssessment(
            weight_risk="low",
            joint_risk="low",
            digestive_risk="medium",
            metabolic_risk="low",
            kidney_risk="low",
            dental_risk="low"
        )
        
        output = ModelOutput(
            calories_per_day=1250,
            calorie_range_min=1125,
            calorie_range_max=1375,
            protein_percent=32,
            fat_percent=18,
            carbohydrate_percent=35,
            diet_style="growth_puppy",
            diet_style_confidence=0.94,
            risks=risks,
            meals_per_day=3,
            portion_size_grams=130,
            model_version="1.0.0",
            prediction_timestamp="2025-12-01T14:38:45Z",
            confidence_score=0.91,
            veterinary_consultation_recommended=False,
            alert_messages=[
                "Growth stage - ensure food is labeled for puppies/growth"
            ]
        )
        
        serializer = ModelOutputSerializer(output)
        data = serializer.data
        
        # Assert puppy-specific values
        self.assertEqual(data["calories_per_day"], 1250)
        self.assertEqual(data["diet_style"], "growth_puppy")
        self.assertEqual(data["protein_percent"], 32)
        self.assertFalse(data["veterinary_consultation_recommended"])
    
    def test_empty_alert_messages(self):
        """Test that empty alert_messages list is handled correctly."""
        output = ModelOutput(
            calories_per_day=850,
            calorie_range_min=765,
            calorie_range_max=935,
            protein_percent=26,
            fat_percent=14,
            carbohydrate_percent=45,
            diet_style="maintenance_standard",
            diet_style_confidence=0.88,
            risks=self.sample_risks,
            meals_per_day=2,
            portion_size_grams=210,
            model_version="1.0.0",
            prediction_timestamp="2025-12-01T14:40:00Z",
            confidence_score=0.86,
            veterinary_consultation_recommended=False,
            alert_messages=[]  # Empty list
        )
        
        serializer = ModelOutputSerializer(output)
        data = serializer.data
        
        # Assert empty list is preserved
        self.assertEqual(data["alert_messages"], [])
        self.assertIsInstance(data["alert_messages"], list)


class IntegrationTestCase(TestCase):
    """Integration tests for the complete serialization workflow."""
    
    def test_full_workflow_pet_profile_to_output(self):
        """Test complete workflow: JSON input -> PetProfile -> (mock prediction) -> ModelOutput -> JSON output."""
        # Step 1: Input JSON
        input_data = {
            "species": "dog",
            "breed": "Beagle",
            "breed_size_category": "medium",
            "age_years": 5.0,
            "life_stage": "adult",
            "weight_kg": 12.0,
            "body_condition_score": 3,
            "sex": "female",
            "neutered": True,
            "activity_level": "moderate",
            "health_goal": "maintenance"
        }
        
        # Step 2: Validate and convert to PetProfile
        input_serializer = PetProfileSerializer(data=input_data)
        self.assertTrue(input_serializer.is_valid())
        pet_profile = input_serializer.to_pet_profile()
        
        # Step 3: Mock AI prediction (in real code, this would be engine.predict(pet_profile))
        risks = RiskAssessment(
            weight_risk="low",
            joint_risk="low",
            digestive_risk="low",
            metabolic_risk="low",
            kidney_risk="low",
            dental_risk="medium"
        )
        
        output = ModelOutput(
            calories_per_day=450,
            calorie_range_min=405,
            calorie_range_max=495,
            protein_percent=26,
            fat_percent=14,
            carbohydrate_percent=45,
            diet_style="maintenance_standard",
            diet_style_confidence=0.91,
            risks=risks,
            meals_per_day=2,
            portion_size_grams=115,
            model_version="1.0.0",
            prediction_timestamp="2025-12-01T15:00:00Z",
            confidence_score=0.88,
            veterinary_consultation_recommended=False,
            alert_messages=[]
        )
        
        # Step 4: Serialize output to JSON
        output_serializer = ModelOutputSerializer(output)
        response_data = output_serializer.data
        
        # Step 5: Assert complete workflow
        self.assertEqual(response_data["calories_per_day"], 450)
        self.assertEqual(response_data["diet_style"], "maintenance_standard")
        self.assertEqual(response_data["risks"]["weight_risk"], "low")
        self.assertEqual(response_data["risks"]["dental_risk"], "medium")
        self.assertFalse(response_data["veterinary_consultation_recommended"])
