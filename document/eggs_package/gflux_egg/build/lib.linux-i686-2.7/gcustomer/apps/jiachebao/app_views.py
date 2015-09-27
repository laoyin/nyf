# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb,json,datetime,logging,hashlib,time
from django.http import *
from django.conf import settings
from django.shortcuts import render_to_response
from django.db.models import Q
from gcustomer.apps.jiachebao.models import *
from gcustomer.models import *
from gcustomer.apps.jiachebao.app_data import *
from django.conf import settings
from gcustomer.utils import *
from gcustomer.status  import *
from sqlalchemy.sql import or_,func
from django.utils.translation import ugettext as _
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
NEAR_DISTANCE = 20 #km

ajax_logger=logging.getLogger('ajax')

#app 版本号
class Version:
    version = {
        "jiachebao" : settings.JCHEBAO_APP_VERSION,
        "jiayouyuan" : settings.JYOUYUAN_APP_VERSION
    }

#获取版本号
def get_app_version(request,app_name=None):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    if app_name == None :
        app_version = Version.version['jiachebao']
    else :
        try :
            result['data']['version'] = Version.version[app_name]
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.UNKNOWNERR
            result['info'] = "版本请求参数出错"
            result['data'] = {}
    return result

#注册
def register(request,name,password,career):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    try :
          session = request.get_session()
          #验证用户唯一性
          session.query(CustomerAccount).filter_by(name = name).one()
          result['ret'] = Status.USEREXIST
          result['info'] = Status().getReason(result['ret'])
          return result
    except :
          user = CustomerAccount(
            cardnum = name,
            name = name ,
            password = password,
            career = career
          )
    try:
          session.add(user)
          session.commit()
    except Exception,e:
          ajax_logger.error(str(e))
          result['ret'] = Status.REGISTER_ERROR
          result['info'] = Status().getReason(result['ret'])
          return result
    return result

#登录
def login(request,name,password):
    result={}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    try:
      session = request.get_session()
      user=session.query(CustomerAccount).filter_by(name=name).one()
      if not user.password == password :
          result['ret']  = Status.PASSWORDERROR
          result['info'] = Status().getReason(result['ret'])
          return result
      # 更新request session参数
      request.session.set_expiry(0)
      request.session['username'] = name
      sid=request.session.session_key
      cache.set('%s_sessionid'%name,sid)
      if sid is None:
          request.session.save()
          sid=request.session.session_key
      dic = {}
      dic['vcard_id'] = user.name
      dic['session_id'] = sid
      dic['avarta_sha1'] = user.avarta_sha1
      dic['nick'] = user.nick or ""
      dic['score'] = user.score
      dic['career'] = user.career
      dic['id_card'] = user.id_card
      dic['is_pay_in_advance'] = user.is_pay_in_advance
      dic['time'] = str(user.time).split(" ")[0]

      result['data'] = dic
      result['ret'] = Status.LOGINSUCCESS
      result['info'] = Status().getReason(result['ret'])
    except Exception,e:
      ajax_logger.error(BASE_DIR+":"+str(e))
      result['ret'] = Status.USERNOTEXIST
      result['info'] = Status().getReason(result['ret'])
    return result

#忘记登录密码
def forget_login_password(request,name,new_password,re_new_password):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    #用户验证
    try :
        user = session.query(CustomerAccount).filter_by(name = name).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证两次输入的密码
    if not new_password == re_new_password :
        result['ret'] = Status.PASSWORDINCONSISTENT
        result['info'] = Status().getReason(result['ret'])
        return result
    #修改密码
    user.password = new_password
    try :
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.ALTER_LODIN_PASSWORD_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result
        


#激活帐号
def activate_vcard(request,vcard_id,id_card,pay_password,re_pay_password):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    try :
          session = request.get_session()
          #用户验证
          try :
              user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
          except Exception,e:
              ajax_logger.error(str(e))
              result['ret'] = Status.USERNOTEXIST
              result['info'] = Status().getReason(result['ret'])
              return result
          #用户身份证验证
          if not check_card_id(id_card[0:17],id_card[17]) :
                result['ret'] = Status.ID_CARD_FORMAT_ERROR
                result['info'] = Status().getReason(result['ret'])
                return result
          user_info = get_age_sex_by_card_id(id_card)
          #验证两次密码输入是否一致
          if not pay_password == re_pay_password :
                result['ret'] = Status.PASSWORDINCONSISTENT
                result['info'] = Status().getReason(result['ret'])
                return result
          user.pay_password = pay_password
          user.id_card = id_card
          user.age = user_info['age']
          user.gender = user_info['sex']
          account = CustomerCompInfo(
                vcard_id = vcard_id,
                comp_id = 0,
                balance = 0,
                total_charge_num = 0
              )
          user_profile = CustomerProfile(
                vcard_id = vcard_id
            )
          session.add(user_profile)
          session.add(account)
          try :
              session.commit()
          except Exception,e:
              ajax_logger.error(str(e))
              result['ret'] = Status.HAS_ACTIVITY_VCARD_ERROR
              result['info'] = Status().getReason(result['ret'])
              return result
    except Exception,e:
          ajax_logger.error(str(e))
          result['ret'] = Status.ACTIVITY_VCARD_ERROR
          result['info'] = Status().getReason(result['ret'])
          return  result
    return result

#匿名登录
def anonymous_login(request,imei_code,mac_address,sim_number,device_type):
    result = {}
    result['data'] = {}
    try :
        anonymous = WheelDevice.objects.filter(imei_code=imei_code).get()
        result['ret'] = Status.OK
        result['info'] = Status().getReason(result['ret'])
        result['data']['sessionid'] = request.session.session_key
    except :
        anonymous_user=WheelDevice(
        		imei_code=imei_code,
        		mac_address=mac_address,
        		sim_number=sim_number,
        		device_type=device_type
        	)
    try:
        anonymous_user.save()
        result['ret'] = Status.OK
        result['info'] = Status().getReason(result['ret'])
        result['data']['sessionid'] = request.session.session_key
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
        result['data']['sessionid'] = request.session.session_key
    return result

