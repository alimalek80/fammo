from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    # ✅ This is required for {% url 'set_language' %} to work
    path('i18n/', include('django.conf.urls.i18n')),
]

# Your actual app routes
urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    path('users/', include('userapp.urls')),
    path('pets/', include(('pet.urls', 'pet'), namespace='pet')),
    path('admin/', admin.site.urls),
    path('ai/', include('aihub.urls')),
    path('subscription/', include('subscription.urls')),
    path('blog/', include('blog.urls')),
)

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
