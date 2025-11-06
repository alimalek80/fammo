from django.conf import settings

try:
    from allauth.socialaccount.models import SocialApp
except ImportError:  # If allauth not installed for some reason
    SocialApp = None


def social_login_flags(request):
    """Provide boolean flags indicating availability of social providers.

    This avoids template errors (DoesNotExist) when a SocialApp hasn't been
    associated with the current Site yet.
    """
    google_enabled = False
    if SocialApp:
        try:
            google_enabled = SocialApp.objects.filter(
                provider='google', sites__id=getattr(settings, 'SITE_ID', None)
            ).exists()
        except Exception:
            google_enabled = False
    return {
        'google_enabled': google_enabled,
    }