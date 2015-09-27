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
import base64

ajax_logger=logging.getLogger('ajax')

from django.shortcuts import *
from django.http import *
import app_views
from app_views import *
from gflux import settings
from gcustomer.status  import *
from gcustomer.utils import *
from django.core.context_processors import csrf

# 定义api view的路由类
class API_ROUTER:
    def __init__(self):
        self.a = 'a'

    def get_token(self,request,params):
        result={}
        result['ret'] = Status.OK
        result['info'] = Status().getReason(result['ret'])
        try:
            dic=csrf(request)
            result['data']={}
            result['data']['csrf_token'] =dic['csrf_token'].title()
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.CSRF_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        return result

    #油站工作人员注册
    def worker_register(self,request,params):
        name = params['name']
        password = params['password']
        result = {}
        #验证用户名和密码长度
        if len(name) < 6 or  len(name) > 16 : 
            result['ret'] = Status.USERNAME_PASSWORD_ERROR
            result['info'] = _(u"请输入6-16位用户名！")
            return result
        elif len(password) < 6 or len(password) > 16 : 
            result['ret'] = Status.USERNAME_PASSWORD_ERROR
            result['info'] = _(u"请输入6-16位密码！")
            return result
        else : 
            pass 
        #md5加密
        password = md5_data(password)
        comp_id = params['comp_id']
        site_sha1 = params['site_sha1']
        user_type = params['user_type']
        return app_views.register(request,name,password,comp_id,site_sha1,user_type)

    #油站工作人员登录
    def worker_login(self,request,params):
        username = params['username']
        password = params['password']
        #获取md5字符串
        password = md5_data(password)
        return app_views.login(request,username,password)

    def worker_logout(self,request,params):
        session_id = params['session_id']
        return app_views.logout(request,session_id)

    # 油站人员扫码之后，确认订单的状态
    def confirm_order(self,request,params):
        worker_sha1 = params['worker_sha1']
        order_sha1 = params['order_sha1']
        return app_views.confirm_order(request,worker_sha1,order_sha1)

    # 油站人员确认订单的状态之后，点击完成交易
    def purchase_complete(self,request,params):
        order_id = params['order_id']
        seller_sha1 = params['seller_sha1']
        return app_views.purchase_complete(request,order_id,seller_sha1)

    #获取油站的交易流水线
    def get_site_trades(self,request,params):
        site_sha1 = params['station_sha1']
        start = params['start']
        end = params['end']
        status = params['status']
        return app_views.get_site_trades(request,site_sha1,start,end,status)

    #获取油站的交易流水详情
    def get_site_trade_details(self,request,params):
        order_id = params['order_id']
        return app_views.get_site_trade_details(request,order_id)

    #获取某个加油员的订单列表
    def get_trades_by_worker(self,request,params):
        jiayouyuan_sha1 = params['user_sha1']
        start = params['start']
        end = params['end']
        return app_views.get_trades_by_worker(request,jiayouyuan_sha1,start,end)

    #订单完成
    def confirm_recorded(self,request,params):
        worker_sha1 = params['worker_sha1']
        order_id = params['order_id']
        return app_views.confirm_recorded(request,worker_sha1,order_id)

    #新增功能
    #收银员注册选择公司和油站信息
    def worker_register_init_info(self,request,params):
        return app_views.worker_register_init_info(request)

    #收银员获取生成订单初始化信息
    def get_oil_order_init_info(self,request,params):
        station_sha1 = params['station_sha1']
        return app_views.get_oil_order_init_info(request,station_sha1)

    #收银员生成订单
    def create_order_by_worker(self,request,params):
        worker_sha1 = params['worker_sha1']
        item_sha1 = params['item_sha1']
        order_type = params['order_type']
        price = params['price']
        pay = params['pay']
        pump_id = params['pump_id']
        return app_views.create_order_by_worker(request,worker_sha1,item_sha1,order_type,price,pay,pump_id)

    def confirm_order_by_worker(self,request,params):
        order_sha1 = params['order_sha1']
        return app_views.confirm_order_by_worker(request,order_sha1)

    #收银员取消订单
    def delete_order_by_work(self,request,params):
        order_sha1 = params['order_id']
        return app_views.delete_order_by_work(request,order_sha1)

    #确认商品已交易,打印小票
    def purchase_complete_worker(self,request,params):
        order_sha1 = params['order_sha1']
        return app_views.purchase_complete_worker(request,order_sha1)

    #检查商品是否已支付ji
    def check_has_purchase_worker(self,request,params):
        order_sha1 = params['order_sha1']
        return app_views.check_has_purchase_worker(request,order_sha1)

    #确认预订商品是否可以支付购买
    def confirm_reservation_by_worker(self,request,params):
        order_sha1  = params['order_sha1']
        status = params['status']
        return app_views.confirm_reservation_by_worker(request,order_sha1,status)



# 初始化一个 USER_ROUTER的对象
api_router = API_ROUTER()

