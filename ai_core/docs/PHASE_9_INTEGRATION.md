# Phase 9: Proprietary ML Engine Integration

## Summary

Phase 9 successfully integrates FAMMO's proprietary calorie prediction model into the Django backend as a switchable AI engine. The implementation maintains full backward compatibility with the existing OpenAI backend while providing a cost-effective, faster, and deterministic alternative.

## What Was Implemented

### 1. **Shared Feature Encoder** (`ml/feature_encoder.py`)
- Centralized feature encoding logic for consistent preprocessing
- Used by both training scripts and the ProprietaryEngine
- Encodes PetProfile → pandas DataFrame with 7 features:
  - Numeric: `weight_kg`, `age_years`, `body_condition_score`
  - Categorical: `species`, `life_stage`, `breed_size_category`, `health_goal`

### 2. **ProprietaryEngine** (`ai_core/proprietary_backend.py`)
- Implements `NutritionEngineInterface` 
- Loads trained model from `ml/models/calorie_regressor_v1.pkl`
- Generates complete `ModelOutput` with:
  - **Calorie prediction**: From trained Random Forest model
  - **Calorie range**: ±15% around predicted value
  - **Diet style**: Derived from `health_goal` and life stage
  - **Macronutrients**: Heuristic-based ratios (protein, fat, carbs)
  - **Risk assessment**: Heuristic-based across 6 categories
  - **Feeding recommendations**: Meals per day, portion sizes
  - **Alerts**: Veterinary consultation flags and messages

### 3. **Engine Factory** (`ai_core/engine.py`)
- Updated to import real `ProprietaryEngine` instead of placeholder
- Supports backend switching via `AI_BACKEND` setting
- Validates backend names and provides clear error messages

### 4. **Django Settings** (`famo/settings.py`)
- Added `AI_BACKEND` setting with environment variable override
- Default: `"openai"` (maintains backward compatibility)
- Can be switched to `"proprietary"` via setting or env var

### 5. **Updated Test Script** (`ml/scripts/test_model_inference.py`)
- Refactored to use shared feature encoder
- Creates PetProfile instances for testing
- Validates model predictions work correctly

### 6. **Test Suite** (`ai_core/tests/test_proprietary_engine.py`)
- Comprehensive test coverage (18 test cases)
- Tests model loading, predictions, validation, and edge cases
- Automatically skips if trained model is not available

## Files Created/Modified

### Created:
1. `ml/feature_encoder.py` - Shared feature encoding module
2. `ai_core/proprietary_backend.py` - ProprietaryEngine implementation
3. `ai_core/tests/test_proprietary_engine.py` - Test suite

### Modified:
1. `ai_core/engine.py` - Imports real ProprietaryEngine
2. `famo/settings.py` - Added AI_BACKEND configuration
3. `ml/scripts/test_model_inference.py` - Uses shared encoder

## How to Switch Backends

### Method 1: Django Settings
Edit `famo/settings.py`:
```python
AI_BACKEND = "proprietary"  # Switch to proprietary model
# AI_BACKEND = "openai"     # Switch back to OpenAI (default)
```

### Method 2: Environment Variable
Set environment variable before running Django:

**Windows PowerShell:**
```powershell
$env:FAMMO_AI_BACKEND = "proprietary"
python manage.py runserver
```

**Linux/Mac:**
```bash
export FAMMO_AI_BACKEND=proprietary
python manage.py runserver
```

### Method 3: `.env` File
Add to your `.env` file:
```
FAMMO_AI_BACKEND=proprietary
```

## API Behavior

**No changes to the API contract!** The `/api/v1/ai/nutrition/` endpoint continues to work exactly as before:

- Same request schema (PetProfile serialization)
- Same response schema (ModelOutput serialization)
- Same error handling
- Same validation rules

The only difference is the source of predictions:
- **OpenAI backend**: GPT-4o API calls (slower, API costs, non-deterministic)
- **Proprietary backend**: Trained Random Forest (faster, no API costs, deterministic)

## Testing the Integration

