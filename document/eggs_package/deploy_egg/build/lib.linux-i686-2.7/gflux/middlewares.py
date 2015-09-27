# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,logging
from dash.core.backends.sql.models import dash_db_manager
from dash.core.types import Singleton
from gflux.apps.station.sql_utils import *
from django.utils import html
from django.utils.datastructures import SortedDict

#demo keywords
demo_keywords=SortedDict()
demo_keywords[u"长春市长通站"]=u"星海1站"
demo_keywords[u"长春市光谷站"]=u"星海2站"
demo_keywords[u"长春市硅谷站"]=u"星海3站"
demo_keywords[u"长春市浦东站"]=u"星海4站"
demo_keywords[u"长春市普庆站"]=u"星海5站"
demo_keywords[u"长春市亚泰站"]=u"星海6站"
demo_keywords[u"吉林省"]=u"星海省"
demo_keywords[u"长春市"]=u"星海市"
demo_keywords[u"朝阳区"]=u"星海一区"
demo_keywords[u"二道区"]=u"星海二区"
demo_keywords[u"农安县"]=u"星海三区"

dumps_keywords=SortedDict()
escapejs_keywords=SortedDict()
for x,y in demo_keywords.iteritems():
    dumps_keywords[json.dumps(x)[1:-1]]=json.dumps(y)[1:-1]
for x,y in dumps_keywords.iteritems():
    escapejs_keywords[html.escapejs(x)]=html.escapejs(y)

def process_response_for_demo(request,response):
    if request.path_info.find('/static/')!=-1:
        return response

    #替换escapejs的值
    for x,y in escapejs_keywords.iteritems():
        response.content=response.content.replace(x,y)

    #替换网页中的值
    for x,y in demo_keywords.iteritems():
        response.content=response.content.replace(x,y)

    #替换json中的值
    for x,y in dumps_keywords.iteritems():
        response.content=response.content.replace(x,y)

    return response

class GFLUXDBManager(object):

    #销毁session
    def destorySession(self,request):
        for site_name in request.session_pools:
            s=request.session_pools[site_name]
            try:
                s.close()
            except:
                pass

    def process_request(self,request):

        #判断如果url请求中有今天文件的请求，那么就拦截下来
        import re
        if request.path_info.startswith('/gflux/static/'):
            #得到path路径，使用正则表达式将版本号过滤掉
            request.path_info = re.sub(r'\.v\d+','',request.path_info)

        #使用闭包来cache session
        request.session_pools={}
        def get_session(site_name=None):
            if not request.session_pools.has_key(site_name):
                session=dash_db_manager.getSessionMaker(site_name)()
                request.session_pools[site_name]=session

            return request.session_pools[site_name]
        request.get_session=get_session

    #django 在进行框架内301跳转时不会调用process_request
    #例如/gflux==>/gflux/,但是会调用process_response
    def process_response(self,request,response):
        if hasattr(request,'session_pools'):
            self.destorySession(request)

        #demo账号的支持
        #过滤结果中吉林油站描述
        try:
            if request.session.has_key('username'):
                if request.session.get('username','None')=='demo':
                    response=process_response_for_demo(request,response)
        except:
            pass
            
        return response

    def process_exception(self,request, exception):
        if hasattr(request,'session_pools'):
            self.destorySession(request)
        return None

# 对URL路径做语言扩展
from django.conf import settings
import django.core.exceptions
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils import translation
from django.utils.encoding import iri_to_uri
from django.utils.translation.trans_real import parse_accept_lang_header
from localeurl import settings as localeurl_settings
# Importing models ensures that reverse() is patched soon enough. Refs #5.
from localeurl import utils

def strip_path(path):
    """
    Separates the locale prefix from the rest of the path. If the path does not
    begin with a locale it is returned without change.
    """
    import pdb
    # 匹配gflux的路径
    if hasattr(settings,'GFLUX_LOCALEURL_PATH_RE'):
        match_ret = settings.GFLUX_LOCALEURL_PATH_RE.match(path)
    # 匹配gcustomer的路径
    if match_ret==None and hasattr(settings,'GCUSTOMER_LOCALEURL_PATH_RE'):
        match_ret = settings.GCUSTOMER_LOCALEURL_PATH_RE.match(path)
    # 匹配wheel的路径
    if match_ret==None and hasattr(settings, 'APP_LOCALEURL_PATH_RE'):
        match_ret = settings.APP_LOCALEURL_PATH_RE.match(path)
    #匹配支付的路径
    if match_ret==None and hasattr(settings, 'JCBPAY_LOCALEURL_PATH_RE'):
        match_ret = settings.JCBPAY_LOCALEURL_PATH_RE.match(path)
    # 匹配缺省路径
    if match_ret==None :
        match_ret = localeurl_settings.PATH_RE.match(path)

    # 如果匹配到
    if match_ret!=None:
        path_info = match_ret.group('path') or '/'
        if path_info.startswith('/'):
            return match_ret.group('locale'), path_info
    return '', path

