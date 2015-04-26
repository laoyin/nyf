#coding=utf-8
"""
Django settings for nyf project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4%-%dca6dkcxze1m!*-4@0w&fy!dr&&v4l4m4t_mnix075*0v@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'demosite',
    'gdesign',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'nyf.urls'

WSGI_APPLICATION = 'nyf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'master'  ,           # Or path to database file if using sqlite3.
        'USER': 'root',
        'PASSWORD': 'nyf',
        'HOST': '',             # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',                      # Set to empty string for default.
    },
    'demosite': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'demosite'   ,   # Or path to database file if using sqlite3.
        'USER': 'root',
        'PASSWORD': 'nyf',
        'HOST': '',             # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',                      # Set to empty string for default.
    },
    'gdesign': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gdesign'        ,             # Or path to database file if using sqlite3.
        'USER': 'root',
        'PASSWORD': 'nyf',
        'HOST': '',             # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',                      # Set to empty string for default.
    },
}

DATABASE_ROUTERS=['nyf.router.DemositeRouter','nyf.router.GdesignRouter']
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    BASE_DIR+'/nyf/static',
    BASE_DIR+'/gdesign/static',
    BASE_DIR+'/demosite/static',
)

#template file
#使用绝对路径

TEMPLATE_DIRS = (

     BASE_DIR+'/nyf/templates',
     BASE_DIR+'/gdesign/templates', 
                )

MEDIA_ROOT=BASE_DIR+"/nyf/static"


