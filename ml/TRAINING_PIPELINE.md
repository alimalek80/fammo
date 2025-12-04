# ML Training Pipeline - Summary

## Overview

The FAMMO ML training pipeline is now complete with scripts for training and evaluating calorie prediction models.

## Available Scripts

### 1. `train_calorie_model.py` ✓
**Purpose**: Train a Random Forest regression model to predict daily calorie requirements

**Usage**:
```bash
python ml/scripts/train_calorie_model.py
python ml/scripts/train_calorie_model.py --input=ml/data/nutrition_logs.jsonl
python ml/scripts/train_calorie_model.py --output-model=ml/models/my_model.pkl
```

**Features Used**:
- Numeric: `weight_kg`, `age_years`, `body_condition_score`
- Categorical: `species`, `life_stage`, `breed_size_category`, `health_goal`

**Output**:
- `ml/models/calorie_regressor_v1.pkl` - Trained sklearn Pipeline
- `ml/models/calorie_regressor_v1.json` - Model metadata

**Key Features**:
- Handles small datasets gracefully (trains on all data if < 20 samples)
- Uses ColumnTransformer with StandardScaler and OneHotEncoder
- Random Forest with 200 trees, max_depth=10
- Prints training metrics (MAE, RMSE, R²)
- Shows feature importance

### 2. `evaluate_calorie_model.py` ✓
**Purpose**: Evaluate trained model against original OpenAI/aihub predictions

**Usage**:
```bash
python ml/scripts/evaluate_calorie_model.py
python ml/scripts/evaluate_calorie_model.py --input=ml/data/nutrition_logs.jsonl
python ml/scripts/evaluate_calorie_model.py --model=ml/models/my_model.pkl
```

**Metrics Computed**:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² (Coefficient of Determination)
- MAPE (Mean Absolute Percentage Error)

**Output Sections**:
1. Overall prediction metrics
2. Residual statistics
3. Prediction range comparison
4. Sample predictions (first 10)
5. Worst predictions (largest errors)
6. Performance by data source (api vs aihub)

### 3. `test_model_inference.py` ✓
**Purpose**: Quick test to verify model can be loaded and used for inference

**Usage**:
```bash
python ml/scripts/test_model_inference.py
```

**Output**: Sample predictions for cat, dog, and puppy profiles

### 4. `eda_nutrition_logs.py` ✓
**Purpose**: Full exploratory data analysis with visualizations

**Usage**:
```bash
python ml/scripts/eda_nutrition_logs.py
python ml/scripts/eda_nutrition_logs.py --input=ml/data/dog_logs.jsonl
```

**Generates**:
- Weight distribution by species
- Calorie distribution histogram
- Macronutrient box plots
- Age vs weight scatter plot

### 5. `quick_eda.py` ✓
**Purpose**: Fast text-based analysis without plotting dependencies

**Usage**:
```bash
python ml/scripts/quick_eda.py
```

## Current Results

### Test Run (13 cat samples from aihub backfill)

**Training Metrics**:
- MAE: 13.97 kcal/day
- RMSE: 18.76 kcal/day
- R²: -0.0000 (model predicts mean due to identical features)

**Evaluation Results**:
- All predictions: 236 kcal/day (the mean)
- True values range: 190-266 kcal/day
- MAPE: 6.21% average error

**Interpretation**:
The model performs poorly because all 13 training samples are identical:
- Same species (cat)
- Same weight (4.0 kg)
- Same age (1.2 years)
- Same body condition score (5)
- Same life stage (adult)
- Same health goal (maintenance)

The Random Forest learns to predict the mean (236 kcal/day) since there's no variance in features to learn from.

## Recommendations for Production Use

### 1. Collect Diverse Training Data
**Goal**: At least 500-1000 samples with variety

**Strategy**:
```bash
# Monitor growth over time
python manage.py shell -c "from ai_core.models import NutritionPredictionLog; print(f'Total logs: {NutritionPredictionLog.objects.count()}')"

# Export monthly
python manage.py export_nutrition_logs --output=ml/data/logs_$(date +%Y%m).jsonl

# Retrain quarterly
python ml/scripts/train_calorie_model.py
```

**Diversity needed**:
- Multiple species (dogs, cats)
- Various weight ranges (2-50+ kg)
- Different ages (puppies, adults, seniors)
- All health goals (weight_loss, maintenance, weight_gain, etc.)
- Different body condition scores (underweight to obese)

### 2. Feature Engineering

**Add derived features**:
```python
# In training script
X['weight_age_ratio'] = X['weight_kg'] / (X['age_years'] + 1)
X['is_senior'] = (X['life_stage'] == 'senior').astype(int)
X['needs_weight_management'] = X['health_goal'].isin(['weight_loss', 'weight_gain']).astype(int)
```

**Extract from input payload**:
- `activity_level` (sedentary, active, very active)
- `is_neutered` (affects metabolism)
- `health_conditions` (count or one-hot encode)
- `breed` (group into size categories or breed families)

### 3. Model Improvements

**Try different algorithms**:
```python
# Gradient Boosting (often better than RF)
from sklearn.ensemble import GradientBoostingRegressor
regressor = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, random_state=42)

# XGBoost (if installed)
from xgboost import XGBRegressor
regressor = XGBRegressor(n_estimators=200, learning_rate=0.1, random_state=42)

# Neural Network
from sklearn.neural_network import MLPRegressor
regressor = MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42)
```

