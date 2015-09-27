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

from django.shortcuts import *
from django.http import *
import app_views
from app_views import *
from gflux import settings
from gflux.util import *
from gcustomer.status  import *
from gcustomer.utils import *
import base64
from decrypt_views import *
from django.core.context_processors import csrf
ajax_logger=logging.getLogger('ajax')


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

    #获取服务器版本
    def get_service_version(self,request,params):
        app_name = params['app_name']
        return app_views.get_app_version(request,app_name)

    #注册
    def register(self,request,params):
        name = params['name']
        password = params['password']
        career = params['career']
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
        try :
            password = md5_data(password)
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.MD5_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        return app_views.register(request,name,password,career)

    #登录
    def login(self,request,params):
        name = params['name']
        password = params['password']
        #获得加密字符串
        password = md5_data(password)
        return app_views.login(request,name,password)

    #激活帐号
    def activate_vcard(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        pay_password = params['pay_password']
        re_pay_password = params['re_pay_password']
        #md5加密
        try :
            pay_password = md5_data(pay_password)
            re_pay_password = md5_data(re_pay_password)
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.MD5_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        return app_views.activate_vcard(request,vcard_id,id_card,pay_password,re_pay_password)

    #匿名登录
    def anonymous_login(self,request,params):
        imei_code = params['imei_code']
        mac_address = params['mac_address']
        sim_number = params['sim_number']
        device_type = params['device_type']
        return app_views.anonymous_login(request,imei_code,mac_address,sim_number,device_type)

    #登出
    def logout(self,request,params):
        session_id = params['session_id']
        return app_views.logout(request,session_id)

    #获取附近油站sha1列表
    def get_near_by_station_sha1s(self,request,params):
        cardnum = params['cardnum']
        longitude = params['longitude']
        latitude = params['latitude']
        start = params['start']
        end = params['end']
        return app_views.get_near_by_station_sha1s(request,longitude,latitude,start,end,cardnum)

    #获取附近油站详情
    def get_near_by_station(self,request,params):
        cardnum = params['cardnum']
        sha1s = params['sha1s']
        longitude = params['longitude']
        latitude = params['latitude']
        return app_views.get_near_by_station(request,sha1s,longitude,latitude,cardnum)

    #获取商品sha1列表
    def get_goods_list_sha1s(self,request,params):
        longitude = params['longitude']
        latitude = params['latitude']
        cardnum = params['cardnum']
        start = params['start']
        end = params['end']
        return app_views.get_goods_list_sha1s(request,longitude,latitude,cardnum,start,end)

    #获取商品列表详情
    def get_goods_list(self,request,params):
        sha1s = params['sha1s']
        longitude = params['longitude']
        latitude = params['latitude']
        return app_views.get_goods_list(request,sha1s,longitude,latitude)

    #我收到的消息
    def my_received_messages(self,request,params):
        user_sha1 = params['user_sha1']
        start = params['start']
        end = params['end']
        return app_views.my_received_messages(request,user_sha1)

    #我发布的消息
    def my_released_messages(self,request,params):
        user_sha1 = params['user_sha1']
        start = params['start']
        end = params['end']
        return app_views.my_received_messages(request,user_sha1)

    #获取车后服务sha1列表
    def get_service_list_sha1s(self,request,params):
        longitude = params['longitude']
        latitude = params['latitude']
        start = params['start']
        end = params['end']
        return app_views.get_service_list_sha1s(request,longitude,latitude,start,end)

    #获取车后服务列表详情
    def get_service_list(self,request,params):
        sha1s = params['sha1s']
        longitude = params['longitude']
        latitude = params['latitude']
        return app_views.get_service_list(request,sha1s,longitude,latitude)

    #商品评论
    def comment_item(self,request,params):
        user_sha1 = params['user_sha1']
        item_sha1 = params['item_sha1']
        score = int(params['score'])
        return app_views.comment_item(request,user_sha1,item_sha1,score)

    #获取商家信息
    def get_merchants_info(self,request,params):
        sha1 = params['sha1']
        return app_views.get_merchants_info(request,sha1)

    #消息盒子
    def myMessagesBox(self,request,params):
        sha1 = params['user_sha1']
        messageType = params['Messagetype']
        start = params['start']
        end = params['end']
        return app_views.myMessagesBox(request,sha1,messageType,start,end)

    #用户行为
    def user_action(self,request,params):
        action_type = params['action_type']
        username = params['username']
        obj_type = params['obj_type']
        sha1 = params['sha1']
        promotion_id = params['promotion_id']
        return app_views.user_action(request,action_type,username,obj_type,sha1,promotion_id)

    #创建商品订单
    def create_order(self,request,params):
        vcard_id = params['vcard_id']
        good_sha1 = params['good_sha1']
        order_type = params['order_type']
        item_count = params['item_count']
        promotion_id = params['promotion_id']
        price = params['price']
        order_total = params['order_total']
        seller_sha1 = params['seller_sha1']
        status = params['status']
        return app_views.create_order(request,vcard_id,good_sha1,order_type,item_count,promotion_id,price,order_total,seller_sha1,status)

    #创建积分订单
    def create_score_order(self,request,params):
        vcard_id = params['vcard_id']
        good_sha1 = params['good_sha1']
        order_type = params['order_type']
        item_count = params['item_count']
        score = params["score"]
        return app_views.create_score_order(request,vcard_id,good_sha1,order_type,item_count,score)

    #生成充值订单
    def create_recharge_order(self,request,params):
        vcard_id = params['vcard_id']
        comp_id = params['comp_id']
        money = float(params['money'])
        return create_recharge_order(request,vcard_id,comp_id,money)

    #获取用户订单列表
    def get_order_list(self,request,params):
        vcard_id = params['vcard_id']
        start = params['start']
        end = params['end']
        status = int(params['status'])
        return app_views.get_order_list(request,vcard_id,start,end,status)

    #取消订单
    def delete_order(self,request,params):
        vcard_id = params["vcard_id"]
        order_sha1 = params['order_sha1']
        return app_views.delete_order(request,vcard_id,order_sha1)

    #获取用户订单数量
    def get_order_num(self,request,params):
        vcard_id = params['vcard_id']
        return app_views.get_order_num(request,vcard_id)

    #获取用户积分
    def get_user_score(self,request,params):
        vcard_id = params["vcard_id"]
        return app_views.get_user_score(request,vcard_id)

    #获取广告位信息
    def get_advertis(self,request,params):
        name = params["name"]
        return app_views.get_advertis(request,name)

    #获取广告详情
    def get_advertis_detail(self,request,params):
        adv_sha1 = params['sha1']
        return app_views.get_advertis_detail(request,adv_sha1)

    #点击广告
    def read_advertis(self,request,params):
        adv_sha1 = params['sha1']
        user_sha1 = params['user_sha1']
        return app_views.read_advertis(request,adv_sha1,user_sha1)

    #行车轨迹
    def trajectory(self,request,params):
        name = params['name']
        longitude = params['longitude']
        latitude = params['latitude']
        return app_views.trajectory(request,name,longitude,latitude)

    #新版驾车宝新增接口
    #上传用户头像
    def upload_avarta_image(self,request,params):
        name = params['name']
        avarta_image_data = params['avarta_image_data']
        return app_views.upload_avarta_image(request,name,avarta_image_data)

    #修改用户信息
    def modify_user_info(self,request,params):
        name = params['name']
        nick = params['nick']
        return app_views.modify_user_info(request,name,nick)

    #修改驾车宝用户登录密码
    def modify_login_password(self,request,params):
        name = params['name']
        old_pasword = params['old_pasword']
        new_password = params['new_password']
        re_new_password = params['re_new_password']
        #获取加密字符串
        old_pasword = md5_data(old_pasword)
        #md5加密
        try :
            new_password = md5_data(new_password)
            re_new_password = md5_data(re_new_password)
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.MD5_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        return app_views.modify_login_password(request,name,old_pasword,new_password,re_new_password)

    #获取石油公司信息
    def get_oil_company_info(self,request,params):
        name = params['name']
        return app_views.get_oil_company_info(request,name)

    #关联石油公司
    def associated_oil_company(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        comp_id = params['comp_id']
        return app_views.associated_oil_company(request,vcard_id,id_card,comp_id)

    #绑定加油卡
    def band_oil_card(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        comp_id = params['comp_id']
        card_num = params['card_num']
        card_type = params['card_type']
        return app_views.band_oil_card(request,vcard_id,id_card,comp_id,card_num,card_type)

    #解除绑定
    def delete_oil_card_bind(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        comp_id = params['comp_id']
        card_num = params['card_num']
        pay_password = params['pay_password']
        #获取加密字符串
        pay_password = md5_data(pay_password)
        return app_views.delete_oil_card_bind(request,vcard_id,id_card,comp_id,card_num,pay_password)

    #查看我的账户
    def get_pump_card(self,request,params):
        vcard_id = params['vcard_id']
        return app_views.get_pump_card(request,vcard_id)

    #获取我关联的石油公司的实体卡信息
    def get_my_oil_card(self,request,params):
        vcard_id = params['vcard_id']
        comp_id = params['comp_id']
        return app_views.get_my_oil_card(request,vcard_id,comp_id)

    #忘记支付密码
    def forget_pay_password(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        return app_views.forget_pay_password(request,vcard_id,id_card)

    #修改支付密码
    def modify_pay_password(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        old_pay_password = params['old_pay_password']
        new_pay_password = params['new_pay_password']
        re_new_pay_password = params['re_new_pay_password']
        try :
            new_pay_password = md5_data(new_pay_password)
            re_new_pay_password = md5_data(re_new_pay_password)
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.MD5_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        return app_views.modify_pay_password(request,vcard_id,id_card,old_pay_password,new_pay_password,re_new_pay_password)

    #检查支付密码
    def check_pay_password(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        pay_password = params['pay_password']
        #获取加密字符串
        pay_password = md5_data(pay_password)
        return app_views.check_pay_password(request,vcard_id,id_card,pay_password)

    #冲值加油虚拟卡
    def recharge(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        comp_id = params['comp_id']
        money = float(params['money'])
        return app_views.recharge(request,vcard_id,id_card,comp_id,money)

    #加油用户确认订单
    def confirm_order_by_user(self,request,params):
        vcard_id = params['vcard_id']
        order_sha1 = params['order_sha1']
        return app_views.confirm_order_by_user(request,vcard_id,order_sha1)

    #获取可加油支付的账户
    def get_pay_account(self,request,params):
        vcard_id = params['vcard_id']
        id_card = params['id_card']
        order_sha1 = params['order_sha1']
        return app_views.get_pay_account(request,vcard_id,id_card,order_sha1)

    #加油虚拟卡支付
    def pay_by_oil_card(self,request,params):
        vcard_id = params['vcard_id']
        order_sha1 = params['order_sha1']
        id_card = params['id_card']
        comp_id = params['comp_id']
        pay_password = params['pay_password']
        #获取加密字符串
        pay_password = md5_data(pay_password)
        pay = float(params['pay'])
        return  app_views.pay_by_oil_card(request,vcard_id,order_sha1,id_card,comp_id,pay_password,pay)

    #加油用户支付完成
    def purchase_complete_by_user(self,request,params):
        order_sha1 = params['order_sha1']
        vcard_id = params['vcard_id']
        return app_views.purchase_complete_by_user(request,order_sha1,vcard_id)

    #加油用户支付完成
    def purchase_complete_by_the_third(self,request,params):
        order_sha1 = params['order_sha1']
        vcard_id = params['vcard_id']
        return app_views.purchase_complete_by_the_third(request,order_sha1,vcard_id)

    #获取附近信息
    def get_near_by_infos(self,request,params):
        longitude = params['longitude']
        latitude = params['latitude']
        info_flag = params['info_flag']
        return app_views.get_near_by_infos(request,longitude,latitude,info_flag)

    #获取热销商品
    def get_hot_goods(self,request,params):
        longitude = params['longitude']
        latitude = params['latitude']
        flag = params['flag']
        username = params['username']
        return app_views.get_hot_goods(request,username,longitude,latitude,flag)

    #获取道路救援
    def get_help(self,request,params):
        return app_views.get_help(request)

    #获取我的专享
    def get_my_sales_summary(self,request,params):
        vcard_id = params['vcard_id']
        flag = params["flag"]
        start = params['start']
        end = params['end']
        return app_views.get_my_sales_summary(request,vcard_id,flag,start,end)

    #获取我的信息
    def get_user_info(self,request,params):
        name = params['name']
        password = params['password']
        #获取加密字符串
        password = md5_data(password)
        return app_views.get_user_info(request,name,password)

    #查看预订是否可以购买
    def check_reservation_by_user(self,request,params):
        order_sha1 = params['order_sha1']
        return app_views.check_reservation_by_user(request,order_sha1)

    #获取积分兑换商品概要信息
    def get_score_list(self,request,params):
        vcard_id = params['vcard_id']
        start = params['start']
        end = params['end']
        return app_views.get_score_list(request,vcard_id,start,end)

    #获取积分商品详情
    def get_score_good_detials(self,request,params):
        sha1 = params['sha1']
        return app_views.get_score_good_detials(request,sha1)

    #积分支付
    def purchase_score_item(self,request,params):
        vcard_id = params['vcard_id']
        pay_password = params['pay_password']
        #获取加密字符串
        pay_password = md5_data(pay_password)
        order_sha1 = params['order_sha1']
        return app_views.purchase_score_item(request,vcard_id,pay_password,order_sha1)

    #申请退款
    def apply_refund(self,request,params):
        order_sha1 = params['order_sha1']
        vcard_id = params['vcard_id']
        pay_password = params['pay_password']
        #获取加密字符串
        pay_password = md5_data(pay_password)
        return app_views.apply_refund(request,order_sha1,vcard_id,pay_password)

    #存储out_trade_no 与订单的关联
    def download_trade_no_with_order(self,request,params):
        order_sha1 = params['order_sha1']
        vcard_id = params['vcard_id']
        out_trade_no = params['out_trade_no']
        return app_views.download_trade_no_with_order(request,order_sha1,vcard_id,out_trade_no)

    #微信支付 生成移动端发起支付的订单参数
    def query_weixin_order_params(self,request,params):
        order_sha1 = params['order_sha1']
        return app_views.query_weixin_order_params(request,order_sha1)

    #忘记登录密码
    def forget_login_password(self,request,params):
        name = params['name']
        new_password = params['new_password']
        re_new_password = params['re_new_password']
        #获取md5加密字符串
        new_password = md5_data(new_password)
        re_new_password = md5_data(re_new_password)
        return app_views.forget_login_password(request,name,new_password,re_new_password)

    #意见反馈
    def app_user_feedback(self,request,params):
        vcard_id = params['vcard_id']
        content = params['content']
        return app_views.app_user_feedback(request,vcard_id,content)

# 初始化一个 API_ROUTER的对象
api_router = API_ROUTER()

# api view 的路由参数
def jiachebao_api_router(request) :
    try:
        #在调试模式下记录app输入输出日志
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
    #app_output_log_record(response)
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
            "register",
            "logout",
            "render_image",
            "get_near_by_infos",
            "get_hot_goods",
            "get_advertis",
            "purchase_complete_by_the_third",
        ]
    for keyword in keywords :
        if action.find(keyword) != -1 :
            return Status.LOGINSUCCESS
        else:
            continue
    username = request.session.get('username',None)
    ret=checkUserOnlineStatus(request)
    if ret!=Status.LOGINSUCCESS:
        return ret
    else :
        return Status.LOGINSUCCESS
