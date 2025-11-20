from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split a string by the given argument"""
    if value:
        return value.split(arg)
    return []

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary"""
    return dictionary.get(key)

@register.simple_tag
def clinic_referral_url(request, clinic):
    """Generate a referral URL for a clinic"""
    if clinic and clinic.active_referral_code:
        from django.urls import reverse
        referral_path = reverse('vets:referral_landing', kwargs={'code': clinic.active_referral_code})
        return request.build_absolute_uri(referral_path)
    return ''

@register.filter
def strip(value):
    """Strip whitespace from a string"""
    if value:
        return str(value).strip()
    return value

@register.filter
def mul(value, arg):
    """Multiply two values"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide two values"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def format_working_hours(clinic):
    """Format working hours for display"""
    try:
        schedule = clinic.working_hours_schedule.all().order_by('day_of_week')
        if not schedule.exists():
            return clinic.working_hours if clinic.working_hours else "Not set"
        
        hours_html = '<div class="space-y-1">'
        for hours in schedule:
            day_name = hours.get_day_of_week_display()
            if hours.is_closed:
                hours_html += f'<div class="flex justify-between"><span class="font-medium">{day_name}:</span> <span class="text-gray-500">Closed</span></div>'
            elif hours.open_time and hours.close_time:
                time_str = f"{hours.open_time.strftime('%H:%M')} - {hours.close_time.strftime('%H:%M')}"
                hours_html += f'<div class="flex justify-between"><span class="font-medium">{day_name}:</span> <span>{time_str}</span></div>'
        hours_html += '</div>'
        
        return hours_html
    except:
        return clinic.working_hours if clinic.working_hours else "Not set"

@register.inclusion_tag('vets/partials/clinic_card.html')
def clinic_card(clinic, show_referral=False):
    """Render a clinic card"""
    return {
        'clinic': clinic,
        'show_referral': show_referral,
    }