# api view 的路由参数
def jiayouyuan_api_router(request):
    try:
        #在调试模式下记录app输入输出\日志
        app_input_log_record(request)
        rsdic = {}
        action,data = checkRequestMethod(request)
        try :
            #ios解密
            if  request.META.has_key("HTTP_USER_AGENT")  and  request.META['HTTP_USER_AGENT'].find("iOS")  != -1 :
                action,data  = decrypt_data_for_ios(request,action,data)
            else :
                action,data = decrypt_data_for_andriod(request,action,data)
        except Exception,e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.DECRYPTION_DATA_ERROR
            rsdic['info'] = Status().getReason(rsdic['ret'])
            return HttpResponse(json.dumps(rsdic),mimetype="application/json")
        #用户在线状态检查
        if action != 'get_token':
            ret = check_user_status_by_views(request,action)
            if ret != Status.LOGINSUCCESS :
                rsdic['ret'] = Status.NOTLOGGEDIN
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic),mimetype="application/json")
            else :
                data = getattr(api_router,"%s"%action,"default")(request,data)
                rsdic.update(data)
        else:
            data = getattr(api_router,"%s"%action,"default")(request,data)
            rsdic.update(data)
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")
    response = HttpResponse(json.dumps(rsdic),mimetype="application/json")
    #调试模式下记录输出日志
    app_output_log_record(response)
    return response

# 检查请求方法取得参数信息
def checkRequestMethod(request):
    #检查请求的方法类型
    if request.method == 'GET':
        action = request.GET['action']
        if action == 'get_token':
            params = {}
            return action,params
        params = request.GET['data']
        params = params.replace("\n","")
        params=json.loads(params)
        params = simulate_app_encryption(request,action,params)
    elif request.method == 'POST':
        action = request.POST['action']
        params = request.POST['data']
        params = params.replace("\n","")
        params=json.loads(params)
    return action,params

#对指定函数进行用户在线状态检查
def check_user_status_by_views(request,action):
    keywords = [
            "login",
            "logout",
            "register",
            "render_image",
        ]
    for keyword in keywords :
        if action.find(keyword) != -1 :
            return Status.LOGINSUCCESS
        else:
            continue
    ret=checkUserOnlineStatus(request)
    if ret!=Status.LOGINSUCCESS:
        return ret
    else :
        return Status.LOGINSUCCESS


#解密andriod
def decrypt_data_for_andriod(request,action,data):
    rsa_key = request.META['rsa_key_android']
    if action == "worker_login" :
            password = base64.b64decode(data['password'])
            password = rsa_key.decrypt(password)
            data['password'] = password
            return  action,data

    elif action == "worker_register" :
            password = base64.b64decode(data['password'])
            password = rsa_key.decrypt(password)
            data['password'] = password
            return action,data

    elif action == "create_order_by_worker" :

            item_sha1 = base64.b64decode(data['item_sha1'])
            price = base64.b64decode(data['price'])
            pay = base64.b64decode(data['pay'])

            item_sha1 = rsa_key.decrypt(item_sha1)
            price = float(rsa_key.decrypt(price))
            pay = float(rsa_key.decrypt(pay))

            data['item_sha1'] = item_sha1
            data['price'] = price
            data['pay'] = pay

            return action,data

    else :
            return action,data

#解密 ios
def decrypt_data_for_ios(request,action,data):
    rsa_key = request.META['rsa_key_ios']
    if action == "worker_login" :
            password = base64.b64decode(data['password'])
            password = rsa_key.private_decrypt(password,1)
            data['password'] = password
            return  action,data
    elif action == "worker_register" :
            password = base64.b64decode(data['password'])
            password = rsa_key.private_decrypt(password,1)
            data['password'] = password
            return action,data
    elif action == "create_order_by_worker" :

            item_sha1 = base64.b64decode(data['item_sha1'])
            price = base64.b64decode(data['price'])
            pay = base64.b64decode(data['pay'])

            item_sha1 = rsa_key.private_decrypt(item_sha1,1)
            price = rsa_key.private_decrypt(price,1)
            pay = rsa_key.private_decrypt(pay,1)

            data['item_sha1'] = item_sha1
            data['price'] = price
            data['pay'] = pay

            return action,data

    else :
            return action,data

#模拟移动端加密
def simulate_app_encryption(request,action,data):
    rsa_key = request.META['rsa_key']
    if action == "worker_login" :

            password = rsa_key.encrypt(str(data['password']),request.META['rsa_public_key'])[0]

            password = base64.b64encode(password)

            data['password'] = password

            return  data

    elif action == "worker_register" :

            password = rsa_key.encrypt(str(data['password']),request.META['rsa_public_key'])[0]

            password = base64.b64encode(password)

            data['password'] = password

            return data

    elif action == "create_order_by_worker" :

            item_sha1 = rsa_key.encrypt(str(data['item_sha1']),request.META['rsa_public_key'])[0]
            price = rsa_key.encrypt(str(data['price']),request.META['rsa_public_key'])[0]
            pay = rsa_key.encrypt(str(data['pay']),request.META['rsa_public_key'])[0]

            item_sha1 = base64.b64encode(item_sha1)
            price = base64.b64encode(price)
            pay = base64.b64encode(pay)

            data['item_sha1'] = item_sha1
            data['price'] = price
            data['pay'] = pay

            return data

    else :
            return data
