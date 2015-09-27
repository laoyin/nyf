# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb,json,datetime,logging,hashlib,time
from django.http import *
from django.conf import settings
from django.shortcuts import render_to_response
from django.db.models import Q
from gcustomer.models import *
from gcustomer.apps.jiachebao.app_data import *
from gcustomer.apps.jiachebao.models import *
from gcustomer.apps.jiachebao.app_views import *
from gcustomer.status  import *
from gcustomer.utils import *
from gflux.apps.common.models import Station as common_station
ajax_logger=logging.getLogger('ajax')

#登录
def login(request,username,password):
    result={}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    try:
      session = request.get_session()
      user=session.query(GasWorker).filter_by(name=username).one()
      if not user.password == password :
        result['ret'] = Status.PASSWORDERROR
        result['info'] = Status().getReason(result['ret'])
        return result
      if user.user_type == 0 :
        result['ret'] = Status.WAITCHECK
        result['info'] = Status().getReason(result['ret'])
        return result
      # 更新request session参数
      request.session.set_expiry(0)
      request.session['username'] = username
      sid=request.session.session_key
      if sid is None:
        request.session.save()
        sid=request.session.session_key
      dic = {}
      dic['user_name'] = user.name
      dic['user_type'] = user.user_type
      dic['site_sha1'] = user.station_sha1
      dic['user_sha1'] = user.sha1
      dic['sessionid'] = sid
      dic['avarta_sha1'] = user.avarta_sha1
      dic['nick'] = user.nick
      result['data'] = dic
      result['ret'] = Status.LOGINSUCCESS
      result['info'] = Status().getReason(result['ret'])
    except Exception,e:
      ajax_logger.error(str(e))
      result['ret'] = Status.USERNOTEXIST
      result['info'] = Status().getReason(result['ret'])
    return result

