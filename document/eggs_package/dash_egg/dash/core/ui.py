# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

import sys
import uuid
import copy
from abc import ABCMeta, abstractmethod
from django.forms import Media
from django.template import Context, loader
from django.http import HttpResponse,HttpResponseRedirect
from django.utils import six
from django.conf.urls import patterns, url
from django.utils.safestring import mark_safe
from django.utils.encoding import python_2_unicode_compatible
from django.views.decorators.cache import never_cache
from dash.core.types import overrides, Singleton, DashDefiningClass
from dash.core.processors import force_utf8
from django.conf import settings
from . import utils
from . import reports
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
import pdb,traceback,StringIO,copy

"""
请不要在这个地方引入非底层的接口，容易循环引用
请在使用的地方引入对应接口
"""

class UIException(Exception):
    "UI Exception"

#UI抽象类
class UIDefiningClass(DashDefiningClass, ABCMeta):
    "Metaclass for UI classes"
    def __new__(cls, name, bases, attrs):
        new_class = super(UIDefiningClass, cls).__new__(cls, name, bases, attrs)

        #如果子类非抽象则需要算出uid
        if not new_class.__abstract__:
            if new_class.uid is None:
                new_class.uid = utils.uid(new_class.__name__)

        #添加类属性label
        if isinstance(new_class.label, six.string_types):
            new_class.label = force_utf8(new_class.label)
        elif type(new_class.label)==type(ugettext_lazy('')):
            pass
        else:
            new_class.label = new_class.uid
        return new_class

#python3 要求__str__ return unicode
#python2 要求__str__ return encoded string
#使用此修饰符兼容python2
@python_2_unicode_compatible
class BaseUI(object):
    "Base class for all UI classes"
    __metaclass__ = UIDefiningClass
    __abstract__ = True

    uid = None
    label = None
    desc = ''

    def __new__(cls, *args, **kwargs):
        #子类不是抽象类
        if cls.__abstract__:
            raise UIException("Abstract UI class '%s' cannot be instantiated."
                              % cls.__name__)
        return super(BaseUI, cls).__new__(cls, *args, **kwargs)

    def __init__(self):
        #添加实例变量media，使用django form media组件
        #url映射，由settings中STATIC_URL
        self.media = Media()
        self.media += self.__aggregate_media__()


    def __str__(self):
        return u"<%s '%s'>" % (self.__class__.__name__, self.uid)

    #抽象方法，由子类实现
    @abstractmethod
    def render(self, **context):
        pass

    def warn(self, msg):
        #print >> sys.stderr, "[WARNING] <%s> %s" % (self.__class__.__name__, msg)
        pass

    def error(self, msg):
        raise UIException("<%s> %s" % (self.__class__.__name__, msg))

    def __aggregate_media__(self):
        # Get the media property of the superclass, if it exists
        cls = self.__class__
        sup_cls = super(cls, self)
        try:
            base = sup_cls.media
        except AttributeError:
            base = Media()

        # Get the media definition for this class
        definition = getattr(cls, 'Media', None)
        if definition:
            extend = getattr(definition, 'extend', True)
            if extend:
                if extend == True:
                    m = base
                else:
                    m = Media()
                    for medium in extend:
                        m = m + base[medium]
                return m + Media(definition)
            else:
                return Media(definition)
        else:
            return base

#抽象类
class UIView(BaseUI):
    "Base class for all the UI classes which can act as view"
    __abstract__ = True

    #闭包用法
    #惰性返回view处理
    def as_view(self):
        """
        Main entry point for a request-response process.
        """
        @never_cache
        def view(request, *args, **kwargs):
            from gflux.util import checkUserOnlineStatus,Status
            ret=checkUserOnlineStatus(request)
            if ret!=Status.LOGINSUCCESS:
                return HttpResponseRedirect("/%slogin.html"%settings.GFLUX_URL_PREFIX)
            return HttpResponse(self.render(request=request))

        return view

    #抽象方法，由子类实现
    #自定义path
    @abstractmethod
    def path(self):
        pass

    @property
    def urlpattern(self):
        return url(r'^%s%s$' % (settings.GFLUX_URL_PREFIX, self.path()), self.as_view(), name=self.path())

    @property
    def url(self):
        return '/' + settings.GFLUX_URL_PREFIX + self.path()

