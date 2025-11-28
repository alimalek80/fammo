from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from pet.models import Pet, PetType
from aihub.models import AIRecommendation, AIHealthReport, RecommendationType
from django.db.models import Count, Q
from django.db.models.functions import TruncWeek
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import json

User = get_user_model()

def evidence_dashboard(request):
    """
    Evidence dashboard showing key statistics for BF (Business/Staff)
    Section 1: Overview statistics
    Section 2: Product Usage Graphs
    Sections 3-6: Reserved for future features
    """
    
    # Calculate date ranges for active user tracking
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    last_8_weeks = now - timedelta(weeks=8)
    
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
    
    # ===== SECTION 2: Product Usage Graphs =====
    
    # Week-over-week user growth
    weekly_users = []
    for i in range(7, -1, -1):  # Last 8 weeks
        week_start = now - timedelta(weeks=i+1)
        week_end = now - timedelta(weeks=i)
        
        users_count = User.objects.filter(date_joined__gte=week_start, date_joined__lt=week_end).count()
        cumulative_count = User.objects.filter(date_joined__lt=week_end).count()
        
        # Calculate percentage growth
        if i < 7:
            prev_cumulative = User.objects.filter(date_joined__lt=week_start).count()
            growth_percent = ((cumulative_count - prev_cumulative) / prev_cumulative * 100) if prev_cumulative > 0 else 0
        else:
            growth_percent = 0
        
        weekly_users.append({
            'week_start': week_start.strftime('%b %d'),
            'week_end': week_end.strftime('%b %d'),
            'new_users': users_count,
            'total_users': cumulative_count,
            'growth_percent': round(growth_percent, 1)
        })
    
    # Meal Plans Generated per Week
    weekly_meal_plans = []
    for i in range(7, -1, -1):  # Last 8 weeks
        week_start = now - timedelta(weeks=i+1)
        week_end = now - timedelta(weeks=i)
        
        meal_count = AIRecommendation.objects.filter(
            type=RecommendationType.MEAL,
            created_at__gte=week_start,
            created_at__lt=week_end
        ).count()
        
        weekly_meal_plans.append({
            'week_start': week_start.strftime('%b %d'),
            'week_end': week_end.strftime('%b %d'),
            'meal_plans': meal_count
        })
    
    # Health Reports Generated per Week
    weekly_health_reports = []
    for i in range(7, -1, -1):  # Last 8 weeks
        week_start = now - timedelta(weeks=i+1)
        week_end = now - timedelta(weeks=i)
        
        health_count = AIHealthReport.objects.filter(
            created_at__gte=week_start,
            created_at__lt=week_end
        ).count()
        
        weekly_health_reports.append({
            'week_start': week_start.strftime('%b %d'),
            'week_end': week_end.strftime('%b %d'),
            'health_reports': health_count
        })
    
    # Returning Users Count
    # Users who logged in at least twice
    returning_users_7d = User.objects.filter(
        last_login__gte=last_7_days,
        date_joined__lt=last_7_days  # Joined before the 7-day window
    ).count()
    
    returning_users_30d = User.objects.filter(
        last_login__gte=last_30_days,
        date_joined__lt=last_30_days  # Joined before the 30-day window
    ).count()
    
    # ===== SECTION 3: Sample Meal Plan =====
    # Get the latest meal plan with JSON data (preferably from admin user)
    latest_meal_plan = None
    admin_user = User.objects.filter(email='alianta2016@gmail.com').first()
    
    if admin_user:
        # Try to get latest meal plan from admin user
        latest_meal_plan = AIRecommendation.objects.filter(
            type=RecommendationType.MEAL,
            pet__user=admin_user,
            content_json__isnull=False
        ).order_by('-created_at').first()
    
    # Fallback to any latest meal plan with JSON if admin doesn't have one
    if not latest_meal_plan:
        latest_meal_plan = AIRecommendation.objects.filter(
            type=RecommendationType.MEAL,
            content_json__isnull=False
        ).order_by('-created_at').first()
    
    # Format JSON for display
    sample_meal_plan_json_formatted = None
    if latest_meal_plan and latest_meal_plan.content_json:
        sample_meal_plan_json_formatted = json.dumps(latest_meal_plan.content_json, indent=2)
    
    # Section 4: Sample Health Report
    # Try to get from admin user first, otherwise get any latest health report
    latest_health_report = None
    if admin_user:
        latest_health_report = AIHealthReport.objects.filter(
            pet__user=admin_user,
            summary_json__isnull=False
        ).order_by('-created_at').first()
    
    # Fallback to any latest health report with JSON if admin doesn't have one
    if not latest_health_report:
        latest_health_report = AIHealthReport.objects.filter(
            summary_json__isnull=False
        ).order_by('-created_at').first()
    
    # Format health report JSON for display
    sample_health_report_json_formatted = None
    if latest_health_report and latest_health_report.summary_json:
        sample_health_report_json_formatted = json.dumps(latest_health_report.summary_json, indent=2)
    
    context = {
        'total_users': total_users,
        'total_dogs': total_dogs,
        'total_cats': total_cats,
        'total_pets': total_pets,
        'total_meal_plans': total_meal_plans,
        'total_health_reports': total_health_reports,
        'active_users_7_days': active_users_7_days,
        'active_users_30_days': active_users_30_days,
        
        # Section 2 data
        'weekly_users': weekly_users,
        'weekly_meal_plans': weekly_meal_plans,
        'weekly_health_reports': weekly_health_reports,
        'returning_users_7d': returning_users_7d,
        'returning_users_30d': returning_users_30d,
        
        # Section 3 data
        'sample_meal_plan': latest_meal_plan,
        'sample_meal_plan_json': sample_meal_plan_json_formatted,
        
        # Section 4 data
        'sample_health_report': latest_health_report,
        'sample_health_report_json': sample_health_report_json_formatted,
    }
    
    return render(request, 'evidence/dashboard.html', context)


