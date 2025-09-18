"""
Django settings for PlayBharat project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Development settings
SECRET_KEY = "django-insecure-a$uqchulz($5k@*-6!b+lw(q7ghabuogd!w#=md@mu$zt@*-$*"

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Third-party apps
    "rest_framework",
    "django_htmx",
    "crispy_forms",
    "crispy_bootstrap5",
    "corsheaders",
    "django_filters",
    
    # PlayBharat apps
    "home",
    "accounts",
    "videos",
    "channels", 
    "streaming",
    "interactions",
    "search",
    "custom_admin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "playbharat.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
            ],
        },
    },
]

WSGI_APPLICATION = "playbharat.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Video file settings
VIDEO_UPLOAD_PATH = 'videos/'
THUMBNAIL_UPLOAD_PATH = 'thumbnails/'
PROFILE_PICTURE_UPLOAD_PATH = 'profile_pictures/'
CHANNEL_BANNER_UPLOAD_PATH = 'channel_banners/'
CHANNEL_AVATAR_UPLOAD_PATH = 'channel_avatars/'

# Allowed file types
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
ALLOWED_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.aac', '.flac']

# File size limits
MAX_VIDEO_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_AUDIO_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Video-specific media directories
VIDEO_UPLOAD_PATH = "videos/uploads/"
VIDEO_PROCESSED_PATH = "videos/processed/"
THUMBNAIL_PATH = "videos/thumbnails/"

# FFmpeg configuration
FFMPEG_BINARY_PATH = BASE_DIR / "ffmpeg-8.0-essentials_build" / "bin" / "ffmpeg.exe"

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB

# Internationalization - Professional global setup
# Default language and timezone
LANGUAGE_CODE = "en"
TIME_ZONE = "Asia/Kolkata"  # Indian Standard Time as default
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Supported languages for global reach
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'Hindi (हिन्दी)'),
    ('ta', 'Tamil (தமிழ்)'),
    ('te', 'Telugu (తెలుగు)'),
    ('bn', 'Bengali (বাংলা)'),
    ('mr', 'Marathi (मराठी)'),
    ('gu', 'Gujarati (ગુજરાતી)'),
    ('kn', 'Kannada (ಕನ್ನಡ)'),
    ('ml', 'Malayalam (മലയാളം)'),
    ('pa', 'Punjabi (ਪੰਜਾਬੀ)'),
    ('ur', 'Urdu (اردو)'),
    ('as', 'Assamese (অসমীয়া)'),
    ('or', 'Odia (ଓଡ଼ିଆ)'),
]

# Locale paths for translations
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Time zone choices for user preference
COMMON_TIMEZONES = [
    ('Asia/Kolkata', 'India (IST)'),
    ('Asia/Dhaka', 'Bangladesh'),
    ('Asia/Karachi', 'Pakistan'),
    ('America/New_York', 'Eastern Time (US)'),
    ('America/Los_Angeles', 'Pacific Time (US)'),
    ('Europe/London', 'London (GMT)'),
    ('Asia/Dubai', 'UAE (GST)'),
    ('Asia/Singapore', 'Singapore'),
    ('Australia/Sydney', 'Sydney'),
    ('UTC', 'UTC'),
]

# Date and number formatting
DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Number formatting
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
DECIMAL_SEPARATOR = '.'
NUMBER_GROUPING = 3

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# Crispy Forms configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOW_CREDENTIALS = True

# Security settings
ALLOWED_HOSTS = ['*']  # Restrict in production

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
