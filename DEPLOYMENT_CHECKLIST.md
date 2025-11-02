# ✅ cPanel Deployment Checklist

## Files to Copy-Paste (in this order):

### 1. CSS File (MOST IMPORTANT!)
- [ ] Local file: `theme/static/css/dist/styles.css`
- [ ] cPanel location 1: `theme/static/css/dist/styles.css`
- [ ] cPanel location 2: `staticfiles/css/dist/styles.css` (after collectstatic)
- **Size should be ~128KB**

### 2. Base Template (CACHE-BUSTING!)
- [ ] `templates/base.html` (includes ?v=20251102 to force CSS reload)

### 3. AI Hub Template Files
- [ ] `aihub/templates/aihub/meal_result.html`
- [ ] `aihub/templates/aihub/health_report.html`

### 4. Python Files
- [ ] `aihub/views.py`
- [ ] `aihub/models.py`
- [ ] `aihub/migrations/0003_add_structured_fields.py` (create new file)

**Total: 7 files to upload**

## Commands to Run in cPanel Terminal:

```bash
cd ~/public_html
source venv/bin/activate
python manage.py migrate aihub
python manage.py collectstatic --noinput
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
mkdir -p tmp && touch tmp/restart.txt
```

## After Deployment:

- [ ] Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
- [ ] Check meal recommendation page - should see gradients
- [ ] Check health report page - should see colors
- [ ] Test generating new AI recommendations

## If Colors Still Don't Show:

1. Check browser DevTools (F12) → Network tab
2. Look for `styles.css` - should be ~128KB
3. If smaller, the CSS file didn't upload correctly
4. Re-upload the CSS file and run collectstatic again
