from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import index, sitemap
from userapp.views import reset_password_from_email
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from userapp.views import account_deletion_view, privacy_policy_view

# Import sitemaps
from .sitemaps import (
    StaticViewSitemap,
    BlogPostSitemap,
    ForumQuestionSitemap,
    ClinicSitemap,
)

# CRITICAL: Sitemap configuration dictionary
# All sitemaps have i18n=True to support multilingual URLs
sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
    'forum': ForumQuestionSitemap,
    'clinics': ClinicSitemap,
}

# Custom 404 handler
def custom_404(request, exception=None):
    from blog.models import BlogPost
    latest_posts = BlogPost.objects.filter(
        published_at__isnull=False,
        published_at__lte=timezone.now()
    ).order_by('-published_at')[:3]
    return render(request, '404.html', {'latest_posts': latest_posts}, status=404)

urlpatterns = [
    # ✅ This is required for {% url 'set_language' %} to work
    path('i18n/', include('django.conf.urls.i18n')),
    path('markdownx/', include('markdownx.urls')),  # move outside i18n for uploads
    # API routes should be outside i18n_patterns for mobile apps
    path('api/v1/', include('api.urls')),
    path('api/v1/ai/', include(('ai_core.urls', 'ai_core'), namespace='ai_core')),
    # Legal pages outside i18n for direct access (required for app store)
    path('delete-account/', account_deletion_view, name='delete_account_direct'),
    path('privacy-policy/', privacy_policy_view, name='privacy_policy_direct'),
    # Google Search Console verification
    path('google18424ee3e3bbdebf.html', TemplateView.as_view(
        template_name='google18424ee3e3bbdebf.html',
        content_type='text/plain'
    ), name='google_verification'),
    # CRITICAL: Dynamic sitemap routes must stay outside i18n_patterns.
    path('sitemap.xml', index, {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemap-section'}, name='sitemap-index'),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap-section'),
    # Robots.txt
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain'
    ), name='robots_txt'),
    # llms.txt — helps LLM crawlers understand site content
    path('llms.txt', TemplateView.as_view(
        template_name='llms.txt',
        content_type='text/plain'
    ), name='llms_txt'),
]

# Your actual app routes (web interface with i18n)
urlpatterns += i18n_patterns(
    path('', include(('core.urls', 'core'), namespace='core')),
    path('users/', include('userapp.urls')),
    path('pets/', include(('pet.urls', 'pet'), namespace='pet')),
    path('vets/', include(('vets.urls', 'vets'), namespace='vets')),
    path('admin/', admin.site.urls),
    path('ai/', include('aihub.urls')),
    path('subscription/', include('subscription.urls')),
    path('blog/', include('blog.urls')),
    path('chat/', include('chat.urls')),
    path('forum/', include(('forum.urls', 'forum'), namespace='forum')),
    path('evidence/', include(('evidence.urls', 'evidence'), namespace='evidence')),
)

urlpatterns += [
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='userapp/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='userapp/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='userapp/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='userapp/password_reset_complete.html'), name='password_reset_complete'),
    # API-based password reset (for forgot password via email from app)
    path('reset-password/<uidb64>/<token>/', reset_password_from_email, name='api_reset_password_from_email'),
    path('accounts/', include('allauth.urls')),
    
]

from core.email_preview import email_preview_index, email_preview_detail

_email_preview_urls = [
    path('', email_preview_index, name='email_preview_index'),
    path('<str:email_key>/', email_preview_detail, name='email_preview_detail'),
]

# Email preview tool — staff-only, works in both dev and production
# Visit: /dev/emails/
urlpatterns += [
    path('dev/emails/', include((_email_preview_urls, 'dev'))),
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        # Test 404 page - visit http://localhost:8000/test-404/ to see the custom 404 page
        path('test-404/', lambda request: custom_404(request), name='test_404'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'famo.urls.custom_404'
