"""
Tests for NutritionPredictionView API endpoint.

Tests focus on API contract validation, not AI/ML logic.
The AI engine is mocked to return predictable test data.
"""

from datetime import datetime
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from ai_core.interfaces import ModelOutput, RiskAssessment, PetProfile


class DummyEngine:
    """
    Fake AI engine for testing.
    Returns hardcoded predictions without calling real AI services.
    """
    
    def predict(self, pet_profile: PetProfile) -> ModelOutput:
        """Return a fake prediction with valid data."""
        return ModelOutput(
            calories_per_day=700,
            calorie_range_min=630,
            calorie_range_max=770,
            protein_percent=28,
            fat_percent=12,
            carbohydrate_percent=40,
            diet_style="weight_loss",
            diet_style_confidence=0.87,
            risks=RiskAssessment(
                weight_risk="high",
                joint_risk="medium",
                digestive_risk="low",
                metabolic_risk="medium",
                kidney_risk="low",
                dental_risk="low",
            ),
            meals_per_day=2,
            portion_size_grams=195,
            model_version="1.0.0-test",
            prediction_timestamp=datetime.utcnow().isoformat() + "Z",
            confidence_score=0.85,
            veterinary_consultation_recommended=False,
            alert_messages=[
                "Weight loss target detected - reduce calories by 15-20%",
                "Monitor weight weekly and adjust portions as needed"
            ],
        )


