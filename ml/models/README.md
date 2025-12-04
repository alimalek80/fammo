# Models Directory

This directory contains trained machine learning models for FAMMO nutrition prediction.

## Generated Models

Models are created by running:
```bash
python ml/scripts/train_calorie_model.py
```

Typical files:
- `calorie_regressor_v1.pkl` - Trained sklearn Pipeline
- `calorie_regressor_v1.json` - Model metadata

## Note

Model files (*.pkl) are excluded from git due to size. Regenerate models by training on your local data.
