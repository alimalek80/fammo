from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    i18n = True  # Enable i18n support

    def items(self):
        # Return list of static page URL names (without namespace for simplicity)
        return [
            'home', 'about', 'how_it_works', 'how_fammo_works', 'contact', 'faq'
        ]

    def location(self, item):
        # Reverse with core namespace
        try:
            return reverse(f'core:{item}')
        except:
            return f'/{item}/'


class BlogPostSitemap(Sitemap):
    """Sitemap for published blog posts"""
    changefreq = 'weekly'
    priority = 0.9
    i18n = True

    def items(self):
        from blog.models import BlogPost
        return BlogPost.objects.filter(
            is_published=True,
            published_at__isnull=False,
            published_at__lte=timezone.now()
        ).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        try:
            return reverse('blog:blog_detail', kwargs={'slug': obj.slug})
        except:
            return f'/blog/{obj.slug}/'


class ForumQuestionSitemap(Sitemap):
    """Sitemap for forum questions"""
    changefreq = 'daily'
    priority = 0.7
    i18n = True

    def items(self):
        from forum.models import Question
        return Question.objects.all().order_by('-created_at')[:100]  # Limit to latest 100

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        try:
            return reverse('forum:question_detail', kwargs={'pk': obj.pk})
        except:
            return f'/forum/question/{obj.pk}/'


class ClinicSitemap(Sitemap):
    """Sitemap for verified partner clinics"""
    changefreq = 'weekly'
    priority = 0.8
    i18n = True

    def items(self):
        from vets.models import Clinic
        return Clinic.objects.filter(
            email_confirmed=True,
            admin_approved=True,
            is_verified=True
        ).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        try:
            return reverse('vets:clinic_detail', kwargs={'slug': obj.slug})
        except:
            return f'/vets/clinic/{obj.slug}/'