**Hyperparameter tuning**:
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'regressor__n_estimators': [100, 200, 300],
    'regressor__max_depth': [5, 10, 15],
    'regressor__min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='neg_mean_absolute_error')
grid_search.fit(X_train, y_train)
```

### 4. Validation Strategy

**With enough data (>100 samples)**:
```python
# Use train/val/test split
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.2, random_state=42)

# Or use cross-validation
from sklearn.model_selection import cross_val_score
scores = cross_val_score(pipeline, X, y, cv=5, scoring='neg_mean_absolute_error')
```

### 5. Integration into Django

**Create `ai_core/proprietary_backend.py`**:
```python
import joblib
from pathlib import Path
from .interfaces import NutritionEngineInterface, PetProfile, ModelOutput

class ProprietaryEngine(NutritionEngineInterface):
    def __init__(self):
        model_path = Path(__file__).parent.parent / 'ml' / 'models' / 'calorie_regressor_v1.pkl'
        self.pipeline = joblib.load(model_path)
        self.model_version = "proprietary_v1"
    
    def predict(self, pet_profile: PetProfile) -> ModelOutput:
        # Prepare features
        features = {
            'weight_kg': pet_profile.weight_kg,
            'age_years': pet_profile.age_years,
            'body_condition_score': pet_profile.body_condition_score,
            'species': pet_profile.species,
            'life_stage': pet_profile.life_stage,
            'breed_size_category': pet_profile.breed_size_category,
            'health_goal': pet_profile.health_goal
        }
        
        import pandas as pd
        X = pd.DataFrame([features])
        
        # Predict
        calories = int(self.pipeline.predict(X)[0])
        
        # Build output
        return ModelOutput(
            calories_per_day=calories,
            calorie_range_min=int(calories * 0.9),
            calorie_range_max=int(calories * 1.1),
            protein_percent=35.0,  # Default or use another model
            fat_percent=25.0,
            carbohydrate_percent=40.0,
            diet_style="balanced",
            diet_style_confidence=0.85,
            risks={},
            model_version=self.model_version
        )
```

**Update `ai_core/engine.py`**:
```python
from .proprietary_backend import ProprietaryEngine

_ENGINE_REGISTRY = {
    "openai": OpenAIEngine,
    "proprietary": ProprietaryEngine,  # Add this
}
```

**Update `famo/settings.py`**:
```python
# Switch to proprietary model
AI_BACKEND = "proprietary"  # Was "openai"
```

### 6. A/B Testing

**Track both models**:
```python
# In views.py
openai_prediction = openai_engine.predict(pet_profile)
proprietary_prediction = proprietary_engine.predict(pet_profile)

# Log both for comparison
NutritionPredictionLog.objects.create(
    source="api_ab_test",
    backend="openai",
    output_payload=openai_prediction.to_dict()
)
NutritionPredictionLog.objects.create(
    source="api_ab_test",
    backend="proprietary",
    output_payload=proprietary_prediction.to_dict()
)

# Return one to user (randomly or based on user segment)
```

### 7. Cost Analysis

**OpenAI Costs** (as of Dec 2025):
- GPT-4o: ~$0.005 per prediction
- 1000 predictions/day = $5/day = $150/month

**Self-Hosted Costs**:
- Compute: ~$0.0001 per prediction (minimal CPU)
- Infrastructure: $20-50/month (shared server)
- 1000 predictions/day = $0.10/day = $3/month

**Break-even**: ~30-40 predictions per day

## Monitoring Checklist

- [ ] Track prediction latency (OpenAI vs proprietary)
- [ ] Monitor MAE/RMSE over time as data grows
- [ ] Set up alerts for prediction drift
- [ ] Log model version with each prediction
- [ ] A/B test before full cutover
- [ ] Keep fallback to OpenAI if proprietary fails
- [ ] Retrain monthly with new data
- [ ] Version control model artifacts

## File Locations

```
ml/
├── data/
│   ├── nutrition_logs.jsonl           # Exported training data
│   ├── eda_summary.csv                # Analysis output
│   └── *.png                          # Visualization plots
├── models/
│   ├── calorie_regressor_v1.pkl       # Trained model
│   └── calorie_regressor_v1.json      # Model metadata
├── scripts/
│   ├── train_calorie_model.py         # Training script ✓
│   ├── evaluate_calorie_model.py      # Evaluation script ✓
│   ├── test_model_inference.py        # Quick test ✓
│   ├── eda_nutrition_logs.py          # Full EDA ✓
│   └── quick_eda.py                   # Fast EDA ✓
├── requirements.txt                   # Python dependencies
└── README.md                          # Documentation
```

## Next Steps

1. **Short term** (1-2 weeks):
   - Collect more diverse prediction data via API usage
   - Export and analyze data quality
   - Identify data gaps and edge cases

2. **Medium term** (1-2 months):
   - Once 100+ diverse samples collected, retrain model
   - Run evaluation and compare to OpenAI
   - If MAE < 20-30 kcal/day, consider deploying

3. **Long term** (3-6 months):
   - Implement A/B testing framework
   - Gradually shift traffic to proprietary model
   - Monitor user satisfaction and prediction quality
   - Iterate on features and model architecture