#注册
def register(request,name,password,comp_id,site_sha1,user_type):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    session = request.get_session()
    import hashlib
    sha1 = hashlib.sha1()
    sha1.update(str(name))
    sha1.update(site_sha1)
    sha1.update(str(user_type))
    sha1 = sha1.hexdigest()
    #验证用户
    has_user = session.query(GasWorker).filter_by(name =name).first()
    if has_user :
        result['ret'] = Status.USEREXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #验证油站信息
    try :
        station = session.query(Station).filter_by(sha1 = site_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_SITE_ERROR
        result['info'] = "查询站点信息失败"
        return result
    #验证油站和公司的关系
    if not station.comp_id == comp_id :
        result['ret'] = Status.SITE_AND_COMPANY_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    else :
        user = GasWorker(
          name = name,
          user_type = 0,
          password = password,
          station_sha1 = site_sha1,
          sha1 = sha1,
          nick = ""
        )
        try:
            session.add(user)
            session.commit()
            result['ret'] = Status.OK
            result['info'] = Status().getReason(result['ret'])
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.USEREXIST
            result['info'] = "注册失败"
            return result
    return result

#登出
def logout(request,session_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result["data"] = {}
    return result

# 油站人员扫码之后，确认订单的状态
def confirm_order(request,worker_sha1,order_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    result['data']['order_info'] = {}
    result['data']['order_info']['goods_info'] = {}
    result['data']['order_info']['seller_info'] = {}
    session = request.get_session()
    try :
        worker = session.query(GasWorker).filter_by(sha1 = worker_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_WORKER_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    # 根据订单的sha1来查询订单信息
    try:
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    try :
            order.worker_sha1 = worker_sha1
            # 查询订单，按照传递参数修改订单状态
            result['data']['order_info']['order_sha1'] = order_sha1
            result['data']['order_info']['user_sha1'] = order.vcard_id
            result['data']['order_info']['item_sha1'] = order.item_sha1
            result['data']['order_info']['item_type'] = order.trans_type
            result['data']['order_info']['item_total'] = order.item_total
            result['data']['order_info']['item_count'] = order.item_count
            result['data']['order_info']['time'] = str(order.time)
            result['data']['order_info']['status'] = order.status
            if not order.station_sha1 or not order.seller_sha1 :
                order.station_sha1 = worker.station_sha1
            if not order.station_sha1 == worker.station_sha1 :
                result['ret'] = Status.HAS_NO_AUTHORITY_FOR_ORDER
                result['info'] = Status().getReason(result['ret'])
                return result
            #查询商品信息 0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城
            station_sha1 =  order.station_sha1 or order.seller_sha1
            barcode = order.item_sha1
            try :
                station = session.query(Station).filter_by(sha1 = station_sha1).one()
            except Exception,e:
                ajax_logger.error(str(e))
                result['ret'] = Status.QUERY_SITE_ERROR
                result['info'] = Status().getReason(result['ret'])
                return result
            if order.trans_type == 1 : 
                fuel_barcode = order.item_sha1
                try :
                    fuel_object = session.query(StationFuelType).filter_by(station = station.site_code,barcode = barcode).one()
                except Exception,e:
                    ajx_logger.error(str(e))
                    result['ret'] = Status.QUERY_OIL_INFORMATION_ERROR
                    result['info'] = Status().getReason(rsdic['info'])
                    result['data'] = {}
                    return result
                result['data']['order_info']['goods_info']['goods_name'] = fuel_object.description
                result['data']['order_info']['goods_info']['goods_sha1'] = order.item_sha1
                result['data']['order_info']['goods_info']['seller_sha1'] = order.station_sha1 or order.seller_sha1
                result['data']['order_info']['goods_info']['price'] = float(order.item_total)/float(order.item_count)
                result['data']['order_info']['goods_info']['src'] = ""
                result['data']['order_info']['goods_info']['img_sha1'] = ""
                
                result['data']['order_info']['seller_info']['name'] = station.name
                result['data']['order_info']['seller_info']['sha1'] = station.sha1
                result['data']['order_info']['seller_info']['address'] = station.address
                result['data']['order_info']['seller_info']['geo_x'] = station.geo_x
                result['data']['order_info']['seller_info']['geo_y'] = station.geo_y
                result['data']['order_info']['seller_info']['phone'] = station.site_tel
                result['data']['order_info']['seller_info']['img_sha1'] = station.img_sha1 or ""
                result['data']['order_info']['seller_info']['score'] = 0
                result['data']['order_info']['seller_info']['introduction'] = ""
            elif order.trans_type == 2 or order.trans_type == 4 :
                try :
                    store_good = session.query(StoreItem).filter_by(sha1 = order.item_sha1).one()
                except Exception,e:
                    ajx_logger.error(str(e))
                    result['ret'] = Status.QUERY_STOREITEM_ERROR
                    result['info'] = Status().getReason(rsdic['info'])
                    result['data'] = {}
                    return result
                result['data']['order_info']['goods_info']['goods_name'] = store_good.name
                result['data']['order_info']['goods_info']['goods_sha1'] = order.sha1
                result['data']['order_info']['goods_info']['seller_sha1'] = order.station_sha1 or order.seller_sha1
                result['data']['order_info']['goods_info']['price'] = float(order.item_total)/float(order.item_count)
                result['data']['order_info']['goods_info']['src'] = "/gcustomer/ajax/render_image/"
                result['data']['order_info']['goods_info']['img_sha1'] = store_good.img_sha1 or ""

                result['data']['order_info']['seller_info']['name'] = station.name
                result['data']['order_info']['seller_info']['sha1'] = station.sha1
                result['data']['order_info']['seller_info']['address'] = station.address
                result['data']['order_info']['seller_info']['geo_x'] = station.geo_x
                result['data']['order_info']['seller_info']['geo_y'] = station.geo_y
                result['data']['order_info']['seller_info']['phone'] = station.site_tel
                result['data']['order_info']['seller_info']['img_sha1'] = station.img_sha1 or ""
                result['data']['order_info']['seller_info']['score'] = 0
                result['data']['order_info']['seller_info']['introduction'] = ""
            elif order.trans_type == 3 :
                try :
                    service = session.query(ServiceInformation).filter_by(sha1 = order.item_sha1).one()
                except Exception,e:
                    ajax_logger.error(str(e))
                    result['ret'] = Status.QUERY_SERVICE_INFORMATION_ERROR
                    result['info']  = Status().getReason(result['ret'])
                    return result
                result['data']['order_info']['goods_info']['goods_name'] = service.title
                result['data']['order_info']['goods_info']['goods_sha1'] = order.sha1
                result['data']['order_info']['goods_info']['seller_sha1'] =  service.seller_sha1 or ''
                result['data']['order_info']['goods_info']['price'] = float(order.item_total)/float(order.item_count)
                result['data']['order_info']['goods_info']['src'] = "/gcustomer/ajax/render_image/"
                result['data']['order_info']['goods_info']['img_sha1'] = service.img_sha1

                if not service.seller_sha1 :
                    result['data']['order_info']['seller_info']['name'] = ''
                    result['data']['order_info']['seller_info']['sha1'] = ''
                    result['data']['order_info']['seller_info']['address'] = ''
                    result['data']['order_info']['seller_info']['geo_x'] = ''
                    result['data']['order_info']['seller_info']['geo_y'] = ''
                    result['data']['order_info']['seller_info']['phone'] = ''
                    result['data']['order_info']['seller_info']['img_sha1'] = ''
                    result['data']['order_info']['seller_info']['score'] = ''
                    result['data']['order_info']['seller_info']['introduction'] = ''
                else :
                    try :
                        seller = session.query(seller).filter_by(sha1 = service.seller_sha1).one()
                        result['data']['order_info']['seller_info']['name'] = station.name
                        result['data']['order_info']['seller_info']['sha1'] = seller.sha1 or ''
                        result['data']['order_info']['seller_info']['address'] = seller.address
                        result['data']['order_info']['seller_info']['geo_x'] = seller.geo_x
                        result['data']['order_info']['seller_info']['geo_y'] = seller.geo_y
                        result['data']['order_info']['seller_info']['phone'] = seller.phone
                        result['data']['order_info']['seller_info']['img_sha1'] = station.img_sha1
                        result['data']['order_info']['seller_info']['score'] = seller.score
                        result['data']['order_info']['seller_info']['introduction'] = seller.introduction
                    except Exception,e:
                        result['data']['order_info']['seller_info']['name'] = ''
                        result['data']['order_info']['seller_info']['sha1'] = ''
                        result['data']['order_info']['seller_info']['address'] = ''
                        result['data']['order_info']['seller_info']['geo_x'] = ''
                        result['data']['order_info']['seller_info']['geo_y'] = ''
                        result['data']['order_info']['seller_info']['phone'] = ''
                        result['data']['order_info']['seller_info']['img_sha1'] = ''
                        result['data']['order_info']['seller_info']['score'] = ''
                        result['data']['order_info']['seller_info']['introduction'] = ''
            else :
                result['ret'] = Status.ORDER_TYPR_ERROR
                result['info'] = Status().getReason(result['ret'])
                return result
            try :
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                result['ret'] = Status.UPDATE_ORDER_ERROR
                result['info'] = Status().getReason(result['ret'])
                return result
    except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.QUERY_ORDER_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
    return result

# 油站人员确认订单的状态之后，点击完成交易
def purchase_complete(request,order_id,seller_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    # 根据订单的id来查询订单信息
    try:
        order = WheelTransaction.objects.get(sha1=order_id)
        jiayouyuan = GasWorker.objects.filter(sha1 = order.jiayouyuan_sha1).first()
        if not jiayouyuan :
            result['ret'] = Status.UNKNOWNERR
            result['info'] = "查询订单加油员信息失败"
            return result
        if jiayouyuan.station_sha1 :
            order.seller_sha1 = jiayouyuan.station_sha1
        else :
            result['ret'] = Status.UNKNOWNERR
            result['info'] = "修改订单信息失败"
            return result
        #修改用户积分
        if not order.order_type == 1 :
            if not alter_user_score(request,order) :
                result['ret'] = Status.UNKNOWNERR
                result['info'] = "修改用户积分失败"
                return result
        # 更改商品库存
        if order.promotion_id != -1:
             try:
                # 如果该用户是卡号用户，检查促销活动信息
                user = CustomerAccount.objects.get(sha1 = order.user_sha1)

                if user.cardnum != "" :
                    session=request.get_session()
                    promotion_info = session.query(Promotion).filter_by(id=order.promotion_id).one()
                    # 更新user action的信息
                    action_time = datetime.datetime.now()
                    action_object = UserAction(user_source=promotion_info.user_source,
                                        cardnum=user.cardnum,
                                        obj_type=0,
                                        obj_id=order.promotion_id,
                                        action=1,
                                        action_time=action_time)
                    session.add(action_object)
                    session.commit()

                    # 如果是营销活动，需要记录修改参与人数
                    res_obj=session.query(PromotionEffect).filter_by(promotion_id=order.promotion_id).one()
                    res_obj.nb_participates = res_obj.nb_participates + 1
                    try:
                        participates = json.loads(res_obj.user_participates)
                    except Exception,e:
                        participates = []
                    res_obj.total_fuel_purchase = res_obj.total_fuel_purchase + int(order.item_total)
                    participates.append(user.cardnum)
                    res_obj.user_participates = json.dumps(participates)
                    session.commit()
             except Exception,e:
                pass
        #修改订单状态
        order.status = 2
        order.save()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
    return result

#获取油站的交易流水线
def get_site_trades(request,site_sha1,start,end,status):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    # 查询当前油站的所有订单
    try :
        session = request.get_session()
        order_list = session.query(CustomerAccountTransaction).filter(CustomerAccountTransaction.station_sha1==site_sha1,CustomerAccountTransaction.status==status,CustomerAccountTransaction.trans_type>0).order_by("time desc").all()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    result['data']['has_next'] = "true"
    if len(order_list) <= int(end) - int(start):
        result['data']['has_next'] = "false"
    order_info_list = []
    for order in order_list[start:end]:
        dic = {}
        try :
            img_sha1 = session.query(StoreItem).filter_by(sha1 = order.item_sha1).one().img_sha1
        except:
            img_sha1 = ''

        #交易号
        dic['order_id'] = order.sha1

        #交易类型
        dic['item_type'] = order.trans_type

        #交易金额
        dic['item_total'] = order.item_total

        #交易数量
        dic['item_count'] = order.item_count

        #商品名字
        dic['item_name'] = order.item_name or ''

        #订单状态
        dic['status'] = order.status

        #商品图片
        dic['src'] = "/gcustomer/ajax/render_image/"
        dic['img_sha1'] = img_sha1 or ''
        order_info_list.append(dic)

    result['data']['order_list'] = order_info_list
    return result

#获取油站的交易流水详情
def get_site_trade_details(request,order_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    try:
        session = request.get_session()
        order = session.query(CustomerAccountTransaction).filter_by(sha1=order_id).one()
        result['data']['pay'] = float('%0.2f'%(order.item_total/order.item_count))
        result['data']['pump_id'] = order.pump_id or 0
        result['data']['time'] = order.time.strftime('%Y-%m-%d %H:%M')
        result['data']['card_num'] = order.vcard_id or ''

    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
    finally:
        return result


#获取某个加油员的订单列表
def get_trades_by_worker(request,jiayouyuan_sha1,start,end):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    # 查询当前油站的所有订单
    try :
        order_list = WheelTransaction.objects.filter(jiayouyuan_sha1=jiayouyuan_sha1,status = 2).order_by("-time").all()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    order_info_list = []
    for order in order_list:
        dic = {}
        dic['order_id'] = order.sha1
        dic['user_sha1'] = order.user_sha1
        #查询商品信息
        if order.order_type == 0 or order.order_type == 1 :
            goods_obejct = get_goods_info(request,order.item_sha1)
        elif order.order_type == 2 :
            goods_obejct = get_fuel_info(request,order.item_sha1)
        elif order.order_type == 3 :
            goods_obejct = get_services_info(request,order.item_sha1)
        dic['goods_info'] = goods_obejct
        # 查询订单商家信息
        seller_object = get_seller_info(request,order.seller_sha1)
        dic['seller_info'] = seller_object
        dic['item_sha1'] = order.item_sha1
        dic['item_type'] = order.item_type
        dic['item_total'] = order.item_total
        dic['item_count'] = order.item_count
        dic['time'] = order.time.strftime('%Y-%m-%d %H:%M')
        dic['status'] = order.status
        order_info_list.append(dic)

    result['data'] = {"order_list":order_info_list}
    return result

#订单完成
def confirm_recorded(request,worker_sha1,order_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    try :
        session = request.get_session()
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_id).first()
        if not order :
            result['ret'] = Status.UNKNOWNERR
            result['info'] = "查询订单失败!"
            return result
        order.status = 3
        try :
            session.commit()
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.UNKNOWNERR
            result['info'] = "更改订单状态失败!"
            return result
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(rsdic['ret'])
        return result
    return result

#收银员注册选择公司和油站信息
def worker_register_init_info(request):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] ={}
    result['data']['comp_list'] = []
    try :
        comp_list = get_company_info()
        for comp in comp_list :
            station_list = get_company_station_list(comp['comp_id'])
            result['data']['comp_list'].append(dict(
                    comp_id = comp['comp_id'],
                    comp_name = comp['comp_name'],
                    station_list = station_list
                ))
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_COMP_INFO_ERROR
        result['info'] = Status().getReason(rsdic['ret'])
        result['data'] = {}
        return result
    return result

def get_oil_order_init_info(request,station_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    result['data']['pump_ids'] = []
    result['data']['fuel_list'] = []
    try :
            session = request.get_session()
            station = session.query(Station).filter_by(sha1 = station_sha1).one()
            site_code = station.site_code
            fuel_list = get_fuel_type(request,site_code)
            for fuel in fuel_list :
                result['data']['fuel_list'].append(dict(
                        barcode = fuel['barcode'],
                        fuel_name = fuel['name'],
                        price = fuel['price']
                    ))
            #common_station = session.query(common_station).filter_by(name = site_code).one()
            #result['id_guns'] = json.loads(common_station.id_guns)
            result['data']['pump_ids'] = [1,2,3,4]
    except Exception,e:
            result['ret'] = Status.QUERY_SITE_ERROR
            result['info'] = Status().getReason(result['ret'])
            result['data'] = {}
            return result
    return result


#收银员生成油品订单
def create_order_by_worker(request,worker_sha1,item_sha1,trans_type,price,pay,pump_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    try :
        session = request.get_session()
        worker = session.query(GasWorker).filter_by(sha1 = worker_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.GasWorkerNOTEXIST
        result['info'] = Status().getReason(result['ret'])
        return result
    #user_type 1:加油员 2:收银员
    if not worker.user_type == 2 :
        result['ret'] = Status.USER_ID_CARD_CHECK_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    try :
        station_sha1 = worker.station_sha1
        station = session.query(Station).filter_by(sha1 = station_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_SITE_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #驾车宝账户确认订单时获取该信息
    vcard_id = ""
    comp_id = station.comp_id
    order_sha1 = hashlib.sha1()
    time = datetime.datetime.now()
    sha1_string = str(vcard_id) + str(comp_id) + str(time)
    order_sha1.update(sha1_string)
    sha1 = order_sha1.hexdigest()
    #交易类型  0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城
    #如果是油品 item_sha1为油品的barcode,其它的, item_sha1为商品的sha1
    if trans_type == 1 :
        try :
            item_name = session.query(StationFuelType).filter_by(station=station.site_code,\
                barcode=item_sha1).one().description
            order = CustomerAccountTransaction(
                vcard_id = "",
                comp_id = comp_id,
                trans_type = trans_type,
                station_sha1 = station_sha1,
                item_sha1 = item_sha1,
                item_name = item_name,
                item_count = round(float(pay)/float(price),2),
                sha1 = sha1 ,
                seller_sha1 = "",
                worker_sha1 = worker_sha1,
                item_total = pay,
                pump_id = pump_id,
                status = 0
            )
            session.add(order)
            try :
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                result['ret'] =  Status.CREATE_ORDER_ERROR
                result['info'] = Status().getReason(result['ret'])
                return result
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] =  Status.QUERY_OIL_INFORMATION_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
    else :
        result['ret'] = Status.TRANS_TYPE_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    try :
        result['data']['order_sha1'] = sha1
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.CREATE_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
    return result

#收银员确认订单
def confirm_order_by_worker(request,order_sha1):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result['data'] = {}
    result['data']['order_info'] = {}
    result['data']['order_info']['fuel_info'] = {}
    try :
        session = request.get_session()
        order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QUERY_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        result['data'] = {}
        return result
    try :
        result['data']['order_info']['order_total'] = order.item_total
        result['data']['order_info']['time'] = str(order.time)
        result['data']['order_info']['gun_id'] = order.pump_id or ""
        #查询商品信息
        station_sha1 =  order.station_sha1 or ""
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


#收银员取消订单
def delete_order_by_work(request,order_sha1):
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
    try :
        session.delete(order)
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.DELETE_ORDER_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#检查订单是否已支付
def check_has_purchase_worker(request,order_sha1):
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
    if  order.status == 1 :
        return result
    else :
        result['ret'] = Status.ORDER_HAS_NOT_PURCHASE
        result['info'] = Status().getReason(result['ret'])
        return result


#确认油品已交易,打印小票
def purchase_complete_worker(request,order_sha1):
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
    try :
        if order.status == 2 :
            result['ret'] = Status.ORDER_HAS_COMPLETE
            result['info'] = Status().getReason(result['ret'])
            return result
        else :
            order.status = 2
            session.commit()
    except Exception,e:
        result['ret'] = Status.ALTER_ORDER_STATUS_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#确认预订商品是否可以支付购买
def confirm_reservation_by_worker(request,order_sha1,status):
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
    try :
            order.status = status
            session.commit()
    except Exception,e:
        result['ret'] = Status.ALTER_ORDER_STATUS_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

