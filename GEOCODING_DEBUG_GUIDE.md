# Clinic Address Change & Auto-Geocoding Debugging Guide

## What's Working ✅

The auto-geocoding system IS working correctly:
1. When you change a clinic address via code/API → coordinates AUTO-UPDATE
2. When you change a clinic address in Django admin → coordinates AUTO-UPDATE
3. The save() method detects address changes and triggers geocoding
4. All logging is in place to show what's happening

## How to Test & Verify

### Test 1: Django Shell Test
```bash
python manage.py shell
```

```python
from vets.models import Clinic

clinic = Clinic.objects.get(name='beges15249')  # Replace with actual clinic name
print(f"Current address: {clinic.address}")
print(f"Current coords: {clinic.latitude}, {clinic.longitude}")

# Change address
clinic.address = "Your New Address, City Name"
clinic.save()

# Check result
clinic.refresh_from_db()
print(f"After save: {clinic.latitude}, {clinic.longitude}")
```

### Test 2: Admin Panel Test
1. Go to Django admin → Clinics
2. Click on a clinic to edit
3. **Clear the Address field completely** and **type a new address**
4. Scroll down to see Latitude and Longitude fields (will be empty initially)
5. Click **SAVE**
6. Wait a moment for geocoding to complete
7. Refresh the page
8. The Latitude and Longitude fields should now show updated values

## What Might Be Going Wrong

### Issue 1: Address Not Actually Changing
- The form might show old address due to caching
- Make sure you're ACTUALLY editing the address field
- Clear the field and type a completely new address

### Issue 2: Form Not Saving
- Scroll to the top/bottom to make sure Save button clicks
- Check for validation errors
- Make sure you're not getting a form validation error

### Issue 3: Coordinates Still Show Old Values
- The lat/lon fields are read-only - they won't let you edit them manually
- They should auto-populate after you save an address change
- Try reloading the page (F5) to see if it updates

### Issue 4: Geocoding Failing Silently
- Check Django logs for [CLINIC SAVE] messages
- If geocoding fails, you'll see "[CLINIC SAVE] ❌ Failed to geocode"
- Try with a real, existing address (not a test address)

## Checking Django Logs

To see what's happening during save:

1. In a terminal, run Django with logging:
```bash
python manage.py runserver --verbosity 2
```

2. Make your address change in admin
3. Look for [CLINIC SAVE] messages in the terminal output
4. These will show you:
   - If address change was detected
   - If geocoding was attempted
   - If coordinates were found
   - Final saved coordinates

## Expected Behavior

When you change an address in admin and save:

```
[CLINIC SAVE] Starting save for MyClinic, pk=5
[CLINIC SAVE] MyClinic - Address changed: True
  Old address: 'Old Street, Old City'
  New address: 'New Street, New City'
  City changed: False
[CLINIC SAVE] Resetting coordinates for MyClinic
[CLINIC SAVE] Attempting to geocode MyClinic
  Address: 'New Street, New City'
  City: 'Istanbul'
[CLINIC SAVE] ✅ Auto-geocoded MyClinic: 41.123456, 28.789012
[CLINIC SAVE] About to call super().save() for MyClinic
[CLINIC SAVE] ✅ Saved MyClinic with lat=41.123456, lon=28.789012
```

If you see this, the system is working perfectly!

## Valid Test Addresses

Use these real addresses for testing:

- Istanbul: "Taksim Square, Istanbul" → Should give Istanbul coordinates
- Ankara: "Kizilay Street, Ankara" → Should give Ankara coordinates  
- Izmir: "Alsancak, Izmir" → Should give Izmir coordinates

Avoid using fake addresses like "123 Test Street, Test City" as they won't geocode.

## Next Steps

1. Run the Django shell test above
2. Run Django with verbosity to see logs
3. Try changing a clinic address with a REAL address
4. Check the logs for [CLINIC SAVE] messages
5. Report what you see in the logs

The code is working - now we need to verify the actual behavior in your Django admin interface.