#page类容器
class PageGroup(object):
    def __init__(self, label, page_or_tuple):
        self.label = force_utf8(label)
        if isinstance(page_or_tuple, Page):
            self.pages = (page_or_tuple, )
        else:
            self.pages = page_or_tuple
        self.uid = uuid.uuid4().hex[:8]

    def page_uids(self):
        return [page.uid for page in self]

    #实现类的迭代器
    def __iter__(self):
        return iter(self.pages)

#抽象类
class Portal(UIView):
    "Base class for portals"
    __abstract__ = True
    list_page = ()
    try_user_page =()
    startpage = None

    def __init__(self):
        super(Portal, self).__init__()
        #print 'init ',self.label,' portal...'
        self._page_groups = []
        self._page_groups_try_user=[]
        self._registry = {}
        self._registry_try_user={}
        self._pages = []
        self._pages_try_user=[]
        self.try_user_portal=None

        # Register pages
        #注册page
        #list page是子类定义列表
        for index, node in enumerate(self.list_page):
            #判断是否是元类，是否是Page子类
            if isinstance(node, type) and issubclass(node, Page):
                page_class = node

                #注册类取得实例，加入容器
                page = self.register(page_class)
                if page is not None:
                    self._page_groups.append(PageGroup(None, page))

            #判断是否是list或者tuple
            elif isinstance(node, (list, tuple)):
                if len(node) != 2:
                    self.error("'list_page[%d]' does not have exactly two elements" % index)

                #解包
                label, page_or_tuple = node

                #以下逻辑繁杂
                #大意是同上注册类，实例化，加入容器
                if isinstance(page_or_tuple, type) and issubclass(page_or_tuple, Page):
                    page_classes = (page_or_tuple, )
                elif isinstance(page_or_tuple, (list, tuple)):
                    page_classes = page_or_tuple
                else:
                    continue

                pages = []
                for page_class in page_classes:
                    page = self.register(page_class)
                    if page is not None:
                        pages.append(page)
                if len(pages) > 0:
                    if isinstance(label, six.string_types):
                        self._page_groups.append(PageGroup(label, pages))
                    elif type(label)==type(ugettext_lazy(u"")):
                        self._page_groups.append(PageGroup(label, pages))
                    elif label is None:  # if group's label is None, flatten its pages
                        for page in pages:
                            self._page_groups.append(PageGroup(None, page))
            else:
                self.error("'list_page[%d]' must be a Page or tuple" % index)

        # Register try user pages
        #注册page
        #list page是子类定义列表
        for index, node in enumerate(self.try_user_page):

            #判断是否是元类，是否是Page子类
            if isinstance(node, type) and issubclass(node, Page):
                page_class = node

                #注册类取得实例，加入容器
                page = self.register(page_class,from_try_user=True)
                if page is not None:
                    self._page_groups_try_user.append(PageGroup(None, page))

            #判断是否是list或者tuple
            elif isinstance(node, (list, tuple)):
                if len(node) != 2:
                    self.error("'list_page[%d]' does not have exactly two elements" % index)

                #解包
                label, page_or_tuple = node

                #以下逻辑繁杂
                #大意是同上注册类，实例化，加入容器
                if isinstance(page_or_tuple, type) and issubclass(page_or_tuple, Page):
                    page_classes = (page_or_tuple, )
                elif isinstance(page_or_tuple, (list, tuple)):
                    page_classes = page_or_tuple
                else:
                    continue

                pages = []
                for page_class in page_classes:
                    page = self.register(page_class,from_try_user=True)
                    if page is not None:
                        pages.append(page)
                if len(pages) > 0:
                    if isinstance(label, six.string_types):
                        self._page_groups_try_user.append(PageGroup(label, pages))
                    elif type(label)==type(ugettext_lazy(u"")):
                        self._page_groups_try_user.append(PageGroup(label, pages))
                    elif label is None:  # if group's label is None, flatten its pages
                        for page in pages:
                            self._page_groups_try_user.append(PageGroup(None, page))
            else:
                self.error("'list_page[%d]' must be a Page or tuple" % index)

        #获取子类类属性
        startpage_class = self.__class__.startpage

        #对实例添加startpage变量
        if startpage_class is not None and issubclass(startpage_class, Page):
            self.startpage = startpage_class()
            self.startpage.portal = self
        else:
            self.startpage = self._pages[0] if len(self._pages) > 0 else None

        if len(self._page_groups) == 0 and self.startpage is None:
            self.error('no valid pages')

    #注册page子类
    def register(self, page_class,from_try_user=False):
        if not issubclass(page_class, Page):
            self.warn("the class to register is not a subclass of Page")
            return None

        if from_try_user==True and page_class.uid in self._registry_try_user:
            self.warn("ignore the page class whose uid is '%s' and already registered to %s"
                      % (page_class.uid, self))
            return None

        if from_try_user==False and  page_class.uid in self._registry:
            self.warn("ignore the page class whose uid is '%s' and already registered to %s"
                      % (page_class.uid, self))
            return None

        page = page_class(portal=self)

        if from_try_user:
            self._registry_try_user[page.uid] = page
            self._pages_try_user.append(page)

        else:
            self._registry[page.uid] = page
            self._pages.append(page)

        return page

    def generateTryUserPortal(self):
        self.try_user_portal=type('TryUserPortal', (object,), dict())
        self.try_user_portal.uid=self.uid
        self.try_user_portal.label=self.label
        self.try_user_portal.page_groups=self.page_groups_try_user

    @overrides(UIView)
    def path(self):
        return self.uid

    def check_user_portal_permission(self, username) :
        from gflux.apps.station.sql_utils import get_user_account_type_by_name
        from gflux.apps.station.sql_utils import get_enable_advanced_features_by_name
        from gflux.apps.station.sql_utils import check_if_user_is_allowed_to_portal
        # 获取用户类型
        user_type=get_user_account_type_by_name(username)
        #get enable_advanced_features
        enable_advanced_features=get_enable_advanced_features_by_name(username)

        # 检查该用户类型是否允许访问该portal
        allowed=check_if_user_is_allowed_to_portal(self, user_type)

        return (user_type,allowed,enable_advanced_features)

    @overrides(UIView)
    def render(self, **context):
        #生成试用版用户的portal
        if self.try_user_portal is None:
            self.generateTryUserPortal()
        # 检查用户是否有读取该portal的权限
        (user_type, allowed,enable_advanced_features)=self.check_user_portal_permission(context['request'].session['username'])
        if allowed==False:
            return self.render_default()

        context.update({'portal_allowed': allowed,
                        'account_type': user_type,
                        'enable_advanced_features':enable_advanced_features})
        if self.startpage:
            return self.startpage.render(**context)
        else:
            return self.render_default()

    def render_default(self):
        return _('<h1>你还未通过审核，请耐心等候。</h1>')

    @property
    def page_groups(self):
        return self._page_groups

    @property
    def page_groups_try_user(self):
        return self._page_groups_try_user

    def __iter__(self):
        return iter(self._pages)

