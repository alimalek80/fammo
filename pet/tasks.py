"""
Celery tasks for automatic pet age updates and condition tracking
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Pet, PetAgeHistory
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_pet_age_categories():
    """
    Daily task to check and update pet age categories
    This task should run once daily to check if any pets need age category updates
    """
    try:
        updated_count = 0
        checked_count = 0
        
        # Get all pets with proper age tracking setup
        pets = Pet.objects.filter(
            birth_date__isnull=False,
            age_category__isnull=False,
            pet_type__isnull=False
        ).select_related('age_category', 'pet_type', 'user')
        
        logger.info(f"Starting age category check for {pets.count()} pets")
        
        for pet in pets:
            checked_count += 1
            try:
                # Check if pet needs age category update
                updated = pet.check_and_update_age_category()
                if updated:
                    updated_count += 1
                    current_age = pet.get_current_age()
                    logger.info(
                        f"Pet '{pet.name}' (ID: {pet.id}) transitioned to '{pet.age_category.name}' "
                        f"at age {current_age['years']}y {current_age['months']}m"
                    )
            except Exception as e:
                logger.error(f"Error updating age for pet '{pet.name}' (ID: {pet.id}): {str(e)}")
                continue
        
        logger.info(f"Age category update completed: {updated_count}/{checked_count} pets updated")
        return {
            'success': True,
            'checked_count': checked_count,
            'updated_count': updated_count,
            'message': f"Updated {updated_count} out of {checked_count} pets"
        }
        
    except Exception as e:
        error_msg = f"Error in update_pet_age_categories task: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'checked_count': 0,
            'updated_count': 0
        }

@shared_task 
def create_weekly_condition_snapshots():
    """
    Weekly task to create condition snapshots for all active pets
    This preserves pet condition data over time for analysis
    """
    try:
        created_count = 0
        checked_count = 0
        
        # Get all pets with proper setup
        pets = Pet.objects.filter(
            birth_date__isnull=False,
            age_category__isnull=False
        ).select_related('age_category', 'user')
        
        logger.info(f"Starting weekly condition snapshots for {pets.count()} pets")
        
        # Check if we need to create snapshots (only if no recent snapshot exists)
        cutoff_date = timezone.now() - timedelta(days=6)  # Allow 6 days gap for weekly snapshots
        
        for pet in pets:
            checked_count += 1
            try:
                # Check if pet has a recent snapshot
                recent_snapshot = pet.condition_snapshots.filter(
                    snapshot_date__gte=cutoff_date,
                    transition_reason='weekly_snapshot'
                ).exists()
                
                if not recent_snapshot:
                    snapshot = pet._save_condition_snapshot('weekly_snapshot')
                    if snapshot:
                        created_count += 1
                        logger.info(f"Created weekly snapshot for pet '{pet.name}' (ID: {pet.id})")
                
            except Exception as e:
                logger.error(f"Error creating snapshot for pet '{pet.name}' (ID: {pet.id}): {str(e)}")
                continue
        
        logger.info(f"Weekly snapshot creation completed: {created_count}/{checked_count} snapshots created")
        return {
            'success': True,
            'checked_count': checked_count,
            'created_count': created_count,
            'message': f"Created {created_count} out of {checked_count} possible snapshots"
        }
        
    except Exception as e:
        error_msg = f"Error in create_weekly_condition_snapshots task: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'checked_count': 0,
            'created_count': 0
        }

@shared_task
def initialize_pet_age_history():
    """
    One-time task to create initial age history records for existing pets
    Run this once after deploying the new age tracking system
    """
    try:
        created_count = 0
        checked_count = 0
        
        # Get pets that don't have age history records
        pets = Pet.objects.filter(
            birth_date__isnull=False,
            age_category__isnull=False,
            age_history__isnull=True
        ).distinct().select_related('age_category', 'user')
        
        logger.info(f"Initializing age history for {pets.count()} pets")
        
        for pet in pets:
            checked_count += 1
            try:
                current_age = pet.get_current_age()
                current_age_months = (current_age['years'] * 12) + current_age['months']
                
                # Create initial age history record
                PetAgeHistory.objects.create(
                    pet=pet,
                    age_category=pet.age_category,
                    age_months_at_start=max(0, current_age_months),  # Don't allow negative ages
                    transition_reason='initial_setup'
                )
                
                # Create initial condition snapshot
                pet._save_condition_snapshot('initial_setup')
                
                created_count += 1
                logger.info(f"Initialized age history for pet '{pet.name}' (ID: {pet.id})")
                
            except Exception as e:
                logger.error(f"Error initializing age history for pet '{pet.name}' (ID: {pet.id}): {str(e)}")
                continue
        
        logger.info(f"Age history initialization completed: {created_count}/{checked_count} pets initialized")
        return {
            'success': True,
            'checked_count': checked_count,
            'created_count': created_count,
            'message': f"Initialized {created_count} out of {checked_count} pets"
        }
        
    except Exception as e:
        error_msg = f"Error in initialize_pet_age_history task: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'checked_count': 0,
            'created_count': 0
        }

@shared_task
def cleanup_old_snapshots(days_to_keep=365):
    """
    Monthly task to cleanup old condition snapshots (keep last 1 year by default)
    This prevents the database from growing too large
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Delete old snapshots but keep at least one snapshot per pet per age category
        from django.db.models import Min
        from .models import PetConditionSnapshot, PetConditionSnapshotFoodTypes, PetConditionSnapshotFoodAllergies, PetConditionSnapshotHealthIssues
        
        # Get oldest snapshot per pet per age category to preserve
        preserve_snapshots = PetConditionSnapshot.objects.values('pet', 'age_category').annotate(
            oldest_date=Min('snapshot_date')
        )
        
        preserve_ids = []
        for item in preserve_snapshots:
            oldest_snapshot = PetConditionSnapshot.objects.filter(
                pet=item['pet'],
                age_category=item['age_category'],
                snapshot_date=item['oldest_date']
            ).first()
            if oldest_snapshot:
                preserve_ids.append(oldest_snapshot.id)
        
        # Delete old snapshots (but not the preserved ones)
        old_snapshots = PetConditionSnapshot.objects.filter(
            snapshot_date__lt=cutoff_date
        ).exclude(id__in=preserve_ids)
        
        deleted_count = old_snapshots.count()
        
        # Delete related many-to-many through models first
        PetConditionSnapshotFoodTypes.objects.filter(snapshot__in=old_snapshots).delete()
        PetConditionSnapshotFoodAllergies.objects.filter(snapshot__in=old_snapshots).delete()
        PetConditionSnapshotHealthIssues.objects.filter(snapshot__in=old_snapshots).delete()
        
        # Delete the snapshots
        old_snapshots.delete()
        
        logger.info(f"Cleaned up {deleted_count} old condition snapshots (older than {days_to_keep} days)")
        return {
            'success': True,
            'deleted_count': deleted_count,
            'days_to_keep': days_to_keep,
            'message': f"Cleaned up {deleted_count} old snapshots"
        }
        
    except Exception as e:
        error_msg = f"Error in cleanup_old_snapshots task: {str(e)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'deleted_count': 0
        }