#!/bin/bash
# Quick cPanel Deployment Commands
# Copy and paste these commands ONE BY ONE in cPanel Terminal

# Step 1: Navigate to project
cd ~/public_html

# Step 2: Activate virtual environment
source venv/bin/activate
# (If your venv has different name, adjust above)

# Step 3: Run migration
python manage.py migrate aihub

# Step 4: Collect static files (IMPORTANT for CSS!)
python manage.py collectstatic --noinput

# Step 5: Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Step 6: Restart application
mkdir -p tmp && touch tmp/restart.txt

# Done! Hard refresh browser (Ctrl+F5) to see changes.