#登出
def logout(request,session_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    username=request.session.get('username',None)
    if username!=None:
        cache.delete('%s_sessionid'%username)
    #delete session
    for s in request.session.keys():
        del request.session[s]
    result["data"] = {}
    return result

#获取附近油站sha1列表
def get_near_by_station_sha1s(request,longitude,latitude,start,end,cardnum):
    result = {}
    result['data']={}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = get_near_by_station_sha1s_data(request,longitude=longitude,latitude=latitude,start=start,end=end,cardnum=cardnum)
    return result

#获取附近油站详情
def get_near_by_station(request,sha1s,longitude,latitude,cardnum):
    result = {}
    result['data'] = {}
    result['info'] = 'OK'
    result['ret'] = Status.OK
    result['data'] = get_near_by_station_data(request,sha1s=sha1s,longitude=longitude,latitude=latitude,cardnum=cardnum)
    if not result['data'] :
      result['ret'] = Status.NODATA
      result['info'] = Status().getReason(result['ret'])
    return result

#获取商品sha1列表
def get_goods_list_sha1s(request,longitude,latitude,cardnum,start,end):
    result = {}
    result['info'] = 'OK'
    result['ret'] = Status.OK
    result['data'] = get_goods_list_sha1s_data(request,longitude=longitude,latitude=latitude,cardnum=cardnum,start=start,end=end)
    return result

#获取商品列表详情
def get_goods_list(request,sha1s,longitude,latitude):
    result = {}
    result['info'] = 'OK'
    result['ret'] = Status.OK
    result['data'] = get_goods_list_data(request,sha1s=sha1s,longitude=longitude,latitude=latitude)
    if not result['data'] :
      result['ret'] = Status.NODATA
      result['info'] = Status().getReason(result['ret'])
    return result

#我收到的消息
def my_received_messages(request,user_sha1,start,end):
    result = {}
    result['has_next'] = 'false'
    result['info'] = 'OK'
    result['ret'] = Status.OK
    result['data'] = {}
    return result

#我发布的消息
def my_released_messages(request,user_sha1,start,end):
    result = {}
    result['has_next'] = 'true'
    result['info'] = 'OK'
    result['ret'] = Status.OK
    result['data'] = {}
    return result

#获取车后服务sha1列表
def get_service_list_sha1s(request,longitude,latitude,start,end):
    result = {}
    result['info'] = 'OK'
    result['ret'] = Status.OK
    result['data']= get_service_list_sha1s_data(request,longitude=longitude,latitude=latitude,start=start,end=end)
    return result

#获取车后服务列表详情
def get_service_list(request,sha1s,longitude,latitude):
    result = {}
    result['info'] = 'OK'
    result['ret'] = Status.OK
    result['data'] = get_service_list_data(request,sha1s = sha1s,longitude=longitude,latitude=latitude)
    if not result['data'] :
      result['ret'] = Status.NODATA
      result['info'] = Status().getReason(result['ret'])
    return result

#商品评论
def comment_item(request,user_sha1,item_sha1,score):
    result = {}
    result['info'] = 'OK'
    result['ret'] = Status.OK
    result['data'] = {}
    message = comment_item_data(request,user_sha1 = user_sha1,item_sha1 = item_sha1,score = score)
    if message == 1 :
      result['ret'] = Status.WITHOUTPERMISSION
      result['info'] = Status().getReason(result['ret'])
      return result
    elif message == 2 :
      result['ret'] = Status.HAVECOMMENTS
      result['info'] = Status().getReason(result['ret'])
      return result
    else :
      return result

#获取商家信息
def get_merchants_info(request,sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = get_merchants_info_data(request,result,sha1=sha1)
    check_data(result)
    return result

#检查是否有下一个
def check_has_next(result,start,end):
    if not result['data'] :
      result['ret'] = Status.USERNOTEXIST
      result['info'] = Status().getReason(result['ret'])
      result['data']['has_next'] = 'false'
    elif not len(result['data']['sha1s']) == end-start+1 :
      result['ret'] = Status.NOMOREDATA
      result['info'] = Status().getReason(result['ret'])
      result['data']['has_next'] = 'false'

#检查数据
def check_data(result):
    if not result['data'] :
      result['ret'] = Status.NODATA
      result['info'] = Status().getReason(result['ret'])

#消息盒子
def myMessagesBox(request,sha1,messageType,start,end):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = myMessagesBox_data(request,sha1 = sha1 ,messageType = messageType,start = start,end = end)
    if not result['data'] :
      result['ret'] = Status.USERNOTEXIST
      result['info'] = Status().getReason(result['ret'])
      result['data']['has_next'] = 'false'
    elif not len(result['data']['message_list']) == end-start+1 :
      result['ret'] = Status.NOMOREDATA
      result['info'] = Status().getReason(result['ret'])
      result['data']['has_next'] = 'false'
    return result


# 获取用户行为的数据
def user_action(request,action_type,username,obj_type,sha1,promotion_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    session=request.get_session()
    #查询用户
    try :
        user = session.query(CustomerAccount).filter_by(name = username).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #用户行为数据处理
    vcard_id = user.cardnum
    action_time = str(datetime.datetime.now())
    #验证行为的商品
    if obj_type == 3 :
        try :
            advertisement = session.query(Advertisement).filter_by(sha1 = sha1).one()
        except Exception,e:
            ajax_logger.error("advertisement:"+str(e))
            return result
    #验证营销活动
    if not promotion_id == 0 :
        try:
            # 查询活动的信息
            promotion_info = session.query(Promotion).filter_by(id=promotion_id).one()
        except Exception,e :
            ajax_logger.error("promotion:"+str(e))
            return result
    try :
        action_object = UserAction(
                            vcard_id = vcard_id,
                            obj_type = obj_type,
                            sha1 = sha1,
                            action = action_type,
                            action_time = str(datetime.datetime.now()).split(" ")[0],
                            promotion_id = promotion_id
                            )
        session.add(action_object)
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        return result
    return result


#我的专享 用户点击购买，创建订单
def create_order(request,vcard_id,good_sha1,order_type,item_count,promotion_id,price,order_total,seller_sha1,status):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    # 检查商品库存，检查商品价格，生成订单
    try:
        session = request.get_session()

        #商品总价格
        item_total = order_total

        #商品名称
        item_name = ''

        order_type = int(order_type)


        #油站sha1,非油购买时为空
        station_sha1 = ''
        comp_id = 0
        #order_type 0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城
        if order_type == 1:
            station_sha1 = seller_sha1
            try :
                station = session.query(Station).filter_by(sha1 = station_sha1).one()
                comp_id = station.comp_id
            except Exception,e:
                ajax_logger.error(str(e))
            #获取油品信息
            fuel = session.query(StationFuelType).filter_by(barcode=good_sha1).first()
            item_name = fuel.description

        #商品
        elif order_type == 2:
            try:
                #获取商品信息
                store = session.query(StoreItem).filter_by(sha1=good_sha1).one()
                comp_id = store.comp_id
                item_name = store.name
            except:
                item_name = ''

        #车后服务
        elif order_type == 3:
            station_sha1 = ''
            #获取车后服务信息
            try:
                service = session.query(ServiceInformation).filter_by(sha1=good_sha1).one()
                comp_id = service.comp_id
                item_name = service.title
            except:
                item_name = ''

        # 创建订单记录
        time_string = str(time.time())
        order_sha1=hashlib.sha1()
        order_sha1.update(vcard_id+str(good_sha1)+time_string+str(promotion_id))
        sha1=order_sha1.hexdigest()
        try :
            promotion = session.query(Promotion).filter_by(id = int(promotion_id)).one()
            comp_id = promotion.comp_id
        except Exception,e:
            ajax_logger.error(str(e))
            
        order = CustomerAccountTransaction(
                                 vcard_id=vcard_id,
                                 trans_type=order_type,
                                 item_total=item_total,
                                 status=status,
                                 promotion_id=promotion_id,
                                 item_count=item_count ,
                                 item_sha1=good_sha1,
                                 seller_sha1=seller_sha1,
                                 station_sha1 = station_sha1,
                                 sha1 = sha1,
                                 comp_id = comp_id,
                                 item_name = item_name,
                                 time = str(datetime.datetime.now()))

        session.add(order)
        session.commit()

        result['data'] = {"order_sha1":order.sha1}
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.CREATE_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result

    return result

# 获取当前用户的订单列表
def get_order_list(request,vcard_id,start,end,status):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()

    #时间倒序查询相关订单
    if status == 5 :
        orders_5 = session.query(CustomerAccountTransaction).filter(CustomerAccountTransaction.status==5,
          CustomerAccountTransaction.vcard_id==vcard_id,CustomerAccountTransaction.trans_type>0\
        ).order_by('time desc').all()
        orders_6 = session.query(CustomerAccountTransaction).filter(CustomerAccountTransaction.status==6,
          CustomerAccountTransaction.vcard_id==vcard_id,CustomerAccountTransaction.trans_type>0\
        ).order_by('time desc').all()
        orders_6.extend(orders_5)
        orders = orders_6
    else :
        orders = session.query(CustomerAccountTransaction).filter(CustomerAccountTransaction.status==status,
          CustomerAccountTransaction.vcard_id==vcard_id,CustomerAccountTransaction.trans_type>0\
        ).order_by('time desc').all()
    order_list = orders[int(start):int(end)]

    result['data'] = {}
    result['data']['has_next'] = 'true'
    order_info_list = []

    #订单数量
    need_order_count = int(end) - int(start)
    if need_order_count >= len(orders):
        result['data']['has_next'] = 'false'

    for order in order_list:
        dic = {}

        status = ''

        #查询交易地点
        station = session.query(Station).filter_by(sha1=order.station_sha1).first()
        if station :
            address = station.name
        else :
            address = ""

        #处理订单状态
        if order.status == 0:
            status = '交易未完成'
        elif order.status == 1:
            status = '已付款，等待确认'
        elif order.status == 2:
            status = '交易完成'
        elif order.status == 3:
            status = '交易关闭'
        elif order.status == 4:
            status = '已订购，等待确认'
        elif order.status == 5: 
            status = '申请退款成功,请持身份证件到相关地点确认'
        elif order.status == 6 :
            status = '退款成功'
        else:
            status = '交易关闭'


        #商品名字
        dic['item_name'] = order.item_name or ''

        #商品的sha1
        dic['item_sha1'] = order.item_sha1 or ''

        #订单的交易时间
        dic['time'] = order.time.strftime('%Y-%m-%d %H:%M') or ''

        #订单的交易金额
        dic['item_total'] = order.item_total or 0

        #购买数量
        dic['item_count'] = order.item_count or 1

        #订单的交易状态
        dic['status'] = status or ''

        #交易地点
        dic['address'] = address or ''

        #站点的sha1
        dic['station_sha1'] = order.station_sha1 or ''

        #取货位置
        try :
           station = session.query(Station).filter_by(sha1 = order.station_sha1).one()
           dic['geo_x'] = station.geo_x
           dic['geo_y'] = station.geo_y
        except :
          dic['geo_x'] = 0.0
          dic['geo_y'] = 0.0

        #便利店的sha1
        dic['seller_sha1'] = order.seller_sha1 or ''

        #交易类型
        dic['trans_type'] = order.trans_type

        #订单号
        dic['order_sha1'] = order.sha1 or ''

        #订单状态
        dic['status_flag'] = order.status

        order_info_list.append(dic)

    result['data']['trans_list'] = order_info_list
    return result

#用户删除订单
def delete_order(request,vcard_id,order_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    #查询用户
    try :
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证订单信息
    try :
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1,vcard_id = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    #验证成功,修改订单状态为已过期
    #订单状态  0 代表订单生成  1代表支付完成 2代表交易完成 3代表交易被收银员录入 
    #4商品预订状态  5 申请退款完成状态 6 工作人员完成退款  7 订单已过期
    order.status = 7
    try :
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UPDATE_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    return result

#获取用户订单数量
def get_order_num(request,vcard_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()

    try:
        result['data'] = {}
        #获取待支付订单数量
        wait_pay_num = session.query(func.count('*')).filter(CustomerAccountTransaction.status==0,CustomerAccountTransaction.vcard_id==vcard_id,CustomerAccountTransaction.trans_type>0\
        ).scalar()

        #获取待取货订单数量
        wait_pick_up_num = session.query(func.count('*')).filter(CustomerAccountTransaction.status==1,CustomerAccountTransaction.vcard_id==vcard_id,CustomerAccountTransaction.trans_type>0\
        ).scalar()

        #已订购订单数量
        wait_fix_num = session.query(func.count('*')).filter(CustomerAccountTransaction.status==4,CustomerAccountTransaction.vcard_id==vcard_id,CustomerAccountTransaction.trans_type>0\
        ).scalar()

        wait_refund_num = session.query(func.count('*')).filter(CustomerAccountTransaction.status==5,CustomerAccountTransaction.vcard_id==vcard_id,CustomerAccountTransaction.trans_type>0\
        ).scalar()

        wait_refund_num = wait_refund_num + session.query(func.count('*')).filter(CustomerAccountTransaction.status==6,CustomerAccountTransaction.vcard_id==vcard_id,CustomerAccountTransaction.trans_type>0\
        ).scalar()


        result['data']['wait_pick_up_num'] = wait_pick_up_num
        result['data']['wait_pay_num'] = wait_pay_num
        result['data']['wait_fix_num'] = wait_fix_num
        result['data']['wait_refund_num'] = wait_refund_num

    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])

    finally:
      return result

#获取用户积分
def get_user_score(request,vcard_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    try:
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
        result['data']['total_scores'] = user.all_score
        result['data']['current_scores'] = user.score
        result['data']['level'] = user.score_rank
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
    finally:
      return result

#获取广告位信息
def get_advertis(request,name):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    result['data']['list'] = []
    try:
      session = request.get_session()
      advertisements = session.query(Advertisement).all()
      ajax_logger.info("len:"+str(len(advertisements)))
      for obj in advertisements :
          advert_id = obj.id
          try :
              advertisement_launch_setting = session.query(AdvertisementLaunchSetting).filter_by(advert_id =advert_id).one()
              if advertisement_launch_setting.is_close == 0 :
                  continue
              play_time = advertisement_launch_setting.play_time
          except Exception,e:
              ajax_logger.error(str(e))
              result['ret'] = Status.GET_ADVERTISE_SETTING_ERROR
              result['info'] = Status().getReason(result['ret'])
              result['data']['list'] = []
              return data
          result['data']['list'].append(dict(
                title = obj.title,
                play_time = play_time,
                src = '/gcustomer/ajax/render_image/',
                img_sha1 = obj.image_sha1 or '',
                sha1 = obj.sha1
            ))
    except Exception,e:
      ajax_logger.error(str(e))
      result['ret'] = Status.QUERY_ADVERTISE_ERROR
      result['info'] = Status().getReason(result['ret'])
      result['data']['list'] = []
      return result
    return result


#获取广告详情
def get_advertis_detail(request,adv_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    try:
          session = request.get_session()
          obj = session.query(Advertisement).filter_by(sha1 = adv_sha1).one()
          result['data']['title'] = obj.title
          result['data']['content'] = obj.abstract
    except Exception,e:
          ajax_logger.error(str(e))
          result['ret'] = Status.QUERY_ADVERTISE_ERROR
          result['info'] = Status().getReason(result['ret'])
          result['data'] = {}
          return  result
    return result


#查看广告
def read_advertis(request,adv_sha1,user_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    try :
      session = request.get_session()
      try:
          adv_id = session.query(Advertisement).filter_by(sha1 = adv_sha1).one().id
      except Exception,e:
          ajax_logger.error(str(e))
          result['ret'] = Status.QUERY_ADVERTISE_ERROR
          result['info'] = Status().getReason(result['ret'])
          return result
      try :
          cardnum = CustomerAccount.objects.filter(sha1 = user_sha1).first().cardnum
          customer = session.query(CustomerProfile).filter_by(cardnum = cardnum).one()
      except Exception,e:
          ajax_logger.error(str(e))
          result['ret'] = Status.QUERY_CUSTOMER_ERROR
          result['info'] = Status().getReason(result['ret'])
          return result
      adv_obj = UserAction(
          user_source = customer.user_source,
          cardnum = cardnum,
          obj_type = 1,
          obj_id = adv_id ,
          action = 0 ,
          action_time = str(datetime.datetime.now())
        )
      session.add(adv_obj)
      try :
          session.commit()
      except Exception ,e :
          ajax_logger.error(str(e))
          result['ret'] = Status.ADVERTISEMENT_RECORD
          result['info'] =  Status().getReason(result['ret'])
          return result
    except Exception,e :
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#行车轨迹
def trajectory(request,name,longitude,latitude):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    try :
        user = session.query(CustomerAccount).filter_by(name = name).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    try :
        trace_point = WheelAccountLocation(
            user_type = 1,
            user_id = name,
            geo_x = longitude,
            geo_y = latitude
        )
        trace_point.save()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.DRIN_TRACE_RECORD_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#新增功能
#上传头像
def upload_avarta_image(request,name,avarta_image_data) :
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(name = name).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    try :
        imagebinarydata = avarta_image_data
        sha1=hashlib.sha1()
        sha1.update(str(imagebinarydata))
        img_sha1=sha1.hexdigest()
        if img_sha1 :
            try :
                WheelFileImage.objects.get(sha1 = img_sha1)
                user.avarta_sha1 = img_sha1
                session.commit()
                return result
            except :
                import base64
                imagebinarydata = base64.b64encode(imagebinarydata)
                obj = WheelFileImage(sha1 = img_sha1,base64_content=imagebinarydata,file_name = user.nick or "")
                obj.save()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UPLOAD_IMAGE_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    user.avarta_sha1 = img_sha1
    session.commit()
    return result

#修改用户昵称
def modify_user_info(request,name,nick):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    try :
          user = session.query(CustomerAccount).filter_by(name = name).one()
          user.nick = nick
          try :
              session.commit()
          except Exception,e :
              ajax_logger.error(str(e))
              result['ret'] = Status.ALTER_USER_ERROR
              result['info'] = Status().getReason(result['ret'])
              return result
    except Exception,e:
          ajax_logger.error(str(e))
          result['ret'] = Status.USERNOTEXIST
          result['info'] = Status().getReason(result['ret'])
          return result
    return result

#修改用户密码
def modify_login_password(request,name,old_pasword,new_password,re_new_password) :
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    try :
        user = session.query(CustomerAccount).filter_by(name = name).one()
        if not old_pasword == user.password :
            result['ret'] = Status.PASSWORDERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        elif not new_password == re_new_password :
            result['ret'] = Status.PASSWORDINCONSISTENT
            result['info'] = Status().getReason(result['ret'])
            return result
        else :
            user.password = new_password
        try :
            session.commit()
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.ALTER_USER_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#获取石油公司信息
def get_oil_company_info(request,name):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = []
    try :
          session = request.get_session()
          #用户验证
          try :
              user = session.query(CustomerAccount).filter_by(name = name).one()
          except Exception,e:
              ajax_logger.error(str(e))
              result['ret'] = Status.USERNOTEXIST
              result['info'] = Status().getReason(result['ret'])
              return result
          comps = session.query(GCompany).all()
          #获取当前用户关联的公司
          associated_oil_company_list = get_associated_oil_company(user.cardnum)
          for comp in comps :
              if not comp.id in associated_oil_company_list :
                  result['data'].append(dict(
                        comp_id = comp.id,
                        comp_name = comp.name
                    ))
    except Exception,e:
          ajax_logger.error(str(e))
          result['ret'] = Status.QUERY_COMPANY_ERROR
          result['info'] = Status().getReason(result['ret'])
          return result
    return result

#关联石油公司帐号
def associated_oil_company(request,vcard_id,id_card,comp_id) :
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证公司
    try :
        comp = session.query(GCompany).filter_by(id = comp_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_COMPANY_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    try :
        account = session.query(CustomerCompInfo).filter_by(vcard_id=vcard_id,comp_id=int(comp_id)).one()
        result['ret'] = Status.PUMP_CARD_HAS_EXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    except:
        account = CustomerCompInfo(
            vcard_id = vcard_id,
            comp_id = comp_id,
            balance = 0 ,
            total_charge_num = 0,
        )
        try :
            session.add(account)
            session.commit()
            try :
                  associate_user_to_group(comp_id,vcard_id)
            except Exception,e:
                  ajax_logger.info("associate user to group error")
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.ASSOCIATE_COMPANY_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
    return result

#绑定加油卡
def band_oil_card(request,vcard_id,id_card,comp_id,card_num,card_type):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id,id_card=id_card).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证实体卡是否存在
    try :
        card = UserCardProfilingResult.objects.get(cardnum=card_num)
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_BIND_CARD_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证卡绑定
    try :
        customer_compInfo = session.query(CustomerCompInfo).filter_by(vcard_id=vcard_id,
          comp_id=comp_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QYERY_ACCOUNT_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    card_obj_list = json.loads(customer_compInfo.card_list)
    temp_card_list = []
    for temp_card in card_obj_list :
        temp_card_list.append(temp_card['cardnum'])
    if card_num  in temp_card_list:
        result['ret'] = Status.OIL_CARD_HAS_BIND
        result['info'] = Status().getReason(result['ret'])
        return result
    else :
        #绑定
        card.comp_id = comp_id
        card_obj_list.append(dict(
            cardnum = card_num,
            card_type = card_type,
          ))
        customer_compInfo.card_list = json.dumps(card_obj_list)
    try :
        card.save()
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.BIND_PUMP_CARD_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#解除绑定加油卡
def delete_oil_card_bind(request,vcard_id,id_card,comp_id,card_num,pay_password):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id,pay_password = pay_password,
          id_card=id_card).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.PASSWORDERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证卡绑定
    try :
        customer_compInfo = session.query(CustomerCompInfo).filter_by(vcard_id=vcard_id,
          comp_id=comp_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QYERY_ACCOUNT_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    card_obj_list = json.loads(customer_compInfo.card_list)
    temp_card_list = []
    for temp_card in card_obj_list :
        if temp_card['cardnum'] == card_num :
            card_obj_list.remove(temp_card)
            break
    customer_compInfo.card_list = json.dumps(card_obj_list)
    try :
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.DELETE_BIND_CARD_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#查看我的账户
def get_pump_card(request,vcard_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = []
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    try :
        account_list = session.query(CustomerCompInfo).filter_by(vcard_id = vcard_id).all()
        for account in account_list :
            try :
                if not account.comp_id == 0:
                    comp  = session.query(GCompany).filter_by(id = account.comp_id).one()

                    result['data'].append(dict(
                          comp_id = account.comp_id,
                          card_desc = comp.name,
                          current_balance = account.balance,
                      ))
                else :
                    result['data'].append(dict(
                          comp_id = 0 ,
                          card_desc = "志察数据",
                          current_balance = account.balance,
                      ))
            except Exception,e:
                result['ret'] = Status.QUERY_COMPANY_ERROR
                result['info'] = Status().getReason(result['ret'])
                result['data'] = []
                return result
    except Exception,e:
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    return result

#获取我关联的石油公司的实体卡信息
def get_my_oil_card(request,vcard_id,comp_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    try :
        session = request.get_session()
        compInfo = session.query(CustomerCompInfo).filter_by(vcard_id = vcard_id,comp_id=comp_id).one()
        card_list = []
        card_obj_list = json.loads(compInfo.card_list)
        temp_card_list = []
        for temp_card in card_obj_list :
                card_list.append(dict(
                      cardnum = temp_card['cardnum'],
                      card_type = int(temp_card['card_type'])
                  ))
    except Exception,e:
        result['ret'] = Status.CHECK_USER_AND_CARD_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data']['card_list'] = []
        return result
    result['data']['card_list'] = card_list
    return result

#加油卡冲值
def recharge(request,vcard_id,id_card,comp_id,money):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id,id_card=id_card).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    #验证用户账户信息
    try :
        account = session.query(CustomerCompInfo).filter_by(vcard_id = vcard_id,comp_id=comp_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QYERY_ACCOUNT_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    try :
            account.balance = account.balance  + money
            user.balance = user.balance + money
            result['data']['current_balance'] = account.balance
            result['data']['money'] = money
            try :
                session.commit()
                #生成充值完成订单
                if not create_charge_order(vcard_id,comp_id,money) :
                    result['ret'] = Status.CREATE_ORDER_ERROR
                    result['info'] = Status().getReason(result['ret'])
                    return result
            except :
                ajax_logger.error(str(e))
                result['ret'] = Status.RECHARGEERROR
                result['info'] = Status().getReason(result['info'])
                result['data'] = {}
                return result
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.RECHARGEERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    return result

#忘记支付密码处理
def forget_pay_password(request,vcard_id,id_card):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    if user.id_card == id_card :
        result['data']['pay_password'] = user.pay_password
    else :
        result['ret'] = Status.USER_ID_CARD_CHECK_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    return result

#修改支付密码
def modify_pay_password(request,vcard_id,id_card,old_pay_password,new_pay_password,re_new_pay_password) :
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id,id_card=id_card).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    if not old_pay_password == user.pay_password :
        #获取加密字符串
        old_pay_password = md5_data(old_pay_password)
        #md5加密
        if not old_pay_password == user.pay_password :
          result['ret'] = Status.PRE_PASSWORD_ERROR
          result['info'] = Status().getReason(result['ret'])
          return result
    if not new_pay_password == re_new_pay_password :
        result['ret'] = Status.PASSWORDINCONSISTENT
        result['info'] = Status().getReason(result['ret'])
        return result
    user.pay_password = new_pay_password
    try :
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.MODIFYPAYPASSWORDERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#检查支付密码
def check_pay_password(request,vcard_id,id_card,pay_password):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id,id_card=id_card).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    if not pay_password == user.pay_password :
        result['ret'] = Status.PASSWORDERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    else :
        return result

#查看油品订单
def confirm_order_by_user(request,vcard_id,order_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    result['data']['order_info'] = {}
    result['data']['order_info']['fuel_info'] = {}
    result['data']['order_info']['site_info'] = {}
    try :
        session = request.get_session()
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
        order.vcard_id = vcard_id
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    try :
        result['data']['order_info']['order_sha1'] = order.sha1
        result['data']['order_info']['trans_type'] = order.trans_type
        result['data']['order_info']['order_total'] = order.item_total
        result['data']['order_info']['item_count'] = order.item_count
        result['data']['order_info']['time'] = str(order.time)
        result['data']['order_info']['status'] = order.status
        result['data']['order_info']['vcard_id'] = order.vcard_id
        #查询商品信息
        station_sha1 =  order.station_sha1
        barcode = order.item_sha1
        try :
            station = session.query(Station).filter_by(sha1 = station_sha1).one()
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.QUERY_SITE_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        try :
            fuel_object = session.query(StationFuelType).filter_by(station = station.site_code,barcode = barcode).one()
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.QUERY_SITE_FUEL_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        # 订单商品信息
        result['data']['order_info']['fuel_info']['fuel_name'] = fuel_object.description
        result['data']['order_info']['fuel_info']['barcode'] = barcode
        result['data']['order_info']['fuel_info']['price'] = round(fuel_object.price,2)
        result['data']['order_info']['fuel_info']['src'] = "/gcustomer/ajax/render_image/"
        result['data']['order_info']['fuel_info']['img_sha1'] = ""
        #订单商家信息
        result['data']['order_info']['site_info']['name'] = station.name
        result['data']['order_info']['site_info']['sha1'] = station.sha1
        result['data']['order_info']['site_info']['address'] = station.address
        result['data']['order_info']['site_info']['phone'] = station.site_tel
        try :
            session.commit()
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.COMFIRM_ORDER_ERROR
            result['info'] = Status().getReason(result['ret'])
            result['data'] = {}
            return result
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.GET_ORDER_INFO_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    return result

#获取可加油支付的账户
def get_pay_account(request,vcard_id,id_card,order_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = []
    session = request.get_session()
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id,id_card=id_card).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    #查询订单石油公司
    try :
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    comp_id = order.comp_id
    comp_info = None
    if not comp_id == 0 :
        ajax_logger.info(str("get_pay_account:"+str(comp_id)))
        try :
            comp_info = session.query(CustomerCompInfo).filter_by(vcard_id=vcard_id,comp_id=comp_id).first()
        except:
            comp_info = None            
    my_account = session.query(CustomerCompInfo).filter_by(vcard_id=vcard_id,comp_id=0).one()
    result['data'].append(dict(
          comp_id = 0 ,
          comp_desc = "志察数据",
          current_balance = my_account.balance
      ))
    #如果与石油公司关联了
    if comp_info :
          comp = session.query(GCompany).filter_by(id=comp_id).one()
          result['data'].append(dict(
                comp_id = comp_id ,
                comp_desc = comp.name,
                current_balance = comp_info.balance
            ))
    return result

#加油卡支付
def pay_by_oil_card(request,vcard_id,order_sha1,id_card,comp_id,pay_password,pay):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id,id_card=id_card).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    #账户验证
    try :
        account = session.query(CustomerCompInfo).filter_by(comp_id=comp_id,vcard_id=vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QYERY_ACCOUNT_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    if not user.pay_password == pay_password :
        result['ret'] = Status.PASSWORDERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    elif account.balance < pay :
        result['ret'] = Status.CURRENTBALANCEDEFICENTCY
        result['info'] = Status().getReason(result['ret'])
        return result
    else :
        try :
            #验证公司信息
            if comp_id :
                company = session.query(GCompany).filter_by(id = comp_id).one()
            try :
                account.balance = account.balance - pay
                user.balance = user.balance - pay
                session.commit()
            except Exception,e:
                result['ret'] = Status.PAYBYOILCARDERRO
                result['info'] = Status().getReason(result['ret'])
                return result
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.QUERY_COMPANY_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
    #支付完成修改订单状态
    result = purchase_complete_by_user(request,order_sha1,vcard_id)
    return result
    

#支付完成修改订单状态
def purchase_complete_by_user(request,order_sha1,vcard_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    try :
        session = request.get_session()
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    order.status = 1
    try :
        session.commit()
        #修改用户积分
        if order.trans_type == 1 or order.trans_type == 2 or order.trans_type == 3  :
            #查询用户信息
            try :
                user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
            except Exception,e:
                ajax_logger.error(str(e))
                result['ret'] = Status.USERNOTEXIST
                result['info'] = Status().getReason(result['ret'])
                return result
            user.score = user.score + int(order.item_total)
            user.all_score = user.all_score + int(order.item_total)
            try :
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                result['ret'] = Status.ALTER_USER_ERROR
                result['info'] = Status().getReason(result['ret'])
                return result

        #调用消息服务器发送消息
        try :
            from gcustomer.message_server.service.message_service import *
            try :
                user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
            except Exception,e:
                ajax_logger.error(str(e))
                result['ret'] = Status.USERNOTEXIST
                result['info'] = Status().getReason(result['ret'])
                result['data'] = []
                return result
            user_sha1 = user.cardnum
            worker_sha1 = order.worker_sha1
            worker_name = session.query(GasWorker).filter_by(sha1 =worker_sha1).one().name
            MessageService.PushCompleteTransMessage({
                          "user_sha1":user_sha1,
                         "order_sha1":order_sha1,
                         "status":1})
            MessageService.PushCompleteTransMessage({
                          "user_sha1":worker_name,
                         "order_sha1":order_sha1,
                         "status":1})
        except Exception,e:
            ajax_logger.error(str(e))
            pass

    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.ALTER_ORDER_STATUS_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result


#第三方支付完成修改订单状态
def purchase_complete_by_the_third(request,order_sha1,vcard_id):
    try :
        session = request.get_session()
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        return "fail"
    order.status = 1
    try :
        session.commit()
        #修改用户积分
        if order.trans_type == 1 or order.trans_type == 2 or order.trans_type == 3  :
            #查询用户信息
            try :
                user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
            except Exception,e:
                ajax_logger.error(str(e))
                return "fail"
            user.score = user.score + int(order.item_total)
            user.all_score = user.all_score + int(order.item_total)
            try :
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                return "fail"
    except Exception,e:
        ajax_logger.error(str(e))
        return 'fail'
    return "success"

#附近
def get_near_by_infos(request,longitude,latitude,info_flag) :
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = []
    session = request.get_session()
    try :
        near_info_list =  get_near_info(request,longitude,latitude,info_flag)
        #0：油品；1：便利店；2：车后服务
        if info_flag == 0 :
            for near_info in near_info_list :
                try :
                    station = session.query(Station).filter_by(sha1 = near_info['sha1']).one()
                    distance = near_info['distance']
                    result['data'].append(dict(
                          longitude = station.geo_x,
                          latitude = station.geo_y,
                          name = station.name,
                          sha1 = station.sha1,
                          distance = distance,
                      ))
                except Exception,e:
                    ajax_logger.error(str(e))
                    result['ret'] = Status.QUERY_NEAR_INFO_ERROR
                    result['info'] = Status().getReason(result['ret'])
                    result['data'] = []
                    return result
        elif info_flag == 1 :
            for near_info in near_info_list :
                try :
                    station = session.query(Station).filter_by(sha1 = near_info['sha1']).one()
                    distance = near_info['distance']
                    result['data'].append(dict(
                          longitude = station.geo_x,
                          latitude = station.geo_y,
                          name = station.name,
                          sha1 = station.sha1,
                          distance = distance,
                      ))
                except Exception,e:
                    ajax_logger.error(str(e))
                    result['ret'] = Status.QUERY_NEAR_INFO_ERROR
                    result['info'] = Status().getReason(result['ret'])
                    result['data'] = []
                    return result
        elif info_flag == 2 :
            for near_info in near_info_list :
                try :
                    seller = session.query(Seller).filter_by(sha1 = near_info['sha1']).one()
                    distance = near_info['distance']
                    result['data'].append(dict(
                          longitude = seller.geo_x,
                          latitude = seller.geo_y,
                          name = seller.name,
                          sha1 = seller.sha1,
                          distance = distance
                      ))
                except Exception,e:
                    ajax_logger.error(str(e))
                    result['ret'] = Status.QUERY_NEAR_INFO_ERROR
                    result['info'] = Status().getReason(result['ret'])
                    result['data'] = []
                    return result
        else :
            ajax_logger.error(str(e))
            result['ret'] = Status.UNKNOWNERR
            result['info'] = Status().getReason(result['ret'])
            result['data'] = []
    except Exception ,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
    return result

#获取附近信息
def get_near_info(request,longitude,latitude,info_flag):
    near_info_list = []
    session = request.get_session()
    try :
        #0：油品；1：便利店；2：车后服务
        if info_flag == 0 :
            stations = session.query(Station).all()
            for station in stations :
                near_distance = distance(longitude,latitude,station.geo_x,station.geo_y)
                if near_distance <= NEAR_DISTANCE :
                    near_info_list.append(dict(
                        sha1 = station.sha1,
                        distance = near_distance
                      ))
        elif info_flag == 1 :
            stations = session.query(Station).all()
            for station in stations :
                near_distance = distance(longitude,latitude,station.geo_x,station.geo_y)
                if near_distance <= NEAR_DISTANCE :
                    near_info_list.append(dict(
                        sha1 = station.sha1,
                        distance = near_distance
                      ))
        elif info_flag == 2 :
            sellers = session.query(Seller).all()
            for seller in sellers :
                near_distance = distance(longitude,latitude,seller.geo_x,seller.geo_y)
                if near_distance <= NEAR_DISTANCE :
                    near_info_list.append(dict(
                        sha1 = seller.sha1,
                        distance = near_distance
                      ))
        else :
            pass
    except Exception,e:
        ajax_logger.error(str(e))
        near_info_list = []
    return  near_info_list

#获取附近便利店
def get_near_by_sellers(request,longitude,latitude):
    ret_station = None
    pre_distance = 0
    current_distance = 0
    session = request.get_session()
    try :
        stations = session.query(Station).all()
        for station in stations :
            current_distance = distance(longitude,latitude,station.geo_x,station.geo_y)
            #if current_distance <= NEAR_DISTANCE :
            if ret_station == None:
                ret_station = station
                pre_distance = current_distance
            elif pre_distance > current_distance:
                pre_distance = current_distance
                ret_station = station
    except Exception,e:
        ajax_logger.error(str(e))
        ret_station = None
    return  ret_station

#获取热销商品top10
def get_hot_goods(request,username,longitude,latitude,flag):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = []
    hot_goods = {}
    try :
        session = request.get_session()
        #如果用户为测试用户,则显示所有热销商品
        if not username == "" : 
            try :
                  user = session.query(CustomerAccount).filter_by(name = username).one()
            except Exception,e:
              ajax_logger.error(str(e))
              result['ret'] = Status.USERNOTEXIST
              result['info'] = Status().getReason(result['ret'])
              return result
            station_profile_list = []
            if user.is_pay_in_advance == 1 :
                station_list = session.query(Station).all()
                for station in station_list :
                    try :
                        station_profile = session.query(StationProfile).filter_by(station_id = station.id).one()
                    except Exception,e:
                        ajax_logger.error(str(e))
                        continue
                    station_profile_list.append(station_profile)
                #获取该站点的top10便利店商品
                for site in station_profile_list :
                    try :
                        top_100_goods = json.loads(site.top_100_goods)
                        for good in top_100_goods :
                            if good['type'] == flag :
                                if not good['barcode'] in hot_goods.keys() :
                                    hot_goods[good['barcode']] = {"sum":good['sum'],"desc":good['desc'],"geo_x":station.geo_x,"geo_y":station.geo_y,"type":flag}
                            else :
                              continue
                    except Exception,e:
                        ajax_logger.error(str(e))
                        result['ret'] = Status.GET_STORE_HOT_GOODS_ERROR
                        result['info'] = Status().getReason(result['ret'])
                        return result
            else :
                #最近便利店的station_id
                station = get_near_by_sellers(request,longitude,latitude)
                #附近没有相关油站信息
                if station == None:
                    return result
                #获取站点信息
                try :
                    site = session.query(StationProfile).filter_by(station_id = station.id).one()
                except Exception,e:
                    ajax_logger.error(str(e))
                    result['ret'] = Status.QUERY_SITE_ERROR
                    result['info'] = Status().getReason(result['ret'])
                    return result
                #获取该站点的top10便利店商品
                try :
                    top_100_goods = json.loads(site.top_100_goods)
                    for good in top_100_goods :
                        if good['type'] == flag :
                            if not good['barcode'] in hot_goods.keys() :
                                hot_goods[good['barcode']] = {"sum":good['sum'],"desc":good['desc'],"geo_x":station.geo_x,"geo_y":station.geo_y,"type":flag}
                        else :
                          continue
                except Exception,e:
                    ajax_logger.error(str(e))
                    result['ret'] = Status.GET_STORE_HOT_GOODS_ERROR
                    result['info'] = Status().getReason(result['ret'])
                    return result
        else : 
            #最近便利店的station_id
            station = get_near_by_sellers(request,longitude,latitude)
            #附近没有相关油站信息
            if station == None:
                return result
            #获取站点信息
            try :
                site = session.query(StationProfile).filter_by(station_id = station.id).one()
            except Exception,e:
                ajax_logger.error(str(e))
                result['ret'] = Status.QUERY_SITE_ERROR
                result['info'] = Status().getReason(result['ret'])
                return result
            #获取该站点的top10便利店商品
            try :
                top_100_goods = json.loads(site.top_100_goods)
                for good in top_100_goods :
                    if good['type'] == flag :
                        if not good['barcode'] in hot_goods.keys() :
                            hot_goods[good['barcode']] = {"sum":good['sum'],"desc":good['desc'],"geo_x":station.geo_x,"geo_y":station.geo_y,"type":flag}
                    else :
                      continue
            except Exception,e:
                ajax_logger.error(str(e))
                result['ret'] = Status.GET_STORE_HOT_GOODS_ERROR
                result['info'] = Status().getReason(result['ret'])
                return result
        #返回热销商品
        for good_barcode in hot_goods.keys() :
            try :
                if hot_goods[good_barcode]['type'] == 0 :
                    try :
                        fuel = session.query(StationFuelType).filter_by(station= station.site_code,barcode = int(good_barcode)).one()
                        result['data'].append(dict(
                              sha1 = good_barcode,
                              name = fuel.description,
                              counts = int(hot_goods[good_barcode]['sum']),
                              price = round(fuel.price,2),
                              longitude = hot_goods[good_barcode]['geo_x'],
                              latitude = hot_goods[good_barcode]['geo_y'],
                              phone = "",
                              src = "/gcustomer/ajax/render_image/",
                              img_sha1 = '',
                              address = station.address or ''
                          ))
                    except Exception,e:
                        ajax_logger.error(str(e))
                        continue
                elif hot_goods[good_barcode]['type'] == 1 :
                    try :
                        good = session.query(StoreItem).filter_by(comp_id = station.comp_id,pos_id = good_barcode).one()
                        comp_id = good.comp_id 
                        try : 
                            company = session.query(GCompany).filter_by(id=comp_id).one()
                        except Exception,e:
                            result['ret'] = Status.QUERY_COMPANY_ERROR
                            result['info'] = Status().getReason(result['ret'])
                            return result
                        phone = company.phone
                        address = company.address
                        result['data'].append(dict(
                              sha1 = good.sha1,
                              name = good.name,
                              counts = int(hot_goods[good_barcode]['sum']),
                              price = round(good.price,2),
                              longitude = hot_goods[good_barcode]['geo_x'],
                              latitude = hot_goods[good_barcode]['geo_y'],
                              phone = phone,
                              src = "/gcustomer/ajax/render_image/",
                              img_sha1 = good.image or '',
                              address = address
                          ))
                    except Exception,e:
                        ajax_logger.error(str(e))
                        continue
                elif hot_goods[good_barcode]['type'] == 2 :
                  try:
                        good = session.query(ServiceInformation).filter_by(comp_id = station.comp_id,sha1 = good_barcode).one()
                        result['data'].append(dict(
                              sha1 = good.sha1,
                              name = good.title,
                              counts = int(hot_goods[good_barcode]['sum']),
                              price = round(good.price,2),
                              longitude = hot_goods[good_barcode]['geo_x'],
                              latitude = hot_goods[good_barcode]['geo_y'],
                              phone = "",
                              src = "/gcustomer/ajax/render_image/",
                              img_sha1 = good.img_sha1 or '',
                              address = station.address or ''
                          ))
                  except Exception,e:
                      ajax_logger.error(str(e))
                      continue
                else :
                    continue
            except Exception,e:
                ajax_logger.error(str(e))
                continue
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
    return result

#道路救援
def get_help(request):
    result = {}
    result['ret'] = Status.OK
    result['info'] = status().getReason(result['ret'])
    result['data'] = []
    try :
        help_phones = WheelHelpPhone.objects.all()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_HELP_PHONE_ERROR
        result['info'] = status().getReason(result['ret'])
        result['data'] = []
        return result
    try :
        for help_phone in help_phones :
            result['data'].append(dict(
                  name = help_phone.name ,
                  phone = help_phone.phone
              ))
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] =   Status().getReason(result['ret'])
        result['data'] = []
        return result
    return result

#获取我的专享信息
def get_my_sales_summary(request,vcard_id,flag,start,end):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['has_next'] = 'true'
    result['data'] = []
    session=request.get_session()
    #创建完活动给某个用户推的优惠商品包括三部分: 1.给所有用户推的
    # 2:给该用户推的 3:给某个用户群推的该用户在该群中
    if vcard_id != "":
        #给所有用户推的 其中该用户和公司关联
        comp_info_list = session.query(CustomerCompInfo).filter_by(vcard_id = vcard_id).all()
        comp_id_list = []
        for comp_info in comp_info_list :
            comp_id_list.append(comp_info.comp_id)

        objs = session.query(UserTargetedPromotion).filter_by(user_type=1,user_id=0).all()
        for obj in objs :
            promotion_id = obj.promotion_id
            promotion = session.query(Promotion).filter_by(id = promotion_id).one()
            promotion_info = session.query(PromotionInfo).filter_by(promotion_id = promotion_id,obj_id=obj.obj_id,status=1).all()
            #判断商品是否可以预付 pay_type 0:不可以预付,只能预订 1:可以预付
            if promotion.auto_create_option == 1 or promotion.auto_create_option == 7:
                pay_type = 0
            else :
                pay_type = 1

            comp_id = promotion.comp_id
            if not comp_id in comp_id_list :
                continue
            if obj.obj_type == 0 and flag == 0 :
                for info in promotion_info :
                    station_sha1 = info.site_code
                    obj_id = obj.obj_id
                    station = session.query(Station).filter_by(sha1 = station_sha1).one()

                    #获取油站的高峰期  营销活动类型为改善油站设备效率
                    if promotion.auto_create_option == 1 :
                        try :
                            station_profile = session.query(StationProfile).filter_by(station_id = station.id).one()
                        except Exception,e:
                            ajax_logger.error(str(e))
                            continue
                        desc =  ""
                        peak_range_list = json.loads(station_profile.peak_range)
                        for peak_range in peak_range_list :
                            desc = desc + str(peak_range[0]) + "~" + str(peak_range[1]) + "  "
                        desc = desc + u"时"
                    else :
                        desc = ""

                    fuel = session.query(StationFuelType).filter_by(barcode=obj_id).first()
                    #查询购买次数
                    check_count,pay_count = get_user_action(request,str(obj_id),promotion_id)
                    result['data'].append(dict(
                        sha1 = str(obj_id),
                        name = fuel.description,
                        price = round(fuel.price,2),
                        discount = info.discount,
                        count = pay_count,
                        comp_name = station.name,
                        address = station.address,
                        seller_sha1 = station.sha1,
                        phone = station.site_tel,
                        img_sha1 = "",
                        src = "/gcustomer/ajax/render_image/",
			     promotion_id = promotion_id,
                        pay_type = pay_type,
                        desc = desc
                      ))
            elif obj.obj_type == 1 and flag == 1:
                try:
                    good = session.query(StoreItem).filter_by(id = obj.obj_id).one()
                    try :
                        company = session.query(GCompany).filter_by(id = good.comp_id).one()
                    except Exception,e:
                        ajax_logger.error(str(e))
                        result['ret'] = Status.QUERY_COMPANY_ERROR
                        result['info'] =   Status().getReason(result['ret'])
                        result['data'] = []
                        return result
                    for info in promotion_info :
                        station_sha1 = info.site_code
                        obj_id = obj.obj_id
                        station = session.query(Station).filter_by(sha1 = station_sha1).one()

                        #获取油站的高峰期  营销活动类型为改善油站设备效率
                        if promotion.auto_create_option == 1 :
                            try :
                                station_profile = session.query(StationProfile).filter_by(station_id = station.id).one()
                            except Exception,e:
                                ajax_logger.error(str(e))
                                continue
                            desc =  ""
                            peak_range_list = json.loads(station_profile.peak_range)
                            for peak_range in peak_range_list :
                                desc = desc + str(peak_range[0]) + "~" + str(peak_range[1]) + "  "
                            desc = desc + u"时"
                        else :
                            desc =  ""
                        #查询购买次数
                        check_count,pay_count = get_user_action(request,good.sha1,promotion_id)
                        result['data'].append(dict(
                            sha1 = good.sha1,
                            name = good.name,
                            price = round(good.price,2),
                            address = station.address,
                            seller_sha1 = station.sha1,
                            discount = info.discount,
                            count = pay_count,
                            comp_name = station.name,
                            phone = "",
                            img_sha1 = "",
                            src = "/gcustomer/ajax/render_image/",
			         promotion_id = promotion_id,
                            pay_type = pay_type,
                            desc = ""
                      ))
                except:
                    pass
            elif obj.obj_type == 2 and flag == 2:
              for info in promotion_info :
                service = session.query(ServiceInformation).filter_by(id = obj.obj_id).one()
                try :
                    company = session.query(GCompany).filter_by(id = service.comp_id).one()
                except Exception,e:
                    ajax_logger.error(str(e))
                    result['ret'] = Status.QUERY_COMPANY_ERROR
                    result['info'] =   Status().getReason(result['ret'])
                    result['data'] = []
                    return result
                #查询购买次数
                check_count,pay_count = get_user_action(request,service.sha1,promotion_id)
                result['data'].append(dict(
                        sha1 = service.sha1,
                        name = service.title,
                        price = round(service.price,2),
                        discount = info.discount,
                        count = pay_count,
                        comp_name = company.name ,
                        address = "",
                        seller_sha1 = service.seller_sha1 or '',
                        phone = "",
                        promotion_id = promotion_id,
                        pay_type = pay_type,
                        desc = "",
                        img_sha1 = "",
                        src = "/gcustomer/ajax/render_image/",
                  ))
        #给该用户推的 sha1s
        objs=session.query(UserTargetedPromotion).filter_by(user_type=1,user_id=int(vcard_id)).all()
        for obj in objs :
            promotion_id = obj.promotion_id
            promotion = session.query(Promotion).filter_by(id = promotion_id).one()
            promotion_info = session.query(PromotionInfo).filter_by(promotion_id = promotion_id,
              obj_id=obj.obj_id,status=1).all()
            #判断商品是否可以预付 pay_type 0:不可以预付,只能预订 1:可以预付
            if promotion.auto_create_option == 1 or promotion.auto_create_option == 7:
                pay_type = 0
            else :
                pay_type = 1

            if obj.obj_type == 0 and flag == 0 :
                for info in promotion_info :
                    station_sha1 = info.site_code
                    obj_id = obj.obj_id
                    station = session.query(Station).filter_by(sha1 = station_sha1).one()
                    fuel = session.query(StationFuelType).filter_by(barcode=obj_id).first()
                    #查询购买次数
                    check_count,pay_count = get_user_action(request,str(obj_id),promotion_id)
                    result['data'].append(dict(
                        sha1 = str(obj_id),
                        name = fuel.description,
                        price = round(fuel.price,2),
                        discount = info.discount,
                        count = 100,
                        comp_name = station.name,
                        address = station.address,
                        seller_sha1 = station.sha1,
                        phone = station.site_tel,
                        promotion_id = promotion_id,
                        pay_type = pay_type,
                        desc = "",
                        img_sha1 = "",
                        src = "/gcustomer/ajax/render_image/",
                      ))
            elif obj.obj_type == 1 and flag == 1:
                try:
                    good = session.query(StoreItem).filter_by(id = obj.obj_id).one()
                    try :
                        company = session.query(GCompany).filter_by(id = good.comp_id).one()
                    except Exception,e:
                        ajax_logger.error(str(e))
                        result['ret'] = Status.QUERY_COMPANY_ERROR
                        result['info'] =   Status().getReason(result['ret'])
                        result['data'] = []
                        return result
                    for info in promotion_info :
                        station_sha1 = info.site_code
                        obj_id = obj.obj_id
                        station = session.query(Station).filter_by(sha1 = station_sha1).one()
                        #查询购买次数
                        check_count,pay_count = get_user_action(request,good.sha1,promotion_id)
                        result['data'].append(dict(
                            sha1 = good.sha1,
                            name = good.name,
                            price = round(good.price,2),
                            address = station.address,
                            seller_sha1 = station_sha1,
                            discount = info.discount,
                            count = pay_count,
                            comp_name = station.name,
                            phone = "",
                            promotion_id = promotion_id,
                            pay_type = pay_type,
                            desc = "",
                            img_sha1 = "",
                            src = "/gcustomer/ajax/render_image/",
                      ))
                except:
                    pass
            elif obj.obj_type == 2 and flag == 2:
              for info in promotion_info :
                service = session.query(ServiceInformation).filter_by(id = obj.obj_id).one()
                try :
                    company = session.query(GCompany).filter_by(id = service.comp_id).one()
                except Exception,e:
                    ajax_logger.error(str(e))
                    result['ret'] = Status.QUERY_COMPANY_ERROR
                    result['info'] =   Status().getReason(result['ret'])
                    result['data'] = []
                    return result
                #查询购买次数
                check_count,pay_count = get_user_action(request,service.sha1,promotion_id)
                result['data'].append(dict(
                        sha1 = service.sha1,
                        name = service.title,
                        price = round(service.price,2),
                        discount = info.discount,
                        count = pay_count,
                        comp_name = company.name ,
                        address = "",
                        seller_sha1 = service.seller_sha1 or '',
                        phone = "",
                        promtion_id = promotion_id,
                        pay_type = pay_type,
                        desc = "",
                        img_sha1 = "",
                        src = "/gcustomer/ajax/render_image/",
                  ))
        #手动动创建的营销活动 给某个用户群推的该用户在该群中
        objs =  session.query(UserTargetedPromotion).filter_by(user_type=0).all()
        for obj in objs :
            try :
                promotion_id = obj.promotion_id
                promotion = session.query(Promotion).filter_by(id = promotion_id).one()
                promotion_info = session.query(PromotionInfo).filter_by(promotion_id = promotion_id,
                      obj_id=obj.obj_id,status=1).all()
                #判断商品是否可以预付 pay_type 0:不可以预付,只能预订 1:可以预付
                if promotion.auto_create_option == 1 or promotion.auto_create_option == 7:
                    pay_type = 0
                else :
                    pay_type = 1

                user_list = json.loads(session.query(TargetAudience).filter_by(id = obj.user_id).one().user_list)
            except Exception,e:
                continue
            if str(vcard_id) in user_list:
                if obj.obj_type == 0 and flag == 0 :
                    for info in promotion_info :
                        station_sha1 = info.site_code
                        obj_id = obj.obj_id
                        station = session.query(Station).filter_by(sha1 = station_sha1).one()
                        #查询购买次数
                        check_count,pay_count = get_user_action(request,str(obj_id),promotion_id)
                        fuel = session.query(StationFuelType).filter_by(station = station.site_code,barcode=obj_id).one()
                        result['data'].append(dict(
                            sha1 = str(obj_id),
                            name = fuel.description,
                            price = round(fuel.price,2),
                            discount = info.discount,
                            count = pay_count,
                            comp_name = station.name,
                            address = station.address,
                            seller_sha1 = station_sha1,
                            promotion_id = promotion_id,
                            pay_type = pay_type,
                            desc = "",
                            phone = station.site_tel,
                            img_sha1 = "",
                            src = "/gcustomer/ajax/render_image/",
                          ))
                elif obj.obj_type == 1 and flag == 1:
                  for info in promotion_info :
                      try:
                          good = session.query(StoreItem).filter_by(id = obj.obj_id).one()
                          try :
                              company = session.query(GCompany).filter_by(id = good.comp_id).one()
                          except Exception,e:
                              ajax_logger.error(str(e))
                              result['ret'] = Status.QUERY_COMPANY_ERROR
                              result['info'] =   Status().getReason(result['ret'])
                              result['data'] = []
                              return result
                          #查询购买次数
                          check_count,pay_count = get_user_action(request,good.sha1,promotion_id)
                          result['data'].append(dict(
                              sha1 = good.sha1,
                              name = good.name,
                              price = round(good.price,2),
                              address = "",
                              seller_sha1 = "",
                              discount = info.discount,
                              count = pay_count,
                              comp_name = company.name ,
                              phone = "",
                              promotion_id = promotion_id,
                              pay_type = pay_type,
                              desc = "",
                              img_sha1 = "",
                              src = "/gcustomer/ajax/render_image/",
                        ))
                      except:
                          pass
                elif obj.obj_type == 2 and flag == 2:
                  for info in promotion_info :
                      service = session.query(ServiceInformation).filter_by(id = obj.obj_id).one()
                      try :
                          company = session.query(GCompany).filter_by(id = service.comp_id).one()
                      except Exception,e:
                          ajax_logger.error(str(e))
                          result['ret'] = Status.QUERY_COMPANY_ERROR
                          result['info'] =   Status().getReason(result['ret'])
                          result['data'] = []
                          return result
                      #查询购买次数
                      check_count,pay_count = get_user_action(request,service.sha1,promotion_id)
                      result['data'].append(dict(
                              sha1 = service.sha1,
                              name = service.title,
                              price = round(service.price,2),
                              discount = info.discount,
                              count = pay_count,
                              comp_name = company.name ,
                              address = "",
                              seller_sha1 = service.seller_sha1 or '',
                              phone = "",
                              promotion_id = promotion_id,
                              pay_type = pay_type,
                              desc = "",
                              img_sha1 = "",
                              src = "/gcustomer/ajax/render_image/",
                        ))
    count = len(result['data'])
    if end >= count :
        result['has_next'] = "false"
    #排序
    result['data'].sort()
    result['data'] = result['data'][int(start):int(end)]
    return result


#获取用户信息
def get_user_info(request,name,password):
    ajax_logger.info(password)
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    try :
        session = request.get_session()
        user=session.query(CustomerAccount).filter_by(name=name).one()
    except Exception,e:
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Statu().getReason(result['ret'])
        return result
    if not user.password == password :
          result['ret']  = Status.PASSWORDERROR
          result['info'] = Status().getReason(result['ret'])
          return result
    result['data']['score'] = user.score
    result['data']['rank'] = user.score_rank
    result['data']['current_balance'] = user.balance
    result['data']['avarta_image_sha1'] = user.avarta_sha1
    return result

#查看预订是否可以购买
def check_reservation_by_user(request,order_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    try :
        session = request.get_session()
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    if  order.status == 0 :
        return result
    else :
        result['ret'] = Status.RESERVATION_CAN_NOT_PURCHASE
        result['info'] = Status().getReason(result['ret'])
        return result

#获取积分兑换商品列表详情
def get_score_list(request,vcard_id,start,end):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = get_score_list_data(request,vcard_id=vcard_id,start=start,end=end)
    check_data(result)
    return result

#获取积分商品详情
def get_score_good_detials(request,sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    session = request.get_session()
    try :
        score_good = session.query(StoreItem).filter_by(sha1=sha1).one()
        comp_id = score_good.comp_id
        company = session.query(GCompany).filter_by(id = comp_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_STOREITEM_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    #返回积分商品详情
    result['data']['sha1'] = sha1
    result['data']['goods_name'] = score_good.name
    result['data']['purchase_count'] = 152
    result['data']['score'] = score_good.exchange_score
    result['data']['seller_name'] = company.name
    result['data']['seller_address'] = company.address
    result['data']['seller_phone'] = company.phone
    result['data']['img_sha1'] = ''
    result['data']['src'] = ''
    return result

#创建积分订单
def create_score_order(request,vcard_id,good_sha1,order_type,item_count,score):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()

    #检查商品是否存在
    try :
        score_good = session.query(StoreItem).filter_by(sha1=good_sha1).one()
        comp_id = score_good.comp_id
        company = session.query(GCompany).filter_by(id = comp_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_STOREITEM_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    #商品总积分
    item_total =  int(score) * item_count

    #检查订单类型
    order_type = int(order_type)
    #订单类型 0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城
    if not order_type == 4 :
      ajax_logger.info("order_type"+str(order_type))
      result['ret'] = Status.ORDER_TYPR_ERROR
      result['info'] = Status().getReason(result['ret'])
      return result

    # 创建订单记录
    time_string = str(time.time())
    order_sha1=hashlib.sha1()
    order_sha1.update(vcard_id+str(good_sha1)+time_string)
    sha1=order_sha1.hexdigest()
    order = CustomerAccountTransaction(
                             vcard_id=vcard_id,
                             trans_type=order_type,
                             item_total=item_total,
                             status=0,
                             item_count=item_count ,
                             item_sha1=good_sha1,
                             seller_sha1="",
                             station_sha1 = "",
                             sha1 = sha1,
                             comp_id = comp_id,
                             item_name = score_good.name,
                             time = str(datetime.datetime.now()))

    session.add(order)
    try :
        session.commit()
        result['data'] = {"order_sha1":sha1}
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.CREATE_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    return result

#积分支付
def purchase_score_item(request,vcard_id,pay_password,order_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    try :
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    #查询用户信息
    try :
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证用户
    if not user.pay_password == pay_password :
        result['ret'] = Status.PASSWORDERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #检查用户积分
    if order.item_total > user.score :
        result['ret'] = Status.GOODS_SCORE_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    else :
        user.score = user.score - int(order.item_total)
    try :
        session.commit()
    except Exception,e:
        result['ret'] = Status.ALTER_USER_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #兑换完成修改订单状态
    result = purchase_complete_by_user(request,order_sha1,vcard_id)
    return result

#退款申请
def apply_refund(request,order_sha1,vcard_id,pay_password):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    #查询用户信息
    try :
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证用户
    if not user.pay_password == pay_password :
        result['ret'] = Status.PASSWORDERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    try :
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    #验证用户订单信息
    if not user.cardnum == order.vcard_id :
        result['ret'] = Status.USER_ORDER_INFO_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #检查是否已支付
    if  not order.status == 1 :
        result['ret'] = Status.HAS_NOT_PURCHASE
        result['info'] = Status().getReason(result['ret'])
        return result
    #积分兑换订单直接返还积分
    if order.trans_type == 4 :
        user.score = user.score + order.item_total
        order.status = 7
        try :
            session.commit()
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.APPLICATION_ORDER_REFUND_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        return result
    #支付订单需要先申请退款
    #检查是否已申请
    if  order.status == 5 :
        result['ret'] = Status.HAS_SUBMIT_ORDER_REFUND
        result['info'] = Status().getReason(result['ret'])
        return result
    else :
        #修改订单状态,并在退款订单表中存储一条记录
        order.status = 5
        order.application_time = str(datetime.datetime.now())
    try :
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.APPLICATION_ORDER_REFUND_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#存储out_trade_no 与订单的关联
def download_trade_no_with_order(request,order_sha1,vcard_id,out_trade_no):
    ajax_logger.info("download_trade_no_with_order:"+str(order_sha1)+str(out_trade_no))
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    try :
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    #验证订单用户信息
    if not order.vcard_id == vcard_id :
        result['ret'] = Status.USER_ORDER_INFO_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #存储关联
    order.sessionid = out_trade_no 
    try :
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.DOWNLOAD_ORDER__TRADE_INFO_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#创建充值订单
def create_recharge_order(request,vcard_id,comp_id,money):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    #用户验证
    try :
        session = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        result['data'] = []
        return result
    #验证用户账户信息
    try :
        account = session.query(CustomerCompInfo).filter_by(vcard_id = vcard_id,comp_id=comp_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QYERY_ACCOUNT_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #生成订单
    import hashlib
    sha1=hashlib.sha1()
    time = str(datetime.datetime.now())
    sha1.update(str(time)+str(vcard_id)+str(comp_id))
    sha1=sha1.hexdigest()
    order = CustomerAccountTransaction(
            vcard_id = vcard_id,
            comp_id = comp_id,
            trans_type = 0,
            item_name = "充值",
            sha1 = sha1,
            item_total = money,
            item_count = 1,
            status = 0,
            time = str(datetime.datetime.now()),
            item_sha1 = "",
            station_sha1 = "",
            seller_sha1 = "",
            worker_sha1 = "",
        )
    try :
        session.add(order)
        session.commit()
        result['data']["order_sha1"] = sha1
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data']["order_sha1"] = ""
        return result
    return result

#微信支付订单查询
def query_weixin_order_params(request,order_sha1):
    import urllib
    import urllib2
    import httplib 
    result = {}
    #方案一
    # #生成timestramp
    # import time
    # import datetime
    # a = str(datetime.datetime.now()).split(".")[0]
    # time.strptime(a,'%Y-%m-%d %H:%M:%S')
    # timestamp = time.mktime(time.strptime(a,'%Y-%m-%d %H:%M:%S'))
    # #生成sign , package
    # out_trade_no = "1439284482"
    # partner = "yePd1EMqjBHtkIrdrJs0sGtaEjtzb2l0"
    # key = "763850"
    # sign = md5_data("out_trade_no=%s&partner=%s&key=%s" %(out_trade_no ,partner ,key)).upper()
    # package = "out_trade_no=%s&partner=%s&sign=%s" %(out_trade_no ,partner ,sign)
    # #app_signature
    # appid = "wxbc8b2ea585528c56"
    # appkey = "c1902d4711c0f0b6b70ca346c40a422f"
    # string1 = "appid=%s&appkey=%s&package=%s&timestamp=%s&key=%s"%(appid ,appkey ,package ,timestamp ,key)
    # app_signature = md5_data(string1).upper()
    # try :
    #     post_data = {
    #         "appid" : appid,
    #         "package" : package,
    #         "timestamp" : timestamp,
    #         "app_signature" :app_signature,
    #         "sign_method" : "sha1"
    #     }
    #     post_data = json.dumps(post_data)
    #     url = "https://api.weixin.qq.com/pay/orderquery?access_token=UNa8cLM3STYKZCVD74tOnR23sM9nYikJUGHFoAtobxEzWo8mfnZE4CpkSrp_25DDfCYDisIHsIgRK2lq8-lOHVJMq-HVE_y3QyobeaNCXas"
    #     req = urllib2.urlopen(url, post_data)
    #     content = req.read()
    #     result = json.loads(content)
    # except Exception,e:
    #     ajax_logger.error(str(e))
    #     result['ret'] = Status.QUERY_ORDER_ERROR
    #     result['info'] = Status().getReason(rsdic['ret'])
    #     return result
    #方案二
    key = "763850"
    appid = "wxbc8b2ea585528c56"
    mch_id = "1252933401"
    out_trade_no = "1439284482"
    import random
    nonce_str = str(random.random())
    string1 = "appid=%s&mch_id=%s&nonce_str=%s&out_trade_no=%s" %(appid,mch_id,nonce_str,out_trade_no)
    sign = md5_data("stringA&key=%s"%key).upper() 
    post_data = '<xml>'
    post_data = post_data + '<appid>%s</appid>'%appid
    post_data = post_data + '<mch_id>%s</mch_id>'%mch_id
    post_data = post_data + '<nonce_str>%s</nonce_str>'%"050F62E7E481ED4D02066457BAA2653E"
    post_data = post_data + '<out_trade_no>%s</out_trade_no>'%out_trade_no
    post_data = post_data + '<sign>%s</sign>'%sign
    post_data = post_data + '</xml>'
    url = 'https://api.mch.weixin.qq.com/pay/orderquery'
    req = urllib2.Request(url=url,headers={'Content-Type':'text/xml'},data=post_data)
    response = urllib2.urlopen(req)
    res = response.read()
    return result


#意见反馈
def app_user_feedback(request,vcard_id,content):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret']) 
    session = request.get_session()
    #查询用户信息
    try :
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.USERNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result

    #检查反馈意见长度
    if check_content(content) == 1 :
      result['ret'] = Status.FEEDBACK_CONTENT_LENGTH_ERROR
      result['info'] = Status().getReason(result['ret'])
      return result

    #检查反馈意见敏感内容
    if check_content(content) == 2 :
      result['ret'] = Status.FEEDBACK_CONTENT_HAS_SENTENSIVE_ERROR
      result['info'] = Status().getReason(result['ret'])
      return result

    #存储用户反馈意见
    app_user_feedback = AppUserFeedBack(
        vcard_id = vcard_id ,
        content = content,
        time = str(datetime.datetime.now())
      )
    try :
      app_user_feedback.save()
    except Exception,e:
      result['ret'] = Status.UNKNOWNERR
      result['info'] = Status().getReason(result['ret'])
      return result
    return result