def download_pdf_report(request):
    """
    Generate and download PDF evidence report
    """
    from .pdf_generator import generate_evidence_pdf
    from .screenshot_generator import generate_section_screenshots_from_data
    
    # Get all the data (reuse logic from evidence_dashboard)
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    
    # Collect all context data
    context_data = {
        'total_users': User.objects.count(),
        'total_pets': Pet.objects.count(),
        'total_dogs': 0,
        'total_cats': 0,
        'total_meal_plans': AIRecommendation.objects.filter(type=RecommendationType.MEAL).count(),
        'total_health_reports': AIHealthReport.objects.count(),
        'active_users_7_days': User.objects.filter(last_login__gte=last_7_days).count(),
        'active_users_30_days': User.objects.filter(last_login__gte=last_30_days).count(),
    }
    
    # Get pet counts by type
    try:
        dog_type = PetType.objects.get(name='Dog')
        context_data['total_dogs'] = Pet.objects.filter(pet_type=dog_type).count()
    except PetType.DoesNotExist:
        pass
    
    try:
        cat_type = PetType.objects.get(name='Cat')
        context_data['total_cats'] = Pet.objects.filter(pet_type=cat_type).count()
    except PetType.DoesNotExist:
        pass
    
    # Weekly user growth
    weekly_users = []
    for i in range(7, -1, -1):
        week_start = now - timedelta(weeks=i+1)
        week_end = now - timedelta(weeks=i)
        
        users_count = User.objects.filter(date_joined__gte=week_start, date_joined__lt=week_end).count()
        cumulative_count = User.objects.filter(date_joined__lt=week_end).count()
        
        if i < 7:
            prev_cumulative = User.objects.filter(date_joined__lt=week_start).count()
            growth_percent = ((cumulative_count - prev_cumulative) / prev_cumulative * 100) if prev_cumulative > 0 else 0
        else:
            growth_percent = 0
        
        weekly_users.append({
            'week_start': week_start.strftime('%b %d'),
            'week_end': week_end.strftime('%b %d'),
            'new_users': users_count,
            'total_users': cumulative_count,
            'growth_percent': round(growth_percent, 1)
        })
    
    # Weekly meal plans
    weekly_meal_plans = []
    for i in range(7, -1, -1):
        week_start = now - timedelta(weeks=i+1)
        week_end = now - timedelta(weeks=i)
        
        meal_count = AIRecommendation.objects.filter(
            type=RecommendationType.MEAL,
            created_at__gte=week_start,
            created_at__lt=week_end
        ).count()
        
        weekly_meal_plans.append({
            'week_start': week_start.strftime('%b %d'),
            'week_end': week_end.strftime('%b %d'),
            'meal_plans': meal_count
        })
    
    # Weekly health reports
    weekly_health_reports = []
    for i in range(7, -1, -1):
        week_start = now - timedelta(weeks=i+1)
        week_end = now - timedelta(weeks=i)
        
        health_count = AIHealthReport.objects.filter(
            created_at__gte=week_start,
            created_at__lt=week_end
        ).count()
        
        weekly_health_reports.append({
            'week_start': week_start.strftime('%b %d'),
            'week_end': week_end.strftime('%b %d'),
            'health_reports': health_count
        })
    
    # Returning users
    context_data['returning_users_7d'] = User.objects.filter(
        last_login__gte=last_7_days,
        date_joined__lt=last_7_days
    ).count()
    
    context_data['returning_users_30d'] = User.objects.filter(
        last_login__gte=last_30_days,
        date_joined__lt=last_30_days
    ).count()
    
    context_data['weekly_users'] = weekly_users
    context_data['weekly_meal_plans'] = weekly_meal_plans
    context_data['weekly_health_reports'] = weekly_health_reports
    
    # Add sample meal plan and health report data
    admin_user = User.objects.filter(email='alianta2016@gmail.com').first()
    
    # Get latest meal plan
    latest_meal_plan = None
    if admin_user:
        latest_meal_plan = AIRecommendation.objects.filter(
            type=RecommendationType.MEAL,
            pet__user=admin_user,
            content_json__isnull=False
        ).order_by('-created_at').first()
    
    if not latest_meal_plan:
        latest_meal_plan = AIRecommendation.objects.filter(
            type=RecommendationType.MEAL,
            content_json__isnull=False
        ).order_by('-created_at').first()
    
    if latest_meal_plan:
        context_data['sample_meal_plan'] = {
            'pet_name': latest_meal_plan.pet.name,
            'created_at': latest_meal_plan.created_at.strftime('%B %d, %Y at %H:%M')
        }
        context_data['sample_meal_plan_json'] = json.dumps(latest_meal_plan.content_json, indent=2)
        context_data['sample_meal_plan_data'] = latest_meal_plan.content_json  # Add parsed data
    
    # Get latest health report
    latest_health_report = None
    if admin_user:
        latest_health_report = AIHealthReport.objects.filter(
            pet__user=admin_user,
            summary_json__isnull=False
        ).order_by('-created_at').first()
    
    if not latest_health_report:
        latest_health_report = AIHealthReport.objects.filter(
            summary_json__isnull=False
        ).order_by('-created_at').first()
    
    if latest_health_report:
        context_data['sample_health_report'] = {
            'pet_name': latest_health_report.pet.name,
            'created_at': latest_health_report.created_at.strftime('%B %d, %Y at %H:%M')
        }
        context_data['sample_health_report_json'] = json.dumps(latest_health_report.summary_json, indent=2)
        context_data['sample_health_report_data'] = latest_health_report.summary_json  # Add parsed data
    
    # Generate screenshots automatically
    meal_plan_data = context_data.get('sample_meal_plan_data')
    health_report_data = context_data.get('sample_health_report_data')
    if meal_plan_data or health_report_data:
        generate_section_screenshots_from_data(meal_plan_data, health_report_data)
    
    return generate_evidence_pdf(context_data)