def none_locale_path(path):
    if path.startswith('/'+settings.GFLUX_URL_PREFIX):
        return path
    elif path.startswith('/'+settings.GCUSTOMER_URL_PREFIX):
        return path
    elif path.startswith('/'+settings.APP_URL_PREFIX):
        return path
    elif path.startswith('/'+settings.JCB_PAY_URL_PREFIX):
        return path
    elif path.find(settings.GFLUX_URL_PREFIX)!=-1:
        return ''.join([u'',settings.GFLUX_URL_PREFIX,path])
    elif path.find(settings.APP_URL_PREFIX)!=-1:
        return ''.join([u'',settings.APP_URL_PREFIX,path]) 
    elif path.find(settings.JCB_PAY_URL_PREFIX)!=-1:
        return ''.join([u'',settings.JCB_PAY_URL_PREFIX,path]) 
    else:
        return ''.join([u'',settings.GCUSTOMER_URL_PREFIX,path])

def locale_path(path, locale=''):
    """
    Generate the localeurl-enabled path from a path without locale prefix. If
    the locale is empty settings.LANGUAGE_CODE is used.
    """
    locale = utils.supported_language(locale)
    if not locale:
        locale = utils.supported_language(settings.LANGUAGE_CODE)
    if utils.is_locale_independent(none_locale_path(path)):
        return none_locale_path(path)
    elif utils.is_default_locale(locale) and not localeurl_settings.PREFIX_DEFAULT_LOCALE:
        return none_locale_path(path)
    elif path.find(settings.GFLUX_URL_PREFIX)!=-1:
        return ''.join([u'/',settings.GFLUX_URL_PREFIX, locale, path])
    elif path.find(settings.APP_URL_PREFIX)!=-1:
        return ''.join([u'/',settings.APP_URL_PREFIX, locale, path])
    elif path.find(settings.GCUSTOMER_URL_PREFIX)!=-1:
        return ''.join([u'/',settings.GCUSTOMER_URL_PREFIX, locale, path])
    elif path.find(settings.JCB_PAY_URL_PREFIX)!=-1:
        return path
    else :
        return none_locale_path(path)

utils.strip_path=strip_path
utils.locale_path=locale_path

# Make sure the default language is in the list of supported languages
assert utils.supported_language(settings.LANGUAGE_CODE) is not None, \
        "Please ensure that settings.LANGUAGE_CODE is in settings.LANGUAGES."

class LocaleURLMiddleware(object):
    """
    Middleware that sets the language based on the request path prefix and
    strips that prefix from the path. It will also automatically redirect any
    path without a prefix, unless PREFIX_DEFAULT_LOCALE is set to True.
    Exceptions are paths beginning with MEDIA_URL and/or STATIC_URL (if
    settings.LOCALE_INDEPENDENT_MEDIA_URL and/or
    settings.LOCALE_INDEPENDENT_STATIC_URL are set) or matching any regular
    expression from LOCALE_INDEPENDENT_PATHS from the project settings.

    For example, the path '/en/admin/' will set request.LANGUAGE_CODE to 'en'
    and request.path to '/admin/'.

    Alternatively, the language is set by the first component of the domain
    name. For example, a request on 'fr.example.com' would set the language to
    French.

    If you use this middleware the django.core.urlresolvers.reverse function
    is be patched to return paths with locale prefix (see models.py).
    """
    def __init__(self):
        if not settings.USE_I18N:
            raise django.core.exceptions.MiddlewareNotUsed()

    def process_request(self, request):
        locale, path = utils.strip_path(request.path_info)
        #print '\n',locale,path,request.session.get('django_language',''),'\n'
        if localeurl_settings.USE_SESSION and not locale:
            slocale = request.session.get('django_language')
            if slocale and utils.supported_language(slocale):
                locale = slocale
        if localeurl_settings.USE_ACCEPT_LANGUAGE and not locale:
            accept_lang_header = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            header_langs = parse_accept_lang_header(accept_lang_header)
            accept_langs = filter(
                None,
                [utils.supported_language(lang[0]) for lang in header_langs]
                )
            if accept_langs:
                locale = accept_langs[0]
        locale_path = utils.locale_path(path, locale)
        # locale case might be different in the two paths, that doesn't require
        # a redirect (besides locale they'll be identical anyway)
        if locale_path.lower() != request.path_info.lower():
            locale_url = utils.add_script_prefix(locale_path)

            qs = request.META.get("QUERY_STRING", "")
            if qs:
                # Force this to remain a byte-string by encoding locale_path
                # first to avoid Unicode tainting - downstream will need to
                # handle the job of handling in-the-wild character encodings:
                locale_url = "%s?%s" % (locale_path.encode("utf-8"), qs)

            redirect_class = HttpResponsePermanentRedirect
            if not localeurl_settings.LOCALE_REDIRECT_PERMANENT:
                redirect_class = HttpResponseRedirect
            # @@@ iri_to_uri for Django 1.0; 1.1+ do it in HttpResp...Redirect
            return redirect_class(iri_to_uri(locale_url))
        request.path_info = path
        if not locale:
            try:
                locale = request.LANGUAGE_CODE
            except AttributeError:
                locale = settings.LANGUAGE_CODE
        translation.activate(locale)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
