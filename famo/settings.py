import os
from pathlib import Path
from decouple import config

# OpenAI API Key
OPENAI_API_KEY = config("OPENAI_API_KEY")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-a-cmg)jy(6pdt3uz2*n-fjsh-y_20_#&_8x*+(%lx*bju#xo7z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['fammo.ai', 'localhost', 'your_project_id.appspot.com', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'userapp',
    'core',
    'tailwind',
    'theme',
    'pet',
    "widget_tweaks",
    'aihub',
    'subscription',
    'blog',
    'markdownify',
]

TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"
if DEBUG:
    # Add django_browser_reload only in DEBUG mode
    INSTALLED_APPS += ['django_browser_reload']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    # Add django_browser_reload middleware only in DEBUG mode
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

ROOT_URLCONF = 'famo.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'famo.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('tr', 'Türkçe'),
    ('nl', 'Nederlands'),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # where you place custom static files
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # where collectstatic will gather everything

# Media files setup (uploads)
MEDIA_URL = '/media/'

# Set media root for local development
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  

# Production media configuration with Google Cloud Storage
if not DEBUG:
    INSTALLED_APPS += ['storages']
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = 'ali2087.appspot.com'  # Use your bucket name here (either ali2087.appspot.com or staging.ali2087.appspot.com)
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'userapp.CustomUser'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'dashboard'         # After login
LOGOUT_REDIRECT_URL = 'login'

MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',
            'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img', 'hr', 'br'
        ],
        "WHITELIST_ATTRS": ['href', 'src', 'alt', 'class'],
        "MARKDOWN_EXTENSIONS": [
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
        ],
    }
}
