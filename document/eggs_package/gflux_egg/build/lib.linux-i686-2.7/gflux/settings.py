# -*- coding: utf-8 -*-
# Django settings for gflux project.

import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from local_settings import *
from score_settings import *
SITE_ID=1

MAX_LIMIT_UPLOAD_FILE_FREE=2
MAX_LIMIT_UPLOAD_FILE_GENERAL=100

#高峰期关键量

#波峰定义,大于平均值的偏移量,百分比
CREST_OFFSET_AVG=50

#持续时间
CREST_THROUGH_ON_TIMES=1

#波谷定义,低于平均值偏移量,百分比
THROUGH_OFFSET_AVG=70

#单个分片允许的站点数量
MAX_NB_SITES=120

#版本号
STATIC_VERSION = 'v02071635'

#油枪出油时间换算数
#每出40公升油消耗1分钟
PUMP_TRANS_TIME=40

#是否开启用户登陆保护
OPEN_USER_LOGIN_PROTECT=False

#用户登陆状态保存时间
LOGIN_STATUS_KEEP=5*60

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+i8dery6pap!7*i*&f*t)!w-@6d7c5db8t(55n^w!7h8#(^v6)'
TEMPLATE_DEBUG = DEBUG
SQL_DEBUG=DEBUG

ALLOWED_HOSTS = ['*']

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages")

# CACHE of the mapping from site-names to shard-ids


# Application definition

INSTALLED_APPS = (
    'localeurl',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    #'django.contrib.admin',
    'dash.core',
    'gflux.apps.common',
    'gflux.apps.station',                     
    'gcustomer.apps.jiachebao',
    'gcustomer.apps.gcustomer',
    'gcustomer.apps.jiayouyuan',
    'gadvertise',
    'django_gearman_commands',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

#local url django 国际化设置 http://django-localeurl.readthedocs.org/en/v2.0.1/setup.html
LOCALE_INDEPENDENT_PATHS = (
    r'^/%s__report__/'%GFLUX_URL_PREFIX,
    r'^/%sajax/'%GFLUX_URL_PREFIX,
    r'^/%sajax/'%GCUSTOMER_URL_PREFIX,
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'gflux.middlewares.LocaleURLMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'gflux.middlewares.GFLUXDBManager',
    'gcustomer.middlewares.UserOnlineStatusCheck',
    'gcustomer.middlewares.RequestEncryptionMiddleware',
)

ROOT_URLCONF = 'gflux.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'gflux.deploy.wsgi.application'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/gflux/static/'

#调试环境
STATICFILES_DIRS = (
    BASE_DIR+'/dash/core/static',
    BASE_DIR+'/gflux/static',
    BASE_DIR+'/gcustomer/static',
)

GEARMAN_SERVERS = ['127.0.0.1:4730']

#生产环境
STATIC_ROOT=BASE_DIR+'/live_auto_generate_static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR + '/gflux/templates',
    BASE_DIR + '/gcustomer/templates',
)
LOCALE_PATHS = (
    BASE_DIR+'/locale',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
MEMCACHED_TIMEOUT=7*24*60*60
CUBES_MEMCACHED_TIMEOUT=60*60
NEVER_MEMCACHED_TIMEOUT=365*24*60*60

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'ajax_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': HERE+'/logs/ajax.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'gearman_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': HERE+'/logs/gearman.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'sqlalchemy_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': HERE+'/logs/sqlalchemy.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
    },
    'loggers': {
        'django_gearman_commands': {
            'handlers': ['gearman_handler'],
            'level': 'ERROR',
            'propagate': True
        },
        'gearman': {
            'handlers': ['gearman_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'ajax': {
            'handlers': ['ajax_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'sqlalchemy.pool.QueuePool':{
            'handlers': ['sqlalchemy_handler'],
            'level': 'ERROR',
            'propagate': False
        },
    }
}

#smtp setting
SMTP_HOST='smtp.126.com'
SMTP_USERNAME='tmlsystem@126.com'
SMTP_PASSWORD='pku123'
SMTP_MSG_FROM='tmlsystem@126.com'

#服务器版本控制
JCHEBAO_APP_VERSION = 1.0
JYOUYUAN_APP_VERSION = 1.0  

#控制大客户功能
SHOW_OPTION = 0

#rsa key path
SERVER_RSA_PUBLIC_KEY = HERE + '/gcustomer/server_rsa_public_key.pem'
SERVER_RSA_PRIVATE_KEY = HERE + '/gcustomer/server_rsa_private_key.pem'




print sys.stdout,'init settings.py...'
