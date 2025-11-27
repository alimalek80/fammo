from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from pet.models import Pet, PetType
from aihub.models import AIRecommendation, AIHealthReport, RecommendationType

User = get_user_model()

def evidence_dashboard(request):
    """
    Evidence dashboard showing key statistics for BF (Business/Staff)
    Section 1: Overview statistics
    Sections 2-6: Reserved for future features
    """
    
    # Calculate date ranges for active user tracking
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    
    # Total Registered Users
    total_users = User.objects.count()
    
    # Total Pets by type
    total_pets = Pet.objects.count()
    try:
        dog_type = PetType.objects.get(name='Dog')
        total_dogs = Pet.objects.filter(pet_type=dog_type).count()
    except PetType.DoesNotExist:
        total_dogs = 0
    
    try:
        cat_type = PetType.objects.get(name='Cat')
        total_cats = Pet.objects.filter(pet_type=cat_type).count()
    except PetType.DoesNotExist:
        total_cats = 0
    
    # Total AI Generated Reports
    total_meal_plans = AIRecommendation.objects.filter(type=RecommendationType.MEAL).count()
    total_health_reports = AIHealthReport.objects.count()
    
    # Active Users (users who logged in recently)
    active_users_7_days = User.objects.filter(last_login__gte=last_7_days).count()
    active_users_30_days = User.objects.filter(last_login__gte=last_30_days).count()
    
    context = {
        'total_users': total_users,
        'total_dogs': total_dogs,
        'total_cats': total_cats,
        'total_pets': total_pets,
        'total_meal_plans': total_meal_plans,
        'total_health_reports': total_health_reports,
        'active_users_7_days': active_users_7_days,
        'active_users_30_days': active_users_30_days,
    }
    
    return render(request, 'evidence/dashboard.html', context)