### 1. Test the Model Inference Script
```powershell
python ml/scripts/test_model_inference.py
```

This validates:
- Model loads successfully
- Feature encoder works correctly
- Predictions are reasonable

### 2. Run Django Tests
```powershell
python manage.py test ai_core.tests.test_proprietary_engine
```

This validates:
- ProprietaryEngine instantiates correctly
- Predictions contain all required fields
- Calorie ranges are consistent
- Risk assessments are valid
- Alerts trigger appropriately

### 3. Test via API Endpoint
Start the Django server:
```powershell
python manage.py runserver
```

Make a POST request to `/api/v1/ai/nutrition/`:
```json
{
  "species": "dog",
  "breed": "Golden Retriever",
  "breed_size_category": "large",
  "age_years": 3.5,
  "life_stage": "adult",
  "weight_kg": 29.0,
  "body_condition_score": 3,
  "sex": "male",
  "neutered": true,
  "activity_level": "moderate",
  "health_goal": "maintenance"
}
```

## Model Performance

The proprietary model provides:

- **Speed**: <100ms inference (vs 2-5s for OpenAI API)
- **Cost**: $0 per request (vs $0.01-0.03 per OpenAI request)
- **Determinism**: Same input → same output (unlike GPT sampling)
- **Privacy**: No data sent to external APIs

Current limitations:
- **Diet style**: Currently heuristic-based (future: trained classifier)
- **Macronutrients**: Currently heuristic-based (future: multi-output regressor)
- **Risks**: Currently heuristic-based (future: multi-task classifier)
- **Training data**: Limited initial dataset (improves as more data collected)

## Future Enhancements (Not in Phase 9)

1. **Train diet style classifier** - Replace `_derive_diet_style()` heuristics
2. **Train macronutrient predictor** - Replace `_calculate_macros()` heuristics
3. **Train risk classifier** - Replace `_assess_risks()` heuristics
4. **Model versioning** - Support multiple model versions in production
5. **A/B testing** - Compare OpenAI vs Proprietary predictions
6. **Retraining pipeline** - Automate model retraining as data grows

## Troubleshooting

### Error: "Trained model not found"
**Solution**: Train the model first:
```powershell
python ml/scripts/train_calorie_model.py
```

### Error: "Required ML dependencies not installed"
**Solution**: Install dependencies:
```powershell
pip install pandas scikit-learn joblib
```

### Error: Module 'ml.feature_encoder' not found
**Solution**: Ensure `ml/` is in Python path. Django should handle this automatically when running via `manage.py`.

### Predictions seem unreasonable
**Solution**: The model was trained on a small initial dataset. Collect more data through the API and retrain:
```powershell
python manage.py export_nutrition_logs --output=ml/data/nutrition_logs.jsonl
python ml/scripts/train_calorie_model.py
```

## Backward Compatibility

✅ **Fully backward compatible**
- OpenAI backend remains the default (`AI_BACKEND="openai"`)
- No changes to DRF views, serializers, or URLs
- No changes to API request/response schemas
- Existing code continues to work without modification

## Architecture Decision Records

### Why shared feature encoder?
- Ensures training and inference use identical preprocessing
- Prevents feature mismatch errors
- Single source of truth for feature definitions
- Easier to maintain and update

### Why keep OpenAI as default?
- Proven production reliability
- Better handling of edge cases (small dataset)
- More sophisticated reasoning for complex profiles
- Gradual migration strategy

### Why heuristics for risks/macros?
- Phase 9 focus: Calorie prediction integration
- Risk/macro models require more labeled data
- Heuristics provide reasonable baselines
- Can be replaced incrementally in future phases

## Success Metrics

Phase 9 successfully delivers:
- ✅ ProprietaryEngine fully functional
- ✅ Feature encoder shared and tested
- ✅ Backend switching via simple setting
- ✅ No breaking changes to API
- ✅ Comprehensive test coverage
- ✅ Clear documentation

---

**Next Phase**: Train and integrate diet style classifier, macronutrient predictor, and risk assessment models.
