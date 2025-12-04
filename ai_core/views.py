"""
FAMMO AI Core API Views

This module provides DRF API endpoints for AI-powered nutrition predictions.
Mobile apps (Flutter) and web clients consume these endpoints to get personalized
pet nutrition recommendations and health risk assessments.

Endpoints:
- POST /api/v1/ai/nutrition/ - Generate nutrition prediction for a pet profile
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from ai_core.serializers import PetProfileSerializer, ModelOutputSerializer
from ai_core.engine import get_engine
from ai_core.models import NutritionPredictionLog


class NutritionPredictionView(APIView):
    """
    Generate AI-powered nutrition recommendations and health risk assessment.
    
    This endpoint accepts a complete pet profile in JSON format and returns
    personalized nutrition predictions including:
    - Daily caloric requirements
    - Macronutrient targets (protein, fat, carbohydrates)
    - Recommended diet style
    - Health risk scores across six categories
    - Feeding recommendations (meals per day, portion sizes)
    - Veterinary consultation flags and alerts
    
    **Method:** POST
    
    **Authentication:** Required (JWT token)
    
    **Request Body:**
    ```json
    {
        "species": "dog",
        "breed": "Golden Retriever",
        "breed_size_category": "large",
        "age_years": 3.5,
        "life_stage": "adult",
        "weight_kg": 29.0,
        "body_condition_score": 4,
        "sex": "male",
        "neutered": true,
        "activity_level": "moderate",
        "health_goal": "weight_loss",
        "existing_conditions": ["hip_dysplasia"],
        "food_allergies": ["chicken"]
    }
    ```
    
    **Response (200 OK):**
    ```json
    {
        "calories_per_day": 780,
        "calorie_range_min": 702,
        "calorie_range_max": 858,
        "protein_percent": 28,
        "fat_percent": 12,
        "carbohydrate_percent": 40,
        "diet_style": "weight_loss",
        "diet_style_confidence": 0.87,
        "risks": {
            "weight_risk": "high",
            "joint_risk": "medium",
            "digestive_risk": "low",
            "metabolic_risk": "medium",
            "kidney_risk": "low",
            "dental_risk": "low"
        },
        "meals_per_day": 2,
        "portion_size_grams": 195,
        "model_version": "1.0.0",
        "prediction_timestamp": "2025-12-01T14:32:15Z",
        "confidence_score": 0.85,
        "veterinary_consultation_recommended": false,
        "alert_messages": [
            "Weight loss target detected - reduce calories by 15-20%",
            "Monitor weight weekly and adjust portions as needed"
        ]
    }
    ```
    
    **Error Responses:**
    - 400 Bad Request: Invalid input data (validation errors)
    - 500 Internal Server Error: AI engine error
    
    **Example Usage (Flutter/Dart):**
    ```dart
    final response = await http.post(
        Uri.parse('https://api.fammo.ai/api/v1/ai/nutrition/'),
        headers: {
            'Authorization': 'Bearer $accessToken',
            'Content-Type': 'application/json',
        },
        body: jsonEncode(petProfileData),
    );
    ```
    """
    
    # TODO: Change to [permissions.IsAuthenticated] after initial testing
    # For now, allowing any access for easier Flutter integration testing
    permission_classes = [permissions.AllowAny]  # Will be IsAuthenticated in production
    
    def post(self, request):
        """
        Handle POST request to generate nutrition prediction.
        
        Flow:
        1. Validate input JSON with PetProfileSerializer
        2. Convert to PetProfile dataclass
        3. Call AI engine to generate prediction
        4. Serialize ModelOutput to JSON
        5. Return prediction to client
        
        Args:
            request: DRF Request object with pet profile JSON in request.data
        
        Returns:
            Response: JSON with nutrition prediction or error details
        """
        # Step 1: Validate input data
        input_serializer = PetProfileSerializer(data=request.data)
        
        if not input_serializer.is_valid():
            # Return validation errors with 400 status
            return Response(
                {
                    "detail": "Invalid pet profile data",
                    "errors": input_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Step 2: Convert validated data to PetProfile dataclass
            pet_profile = input_serializer.to_pet_profile()
            
            # Step 3: Get AI engine and generate prediction
            engine = get_engine()
            prediction_output = engine.predict(pet_profile)
            
            # Step 4: Serialize ModelOutput to JSON
            output_serializer = ModelOutputSerializer(prediction_output)
            
            # Step 5: Log the prediction to database (for training data)
            self._log_prediction(
                input_data=input_serializer.validated_data,
                output_data=output_serializer.data,
                backend=getattr(engine, '__class__', type(engine)).__name__.replace('Engine', '').lower(),
                source=request.META.get('HTTP_X_SOURCE', 'api')
            )
            
            # Step 6: Return successful prediction
            return Response(
                output_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except NotImplementedError as e:
            # Engine not yet implemented (OpenAI or Proprietary backend missing)
            return Response(
                {
                    "detail": "AI engine not yet implemented",
                    "error": str(e),
                    "message": "The AI prediction service is currently being configured. Please try again later."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        except ValueError as e:
            # Invalid data that passed serializer but failed in dataclass/engine
            return Response(
                {
                    "detail": "Invalid pet profile values",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Catch-all for unexpected errors
            return Response(
                {
                    "detail": "AI engine error",
                    "error": str(e),
                    "message": "An unexpected error occurred during prediction. Please try again or contact support."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _log_prediction(self, input_data, output_data, backend, source):
        """
        Log prediction to database for training data collection.
        
        Args:
            input_data: Validated input data (dict)
            output_data: Serialized output data (dict)
            backend: Backend name (e.g., "openai", "proprietary")
            source: Source of request (e.g., "api", "mobile", "web")
        """
        try:
            NutritionPredictionLog.objects.create(
                source=source,
                backend=backend,
                model_version=output_data.get('model_version', ''),
                # Pet metadata for quick filtering
                species=input_data.get('species', ''),
                life_stage=input_data.get('life_stage', ''),
                breed_size_category=input_data.get('breed_size_category', ''),
                health_goal=input_data.get('health_goal', ''),
                weight_kg=input_data.get('weight_kg'),
                age_years=input_data.get('age_years'),
                body_condition_score=input_data.get('body_condition_score'),
                # Full payloads
                input_payload=input_data,
                output_payload=output_data,
            )
        except Exception as e:
            # Log silently - don't break the API response if logging fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log nutrition prediction: {e}")
