#encoding=utf-8
from django.utils.translation import ugettext_lazy

DEBUG = True
import os
HERE=os.path.abspath(os.path.dirname(__file__))
PYTHON_BIN='/usr/bin/python2.7'
# This setting is used by django orm

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'new_gflux',                      # Or path to database file if using sqlite3.
        'USER': 'nyf',
        'PASSWORD': 'nyf',
        'HOST': 'localhost',             # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',   
    },

}

SITE_NAME = "Dash Analytics"
GCUSTOMER_URL_PREFIX='gcustomer/'
GFLUX_URL_PREFIX = 'gflux/'
APP_URL_PREFIX = 'wheel/'
DASH_URL=HERE+'/../../dash/'
JCB_PAY_URL_PREFIX = 'jcbpay/'

# This setting is used by sqlalchemy orm
# 第一个数据库将用来存一些全局的数据，和用户表格等
# 第二个以后的数据库将用做sharding
SQL_BACKENDS = [
    {
        'db_name': 'new_gflux',
        #'db_url': 'postgresql://wangdong:wangdong@127.0.0.1/gflux',
        'db_url': 'postgresql://nyf:nyf@localhost/new_gflux',
        'db_pool_size': 15,
        'db_charset': 'utf-8',
        'db_pool_recycle': 20000
    },
]

# 强制django将所有请求视为https
SESSION_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
CSRF_COOKIE_SECURE = True

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

LANGUAGES = (
    ('en', ugettext_lazy(u"英文")),
    ('zh-cn',ugettext_lazy(u"中文")),
)

#自定义local url prefix
import re
LOCALEURL_SUPPORTED_LOCALES = dict(
    (code.lower(), name) for code, name in LANGUAGES)
# Issue #15. Sort locale codes to avoid matching e.g. 'pt' before 'pt-br'
LOCALEURL_LOCALES_RE = '|'.join(
    sorted(LOCALEURL_SUPPORTED_LOCALES.keys(), key=lambda i: len(i), reverse=True))
GFLUX_LOCALEURL_PATH_RE = re.compile(r'^/%s(?P<locale>%s)(?P<path>.*)$' %(
    GFLUX_URL_PREFIX,
    LOCALEURL_LOCALES_RE), re.I)
GCUSTOMER_LOCALEURL_PATH_RE = re.compile(r'^/%s(?P<locale>%s)(?P<path>.*)$' %(
    GCUSTOMER_URL_PREFIX,
    LOCALEURL_LOCALES_RE), re.I)
APP_LOCALEURL_PATH_RE = re.compile(r'^/%s(?P<locale>%s)(?P<path>.*)$' %(
    APP_URL_PREFIX,
    LOCALEURL_LOCALES_RE), re.I)
JCBPAY_LOCALEURL_PATH_RE = re.compile(r'^/%s(?P<locale>%s)(?P<path>.*)$' %(
    JCB_PAY_URL_PREFIX,
    LOCALEURL_LOCALES_RE), re.I)

#是否自动判断Accept-Language头转换语言
LOCALEURL_USE_ACCEPT_LANGUAGE=False

#是否显示语言前缀
PREFIX_DEFAULT_LOCALE = True

#是否在session中保存用户指定的语言
LOCALEURL_USE_SESSION=True
