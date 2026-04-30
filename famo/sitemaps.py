from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from blog.models import BlogPost
from forum.models import Question
from vets.models import Clinic


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # Return list of static page URL names
        return [
            'core:home',
            'core:about',
            'core:how_it_works',
            'core:how_fammo_works',
            'core:contact',
            'core:faq',
            'blog:blog_list',
            'forum:question_list',
            'vets:partner_clinics',
        ]

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    """Sitemap for published blog posts"""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(
            is_published=True,
            published_at__isnull=False,
            published_at__lte=timezone.now()
        ).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog:blog_detail', kwargs={'slug': obj.slug})


class ForumQuestionSitemap(Sitemap):
    """Sitemap for forum questions"""
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Question.objects.all().order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('forum:question_detail', kwargs={'pk': obj.pk})


class ClinicSitemap(Sitemap):
    """Sitemap for verified partner clinics"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Clinic.objects.filter(
            email_confirmed=True,
            admin_approved=True,
            is_verified=True
        ).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('vets:clinic_detail', kwargs={'slug': obj.slug})
