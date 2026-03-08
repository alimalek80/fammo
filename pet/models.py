from django.db import models
from django.conf import settings
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

class PetType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Gender(models.Model):
    name = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name
    
class AgeCategory(models.Model):
    name = models.CharField(max_length=50)
    pet_type = models.ForeignKey(PetType, on_delete=models.CASCADE, related_name='age_categories')
    order = models.PositiveIntegerField(default=0, help_text="Controls display order (smallest first)")

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.pet_type.name})"
    
class Breed(models.Model):
    pet_type = models.ForeignKey(PetType, on_delete=models.CASCADE, related_name='breeds')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.pet_type.name})"
    
class FoodType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class FoodFeeling(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.name

class FoodImportance(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class BodyType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.name
    
class ActivityLevel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)  # Add this field

    class Meta:
        ordering = ['order', 'name']  # Default ordering

    def __str__(self):
        return self.name

class FoodAllergy(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)  # Add this

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
    
class HealthIssue(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)  # Add this

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class TreatFrequency(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Pet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pets')
    image = models.ImageField(upload_to='pet_images/', null=True, blank=True)
    name = models.CharField(max_length=100)
    pet_type = models.ForeignKey(PetType, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    neutered = models.BooleanField(null=True, blank=True)
    age_category = models.ForeignKey('AgeCategory', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Registration tracking fields
    registration_date = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="When the pet profile was created")
    
    # Age at registration (user input)
    age_at_registration_years = models.PositiveIntegerField(null=True, blank=True, help_text="Pet's age in years at registration")
    age_at_registration_months = models.PositiveIntegerField(null=True, blank=True, help_text="Pet's age in months at registration")
    age_at_registration_weeks = models.PositiveIntegerField(null=True, blank=True, help_text="Pet's age in weeks at registration")
    
    # Store the calculated birth date based on registration date and initial age input
    birth_date = models.DateField(null=True, blank=True, help_text="Calculated birth date based on age at registration")
    
    # Age at registration date (user input - editable)
    age_years = models.PositiveIntegerField(null=True, blank=True, help_text="Pet's age in years at registration (editable)")
    age_months = models.PositiveIntegerField(null=True, blank=True, help_text="Pet's age in months at registration (editable)")
    age_weeks = models.PositiveIntegerField(null=True, blank=True, help_text="Pet's age in weeks at registration (editable)")
    
    # Automatically calculated current age (read-only)
    current_age_years = models.PositiveIntegerField(null=True, blank=True, help_text="Current age in years (auto-calculated)")
    current_age_months = models.PositiveIntegerField(null=True, blank=True, help_text="Current age in months (auto-calculated)")
    current_age_weeks = models.PositiveIntegerField(null=True, blank=True, help_text="Current age in weeks (auto-calculated)")
    
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    unknown_breed = models.BooleanField(default=False, help_text="Check if breed is unknown")
    food_types = models.ManyToManyField(FoodType, blank=True, related_name='pets')
    food_feeling = models.ForeignKey(FoodFeeling, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    food_importance = models.ForeignKey(FoodImportance, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    body_type = models.ForeignKey(BodyType, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    activity_level = models.ForeignKey(ActivityLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')
    food_allergies = models.ManyToManyField('FoodAllergy', blank=True, related_name='pets')
    food_allergy_other = models.CharField(max_length=255, blank=True, null=True)
    health_issues = models.ManyToManyField('HealthIssue', blank=True, related_name='pets')
    treat_frequency = models.ForeignKey('TreatFrequency', on_delete=models.SET_NULL, null=True, blank=True, related_name='pets')

    def calculate_birth_date_from_registration(self):
        """Calculate birth date from age at registration and registration date"""
        # Use the main age fields (which represent age at registration)
        years = self.age_years or 0
        months = self.age_months or 0
        weeks = self.age_weeks or 0
        
        if not any([years, months, weeks]):
            return None
        
        # Use registration date for calculation, fallback to today if not available
        reference_date = self.registration_date.date() if self.registration_date else date.today()
        
        # Calculate birth date from registration date and entered age
        birth_date = reference_date - relativedelta(years=years, months=months, weeks=weeks)
        return birth_date
    
    def get_age_at_registration(self):
        """Get the age that was entered at registration time"""
        years = self.age_years or 0
        months = self.age_months or 0
        weeks = self.age_weeks or 0
        
        return {
            'years': years,
            'months': months,
            'weeks': weeks,
            'total_days': (years * 365) + (months * 30) + (weeks * 7)
        }
    
    def get_current_age(self):
        """Get the current age calculated from birth_date"""
        if not self.birth_date:
            # Fallback to stored values if no birth_date
            return {
                'years': self.current_age_years or 0,
                'months': self.current_age_months or 0,
                'weeks': self.current_age_weeks or 0,
                'total_days': 0
            }
        
        today = date.today()
        delta = relativedelta(today, self.birth_date)
        
        return {
            'years': delta.years,
            'months': delta.months,
            'weeks': delta.days // 7,
            'days': delta.days % 7,
            'total_days': (today - self.birth_date).days
        }
    
    def update_current_age_fields(self):
        """Update the current age fields based on calculated current age"""
        current_age = self.get_current_age()
        self.current_age_years = current_age['years']
        self.current_age_months = current_age['months']
        self.current_age_weeks = current_age['weeks']
    
    def get_age_at_registration_display(self):
        """Get a formatted string for displaying age at registration"""
        age = self.get_age_at_registration()
        parts = []
        
        if age['years'] > 0:
            parts.append(f"{age['years']}y")
        if age['months'] > 0:
            parts.append(f"{age['months']}m")
        if age['weeks'] > 0:
            parts.append(f"{age['weeks']}w")
        
        return ' '.join(parts) if parts else '0'
    
    def get_weight_reminder_info(self):
        """Get weight reminder information based on species and age"""
        if not self.pet_type or not self.birth_date:
            return None
            
        from django.utils import timezone
        
        # Get latest weight record
        latest_record = self.weight_records.order_by('-recorded_at', '-created_at').first()
        
        # Get current age info
        current_age = self.get_current_age()
        current_age_months = (current_age['years'] * 12) + current_age['months']
        
        # Define reminder intervals based on species and age
        pet_type_name = self.pet_type.name.lower()
        
        if pet_type_name == 'dog':
            if current_age_months < 6:  # Less than 6 months
                reminder_days = 14
            elif current_age_months < 84:  # 6 months to less than 7 years (7*12=84)
                reminder_days = 30 
            else:  # 7 years or older
                reminder_days = 21
        elif pet_type_name == 'cat':
            if current_age_months < 2:  # Less than 2 months  
                reminder_days = 7
            elif current_age_months < 120:  # 2 months to less than 10 years (10*12=120)
                reminder_days = 30
            else:  # 10 years or older
                reminder_days = 21
        else:
            # Default for other pet types
            reminder_days = 30
            
        # Check if reminder is needed
        if not latest_record:
            return {
                'type': 'first_weight',
                'message': f"No weight records yet for {self.name}. Adding the first weight measurement will help track their health over time.",
                'reminder_days': reminder_days
            }
            
        days_since_last = (timezone.now().date() - latest_record.recorded_at).days
        
        if days_since_last >= reminder_days:
            return {
                'type': 'overdue',
                'message': f"It's been {days_since_last} days since {self.name}'s last weight record. For a {current_age['years']}y {current_age['months']}m old {pet_type_name}, we recommend weighing every {reminder_days} days.",
                'days_overdue': days_since_last - reminder_days, 
                'reminder_days': reminder_days
            }
            
        return None  # No reminder needed
    
    def track_field_changes(self, old_instance, changed_by=None, change_reason='user_update'):
        """Track changes to important fields and create change logs"""
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        
        # Define important fields to track
        important_fields = {
            'weight': 'weight',
            'activity_level': 'activity_level_id', 
            'food_feeling': 'food_feeling_id',
            'food_importance': 'food_importance_id',
            'body_type': 'body_type_id',
            'treat_frequency': 'treat_frequency_id',
            'neutered': 'neutered',
            'food_allergy_other': 'food_allergy_other',
        }
        
        # Track simple field changes
        for display_name, field_name in important_fields.items():
            old_value = getattr(old_instance, field_name) if old_instance else None
            new_value = getattr(self, field_name)
            
            if old_value != new_value:
                # Special handling for foreign key fields (store readable names)
                if field_name.endswith('_id'):
                    old_display = getattr(old_instance, display_name).name if old_value and hasattr(old_instance, display_name) else None
                    new_display = getattr(self, display_name).name if new_value and hasattr(self, display_name) else None
                    
                    PetDataChangeLog.objects.create(
                        pet=self,
                        field_name=display_name,
                        old_value=old_display,
                        new_value=new_display,
                        changed_by=changed_by,
                        change_reason=change_reason
                    )
                else:
                    # Handle simple fields
                    PetDataChangeLog.objects.create(
                        pet=self,
                        field_name=field_name,
                        old_value=str(old_value) if old_value is not None else None,
                        new_value=str(new_value) if new_value is not None else None,
                        changed_by=changed_by,
                        change_reason=change_reason
                    )
    
    def track_m2m_changes(self, old_instance, changed_by=None, change_reason='user_update'):
        """Track changes to many-to-many fields after save"""
        if not old_instance:
            return  # Skip for new instances
            
        import json
        
        # Define M2M fields to track  
        m2m_fields = ['food_types', 'food_allergies', 'health_issues']
        
        for field_name in m2m_fields:
            old_values = set(obj.name for obj in getattr(old_instance, field_name).all()) if old_instance else set()
            new_values = set(obj.name for obj in getattr(self, field_name).all())
            
            if old_values != new_values:
                PetDataChangeLog.objects.create(
                    pet=self,
                    field_name=field_name,
                    old_value=json.dumps(list(old_values)) if old_values else None,
                    new_value=json.dumps(list(new_values)) if new_values else None,
                    changed_by=changed_by,
                    change_reason=change_reason
                )
    
    def should_create_condition_snapshot(self, old_instance=None):
        """Determine if a condition snapshot should be created"""
        if not old_instance:
            return True  # Always create snapshot for new pets
            
        # Define significant changes that warrant a snapshot
        significant_changes = [
            'weight', 'activity_level', 'body_type', 
            'food_feeling', 'food_importance', 'treat_frequency'
        ]
        
        for field in significant_changes:
            old_value = getattr(old_instance, field) if old_instance else None
            new_value = getattr(self, field)
            if old_value != new_value:
                return True
                
        # Check M2M changes
        if old_instance:
            m2m_fields = ['food_types', 'food_allergies', 'health_issues']
            for field_name in m2m_fields:
                old_values = set(obj.id for obj in getattr(old_instance, field_name).all())
                new_values = set(obj.id for obj in getattr(self, field_name).all())
                if old_values != new_values:
                    return True
                    
        return False

    def get_age_display(self):
        """Get a formatted string for displaying current age"""
        age = self.get_current_age()
        parts = []
        
        if age['years'] > 0:
            parts.append(f"{age['years']}y")
        if age['months'] > 0:
            parts.append(f"{age['months']}m")
        if age['weeks'] > 0:
            parts.append(f"{age['weeks']}w")
        if age.get('days', 0) > 0 and not parts:  # Only show days if no other units
            parts.append(f"{age['days']}d")
        
        return ' '.join(parts) if parts else '0d'

    @property
    def total_age_in_days(self):
        """Calculate pet's total current age in days"""
        if self.birth_date:
            return (date.today() - self.birth_date).days
        else:
            # Fallback calculation from current age fields
            current_years = self.current_age_years or 0
            current_months = self.current_age_months or 0
            current_weeks = self.current_age_weeks or 0
            return (current_years * 365) + (current_months * 30) + (current_weeks * 7)

    def should_transition_age_category(self):
        """Check if pet should transition to next age category based on current age"""
        if not self.birth_date or not self.age_category or not self.pet_type:
            return None
        
        current_age = self.get_current_age()
        current_age_months = (current_age['years'] * 12) + current_age['months']
        
        # Find the next transition rule for this pet
        try:
            next_transition = AgeTransitionRule.objects.filter(
                pet_type=self.pet_type,
                from_category=self.age_category,
                transition_age_months__lte=current_age_months
            ).order_by('transition_age_months').first()
            
            return next_transition.to_category if next_transition else None
        except:
            return None

    def transition_to_age_category(self, new_category, reason="age_progression"):
        """Transition pet to new age category and save historical data"""
        if not new_category or self.age_category == new_category:
            return False
        
        try:
            # End current age period if exists
            current_history = self.age_history.filter(ended_at__isnull=True).first()
            if current_history:
                current_history.ended_at = timezone.now()
                current_history.save()
            
            # Save condition snapshot before transition
            self._save_condition_snapshot(reason)
            
            # Update pet's age category
            old_category = self.age_category
            self.age_category = new_category
            self.save()
            
            # Start new age period
            current_age = self.get_current_age()
            PetAgeHistory.objects.create(
                pet=self,
                age_category=new_category,
                age_months_at_start=(current_age['years'] * 12) + current_age['months'],
                transition_reason=reason
            )
            
            return True
        except Exception as e:
            # Log error but don't break the application
            print(f"Error transitioning {self.name} to {new_category}: {e}")
            return False

    def _save_condition_snapshot(self, reason="periodic_snapshot"):
        """Save current pet condition as a snapshot"""
        try:
            snapshot = PetConditionSnapshot.objects.create(
                pet=self,
                age_category=self.age_category,
                weight=self.weight,
                activity_level=self.activity_level,
                food_feeling=self.food_feeling,
                food_importance=self.food_importance,
                body_type=self.body_type,
                treat_frequency=self.treat_frequency,
                food_allergy_other=self.food_allergy_other,
                transition_reason=reason
            )
            
            # Save many-to-many relationships through intermediate models
            for food_type in self.food_types.all():
                PetConditionSnapshotFoodTypes.objects.create(
                    snapshot=snapshot,
                    food_type=food_type
                )
            
            for food_allergy in self.food_allergies.all():
                PetConditionSnapshotFoodAllergies.objects.create(
                    snapshot=snapshot,
                    food_allergy=food_allergy
                )
            
            for health_issue in self.health_issues.all():
                PetConditionSnapshotHealthIssues.objects.create(
                    snapshot=snapshot,
                    health_issue=health_issue
                )
            
            return snapshot
        except Exception as e:
            print(f"Error saving condition snapshot for {self.name}: {e}")
            return None

    def check_and_update_age_category(self):
        """Check if pet needs age category update and perform it"""
        new_category = self.should_transition_age_category()
        if new_category:
            return self.transition_to_age_category(new_category, "automatic_update")
        return False

    def get_age_progression_timeline(self):
        """Get pet's age progression history with snapshots"""
        timeline = []
        
        # Get age history with related snapshots
        age_periods = self.age_history.all().order_by('started_at')
        
        for period in age_periods:
            # Get snapshots for this age period
            snapshots = self.condition_snapshots.filter(
                age_category=period.age_category,
                snapshot_date__gte=period.started_at
            )
            if period.ended_at:
                snapshots = snapshots.filter(snapshot_date__lte=period.ended_at)
            
            timeline.append({
                'age_category': period.age_category.name,
                'started_at': period.started_at,
                'ended_at': period.ended_at,
                'age_months_at_start': period.age_months_at_start,
                'transition_reason': period.transition_reason,
                'snapshots_count': snapshots.count(),
                'is_current': period.ended_at is None
            })
        
        return timeline

    def save(self, *args, **kwargs):
        """Override save to handle change tracking, snapshots, and age calculations"""
        # Get old instance for change tracking
        old_instance = None
        if self.pk:
            try:
                old_instance = Pet.objects.select_related(
                    'activity_level', 'food_feeling', 'food_importance', 
                    'body_type', 'treat_frequency'
                ).prefetch_related(
                    'food_types', 'food_allergies', 'health_issues'
                ).get(pk=self.pk)
            except Pet.DoesNotExist:
                pass
        
        # Extract change tracking info from kwargs
        changed_by = kwargs.pop('changed_by', None)
        change_reason = kwargs.pop('change_reason', 'user_update')
        skip_tracking = kwargs.pop('skip_tracking', False)
        
        # Sync registration age fields with main age fields (for historical tracking) 
        if any([self.age_years, self.age_months, self.age_weeks]):
            self.age_at_registration_years = self.age_years
            self.age_at_registration_months = self.age_months
            self.age_at_registration_weeks = self.age_weeks
        
        # Calculate birth_date from registration age and registration date
        if not self.birth_date or self._birth_date_needs_recalculation():
            self.birth_date = self.calculate_birth_date_from_registration()
        
        # Update current age fields automatically
        self.update_current_age_fields()
        
        # Check if snapshot is needed before saving
        should_snapshot = not skip_tracking and self.should_create_condition_snapshot(old_instance)
        
        # Save the instance
        super().save(*args, **kwargs)
        
        # Track changes after save (but before M2M tracking)
        if not skip_tracking and old_instance:
            self.track_field_changes(old_instance, changed_by, change_reason)
        
        # Track M2M changes after save
        if not skip_tracking:
            self.track_m2m_changes(old_instance, changed_by, change_reason) 
        
        # Create condition snapshot if warranted
        if should_snapshot:
            snapshot_reason = change_reason if change_reason != 'user_update' else 'profile_update'
            self._save_condition_snapshot(snapshot_reason)
    
    def _birth_date_needs_recalculation(self):
        """Check if birth_date needs to be recalculated due to changed registration age"""
        if not self.pk:  # New instance
            return True
        
        # Check if registration age fields changed
        try:
            old_instance = Pet.objects.get(pk=self.pk)
            return (old_instance.age_years != self.age_years or 
                   old_instance.age_months != self.age_months or 
                   old_instance.age_weeks != self.age_weeks)
        except Pet.DoesNotExist:
            return True

    def __str__(self):
        return f"{self.name} ({self.user.email})"
    
    def get_full_profile_for_ai(self):
        """Return a detailed, human-readable string of all pet info for AI prompts."""
        registration_age = self.get_age_at_registration()
        current_age = self.get_current_age()
        profile = [
            f"Name: {self.name}",
            f"Species: {self.pet_type.name if self.pet_type else 'N/A'}",
            f"Breed: {self.breed.name if self.breed else 'N/A'}",
            f"Gender: {self.gender.name if self.gender else 'N/A'}",
            f"Neutered: {'Yes' if self.neutered else 'No'}",
            f"Age at Registration: {registration_age['years']} years, {registration_age['months']} months, {registration_age['weeks']} weeks",
            f"Current Age: {current_age['years']} years, {current_age['months']} months, {current_age['weeks']} weeks",
            f"Age Category: {self.age_category.name if self.age_category else 'N/A'}",
            f"Weight: {self.weight or 'N/A'} kg",
            f"Body Type: {self.body_type.name if self.body_type else 'N/A'}",
            f"Activity Level: {self.activity_level.name if self.activity_level else 'N/A'}",
            f"Food Types: {', '.join([ft.name for ft in self.food_types.all()]) or 'None'}",
            f"Food Feeling: {self.food_feeling.name if self.food_feeling else 'N/A'}",
            f"Food Importance: {self.food_importance.name if self.food_importance else 'N/A'}",
            f"Treat Frequency: {self.treat_frequency.name if self.treat_frequency else 'N/A'}",
            f"Health Issues: {', '.join([hi.name for hi in self.health_issues.all()]) or 'None'}",
            f"Food Allergies: {', '.join([fa.name for fa in self.food_allergies.all()]) or 'None'}",
            f"Other Food Allergy: {self.food_allergy_other or 'None'}",
        ]
        return "\n".join(profile)


# Age Tracking System Models

class AgeTransitionRule(models.Model):
    """Defines when pets should transition between age categories"""
    pet_type = models.ForeignKey(PetType, on_delete=models.CASCADE, related_name='age_transition_rules')
    from_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE, related_name='transition_from')
    to_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE, related_name='transition_to')
    transition_age_months = models.PositiveIntegerField(help_text="Age in months when transition occurs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['pet_type', 'from_category', 'to_category']
        ordering = ['pet_type', 'transition_age_months']
    
    def __str__(self):
        return f"{self.pet_type.name}: {self.from_category.name} → {self.to_category.name} at {self.transition_age_months} months"


class PetAgeHistory(models.Model):
    """Tracks pet's journey through different age categories"""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='age_history')
    age_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    age_months_at_start = models.PositiveIntegerField(help_text="Pet's age in months when this category started")
    transition_reason = models.CharField(max_length=100, default='manual_entry', help_text="Reason for this age category assignment")
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Pet Age History"
        verbose_name_plural = "Pet Age Histories"
    
    def __str__(self):
        status = "Current" if not self.ended_at else f"Ended {self.ended_at.date()}"
        return f"{self.pet.name}: {self.age_category.name} ({status})"


class PetConditionSnapshot(models.Model):
    """Saves pet's condition data at different life stages"""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='condition_snapshots')
    age_category = models.ForeignKey(AgeCategory, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    activity_level = models.ForeignKey(ActivityLevel, on_delete=models.SET_NULL, null=True, blank=True)
    food_feeling = models.ForeignKey(FoodFeeling, on_delete=models.SET_NULL, null=True, blank=True)
    food_importance = models.ForeignKey(FoodImportance, on_delete=models.SET_NULL, null=True, blank=True)
    body_type = models.ForeignKey(BodyType, on_delete=models.SET_NULL, null=True, blank=True)
    treat_frequency = models.ForeignKey(TreatFrequency, on_delete=models.SET_NULL, null=True, blank=True)
    food_allergy_other = models.CharField(max_length=255, blank=True, null=True)
    snapshot_date = models.DateTimeField(auto_now_add=True)
    transition_reason = models.CharField(max_length=100, default='age_progression')
    notes = models.TextField(blank=True, help_text="Additional notes about this snapshot")
    
    class Meta:
        ordering = ['-snapshot_date']
        verbose_name = "Pet Condition Snapshot"
        verbose_name_plural = "Pet Condition Snapshots"
    
    def __str__(self):
        return f"{self.pet.name} - {self.age_category.name} ({self.snapshot_date.date()})"


class PetConditionSnapshotFoodTypes(models.Model):
    """Many-to-many through model for food types in snapshots"""
    snapshot = models.ForeignKey(PetConditionSnapshot, on_delete=models.CASCADE, related_name='food_type_snapshots')
    food_type = models.ForeignKey(FoodType, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['snapshot', 'food_type']


class PetConditionSnapshotFoodAllergies(models.Model):
    """Many-to-many through model for food allergies in snapshots"""
    snapshot = models.ForeignKey(PetConditionSnapshot, on_delete=models.CASCADE, related_name='food_allergy_snapshots')
    food_allergy = models.ForeignKey(FoodAllergy, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['snapshot', 'food_allergy']


class PetConditionSnapshotHealthIssues(models.Model):
    """Many-to-many through model for health issues in snapshots"""
    snapshot = models.ForeignKey(PetConditionSnapshot, on_delete=models.CASCADE, related_name='health_issue_snapshots')
    health_issue = models.ForeignKey(HealthIssue, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['snapshot', 'health_issue']


class PetDataChangeLog(models.Model):
    """Tracks granular changes to important pet data fields"""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='data_changes')
    field_name = models.CharField(max_length=100, help_text="Name of the field that changed")
    old_value = models.TextField(null=True, blank=True, help_text="Previous value (JSON for complex fields)")
    new_value = models.TextField(null=True, blank=True, help_text="New value (JSON for complex fields)")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who made the change"
    )
    change_reason = models.CharField(
        max_length=100, 
        default='user_update',
        choices=[
            ('user_update', 'User Update'),
            ('age_transition', 'Age Category Transition'),
            ('weight_entry', 'Weight Record Entry'),
            ('system_recalculation', 'System Recalculation'),
            ('admin_update', 'Admin Update'),
        ],
        help_text="Reason for the change"
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = "Pet Data Change Log"
        verbose_name_plural = "Pet Data Change Logs"
        
    def __str__(self):
        return f"{self.pet.name}: {self.field_name} changed on {self.changed_at.date()}"
    
    @property
    def change_summary(self):
        """Get a human-readable summary of the change"""
        if self.field_name == 'weight':
            try:
                old_kg = float(self.old_value) if self.old_value else 0
                new_kg = float(self.new_value) if self.new_value else 0
                change_kg = new_kg - old_kg
                if change_kg > 0:
                    return f"Weight increased by {change_kg:.1f}kg ({old_kg:.1f}kg → {new_kg:.1f}kg)"
                else:
                    return f"Weight decreased by {abs(change_kg):.1f}kg ({old_kg:.1f}kg → {new_kg:.1f}kg)"
            except (ValueError, TypeError):
                pass
        
        return f"{self.field_name}: {self.old_value or 'None'} → {self.new_value or 'None'}"


class PetWeightRecord(models.Model):
    """Stores historical weight records for each pet"""
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='weight_records')
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kilograms")
    recorded_at = models.DateField(help_text="Date when the weight was recorded")
    note = models.CharField(max_length=255, blank=True, null=True, help_text="Optional note about this weight record")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-recorded_at', '-created_at']
        verbose_name = "Pet Weight Record"
        verbose_name_plural = "Pet Weight Records"
    
    def __str__(self):
        return f"{self.pet.name}: {self.weight_kg}kg on {self.recorded_at}"
    
    def save(self, *args, **kwargs):
        """Override save to preserve original weight and update the pet's current weight field"""
        # Check if this is the first weight record being added for this pet
        is_first_record = not PetWeightRecord.objects.filter(pet=self.pet).exists()
        
        # If this is the first weight record AND the pet has an existing weight (from registration),
        # create an initial weight record to preserve the registration weight
        if is_first_record and self.pet.weight and self.pet.weight > 0:
            # Don't create an initial record if the new record has the same weight and recent date
            # (to avoid duplicates when the registration weight is being added as the first record)
            from django.utils import timezone
            recent_date_threshold = timezone.now().date() - timedelta(days=7)
            
            if not (self.weight_kg == self.pet.weight and self.recorded_at >= recent_date_threshold):
                # Create initial weight record using registration date or a date before this record
                initial_date = self.pet.registration_date.date() if self.pet.registration_date else (self.recorded_at - timedelta(days=1))
                
                # Create the initial record without triggering another save cascade
                initial_record = PetWeightRecord(
                    pet=self.pet,
                    weight_kg=self.pet.weight,
                    recorded_at=initial_date,
                    note='Initial weight at registration'
                )
                # Save without calling our custom save method to avoid recursion
                super(PetWeightRecord, initial_record).save()
        
        # Now save the current record
        super().save(*args, **kwargs)
        
        # Update the pet's weight field with the most recent weight record
        latest_record = PetWeightRecord.objects.filter(pet=self.pet).order_by('-recorded_at', '-created_at').first()
        if latest_record and latest_record.weight_kg != self.pet.weight:
            old_weight = self.pet.weight
            self.pet.weight = latest_record.weight_kg
            # Save with change tracking for weight updates
            self.pet.save(changed_by=getattr(self, '_changed_by', None), change_reason='weight_entry', skip_tracking=False)
    
    @property
    def age_at_recording(self):
        """Calculate pet's age when this weight was recorded"""
        if not self.pet.birth_date:
            return None
        from dateutil.relativedelta import relativedelta
        delta = relativedelta(self.recorded_at, self.pet.birth_date)
        return {
            'years': delta.years,
            'months': delta.months,
            'days': delta.days
        }
    
    def get_percentage_change_from_previous(self):
        """Calculate percentage change from the previous weight record"""
        previous_record = PetWeightRecord.objects.filter(
            pet=self.pet,
            recorded_at__lt=self.recorded_at
        ).order_by('-recorded_at', '-created_at').first()
        
        if not previous_record:
            return None
        
        percent_change = ((self.weight_kg - previous_record.weight_kg) / previous_record.weight_kg) * 100
        return round(float(percent_change), 2)







