#coding=utf-8
from django.shortcuts import render_to_response,render
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.http import *
import pdb
from django.template import Context
from gflux.util import *

version = settings.STATIC_VERSION
url_prefix = settings.GFLUX_URL_PREFIX

def register_views(request):
    context = Context({'version':version,'url_prefix':url_prefix})
    return render_to_response("register.html",context)

def register_success_views(request):
    context = Context({'version':version})
    return render_to_response("register_success.html",context)

def login_views(request):
    context = Context({'version':version})
    return render(request,"login.html",context)

#用户打开链接默认显示地址
def gflux_views(request):
    #检查是否登陆
    ret=checkUserOnlineStatus(request)

    #如果没有登陆,跳转到gflux界面,否则跳转到欢迎界面
    if ret!=Status.LOGINSUCCESS:
        return render(request,"gflux.html")
    return HttpResponseRedirect("/%ssetting_protal/welcome.html"%settings.GFLUX_URL_PREFIX)

#演示页面
def demo_view(request):
    context = Context({'version':version})
    return render(request,"demo.html",context)

def test_view(request):
    context = Context({'version':version})
    return render(request,"test1.html",context)