class FieldWrapper(object):
    def __init__(self, field):
        self.field = field  # A django.forms.BoundField instance

    def label(self):
        return self.field.label

    def label_tag(self):
        #attrs = {'class': 'sr-only'}
        attrs = {}
        return self.field.label_tag(attrs=attrs)

    def errors(self):
        return mark_safe(self.field.errors.as_ul())

#抽象类
class Page(UIView):
    "Base class for pages"
    __abstract__ = True

    icon = ''
    list_module = []
    template = loader.get_template("dash/page.html")
    list_filter = None

    def __init__(self,portal=None):
        super(Page, self).__init__()
        #print 'init ',self.label,' page...'

        self.portal=portal
        self.extend_media=Media()
        self._modules = []
        self._rows = []
        self._registry = {}
        # Register modules
        #注册数据模型
        for index, node in enumerate(self.list_module):
            #判断子类类型
            if isinstance(node, type) and issubclass(node, UIModule):
                module_class = node
                #注册数据模型
                module = self.register(module_class)
                if module is not None:
                    self._rows.append((12, (module,)))

            #同上
            elif isinstance(node, (list, tuple)):
                modules = []
                for module_class in node:
                    if issubclass(module_class, UIModule):
                        module = self.register(module_class)
                        if module is not None:
                            modules.append(module)
                l = len(modules)
                if l == 0:  # ignore empty tuple
                    continue
                if l >= 3:
                    self.error("'list_module[%d]' does not have one or two elements" % index)
                self._rows.append((12 / l, modules))
            else:
                self.error("'list_module[%d]' must be a UIModule or tuple" % index)
        filters = {}
        filter_refcount = {}
        nb_dashes = 0
        for module in self._modules:
            # extract common filters and put them on top of all ui modules
            #抽取数据模型中定义的公共过滤选项
            if isinstance(module, Dash):
                nb_dashes += 1
                for field in module.filters:
                    if field.field.name in filters:
                        field_ = filters[field.field.name].field
                        if str(field.field) != str(field_):
                            self.warn("two different fields have the same field name '%s'" % field.field.name)
                        else:
                            filter_refcount[field.field.name] += 1
                    else:
                        filters[field.field.name] = field
                        filter_refcount[field.field.name] = 1

        # 如果某个过滤选项在所有的dash中都存在
        common_filters = set([field_name for field_name in filter_refcount if filter_refcount[field_name] == nb_dashes])
        list_filter = _clean_list_filter(self.list_filter)
        filters_to_remove = set()
        if list_filter is None:
            self._filters = [field for field in filters.values() if field.field.name in common_filters]
            filters_to_remove = set([field.field.name for field in self._filters])
        else:
            self._filters = []
            for field_name in list_filter:
                if field_name in filters and field_name in common_filters:
                    self._filters.append(filters[field_name])
                    filters_to_remove.add(field_name)

        for module in self._modules:
            if isinstance(module, Dash):
                module.remove_filters(filters_to_remove)

    #注册page
    def register(self, module_class):
        if not issubclass(module_class, UIModule):
            self.warn("the class to register is not a subclass of UIModule")
            return None
        if module_class.uid in self._registry:
            self.warn("ignore the module class whose uid is '%s' and already registered to %s"
                      % (module_class.uid, self))
            return None
        module = module_class(portal=self.portal.__class__)
        self._registry[module.uid] = module
        self._modules.append(module)
        self.media += module.media
        return module

    @overrides(UIView)
    def path(self):
        return "%s/%s" % (self.portal.path(), self.uid)

    def check_user_portal_permission(self, username) :
        from gflux.apps.station.sql_utils import get_user_account_type_by_name
        from gflux.apps.station.sql_utils import get_enable_advanced_features_by_name
        from gflux.apps.station.sql_utils import check_if_user_is_allowed_to_portal
        # 获取用户类型
        user_type=get_user_account_type_by_name(username)

        # 检查该用户类型是否允许访问该portal
        allowed=check_if_user_is_allowed_to_portal(self.portal, user_type)

        #get enable_advanced_features
        enable_advanced_features=get_enable_advanced_features_by_name(username)

        return (user_type, allowed,enable_advanced_features)

    def render_default(self):
        return ''

    def clean_portal_label_on_page(self,user_type):
        from gflux.apps.station.sql_utils import check_if_user_is_allowed_to_portal

        tmp_portal=[]
        for portal in self.portal.site:
            if check_if_user_is_allowed_to_portal(portal, user_type):
                tmp_portal.append(portal)

        return tmp_portal

    @overrides(UIView)
    def render(self, **context):
        # 检查用户是否有读取该portal的权限
        (user_type, allowed,enable_advanced_features)=self.check_user_portal_permission(context['request'].session['username'])

        if allowed==False:
            return self.render_default()

        context.update({'portal_allowed': allowed,
                        'account_type': user_type,
                        'enable_advanced_features':enable_advanced_features})

        #print 'render '+self.label+' page...'
        context.update({
            'current_portal': self.portal,
            'current_page': self,
            'site_portals': self.clean_portal_label_on_page(user_type),
            'site':self.portal.site,
            'settings': settings,
        })

        #试用版用户，只允许看到规定的视图
        if user_type==1:
            if self.portal.try_user_portal is None:
                self.portal.generateTryUserPortal()

            context['current_portal']=self.portal.try_user_portal

        #每次请求都需要动态更新过滤选项,每个请求的过滤选项是不同的
        #都需要将默认的选项拷贝出来，在渲染时传给目标
        #不可更改实例的属性，因为实例是所有用户共享的

        #self._filters放置的从Dash中提取出来的公共过滤选项
        if 'request' in context:
            context['user'] = context['request'].session.get('username',None)
        else:
            context['user']=None

        self.update_filters_by_user_name(context['request'].session['username'],
            context=context,be_page_filter=True)

        #传给page的dash列表
        all_dash_row=[]

        #如果用户类型为试用用户，则根据user_permission控制视图权限和前端显示
        if user_type==1:
            for row in self._rows:
                if row[1][0].enable_on_try_user:
                    all_dash_row.append(row)
        else:
            #对于非公共过滤选项，需要先深拷贝self._rows(Dash列表),再依次更新其过滤选项
            all_dash_row=copy.deepcopy(self._rows)

        for spec,dash_row in all_dash_row:
            for module in dash_row:
                module.update_filters_by_user_name(context['user'],
                    be_module_filter=True,context=context)
        context['current_dash_row']=all_dash_row
        return self.template.render(Context(context))

    #更新公共过滤选项中与用户相关的部分
    def update_filters_by_user_name(self, username,context=None,
        be_module_filter=False,be_page_filter=False):
        from gflux.apps.station.sql_utils import get_user_stations_by_name
        from gflux.apps.station.sql_utils import get_user_fuel_type_by_name
        from gflux.apps.station.sql_utils import get_system_fuel_type
        from gflux.apps.station.sql_utils import locate_china_location_id_from_request
        from gflux.apps.station.sql_utils import get_china_location_name_by_id,getUserLocationInfo
        from gflux.apps.station.sql_utils import getUserTags
        if username==None:
            return

        #print 'update filter '+self.label+' page...'
        _filters=copy.deepcopy(self._filters)
        for field in _filters :
            if field.field.name == 'site' :
                field.field.field.choices=get_user_stations_by_name(username)
            elif field.field.name == 'fuel_type':
                field.field.field.choices=[(0,_(u'任意'))]+get_user_fuel_type_by_name(username)
            elif field.field.name=='system_fuel_type':
                field.field.field.choices=[(0,_(u'任意'))]+get_system_fuel_type()
            elif field.field.name=='china_location':
                request=context['request']
                ids=getUserLocationInfo(request)
                re_ids = []
                for id in ids:
                    re_ids.append((id,get_china_location_name_by_id(id)))
                field.field.field.choices=re_ids
            elif field.field.name == 'tag':
                tags = getUserTags(username)
                field.field.field.choices=tags

        #更新filter
        if be_module_filter:
            self._filters=_filters

        if be_page_filter:
            context['page_filters']=_filters

    @property
    def media_js(self):
        media = Media()
        try:
            media += self.media['js']
            media += self.extend_media['js']
        except:
            pass
        return media

    @property
    def media_css(self):
        media = Media()
        try:
            media += self.media['css']
            media += self.extend_media['css']
        except:
            pass
        return media

    @property
    def filters(self):
        return self._filters

    @property
    def modules(self):
        return self._modules

    def __iter__(self):
        return iter(self._rows)

    class Media:
        js = [
            'js/jquery.min.js',
            'js/jquery-migrate.js',
            'js/jquery.blockUI.js',
            'bootstrap/js/bootstrap.min.js',
            'js/utils.'+settings.STATIC_VERSION+'.js',
            'js/underscore.min.js',
            'js/core.'+settings.STATIC_VERSION+'.js',
            'js/main_framework.'+settings.STATIC_VERSION+'.js',
            'js/jquery.cookie-1.4.1.min.js',
        ]
        css = {
            'all': ('bootstrap/css/bootstrap.css',
                    'css/core.'+settings.STATIC_VERSION+'.css',
                    'css/main_framework.'+settings.STATIC_VERSION+'.css',)
        }

