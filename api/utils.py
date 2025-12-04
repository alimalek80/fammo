"""
Utility functions for the API app
"""
from django.conf import settings


def build_absolute_uri(request, relative_path):
    """
    Build an absolute URL from a relative path
    
    Args:
        request: Django request object
        relative_path: Relative path (e.g., '/media/image.jpg')
    
    Returns:
        Absolute URL (e.g., 'https://fammo.ai/media/image.jpg')
    """
    if not relative_path:
        return None
    
    # If it's already an absolute URL, return as is
    if relative_path.startswith(('http://', 'https://')):
        return relative_path
    
    # Build absolute URL
    base_url = request.build_absolute_uri('/').rstrip('/')
    return f"{base_url}{relative_path}"


def get_media_url(request, file_field):
    """
    Get absolute URL for a FileField or ImageField
    
    Args:
        request: Django request object
        file_field: Django FileField or ImageField instance
    
    Returns:
        Absolute URL or None if file doesn't exist
    """
    if not file_field:
        return None
    
    try:
        return build_absolute_uri(request, file_field.url)
    except ValueError:
        # File doesn't exist
        return None