class NutritionPredictionViewTestCase(APITestCase):
    """Test cases for POST /api/v1/ai/nutrition/ endpoint."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.url = reverse("ai_core:nutrition-prediction")
        
        # Valid pet profile data
        self.valid_data = {
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
            "health_goal": "weight_loss",
            "existing_conditions": ["hip_dysplasia"],
            "food_allergies": ["chicken"],
        }
    
    @patch("ai_core.views.get_engine")
    def test_valid_request_returns_200_with_prediction(self, mock_get_engine):
        """
        Test 1: Valid request with proper pet profile data.
        
        Given: Valid pet profile JSON
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 200 status and contains prediction data
        """
        # Arrange: Mock the engine to return dummy predictions
        mock_get_engine.return_value = DummyEngine()
        
        # Act: POST valid data
        response = self.client.post(self.url, self.valid_data, format="json")
        
        # Assert: Status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert: Response contains required prediction fields
        self.assertIn("calories_per_day", response.data)
        self.assertIn("diet_style", response.data)
        self.assertIn("risks", response.data)
        self.assertIn("protein_percent", response.data)
        self.assertIn("fat_percent", response.data)
        self.assertIn("carbohydrate_percent", response.data)
        self.assertIn("meals_per_day", response.data)
        self.assertIn("portion_size_grams", response.data)
        self.assertIn("model_version", response.data)
        self.assertIn("confidence_score", response.data)
        
        # Assert: Values match dummy engine output
        self.assertEqual(response.data["calories_per_day"], 700)
        self.assertEqual(response.data["diet_style"], "weight_loss")
        self.assertEqual(response.data["protein_percent"], 28)
        self.assertEqual(response.data["fat_percent"], 12)
        self.assertEqual(response.data["meals_per_day"], 2)
        
        # Assert: Risk assessment structure is correct
        risks = response.data["risks"]
        self.assertIsInstance(risks, dict)
        self.assertEqual(risks["weight_risk"], "high")
        self.assertEqual(risks["joint_risk"], "medium")
        self.assertEqual(risks["digestive_risk"], "low")
        self.assertEqual(risks["metabolic_risk"], "medium")
        self.assertEqual(risks["kidney_risk"], "low")
        self.assertEqual(risks["dental_risk"], "low")
        
        # Assert: Alert messages are present
        self.assertIn("alert_messages", response.data)
        self.assertEqual(len(response.data["alert_messages"]), 2)
        self.assertIn("Weight loss", response.data["alert_messages"][0])
    
    def test_invalid_request_missing_required_fields(self):
        """
        Test 2: Invalid request with missing required fields.
        
        Given: Incomplete pet profile (missing required fields)
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 400 status with validation errors
        """
        # Arrange: Invalid data missing required fields
        invalid_data = {
            "species": "dog",
            "breed": "Beagle",
            # Missing: age_years, weight_kg, body_condition_score, etc.
        }
        
        # Act: POST invalid data
        response = self.client.post(self.url, invalid_data, format="json")
        
        # Assert: Status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Assert: Response contains error details
        self.assertIn("detail", response.data)
        self.assertIn("errors", response.data)
        
        # Assert: Errors mention missing fields
        errors = response.data["errors"]
        self.assertIn("age_years", errors)
        self.assertIn("weight_kg", errors)
        self.assertIn("body_condition_score", errors)
    
    def test_invalid_request_wrong_field_types(self):
        """
        Test invalid data types for fields.
        
        Given: Pet profile with wrong data types
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 400 status with type validation errors
        """
        # Arrange: Invalid data with wrong types
        invalid_data = {
            "species": "dog",
            "breed": "Poodle",
            "breed_size_category": "small",
            "age_years": "three years",  # Should be float
            "life_stage": "adult",
            "weight_kg": "five kilos",  # Should be float
            "body_condition_score": 3,
            "sex": "male",
            "neutered": True,
            "activity_level": "moderate",
        }
        
        # Act: POST invalid data
        response = self.client.post(self.url, invalid_data, format="json")
        
        # Assert: Status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
    
    def test_invalid_request_out_of_range_values(self):
        """
        Test validation for out-of-range values.
        
        Given: Pet profile with values outside valid ranges
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 400 status with range validation errors
        """
        # Arrange: Data with out-of-range values
        invalid_data = self.valid_data.copy()
        invalid_data["body_condition_score"] = 10  # Valid range: 1-5
        invalid_data["age_years"] = 30  # Valid range: 0-25
        
        # Act: POST invalid data
        response = self.client.post(self.url, invalid_data, format="json")
        
        # Assert: Status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
    
    def test_invalid_request_invalid_enum_values(self):
        """
        Test validation for invalid enum choices.
        
        Given: Pet profile with invalid enum values
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 400 status with choice validation errors
        """
        # Arrange: Data with invalid enum
        invalid_data = self.valid_data.copy()
        invalid_data["species"] = "hamster"  # Valid: "dog" or "cat"
        invalid_data["activity_level"] = "super_active"  # Invalid choice
        
        # Act: POST invalid data
        response = self.client.post(self.url, invalid_data, format="json")
        
        # Assert: Status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
    
    @patch("ai_core.views.get_engine")
    def test_engine_raises_generic_exception(self, mock_get_engine):
        """
        Test 3: Engine exception handling.
        
        Given: Valid request but AI engine raises an exception
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 500 status with error details
        """
        # Arrange: Mock engine to raise exception
        mock_engine = MagicMock()
        mock_engine.predict.side_effect = Exception("AI service unavailable")
        mock_get_engine.return_value = mock_engine
        
        # Act: POST valid data
        response = self.client.post(self.url, self.valid_data, format="json")
        
        # Assert: Status is 500 Internal Server Error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Assert: Response contains error information
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "AI engine error")
        
        self.assertIn("error", response.data)
        self.assertIn("AI service unavailable", response.data["error"])
        
        self.assertIn("message", response.data)
    
    @patch("ai_core.views.get_engine")
    def test_engine_raises_not_implemented_error(self, mock_get_engine):
        """
        Test engine not implemented scenario.
        
        Given: AI engine is not yet implemented
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 503 status indicating service unavailable
        """
        # Arrange: Mock engine to raise NotImplementedError
        mock_engine = MagicMock()
        mock_engine.predict.side_effect = NotImplementedError("OpenAI engine not implemented yet")
        mock_get_engine.return_value = mock_engine
        
        # Act: POST valid data
        response = self.client.post(self.url, self.valid_data, format="json")
        
        # Assert: Status is 503 Service Unavailable
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Assert: Response explains service is not ready
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "AI engine not yet implemented")
        
        self.assertIn("error", response.data)
        self.assertIn("message", response.data)
    
    @patch("ai_core.views.get_engine")
    def test_engine_raises_value_error(self, mock_get_engine):
        """
        Test engine raises ValueError (invalid data caught by engine).
        
        Given: Data passes serializer but fails in engine/dataclass validation
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 400 status with validation error
        """
        # Arrange: Mock engine to raise ValueError
        mock_engine = MagicMock()
        mock_engine.predict.side_effect = ValueError("Invalid body condition score")
        mock_get_engine.return_value = mock_engine
        
        # Act: POST valid data
        response = self.client.post(self.url, self.valid_data, format="json")
        
        # Assert: Status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Assert: Response contains validation error
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Invalid pet profile values")
        
        self.assertIn("error", response.data)
        self.assertIn("Invalid body condition score", response.data["error"])
    
    @patch("ai_core.views.get_engine")
    def test_minimal_valid_request(self, mock_get_engine):
        """
        Test request with only required fields (optional fields use defaults).
        
        Given: Minimal valid pet profile (no optional fields)
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 200 status with prediction
        """
        # Arrange: Minimal valid data (only required fields)
        minimal_data = {
            "species": "cat",
            "breed": "Domestic Shorthair",
            "breed_size_category": "small",
            "age_years": 2.0,
            "life_stage": "adult",
            "weight_kg": 4.5,
            "body_condition_score": 3,
            "sex": "female",
            "neutered": True,
            "activity_level": "low",
        }
        
        mock_get_engine.return_value = DummyEngine()
        
        # Act: POST minimal data
        response = self.client.post(self.url, minimal_data, format="json")
        
        # Assert: Status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert: Response contains prediction
        self.assertIn("calories_per_day", response.data)
        self.assertIn("diet_style", response.data)
    
    @patch("ai_core.views.get_engine")
    def test_request_with_all_optional_fields(self, mock_get_engine):
        """
        Test request with all optional fields populated.
        
        Given: Complete pet profile with all optional fields
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 200 status with prediction
        """
        # Arrange: Complete data with all optional fields
        complete_data = {
            "species": "dog",
            "breed": "Labrador Retriever",
            "breed_size_category": "large",
            "age_years": 5.0,
            "life_stage": "adult",
            "weight_kg": 32.0,
            "body_condition_score": 3,
            "sex": "male",
            "neutered": True,
            "activity_level": "high",
            "living_environment": "outdoor",
            "existing_conditions": ["arthritis", "allergies"],
            "food_allergies": ["beef", "wheat"],
            "medications": ["pain_relief", "allergy_med"],
            "current_food_type": "raw",
            "food_satisfaction": "satisfied",
            "treat_frequency": "daily",
            "health_goal": "joint_support",
            "dietary_preference": "grain_free",
            "climate_zone": "cold",
            "country": "FI",
        }
        
        mock_get_engine.return_value = DummyEngine()
        
        # Act: POST complete data
        response = self.client.post(self.url, complete_data, format="json")
        
        # Assert: Status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert: Response contains prediction
        self.assertIn("calories_per_day", response.data)
        self.assertIn("risks", response.data)
    
    def test_empty_request_body(self):
        """
        Test completely empty request.
        
        Given: Empty JSON body
        When: POST to /api/v1/ai/nutrition/
        Then: Response has 400 status with validation errors
        """
        # Act: POST empty data
        response = self.client.post(self.url, {}, format="json")
        
        # Assert: Status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Assert: Errors for all required fields
        self.assertIn("errors", response.data)
    
    @patch("ai_core.views.get_engine")
    def test_engine_called_with_correct_pet_profile(self, mock_get_engine):
        """
        Test that engine.predict() is called with PetProfile dataclass.
        
        Given: Valid pet profile JSON
        When: POST to /api/v1/ai/nutrition/
        Then: Engine's predict() method is called with PetProfile instance
        """
        # Arrange: Mock engine
        mock_engine = MagicMock()
        mock_engine.predict.return_value = DummyEngine().predict(None)
        mock_get_engine.return_value = mock_engine
        
        # Act: POST valid data
        response = self.client.post(self.url, self.valid_data, format="json")
        
        # Assert: Engine was called
        mock_engine.predict.assert_called_once()
        
        # Assert: Engine received PetProfile instance
        call_args = mock_engine.predict.call_args[0]
        self.assertEqual(len(call_args), 1)
        pet_profile = call_args[0]
        
        self.assertIsInstance(pet_profile, PetProfile)
        self.assertEqual(pet_profile.species, "dog")
        self.assertEqual(pet_profile.breed, "Golden Retriever")
        self.assertEqual(pet_profile.age_years, 3.5)
        self.assertEqual(pet_profile.weight_kg, 29.0)
