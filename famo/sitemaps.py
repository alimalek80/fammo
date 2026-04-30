from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        # Return simple paths
        return [
            '/',
            '/about/',
            '/contact/',
            '/faq/',
            '/blog/',
            '/forum/',
            '/vets/clinics/',
        ]

    def location(self, item):
        return item


class BlogPostSitemap(Sitemap):
    """Sitemap for published blog posts"""
    changefreq = 'weekly'
    priority = 0.9
    protocol = 'https'

    def items(self):
        try:
            from blog.models import BlogPost
            return BlogPost.objects.filter(
                is_published=True,
                published_at__isnull=False,
                published_at__lte=timezone.now()
            ).order_by('-published_at')
        except Exception:
            return []

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/blog/{obj.slug}/'


class ForumQuestionSitemap(Sitemap):
    """Sitemap for forum questions"""
    changefreq = 'daily'
    priority = 0.7
    protocol = 'https'

    def items(self):
        try:
            from forum.models import Question
            return Question.objects.all().order_by('-created_at')[:100]
        except Exception:
            return []

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/forum/question/{obj.pk}/'


class ClinicSitemap(Sitemap):
    """Sitemap for verified partner clinics"""
    changefreq = 'weekly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        try:
            from vets.models import Clinic
            return Clinic.objects.filter(
                email_confirmed=True,
                admin_approved=True,
                is_verified=True
            ).order_by('-created_at')
        except Exception:
            return []

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/vets/clinic/{obj.slug}/'
