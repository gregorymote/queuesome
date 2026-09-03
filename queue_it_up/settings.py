"""
Django settings for queue_it_up project.

Environment-driven settings for the Queuesome Django application.
"""

import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    return [
        item.strip()
        for item in os.getenv(name, default).split(',')
        if item.strip()
    ]


ENVIRONMENT = os.getenv('DJANGO_ENV', 'development').strip().lower()
if ENVIRONMENT not in {'development', 'staging', 'production'}:
    raise ImproperlyConfigured(
        'DJANGO_ENV must be development, staging, or production.'
    )

STATE = {
    'development': 'DEV',
    'staging': 'STAGE',
    'production': 'PROD',
}[ENVIRONMENT]
HEROKU = ENVIRONMENT != 'development'
STAGE = ENVIRONMENT == 'staging'
DEBUG = env_bool('DJANGO_DEBUG', ENVIRONMENT == 'development')
if ENVIRONMENT == 'production' and DEBUG:
    raise ImproperlyConfigured('DJANGO_DEBUG cannot be enabled in production.')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY') or os.getenv('DJANGO_SECRET_Q')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'unsafe-local-development-key'
    else:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY is required outside development.'
        )


ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS')
DEBUG_PROPAGATE_EXCEPTIONS = False

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', not DEBUG)
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS'
)
SECURE_HSTS_PRELOAD = env_bool('DJANGO_SECURE_HSTS_PRELOAD')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'background_task',
    'start',
    'party',
    'game',
    'blog',
    'spot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SESSION_SAVE_EVERY_REQUEST = True

BACKGROUND_TASK_RUN_ASYNC = True
BACKGROUND_TASK_ASYNC_THREADS = 1000

ROOT_URLCONF = 'queue_it_up.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'queue_it_up' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'queue_it_up.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://queuesome:queuesome@127.0.0.1:5432/queuesome',
        conn_max_age=600 if not DEBUG else 0,
        conn_health_checks=True,
    )
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
PROJECT_ROOT = BASE_DIR
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    },
}

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# aws settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = (
    f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    if AWS_STORAGE_BUCKET_NAME else ''
)
AWS_S3_FILE_OVERWRITE = True


PORT = os.getenv('PORT', '8000')
default_url = {
    'development': f'http://localhost:{PORT}',
    'staging': 'https://q-it-up-staging.herokuapp.com',
    'production': 'https://www.queuesome.com',
}[ENVIRONMENT]
URL = os.getenv('APP_URL', default_url).rstrip('/')
parsed_url = urlparse(URL)
IP = parsed_url.hostname or 'localhost'
URI = os.getenv('SPOTIFY_REDIRECT_URI', f'{URL}/party/auth/')
SPOT_URI = os.getenv('SPOT_REDIRECT_URI', f'{URL}/spot/auth/')

CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SCOPE = 'user-read-playback-state user-modify-playback-state'
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SYSTEM = os.getenv('SYSTEM_USER_ID')
QDEBUG = 'QDEBUG!: '
