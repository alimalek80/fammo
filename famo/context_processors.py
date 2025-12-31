from core.models import SocialLinks, UserNotification

def social_links(request):
    links = SocialLinks.objects.first()
    return {'social_links': links}


def user_notifications(request):
    """
    Add notification counts to context for all authenticated users.
    Available in templates as:
    - unread_notification_count: Total unread notifications
    - action_required_count: Notifications requiring action
    """
    if request.user.is_authenticated:
        unread_count = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        action_count = UserNotification.objects.filter(
            user=request.user,
            is_read=False,
            action_required=True
        ).count()
        
        # Also get clinic notification count if user owns a clinic
        clinic_notification_count = 0
        if hasattr(request.user, 'owned_clinics') and request.user.owned_clinics.exists():
            from vets.models import ClinicNotification
            clinic = request.user.owned_clinics.first()
            clinic_notification_count = ClinicNotification.objects.filter(
                clinic=clinic,
                is_read=False
            ).count()
        
        return {
            'unread_notification_count': unread_count,
            'action_required_count': action_count,
            'clinic_notification_count': clinic_notification_count,
            'total_notification_count': unread_count + clinic_notification_count,
        }
    
    return {
        'unread_notification_count': 0,
        'action_required_count': 0,
        'clinic_notification_count': 0,
        'total_notification_count': 0,
    }