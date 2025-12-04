# ML Experiments for FAMMO

This directory contains machine learning experiments, exploratory data analysis (EDA), and model training scripts for the FAMMO nutrition prediction system.

## Directory Structure

```
ml/
├── data/              # Exported training data (JSONL, CSV)
├── notebooks/         # Jupyter notebooks for interactive analysis
├── scripts/           # Python scripts for EDA and training
└── README.md          # This file
```

## Setup

This folder is separate from the Django backend. Install dependencies in a dedicated environment:

```bash
# Option 1: Use the existing Django .venv (if pandas/matplotlib already installed)
# Just activate and run scripts

# Option 2: Create a separate ML virtual environment
python -m venv ml_env
ml_env\Scripts\activate  # On Windows
source ml_env/bin/activate  # On Linux/Mac

# Install ML dependencies
pip install -r ml/requirements.txt
```

Or install in your existing Django environment:

```bash
pip install pandas matplotlib seaborn scikit-learn jupyter
```

## Workflow

### 1. Export Training Data

From the Django project root, export nutrition logs:

```bash
# Export all logs
python manage.py export_nutrition_logs --output=ml/data/nutrition_logs.jsonl

# Export specific subsets
python manage.py export_nutrition_logs --species=dog --output=ml/data/dog_logs.jsonl
python manage.py export_nutrition_logs --species=cat --output=ml/data/cat_logs.jsonl
python manage.py export_nutrition_logs --format=csv --output=ml/data/nutrition_logs.csv
```

### 2. Run EDA

Analyze the exported data:

```bash
python ml/scripts/eda_nutrition_logs.py
```

This will generate:
- Summary statistics printed to console
- Distribution plots saved to `ml/data/`

### 3. Train Models

(Future: Add model training scripts here)

## Data Format

The exported JSONL files contain one JSON object per line with the following structure:

```json
{
  "id": 1,
  "created_at": "2025-12-02T11:16:56.642823+00:00",
  "source": "api",
  "backend": "openai",
  "model_version": "gpt-4o-2024-08-06",
  "species": "dog",
  "life_stage": "adult",
  "breed_size_category": "medium",
  "health_goal": "weight_loss",
  "weight_kg": 15.5,
  "age_years": 5.0,
  "body_condition_score": 7,
  "input": { ... },
  "output": { ... }
}
```

## Notes

- This folder is for **offline experiments only** - not part of the Django app
- Use version control for scripts, but consider `.gitignore` for large data files
- Export fresh data periodically as more predictions are logged
