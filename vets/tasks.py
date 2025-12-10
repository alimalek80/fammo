"""
Celery tasks for vets app (asynchronous operations)
Falls back to synchronous execution if Celery is not configured
"""
import logging

logger = logging.getLogger(__name__)

# Try to import Celery
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create a dummy decorator that executes synchronously
    def shared_task(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.delay = lambda *args, **kwargs: wrapper(*args, **kwargs)
        return wrapper


@shared_task
def geocode_clinic_async(clinic_id):
    """
    Asynchronously geocode a clinic's address.
    
    This task:
    1. Fetches the clinic from database
    2. Calls the geocoding API
    3. Updates the clinic with coordinates
    4. Non-blocking - won't crash if API fails
    
    Args:
        clinic_id: Primary key of the Clinic model
    """
    try:
        from .models import Clinic
        from .utils import geocode_address
        
        # Fetch the clinic
        clinic = Clinic.objects.get(id=clinic_id)
        
        logger.info(f"[GEOCODE_TASK] Starting geocoding for clinic {clinic_id}: {clinic.name}")
        
        # Skip if we already have coordinates
        if clinic.latitude and clinic.longitude:
            logger.info(f"[GEOCODE_TASK] Clinic {clinic_id} already has coordinates, skipping")
            return
        
        # Call geocoding API
        coords = geocode_address(clinic.address, clinic.city)
        
        if coords:
            # Update clinic
            clinic.latitude = coords['latitude']
            clinic.longitude = coords['longitude']
            
            # Use update_fields to avoid triggering save() logic again
            Clinic.objects.filter(id=clinic_id).update(
                latitude=coords['latitude'],
                longitude=coords['longitude']
            )
            
            logger.info(f"[GEOCODE_TASK] ✅ Clinic {clinic_id} geocoded: ({coords['latitude']}, {coords['longitude']})")
        else:
            logger.warning(f"[GEOCODE_TASK] ⚠️ Failed to geocode clinic {clinic_id}")
            
    except Clinic.DoesNotExist:
        logger.error(f"[GEOCODE_TASK] Clinic {clinic_id} not found")
    except Exception as e:
        logger.error(f"[GEOCODE_TASK] Error geocoding clinic {clinic_id}: {str(e)}", exc_info=True)
