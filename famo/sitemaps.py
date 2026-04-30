"""
Dynamic Sitemaps for FAMMO - Multilingual Support

CRITICAL: All Sitemap classes MUST have `i18n = True` to prevent 500 errors
in multilingual Django projects using i18n_patterns.

The sitemap URLs are generated for each language defined in settings.LANGUAGES.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from blog.models import BlogPost
from forum.models import Question
from vets.models import Clinic


class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages (home, about, contact, etc.)
    
    IMPORTANT: i18n=True prevents 500 errors with i18n_patterns
    """
    priority = 0.8
    changefreq = 'weekly'
    i18n = True  # CRITICAL: Enable i18n support for multilingual URLs
    
    def items(self):
        """
        Return list of URL names for static pages.
        These will be reversed for each language automatically.
        """
        return [
            'core:home',
            'core:about',
            'core:contact',
            'core:faq',
            'core:how_it_works',
            'core:how_fammo_works',
        ]
    
    def location(self, item):
        """Reverse the URL name to get the path"""
        return reverse(item)


class DynamicModelSitemap(Sitemap):
    """Common multilingual sitemap behavior for translated models."""

    i18n = True

    def location(self, obj):
        # Prefer explicit URLs so one missing get_absolute_url implementation
        # does not take down the entire sitemap in production.
        return obj.get_absolute_url()


class BlogPostSitemap(DynamicModelSitemap):
    """
    Sitemap for published blog posts
    
    IMPORTANT: 
    - i18n=True handles multilingual URLs automatically
    - BlogPost model MUST have get_absolute_url() method
    """
    changefreq = 'weekly'
    priority = 0.9
    def items(self):
        """Return all published blog posts"""
        return BlogPost.objects.filter(
            is_published=True,
            slug__isnull=False,
            slug__gt='',
            published_at__isnull=False,
            published_at__lte=timezone.now()
        ).order_by('-published_at')
    
    def lastmod(self, obj):
        """Return the last modification date"""
        return obj.updated_at
    
class ForumQuestionSitemap(DynamicModelSitemap):
    """
    Sitemap for forum questions
    
    IMPORTANT:
    - i18n=True handles multilingual URLs automatically  
    - Question model MUST have get_absolute_url() method
    """
    changefreq = 'daily'
    priority = 0.7
    def items(self):
        """Return latest 200 forum questions to keep sitemap size reasonable"""
        return Question.objects.all().order_by('-created_at')[:200]
    
    def lastmod(self, obj):
        """Return the last modification date"""
        return obj.updated_at
    
class ClinicSitemap(DynamicModelSitemap):
    """
    Sitemap for verified partner veterinary clinics
    
    IMPORTANT:
    - i18n=True handles multilingual URLs automatically
    - Clinic model MUST have get_absolute_url() method
    """
    changefreq = 'weekly'
    priority = 0.8
    def items(self):
        """Return only verified and approved clinics"""
        return Clinic.objects.filter(
            slug__isnull=False,
            slug__gt='',
            email_confirmed=True,
            admin_approved=True,
            is_verified=True
        ).order_by('-created_at')
    
    def lastmod(self, obj):
        """Return the last modification date"""
        return obj.updated_at
    
