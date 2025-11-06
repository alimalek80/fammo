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

## Social Login (Google) Setup

Enable the "Continue with Google" button without runtime errors:

1. Create OAuth 2.0 credentials in Google Cloud Console
	- App type: Web application
	- Authorized redirect URIs:
	  - http://127.0.0.1:8000/accounts/google/login/callback/
	  - http://localhost:8000/accounts/google/login/callback/
	  - https://YOUR_DOMAIN/accounts/google/login/callback/

2. Add credentials to environment (.env or cPanel env vars):
	- GOOGLE_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
	- GOOGLE_CLIENT_SECRET=xxxxxxxxxxxxx

3. Ensure `SITE_ID` in `famo/settings.py` matches an existing `Site` row (usually id=1).
	- In admin: Sites → confirm domain/name for id=1 (e.g., localhost or fammo.ai)

4. Run the management command to create/update and attach the SocialApp:
	```bash
	python manage.py setup_google_socialapp
	```

5. Reload login/signup pages. The Google button renders only when a `SocialApp` for provider `google` is linked to the current Site.

Troubleshooting:
| Symptom | Cause | Fix |
|---------|-------|-----|
| Button missing | No SocialApp linked | Run command above; confirm SITE_ID |
| DoesNotExist at provider_login_url | Template rendered without guard | Ensure updated templates with `google_enabled` condition deployed |
| Redirect mismatch error | Wrong URI in Google console | Add correct callback to OAuth client |

The management command is idempotent; re-run safely after updating credentials.

## If Colors Still Don't Show:

1. Check browser DevTools (F12) → Network tab
2. Look for `styles.css` - should be ~128KB
3. If smaller, the CSS file didn't upload correctly
4. Re-upload the CSS file and run collectstatic again