#元类，没有其他功能，只做传递父类
class UIModuleDefiningClass(UIDefiningClass):
    "Metaclass for UIModule classes"
    def __new__(cls, name, bases, attrs):
        return super(UIModuleDefiningClass, cls).__new__(cls, name, bases, attrs)

# Apply the decorator again to re-bind __unicode__ to the new __str__ method
@python_2_unicode_compatible
#抽象类
class UIModule(BaseUI):
    "Base class for all UI modules which can be rendered as html block in a page"
    __abstract__ = True
    __metaclass__ = UIModuleDefiningClass

    #返回安全的渲染结果
    def __str__(self):
        return mark_safe(self.render_as_module())

    #返回非安全的渲染结果
    def render_as_module(self, **context):
        return self.render(**context)

#工具方法
#将列表中的非字符串类型过滤掉
def _clean_list_filter(list_filter):
    if isinstance(list_filter, (list, tuple)):
        list_filter = set([field_name for field_name in list_filter
                           if isinstance(field_name, six.string_types)])
        if len(list_filter) == 0:
            list_filter = None
    else:
        list_filter = None
    return list_filter

#dash抽象类
class Dash(UIModule, UIView):
    "Base class for all reporting modules which may contain one or more Dashlets"
    __abstract__ = True

    enable_on_try_user=False
    renderer = None
    list_dashlet = []
    list_filter = None
    template = loader.get_template("dash/dash_page.html")
    module_template = loader.get_template("dash/includes/dash.html")

    def __init__(self,portal=None):
        super(Dash, self).__init__()
        #print 'init ',self.label,' dash...'
        self.portal=portal
        self._dashlets = []
        for dashlet_class in self.list_dashlet:
            if issubclass(dashlet_class, Dashlet):
                self._dashlets.append(dashlet_class())
        filters = {}
        for dashlet in self._dashlets:
            for field in dashlet.filters:
                if field.name in filters:
                    field_ = filters[field.name]
                    if str(field) != str(field_):
                        self.error("two different fields have the same name '%s'" % field.name)
                else:
                    filters[field.name] = field
        list_filter = _clean_list_filter(self.list_filter)

        if list_filter is None:
            self._filters = [FieldWrapper(field) for field in filters.values()]
        else:
            self._filters = []
            for field_name in list_filter:
                if field_name in filters:
                    self._filters.append(FieldWrapper(filters[field_name]))

        for field in self._filters:
            self.media += field.field.field.widget.media
        if len(self._filters) > 0:
            self.has_filter = True
        else:
            self.has_filter = False
        self._full_filters = copy.copy(self._filters)

    @overrides(UIView)
    def path(self):
        return "__dash__/%s" % self.uid

    def check_user_portal_permission(self, username) :
        from gflux.apps.station.sql_utils import get_user_account_type_by_name
        from gflux.apps.station.sql_utils import get_enable_advanced_features_by_name
        from gflux.apps.station.sql_utils import check_if_user_is_allowed_to_portal
        # 获取用户类型
        user_type=get_user_account_type_by_name(username)

        # 检查该用户类型是否允许访问该portal
        allowed=check_if_user_is_allowed_to_portal(self.portal, user_type)

        #get enable_advanced_features
        enable_advanced_features=get_enable_advanced_features_by_name(username)

        return (user_type, allowed,enable_advanced_features)

    def render_default(self):
        return _('<h1>你的注册申请尚未被批准或该用户不存在！</h1>')

    @overrides(UIView)
    def render(self, **context):
        # 检查用户是否有读取该portal的权限
        (user_type, allowed,enable_advanced_features)=self.check_user_portal_permission(context['request'].session['username'])

        if allowed==False:
            return self.render_default()

        context.update({'portal_allowed': allowed,
                        'account_type': user_type,
                        'enable_advanced_features':enable_advanced_features})

        #print 'render '+self.label+' dash...'
        context.update({
            'dash': self,
            'settings': settings,
            'params': context['request'].GET.items(),
        })

        #每次请求都需要动态更新过滤选项,每个请求的过滤选项是不同的
        #都需要将默认的选项拷贝出来，在渲染时传给目标
        #不可更改实例的属性，因为实例是所有用户共享的

        if 'request' in context:
            context['user'] = context['request'].session.get('username',None)
        else:
            context['user']=None

        self.update_filters_by_user_name(context['request'].session['username'],
            be_page_filter=True,context=context)

        context['standalone_html']=self.render_as_standalone(**context)
        return self.template.render(Context(context))

    #更新与用户相关的过滤选项
    def update_filters_by_user_name(self, username,context=None,
        be_module_filter=False,be_page_filter=False):
        from gflux.apps.station.sql_utils import get_user_stations_by_name
        from gflux.apps.station.sql_utils import get_user_fuel_type_by_name
        from gflux.apps.station.sql_utils import get_user_none_fuel_type_by_name
        from gflux.apps.station.sql_utils import get_system_fuel_type
        from gflux.apps.station.sql_utils import locate_china_location_id_from_request
        from gflux.apps.station.sql_utils import get_china_location_name_by_id,getUserLocationInfo
        if username==None:
            return

        #print 'update filter '+self.label+' dash...'

        _full_filters=copy.deepcopy(self._full_filters)
        _filters=copy.deepcopy(self._filters)

        #standalone render
        for field in _full_filters :
            if field.field.name == 'site' :
                field.field.field.choices=get_user_stations_by_name(username)
            elif field.field.name == 'fuel_type':
                field.field.field.choices=[(0,_(u'任意'))]+get_user_fuel_type_by_name(username)
            elif field.field.name=='none_fuel_type':
                field.field.field.choices=[(0,_(u'任意'))]+get_user_none_fuel_type_by_name(username)
            elif field.field.name=='system_fuel_type':
                field.field.field.choices=[(0,_(u'任意'))]+get_system_fuel_type()
            elif field.field.name=='china_location':
                request=context['request']
                ids=getUserLocationInfo(request)
                re_ids = []
                for id in ids:
                    re_ids.append((id,get_china_location_name_by_id(id)))
                field.field.field.choices=re_ids

        #none-standalone render
        for field in _filters :
            if field.field.name == 'site' :
                field.field.field.choices=get_user_stations_by_name(username)
            elif field.field.name == 'fuel_type':
                field.field.field.choices=[(0,_(u'任意'))]+get_user_fuel_type_by_name(username)
            elif field.field.name=='none_fuel_type':
                field.field.field.choices=[(0,_(u'任意'))]+get_user_none_fuel_type_by_name(username)
            elif field.field.name=='system_fuel_type':
                field.field.field.choices=[(0,_(u'任意'))]+get_system_fuel_type()
            elif field.field.name=='china_location':
                request=context['request']
                ids=getUserLocationInfo(request)
                re_ids = []
                for id in ids:
                    re_ids.append((id,get_china_location_name_by_id(id)))
                field.field.field.choices=re_ids

        #更新filter
        if be_module_filter:
            self._full_filters=_full_filters
            self._filters=_filters

        if be_page_filter:
            context['dash_full_filters']=_full_filters
            context['dash_filters']=_filters

    @overrides(UIModule)
    def render_as_module(self, **context):
        standalone=context.get('standalone',False)
        if standalone:
            #print 'render as standalone '+self.label+' dash...'
            pass
        else:
            #print 'render as module '+self.label+' dash...'

            #module模式下，当前实例是page深拷贝过之后的
            context['dash_filters']=self._filters

        context.update({
            'dash': self,
            'settings': settings,
        })
        return self.module_template.render(Context(context))

    def render_as_standalone(self, **context):
        context['standalone']=True
        return mark_safe(self.render_as_module(**context))

    @property
    def media_js(self):
        js = [
            'js/jquery.min.js',
            'js/jquery-migrate.js',
            'js/jquery.blockUI.js',
            'bootstrap/js/bootstrap.min.js',
            'js/utils.'+settings.STATIC_VERSION+'.js',
            'js/underscore.min.js',
            'js/core.js',
            'js/main_framework.'+settings.STATIC_VERSION+'.js',
            'js/jquery.cookie-1.4.1.min.js',
        ]
        media = Media(js=js)
        try:
            media += self.media['js']
        except:
            pass
        return media

    @property
    def media_css(self):
        css = {
            'all': ('bootstrap/css/bootstrap.css',
                    'css/core.css',
                    'css/main_framework.'+settings.STATIC_VERSION+'.css',)
        }
        media = Media(css=css)
        try:
            media += self.media['css']
        except:
            pass
        return media

    @property
    def filters(self):
        return self._filters

    @property
    def full_filters(self):
        return self._full_filters

    def remove_filters(self, filters_to_remove):
        if len(filters_to_remove) > 0:
            self._filters = filter(lambda x: x.field.name not in filters_to_remove, self._filters)

    @property
    def size(self):
        return len(self._dashlets)

    @property
    def description(self):
        return utils.get_dash_description(self.uid)

    def __iter__(self):
        return iter(self._dashlets)

    class Media:
        js = ['highcharts/js/highcharts.js', 'highcharts/js/highcharts-more.js', 'highcharts/js/modules/exporting.js','js/render.'+settings.STATIC_VERSION+'.js']

