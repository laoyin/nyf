# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb,json,datetime,logging
from django.http import *
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.core.management import call_command
from django.core.cache import cache
from django.utils import timezone
from gcustomer.models import *
from gflux.util import *

ajax_logger=logging.getLogger('ajax')

from django.shortcuts import *
from django.http import *
import app_views
from app_views import *
from gflux import settings



# 定义api view的路由类
class API_ROUTER:
    def __init__(self):
        self.a = 'a'

    def get_token(self,request,params):
        data = {}
        try:
            csrf_token = request.COOKIES['csrftoken']
            data['ret'] = '0001'
        except:
            data['ret'] = '1001'
        return data

    def login(self,request,params):
        username = params['username']
        password = params['password']
        return app_views.login(request,username,password)

    def register(self,request,params):
        name = params['name']
        password = params['password']
        nick = params['nick']
        career = params['career']
        avarta_sha1 = params['avarta_sha1']
        return app_views.register(request,name,password,nick,career,avarta_sha1)

    def anonymous_login(self,request,params):
        imei_code = params['imei_code']
        mac_address = params['mac_address']
        sim_number = params['sim_number']
        device_type = params['device_type']
        return app_views.anonymous_login(request,imei_code,mac_address,sim_number,device_type)

    def logout(self,request,params):
        session_id = params['session_id']
        return app_views.logout(request,session_id)


# 初始化一个 USER_ROUTER的对象
api_router = API_ROUTER()


# api view 的路由参数
def shout_api_router(request):
    
    try:
        rsdic = {}
        action,data = checkRequestMethod(request)
        data = getattr(api_router,"%s"%action,"default")(request,data)
        rsdic.update(data)
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

# 检查请求方法取得参数信息
def checkRequestMethod(request):
    #检查请求的方法类型
    if request.method == 'GET':
       action = request.GET['action']
       params = request.GET['data']
    elif request.method == 'POST':
       action = request.POST['action']
       params = request.POST['data']
    params=json.loads(params)
    return action,params




