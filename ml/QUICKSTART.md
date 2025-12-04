# Quick Start Guide

## 1. Export Data from Django

```bash
python manage.py export_nutrition_logs --output=ml/data/nutrition_logs.jsonl
```

## 2. Install ML Dependencies

```bash
pip install pandas matplotlib
# Or install all: pip install -r ml/requirements.txt
```

## 3. Run Analysis

### Option A: Quick EDA (Text-based, fast)
```bash
python ml/scripts/quick_eda.py
```

### Option B: Full EDA (With plots)
```bash
python ml/scripts/eda_nutrition_logs.py
```

## 4. Check Results

- **Console output**: Summary statistics
- **ml/data/eda_summary.csv**: Simplified data
- **ml/data/*.png**: Visualization plots

## Common Commands

```bash
# Export dogs only
python manage.py export_nutrition_logs --species=dog --output=ml/data/dog_logs.jsonl

# Export cats only  
python manage.py export_nutrition_logs --species=cat --output=ml/data/cat_logs.jsonl

# Export to CSV
python manage.py export_nutrition_logs --format=csv --output=ml/data/logs.csv

# Analyze specific file
python ml/scripts/eda_nutrition_logs.py --input=ml/data/dog_logs.jsonl
```

## File Structure

```
ml/
├── data/
│   ├── nutrition_logs.jsonl          # Exported data
│   ├── eda_summary.csv                # EDA output
│   └── *.png                          # Plots
├── scripts/
│   ├── quick_eda.py                   # Fast text analysis
│   └── eda_nutrition_logs.py          # Full analysis
├── notebooks/                         # Jupyter notebooks
├── requirements.txt                   # Python dependencies
└── README.md                          # Full documentation
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install pandas matplotlib
```

### "Input file not found"
First export data from Django:
```bash
python manage.py export_nutrition_logs --output=ml/data/nutrition_logs.jsonl
```

### "No data in database"
Run the backfill command:
```bash
python manage.py backfill_nutrition_logs_from_aihub
```

## Next Steps

1. Accumulate more prediction data through API usage
2. Periodically export and analyze trends
3. Use insights to improve prompts and model design
4. Eventually train custom ML model on accumulated data