#抽象类，dashlet是dash的元素
class Dashlet(object):
    " Dashlet is a basic functional element of reporting. One Dash may contain one or more Dashlets"
    __metaclass__ = DashDefiningClass
    __abstract__ = True
    uid = None
    report_interface = None
    list_field = None
    list_filter = None
    render_as = 'chart'

    def __init__(self):
        super(Dashlet, self).__init__()
        #print 'init ',self.label,' dashlet...'
        self._report = None
        cls = self.__class__
        if cls.report_interface is not None and issubclass(cls.report_interface, reports.Report):
            self._report = cls.report_interface()
        if self._report is None:
            raise UIException("Dashlet.__init__ failed due to invalid 'report_interface'")
        list_filter = _clean_list_filter(self.list_filter)
        self._filters = []
        for field in self._report.Form():
            if list_filter is None or field.name in list_filter:
                self._filters.append(field)

    @property
    def report(self):
        return self._report

    @property
    def renderer(self):
        return self.render_as if isinstance(self.render_as, basestring) else 'chart'

    @property
    def filters(self):
        return self._filters

class Site(object):
    __metaclass__ = Singleton
    def __init__(self, title=None):
        self.title = title
        self._registry = {}
        self._portals = []
        self._urls = []
        self.default_portal = None

    def warn(self, msg):
        #print >> sys.stderr, "[WARNING] <%s> %s" % (self.__class__.__name__, msg)
        pass

    #将Portal类实例化，加入容器
    def register(self, portal_class):
        if not issubclass(portal_class, Portal):
            self.warn("the class to register is not a subclass of Portal")
            return None
        if portal_class.uid in self._registry:
            self.warn("ignore the portal class whose uid is '%s' and already registered"
                      % portal_class.uid)
            return None
        portal = portal_class()
        portal.site = self
        self._urls.append(portal.urlpattern)
        for page in portal:
            self._urls.append(page.urlpattern)
            for spec, row in page:
                for module in row:
                    if isinstance(module, Dash):
                        self._urls.append(module.urlpattern)
        self._registry[portal.uid] = portal
        self._portals.append(portal)
        if self.default_portal is None:
            self.default_portal = portal
        return portal

    @property
    def urls(self):
        return patterns('', *self._urls)

    def __iter__(self):
        return iter(self._portals)

    #自动发现服务，加载ui.py
    def autodiscover(self):
        import copy
        from django.utils.importlib import import_module
        from django.utils.module_loading import module_has_submodule
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            # Attempt to import the app's UI
            try:
                before_import_registry = copy.copy(self._registry)
                import_module('%s.ui' % app)
            except Exception, e:
                # Reset the model registry to the state before the last import as
                # this import will have to reoccur on the next request and this
                # could raise NotRegistered and AlreadyRegistered exceptions
                # (see #8245).
                self._registry = before_import_registry

                # Decide whether to bubble up this error. If the app just
                # doesn't have an admin module, we can ignore the error
                # attempting to import it, otherwise we want it to bubble up.
                if module_has_submodule(mod, 'ui'):
                    error_info = StringIO.StringIO()
                    traceback.print_exc(file=error_info)
                    message = '\n%s\n'%error_info.getvalue()
                    #print message
                    raise UIException("failed to import %s's UI: %s" % (app, str(e)))

site = Site(settings.SITE_NAME)
