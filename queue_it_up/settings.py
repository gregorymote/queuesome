"""
Django settings for queue_it_up project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import dj_database_url

STATE="STAGE"
if STATE=="DEV":
    HEROKU = False
    STAGE = False
    DEBUG = True
elif STATE == "STAGE":
    HEROKU = True
    STAGE = True
    DEBUG = True
else:
    HEROKU = True
    DEBUG = False
    STAGE = False

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_Q")


ALLOWED_HOSTS = [
    'localhost',
    'q-it-up.herokuapp.com',
    'q-it-up-staging.herokuapp.com',
    'www.qitup.us',
    'www.friyayvibes.com',
    'www.queuesome.com'
]
DEBUG_PROPAGATE_EXCEPTIONS = False

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
        'DIRS': ["queue_it_up/templates/"],
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
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

if HEROKU:
    ####Heroku Postgresql
    DATABASES = {}
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)
else:
    ##Local Postgresql
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'queue_it_up',
            'USER': 'admin',
            'PASSWORD': 'admin',
            'HOST': '127.0.0.1',
            'PORT': '',
        }
    }
    ##Local SQL Lite
    #DATABASES = {
    #    'default': {
    #        'ENGINE': 'django.db.backends.sqlite3',
    #        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #    }
    #}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
#PROJECT_ROOT   =   os.path.join(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(PROJECT_ROOT,'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(PROJECT_ROOT,'media')
MEDIA_URL = '/media/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

#  Add configuration for static files storage using whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

PORT='8000'
if STAGE:
    proto='http://'
    IP='q-it-up-staging.herokuapp.com'
elif HEROKU:
    proto='https://'
    IP='queuesome.com'
else:
    proto='http://'
    IP='localhost'
if HEROKU:
    URL=proto + IP
    URI = URL + '/party/auth/'
else:
    URL=proto + IP + ':' + PORT
    URI = URL + '/party/auth/'

CLIENT_SECRET=os.environ.get("SPOTIFY_CLIENT_SECRET")
SCOPE = 'user-read-playback-state user-modify-playback-state'
CLIENT_ID='6de276d9e60548d5b05a7af92a5db3bb'
SYSTEM=os.environ.get("SYSTEM_USER_ID")
QDEBUG = 'QDEBUG!: '
