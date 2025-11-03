# Pet Age Auto-Calculation Feature

## Overview
The pet profile now automatically calculates and displays the current age of pets based on their birth date. When users enter the age (years, months, weeks), the system calculates the birth date and stores it. From that point forward, the age is automatically calculated and updated day by day.

## How It Works

### 1. **Birth Date Calculation**
When a user enters a pet's age during creation or editing:
- The system calculates the pet's birth date by subtracting the entered age from today's date
- The birth date is stored in the `birth_date` field
- The original age values (years, months, weeks) are also kept for reference

### 2. **Dynamic Age Display**
When viewing a pet's profile:
- The system calculates the current age from the birth date
- Age is automatically updated without requiring user intervention
- Users see the most accurate age at any time

### 3. **Model Methods**

#### `calculate_birth_date_from_age()`
Converts user-entered age (years, months, weeks) into a calculated birth date.

#### `get_current_age()`
Returns the current age as a dictionary with:
- `years`: Number of full years
- `months`: Number of full months (0-11)
- `weeks`: Number of full weeks (0-3)
- `days`: Number of remaining days (0-6)
- `total_days`: Total age in days

#### `get_age_display()`
Returns a human-readable string of the pet's age, e.g., "2 years, 3 months, 1 week"

## Usage in Templates

### Using the model method directly:
```html
<p>Age: {{ pet.get_age_display }}</p>
```

### Using custom template tags:
```html
{% load pet_tags %}
<p>Age: {{ pet|pet_age }}</p>
<p>Years: {% pet_age_years pet %}</p>
<p>Months: {% pet_age_months pet %}</p>
<p>Weeks: {% pet_age_weeks pet %}</p>
```

## Benefits

1. **No Manual Updates Required**: Users don't need to manually update their pet's age
2. **Always Accurate**: Age is calculated in real-time based on the current date
3. **Precise Tracking**: Shows exact age including years, months, and weeks
4. **Backward Compatible**: Existing pets are automatically migrated using the `update_pet_birthdates` command

## Database Migration

A new field `birth_date` has been added to the Pet model:
```python
birth_date = models.DateField(null=True, blank=True, help_text="Calculated birth date based on age input")
```

To update existing pets after deployment:
```bash
python manage.py update_pet_birthdates
```

## Technical Details

### Dependencies
- `python-dateutil`: Used for accurate date calculations with `relativedelta`

### Form Processing
When a pet form is saved:
1. The `save()` method calculates the birth date from age inputs
2. Birth date is stored in the database
3. On future page loads, age is calculated from birth date

### Age Display in Templates
The pet detail template uses `{{ pet.get_age_display }}` to show the dynamically calculated age.

## Example

If a user enters:
- 2 years, 3 months, 1 week on November 3, 2025

The system:
1. Calculates birth date: ~July 27, 2023
2. Stores this birth date
3. When viewing the profile on December 1, 2025, it automatically shows: "2 years, 4 months, 0 weeks"

No manual update needed by the user!
