# cPanel Deployment Checklist - Async Geocoding Fix

## Quick Deployment (5 minutes)

### Step 1: Pull Code
```bash
cd /home/fammkoqw/public_html/fammo
git pull origin main
```

### Step 2: Verify Packages
```bash
# Should show: geopy 2.4.1 already installed
pip install geopy

# Optional: Install Celery for better async (not required)
# pip install celery redis
```

### Step 3: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 4: Restart Application
In cPanel:
- Go to **Multi PHP Manager** OR **Python Applications**
- Find your FAMMO application
- Click **Restart**

OR via SSH:
```bash
# Kill any running processes
pkill -f "python manage.py"

# Start server again (if using manual startup)
# Or cPanel will auto-restart on next request
```

## What's Fixed

✅ **Admin panel no longer crashes** when editing clinic addresses
✅ **API registration returns instantly** without waiting for geocoding
✅ **Coordinates updated in background** safely
✅ **Server stable** even if Google API is slow

## Testing After Deployment

1. **Test Admin Edit**:
   - Go to `/admin/vets/clinic/`
   - Edit any clinic's address
   - Click Save → Should return immediately ✅

2. **Test API**:
   ```bash
   curl -X POST https://fammo.ai/api/v1/clinics/register/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123","clinic_name":"Test Clinic"}'
   # Should return 201 instantly
   ```

3. **Check Logs** for geocoding:
   ```bash
   tail -f /home/fammkoqw/public_html/fammo/logs/django.log | grep GEOCODE
   ```

## Files Changed

1. **vets/models.py** - Removed blocking geocoding from Clinic.save()
2. **vets/tasks.py** - NEW: Async geocoding task
3. **api/views.py** - Removed blocking geocoding from registration
4. **CPANEL_GEOCODING_FIX.md** - Full documentation

## Rollback (if needed)

```bash
git revert HEAD --no-edit
python manage.py collectstatic --noinput
# Restart application
```

## Support

If you see errors:
- Check logs: `tail -f logs/django.log`
- Look for `[GEOCODING]` or `[GEOCODE_TASK]` messages
- Verify `GOOGLE_MAPS_API_KEY` is set in .env
- Verify geopy installed: `pip list | grep geopy`

---

**Deployment Date**: [Your Date]  
**Status**: Ready for Live
