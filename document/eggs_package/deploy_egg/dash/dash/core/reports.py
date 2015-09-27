# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

import sys
import json,pdb
from abc import ABCMeta, abstractmethod
from django.http import HttpResponse, HttpResponseNotAllowed
from django.conf.urls import patterns, url
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from dash.core.types import Singleton, DashDefiningClass
from . import forms

class ReportException(Exception):
    "Report Exception"

class Reportor(object):
    __metaclass__ = Singleton

    def __init__(self):
        self._registry = {}
        self._urls = []

    def register(self, report):
        #report必须为Report类型
        if not isinstance(report, Report):
            #print >> sys.stderr, "[WARNING] the report to register is not a instance of Report"
            return None

        #report不允许重复注册
        if report.uid in self._registry:
            #print >> sys.stderr, "[WARNING] ignore the report whose uid is '%s' and already registered" % report.uid
            return None

        #注册report，注册report的url参数
        self._registry[report.uid] = report
        self._urls.append(report.urlpattern)
        return report

    #声明urls为只读属性×啊
    @property
    def urls(self):
        #*self._urls将列表解包挨个传入方法中
        return patterns('', *self._urls)

    #自动发现服务
    #根据django提供的app列表，依次搜索app目录下是否有reports模型
    #有则将其import
    def autodiscover(self):
        import copy
        from django.utils.importlib import import_module
        from django.utils.module_loading import module_has_submodule

        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            # Attempt to import the app's reports module.
            try:
                before_import_registry = copy.copy(self._registry)
                import_module('%s.reports' % app)
            except Exception, e:
                # Reset the model registry to the state before the last import as
                # this import will have to reoccur on the next request and this
                # could raise NotRegistered and AlreadyRegistered exceptions
                # (see #8245).
                self._registry = before_import_registry

                # Decide whether to bubble up this error. If the app just
                # doesn't have an admin module, we can ignore the error
                # attempting to import it, otherwise we want it to bubble up.
                if module_has_submodule(mod, 'reports'):
                    raise ReportException("failed to import %s's report: %s" % (app, str(e)))

#全局变量reportor
reportor = Reportor()

#report定义的抽象基类
class ReportDefiningClass(forms.DeclarativeFormDefiningClass, DashDefiningClass, ABCMeta, Singleton):
    def __new__(cls, name, bases, attrs):
        new_class = super(ReportDefiningClass, cls).__new__(cls, name, bases, attrs)
        #如果子类非抽象，自动向reportor容器注册
        if not new_class.__abstract__:
            reportor.register(new_class())

        #为子类添加类属性
        new_class.allowed_methods = [m.upper() for m in new_class.http_method_names if hasattr(new_class, m)]
        return new_class

#report抽象类定义
#object表明其为新式类，类和类型是统一的，即Report.__class__==type(Report)
class Report(object):
    __metaclass__ = ReportDefiningClass
    __abstract__ = True

    uid = None
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']

    #子类类属性__abstract__必须为False
    def __new__(cls, *args, **kwargs):
        if cls.__abstract__:
            raise ReportException("Abstract Report class '%s' cannot be instantiated."
                                  % cls.__name__)
        return super(Report, cls).__new__(cls, *args, **kwargs)

    #抽象方法，子类必须实现
    #当前类会进行一系列的检查，和数据校验，通过调用此方法，具体逻辑由子类实现
    @abstractmethod
    def report(self, request, *args, **kwargs):
        pass

    #闭包用法
    #惰性计算view结果
    def as_view(self):
        """
        Main entry point for a request-response process.
        """
        def view(request, *args, **kwargs):
            if request.method.upper() not in self.allowed_methods:
                return HttpResponseNotAllowed(self.allowed_methods)
            return self.get(request, *args, **kwargs)
        return view

    def path(self):
        return '__report__/%s' % self.uid

    #只读属性
    @property
    def urlpattern(self):
        return url(r'^%s%s$' % (settings.GFLUX_URL_PREFIX, self.path()), self.as_view(), name=self.path())

    #只读属性
    @property
    def url(self):
        return '/' + settings.GFLUX_URL_PREFIX + self.path()

    def format_data(self, data):
        return json.dumps(data)

    #更新公共过滤选项中与用户相关的部分
    #做表单验证时需要
    def update_form_filters_by_user_name(self, username,form,request):
        if username==None:
            return

        #print 'update form filter '+self.uid+' report...'
        for fieldname in form.fields.iterkeys():
            field=form.fields[fieldname]
            if fieldname=='site':
                from gflux.apps.station.sql_utils import get_user_stations_by_name
                field.choices=get_user_stations_by_name(username)

            elif fieldname=='fuel_type':
                from gflux.apps.station.sql_utils import get_user_fuel_type_by_name
                field.choices=[(0,_(u'任意'))]+get_user_fuel_type_by_name(username)

            elif fieldname=='none_fuel_type':
                from gflux.apps.station.sql_utils import get_user_none_fuel_type_by_name
                field.choices=[(0,_(u'任意'))]+get_user_none_fuel_type_by_name(username)

            elif fieldname=='system_fuel_type':
                from gflux.apps.station.sql_utils import get_system_fuel_type
                field.choices=[(0,_(u'任意'))]+get_system_fuel_type()

            elif fieldname=='china_location':
                from gflux.apps.station.sql_utils import \
                locate_china_location_id_from_request,get_china_location_name_by_id
                id=locate_china_location_id_from_request(request)
                field.choices=[(id,get_china_location_name_by_id(id))]

    #request 处理方法，数据验证和结果包装
    def handle(self, request, *args, **kwargs):
        #
        #实例化django内置Form对象
        form = self.Form(request.REQUEST)

        #当前用户
        user = request.session.get('username',None)

        #未登陆
        if user is None:
            return {'status':'NOT LOGIN'}

        #更新filter值
        self.update_form_filters_by_user_name(user,form,request)

        form.full_clean()

        #验证表单
        if form.is_valid():
            # # FIXME: it's brutal to update kwargs with cleaned form data directly.
            # kwargs.update(self.form.cleaned_data)
            kwargs['form']=form
            result = self.report(request, *args, **kwargs)
            if result:
                result['status'] = 'OK'
                return result
            else:
                return {'status': 'ERROR'}
        else:
            return {'status': 'INVALID_FORM'}

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.format_data(self.handle(request, *args, **kwargs)))

    def error(self, msg):
        raise ReportException("<%s> %s" % (self.__class__.__name__, msg))
