# cPanel Deployment Guide - AI Hub Updates

## 📋 What We Changed

1. ✅ Migrated from Chat Completions API to Responses API
2. ✅ Added Structured Outputs with Pydantic models
3. ✅ Added JSON fields to store structured data
4. ✅ Created modern, colorful UI for meal and health reports
5. ✅ Database migration for new fields
6. ✅ **REBUILT TAILWIND CSS with gradient classes**

---

## 🚀 Deployment Steps for cPanel

### IMPORTANT: Follow these steps IN ORDER

---

### Step 1: Upload the Compiled CSS File (CRITICAL for colors!)

**This is the most important step** - Without this, you won't see any colors or gradients.

#### Location on cPanel:
`/home/youruser/public_html/staticfiles/css/dist/styles.css`

OR if you use `theme/static/css/dist/` structure:
`/home/youruser/public_html/theme/static/css/dist/styles.css`

**Action:**
1. Open your local file: `theme/static/css/dist/styles.css` 
2. Copy ALL its content (it's a big file ~128KB)
3. Paste and overwrite the file on cPanel
4. Also copy to: `staticfiles/css/dist/styles.css` (after running collectstatic)

---

### Step 2: Copy Template Files

#### File 1: `aihub/templates/aihub/meal_result.html`
**Location on cPanel:** `/home/youruser/public_html/aihub/templates/aihub/meal_result.html`

**Action:** Copy the entire content from your local file and replace the file on cPanel

---

#### File 2: `aihub/templates/aihub/health_report.html`
**Location on cPanel:** `/home/youruser/public_html/aihub/templates/aihub/health_report.html`

**Action:** Copy the entire content from your local file and replace the file on cPanel

---

### Step 3: Copy Python Files

#### File 3: `aihub/views.py`
**Location on cPanel:** `/home/youruser/public_html/aihub/views.py`

**Action:** Copy the entire content from your local file and replace the file on cPanel

**Important:** This file contains the new Responses API code with Pydantic models

---

#### File 4: `aihub/models.py`
**Location on cPanel:** `/home/youruser/public_html/aihub/models.py`

**Action:** Copy the entire content from your local file and replace the file on cPanel

**Important:** This adds `content_json` and `summary_json` fields

---

#### File 5: Create Migration File
**Location on cPanel:** `/home/youruser/public_html/aihub/migrations/0003_add_structured_fields.py`

**Action:** Create this NEW file and paste the content

---

### Step 4: Run Commands in cPanel Terminal

Open cPanel Terminal and run these commands **in order**:

```bash
# 1. Navigate to your project directory
cd ~/public_html

# 2. Activate your virtual environment (adjust path if different)
source venv/bin/activate
# OR if your venv is named differently:
# source .venv/bin/activate

# 3. Run the migration to add JSON fields to database
python manage.py migrate aihub

# 4. Collect static files (IMPORTANT for CSS)
python manage.py collectstatic --noinput

# 5. Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 6. Restart your application
# This depends on your setup. Common options:

# If using Passenger (most common on cPanel):
touch tmp/restart.txt

# OR create restart.txt if tmp folder doesn't exist:
mkdir -p tmp && touch tmp/restart.txt
```

---

## ⚠️ Critical: CSS File Locations

The CSS file needs to be in **both** locations:

1. **Source:** `theme/static/css/dist/styles.css` (development)
2. **Production:** `staticfiles/css/dist/styles.css` (after collectstatic)

**To verify CSS is loaded:**
- Open your website
- Open browser DevTools (F12)
- Go to Network tab
- Reload page
- Look for `styles.css` - it should be ~128KB

---

## 🎨 Why Colors Weren't Showing

The issue was that Tailwind CSS v4 needs to be **rebuilt** whenever you use new utility classes (like gradients). The classes like:
- `bg-gradient-to-r`
- `from-indigo-600`
- `via-purple-600`
- `to-pink-500`

These were not in your old CSS file. Now they are included in the newly built `styles.css`.

---

## 🧪 Testing

After deployment, test these URLs:

1. Generate a meal recommendation: `/en/ai/recommend/{pet_id}/`
2. Generate a health report: `/en/ai/health-report/{pet_id}/`
3. Check if modern UI with colors appears

---

## 🆘 Troubleshooting

### If you see errors about `responses.parse`:

- Make sure you've updated `aihub/views.py` completely
- Check your OpenAI SDK version: `pip show openai`
- Should be version 1.x or higher

### If database errors occur:

```bash
# Check migration status
python manage.py showmigrations aihub

# If migration shows [ ] not applied:
python manage.py migrate aihub --fake-initial
```

### If colors don't show:

- Hard refresh browser (Ctrl+F5)
- Check if CSS file is loaded in browser dev tools
- Clear browser cache

---

## 📝 Files Summary

Files to copy/paste:
1. `aihub/templates/aihub/meal_result.html` (modern meal UI)
2. `aihub/templates/aihub/health_report.html` (modern health UI)
3. `aihub/views.py` (Responses API code)
4. `aihub/models.py` (JSON fields added)
5. `aihub/migrations/0003_add_structured_fields.py` (new migration)

Commands to run:
1. `cd ~/public_html`
2. `source venv/bin/activate`
3. `python manage.py migrate aihub`
4. `find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null`
5. `touch tmp/restart.txt`
6. `python manage.py collectstatic --noinput` (optional)

---

Need help? Check the error messages in cPanel error logs or Django debug output.
