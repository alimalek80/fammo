import os
from pathlib import Path
from decouple import config
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = ['fammo.ai', 'www.fammo.ai', 'localhost', '127.0.0.1']

# Site URL for email links
SITE_URL = config("SITE_URL", default="https://fammo.ai")

# GOOGLE MAPS
GOOGLE_MAPS_API_KEY = config("GOOGLE_MAPS_API_KEY", default="")

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# APPS
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django.contrib.sites',  # Required by allauth

    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'userapp',
    'chat',
    'core',
    'pet',
    'aihub',
    'ai_core.apps.AiCoreConfig',
    'subscription',
    'blog',
    'forum',
    'markdownify',
    'widget_tweaks',
    'markdownx',
    'formtools',
    'vets.apps.VetsConfig',
    'evidence',
    'rest_framework',
    'api',
    'corsheaders',
    'django_celery_beat',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# JWT TOKEN CONFIGURATION
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),  # Access token valid for 30 days
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365),  # Refresh token valid for 1 year
    'ROTATE_REFRESH_TOKENS': False,  # Set to True to issue new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': False,  # Set to True if using token blacklist
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

MODELTRANSLATION_FALLBACK_LANGUAGES = ('en',)

# Tailwind configuration
TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = config("NPM_BIN_PATH", default="npm")
NODE_BIN_PATH = config("NODE_BIN_PATH", default="node")

# Detect if we're on cPanel by checking for specific cPanel paths
IS_CPANEL = os.path.exists('/home/fammkoqw/nodevenv') or config("IS_CPANEL", default=False, cast=bool)

if DEBUG and not IS_CPANEL:
    INSTALLED_APPS += ['django_browser_reload']

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

if DEBUG and not IS_CPANEL:
    MIDDLEWARE += ['django_browser_reload.middleware.BrowserReloadMiddleware']

ROOT_URLCONF = 'famo.urls'
WSGI_APPLICATION = 'famo.wsgi.application'

# DATABASE
# Environment-aware database configuration
if IS_CPANEL or config("USE_MYSQL", default=False, cast=bool):
    # Use MySQL for cPanel production
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST_LOCAL'),
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
else:
    # Use SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Use SQLite for tests to avoid permission issues (especially on cPanel)
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'test_db.sqlite3',
        }
    }

# AUTH
AUTH_USER_MODEL = 'userapp.CustomUser'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'subscription.context_processors.ai_usage_status',
                'famo.context_processors.social_links',
                'famo.context_processors.user_notifications',
                'userapp.context_processors.social_login_flags',
            ],
        },
    },
]

# LANGUAGE & TIMEZONE
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('tr', 'Türkçe'),
    ('nl', 'Nederlands'),
    ('fi', 'Suomi'),
]
TIME_ZONE = 'UTC'
USE_I18N = True
PREFIX_DEFAULT_LANGUAGE = False  # Allow default language (en) without /en/ prefix
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# STATIC FILES
# Environment-aware static/media URLs
if IS_CPANEL:
    STATIC_URL = 'fammo/static/'
    MEDIA_URL = '/fammo/media/'
else:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# MARKDOWNIFY
MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',
            'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img', 'hr', 'br', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
        ],
        "WHITELIST_ATTRS": ['href', 'src', 'alt', 'class', 'align'],
        "MARKDOWN_EXTENSIONS": [
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.smarty',
        ],
    }
}

# Optional Markdownx config
MARKDOWNX_MEDIA_PATH = 'markdownx/'
MARKDOWNX_UPLOAD_CONTENT_TYPES = ('image/jpeg', 'image/png', 'image/gif', 'image/webp')
MARKDOWNX_UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB
MARKDOWNX_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.codehilite',
    'markdown.extensions.toc',
]

# OPENAI KEY
OPENAI_API_KEY = config("OPENAI_API_KEY")

# AI BACKEND CONFIGURATION
# Controls which AI engine is used for nutrition predictions
# Options: "openai" (default) or "proprietary" (FAMMO's trained models)
# Can be overridden with environment variable: FAMMO_AI_BACKEND
AI_BACKEND = config("FAMMO_AI_BACKEND", default="openai")

# Optional: Override default proprietary model path
# PROPRIETARY_MODEL_PATH = "ml/models/calorie_regressor_v1.pkl"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fammo.ai.official@gmail.com'
EMAIL_HOST_PASSWORD = 'mjvq eetb qqux rhof'
DEFAULT_FROM_EMAIL = 'FAMO <fammo.ai.official@gmail.com>'

# For local development, you can use this to see emails in console instead of sending:
if DEBUG:
    # Uncomment the next line to see emails in console instead of sending
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    pass

SITE_ID = 1  # Make sure this matches a valid Site object in the database

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'
LOGIN_REDIRECT_URL = 'dashboard'  # Changed to match cPanel version
LOGOUT_REDIRECT_URL = 'login'
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = 'userapp.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'userapp.adapters.CustomSocialAccountAdapter'

CONTACT_EMAIL = "info@fammo.ai"

# Screenshot Generation
# Set to False on cPanel if Playwright system dependencies are not available
ENABLE_PLAYWRIGHT_SCREENSHOTS = config('ENABLE_PLAYWRIGHT_SCREENSHOTS', default=True, cast=bool)

# Firebase Cloud Messaging Configuration
# Path to your Firebase service account JSON file (download from Firebase Console)
# Set FIREBASE_CREDENTIALS_PATH in .env for custom path, or use default filename in project root
FIREBASE_CREDENTIALS_PATH = config(
    'FIREBASE_CREDENTIALS_PATH', 
    default=os.path.join(BASE_DIR, 'firebase-service-account.json')
)

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule for automatic pet age updates
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'update-pet-age-categories': {
        'task': 'pet.tasks.update_pet_age_categories',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'weekly-condition-snapshots': {
        'task': 'pet.tasks.create_weekly_condition_snapshots', 
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Weekly Monday 3 AM
    },
    'create-weight-notifications': {
        'task': 'core.tasks.create_weight_update_notifications',
        'schedule': crontab(hour=1, minute=30),  # Daily at 1:30 AM (before age updates)
    },
}

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'