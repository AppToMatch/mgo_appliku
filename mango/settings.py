"""
Django settings for mango project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


REST_FRAMEWORK = {
'DEFAULT_AUTHENTICATION_CLASSES': (
'rest_framework.authentication.TokenAuthentication',
'knox.auth.TokenAuthentication',
# 'rest_framework.authentication.SessionAuthentication',
# 'rest_framework.authentication.BasicAuthentication',
),


'DEFAULT_PERMISSION_CLASSES': (
'rest_framework.permissions.IsAuthenticated',

),


'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination',
'PAGE_SIZE': 50
}
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'app',
    'general',
    'knox',
    'storages'
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mango.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {'default': 
#     {'ENGINE': 'django.db.backends.mysql',  'NAME': 'mango',  'USER': 'skupa',  'PASSWORD': '66585617Ca.',  'HOST': 'localhost',  'PORT': '3306',  }
    
# }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

try:
    import environ

    env = environ.Env()

    DEBUG = env.bool('DJANGO_DEBUG', False)

    DATABASES = {
        'default': env.db('DATABASE_URL'),
    }
    DATABASES['default']['ATOMIC_REQUESTS'] = True  # noqa F405
    DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)  # noqa F405
    SECRET_KEY = env('DJANGO_SECRET_KEY')
    if DEBUG:
        ALLOWED_HOSTS = ['*']
    else:
        ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')
except Exception:
    SECRET_KEY = 'django-insecure-*^5s566d(7i5sz&ei^idi+y#6&mg!=sm2i*r!r-j#@13cl=9j7'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    ALLOWED_HOSTS = ['mgoapi.applikuapp.com','127.0.0.1']
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


#KNOX AUTHENTICATION SETTINGS
from datetime import timedelta
from rest_framework.settings import api_settings

REST_KNOX={
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH':20,
    'TOKEN_TTL':timedelta(days=7),
    'USER_SERIALIZER':'knox.serializer.UserSerializer',
    'TOKEN_LIMIT_PER_USER':None,
    'AUTO_REFRESH':True,
    'EXPIRY_DATETIME_FORMAT':api_settings.DATETIME_FORMAT,
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST='smtp.gmail.com'
EMAIL_HOST_USER='info.intelbyt@gmail.com'
EMAIL_HOST_PASSWORD='tbdzlkfzwwfswpdo'


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
try:
    del DATABASES['default']['OPTIONS']['sslmode']
except Exception:
    pass



STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_LOCATION = 'static'
AWS_MEDIA_LOCATION = 'media'
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/' % (AWS_STORAGE_BUCKET_NAME, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'yousmart.storages.MediaStorage'

# USE_SPACES = os.getenv('USE_SPACES') == 'TRUE'

# if USE_SPACES:
#     # settings
#     AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
#     AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
#     AWS_DEFAULT_ACL = 'public-read'
#     AWS_S3_ENDPOINT_URL = 'https://nyc3.digitaloceanspaces.com'
#     AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
#     # static settings
#     AWS_LOCATION = 'static'
#     STATIC_URL = f'https://{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/'
#     STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     # public media settings
#     PUBLIC_MEDIA_LOCATION = 'media'
#     MEDIA_URL = f'https://{AWS_S3_ENDPOINT_URL}/{PUBLIC_MEDIA_LOCATION}/'
#     DEFAULT_FILE_STORAGE = 'mango.storage_backends.PublicMediaStorage'

# # private media settings
#     PRIVATE_MEDIA_LOCATION = 'private'
#     PRIVATE_FILE_STORAGE = 'mango.storage_backends.PrivateMediaStorage'
# else:
#     STATIC_URL = '/static/'
#     STATIC_ROOT = BASE_DIR / 'staticfiles'
#     MEDIA_URL = '/media/'
#     MEDIA_ROOT = BASE_DIR / 'mediafiles'

# STATICFILES_DIRS = (BASE_DIR / 'static',)

