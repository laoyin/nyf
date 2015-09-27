# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb,json,datetime,logging
from django.http import *
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.shortcuts import render_to_response
from django.core.management import call_command
from django.core.cache import cache
from django.utils import timezone
from gcustomer.models import *
from gcustomer.apps.jiachebao.models import *
from gflux.apps.station.models import FuelTypeRelation
from gflux.apps.common.models import Station
from gflux.util import *
import re, time, hashlib
from gcustomer.utils import *
from gcustomer.apps.gcustomer.cache_views import *
from gcustomer.status import *

ajax_logger=logging.getLogger('ajax')

#取得单个聚合信息
#输入:用户群id
#输出:用户群的聚合信息
def get_group_info(request):
    rsdic = {}
    rsdic['ret']=Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    try:
        #get args
        group_id=int(request.GET['group_id'])
        #get obj
        obj=session.query(TargetAudience).filter_by(comp_id=comp_id,id=group_id).one()
        rsdic['users']=json.loads(obj.user_list)
        rsdic['items']=json.loads(obj.favourite_products)
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#创建用户群
#输入: 用户群参数
#输出: 创建状态
def create_group(request):
    rsdic={}
    rsdic['ret']=Status.OK
    rsdic['info']='创建群成功'
    session = request.get_session()
    user = get_current_user(request)
    source_id= user.id
    comp_id = user.comp_id
    #用户群基本属性
    group_name=request.GET['group_name']
    location=request.GET['group_location']
    description=request.GET['description']
    #用户基本属性
    career=request.GET['career']
    gender=request.GET['gender']
    from_age=int(request.GET['from_age'])
    to_age=int(request.GET['to_age'])
    #用户行为特征
    prefer_cost = request.GET['prefer_cost_map']
    prefer_time = request.GET['prefer_time_map']
    prefer_pump_type = request.GET['prefer_pump_type_map']
    prefer_fuel_cost = request.GET['prefer_fuel_cost_map']
    prefer_nonfuel_cost = request.GET['prefer_nonfuel_cost_map']
    pump_timeout = request.GET['pump_timeout']
    favourite_nonfuel_products = request.GET['favourite_nonfuel_products']
    try:
        
        #检查用户群属性,防止创建两个完全相同的用户群
        if check_target_audience(
                comp_id = comp_id,
                group_location = location,
                career = career,
                gender = gender,
                from_age = int(from_age),
                to_age = int(to_age),
                prefer_cost_map = prefer_cost,
                prefer_time_map = prefer_time,
                prefer_pump_type_map = prefer_pump_type,
                prefer_fuel_cost_map = prefer_fuel_cost,
                pump_timeout = pump_timeout,
                prefer_nonfuel_cost_map = prefer_nonfuel_cost,
                favourite_nonfuel_products = favourite_nonfuel_products
                ) == False :
            rsdic['ret'] = Status.HAS_CREATE_SAME_TARGET_AUDIENCE
            rsdic['info'] = Status().getReason(rsdic['ret'])
            return HttpResponse(json.dumps(rsdic))

        import hashlib,datetime
        create_time = datetime.datetime.now()
        sha1 = hashlib.sha1()
        sha1.update(str(create_time))
        sha1.update(str(comp_id))
        sha1.update(str(group_name))
        sha1 = sha1.hexdigest()
        try :
            session.query(TargetAudience).filter_by(group_name=group_name,comp_id=comp_id).one()
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "客户群名称重复,创建失败!"
            return HttpResponse(json.dumps(rsdic))
        except :
                if gender == '':
                    #用户群不限制年龄
                    gender = -1
                obj = TargetAudience(
                    source_id=source_id,
                    group_name=group_name,
                    location=location,
                    description=description,
                    career=career,
                    gender=int(gender),
                    from_age=from_age,
                    to_age=to_age,
                    prefer_cost = prefer_cost,
                    prefer_time = prefer_time,
                    prefer_pump_type = prefer_pump_type,
                    prefer_fuel_cost = prefer_fuel_cost,
                    pump_timeout = pump_timeout,
                    prefer_nonfuel_cost = prefer_nonfuel_cost,
                    comp_id = comp_id,
                    time = create_time,
                    sha1 = sha1,
                    favourite_products = favourite_nonfuel_products
                    )
                try:
                    #根据群属性聚合出客户列表
                    obj.user_list = cal_user_list_with_group_attribute(dict(
                        comp_id = obj.comp_id,
                        group_location = obj.location,
                        career = obj.career,
                        gender = obj.gender,
                        from_age = int(obj.from_age),
                        to_age = int(obj.to_age),
                        prefer_cost_map = obj.prefer_cost,
                        prefer_time_map = obj.prefer_time,
                        prefer_pump_type_map = obj.prefer_pump_type,
                        prefer_fuel_cost_map = obj.prefer_fuel_cost,
                        pump_timeout = obj.pump_timeout,
                        prefer_nonfuel_cost_map = obj.prefer_nonfuel_cost,
                        favourite_products = obj.favourite_products
                    ))
                except Exception,e:
                    rsdic['ret'] = Status.CAL_TARGET_AUDIENCE_USERLIST_ERROR
                    rsdic['info']= Status().getReason(rsdic['ret'])
                    return HttpResponse(json.dumps(rsdic))
                try :
                    if not json.loads(obj.user_list) :
                         rsdic['ret'] = Status.UNKNOWNERR
                         rsdic['info']="该类型用户群用户为空,无法创建!"
                         return HttpResponse(json.dumps(rsdic))
                    else :
                        session.add(obj)
                        session.commit()
                except Exception,e:
                    session.rollback()
                    ajax_logger.error(str(e))
                    rsdic['ret'] = Status.CREATE_TARGET_AUDIENCE_ERROR
                    rsdic['info']= Status().getReason(rsdic['info'])
                    return HttpResponse(json.dumps(rsdic))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret']=Status.CREATE_TARGET_AUDIENCE_ERROR
        rsdic['info']= Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#查询用户群信息
#输入:用户群关键字,起始索引,结尾索引
#输出:用户群详情
def get_customer_group_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['objs'] = []
    group_name = request.GET['customer_group_name']
    startIndex = int(request.GET['startIndex'])
    endIndex = int(request.GET['endIndex'])
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        objs = session.query(TargetAudience).filter_by(comp_id=comp_id).all()
        search_objs = []
        try :
            for obj in objs :
                #关键字在用户名中
                if str(group_name) in obj.group_name:
                    search_objs.append(obj)
                else :
                    continue
        except Exception,e:
            ajax_logger.error(str(e))
            print e
        rsdic['length'] = len(search_objs)
        for obj in search_objs[startIndex:endIndex] :
                try:
                    group_creator_name = session.query(GCustomerUser).filter_by(comp_id=comp_id,id = obj.source_id).one().name
                except :
                    group_creator_name = "系统创建"
                rsdic["objs"].append(dict(
                    group_id = obj.id,
                    group_name = obj.group_name,
                    group_location = obj.location,
                    gender = obj.gender,
                    from_age = obj.from_age,
                    to_age = obj.to_age,
                    career = obj.career,
                    prefer_cost_map = obj.prefer_cost,
                    prefer_time_map = obj.prefer_time,
                    prefer_pump_type_map = obj.prefer_pump_type,
                    prefer_fuel_cost_map = obj.prefer_fuel_cost,
                    prefer_nonfuel_cost_map = obj.prefer_nonfuel_cost,
                    pump_timeout = obj.pump_timeout,
                    group_creator_name = group_creator_name,
                    description = obj.description,
                    user_list = json.loads(obj.user_list)
                ))
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.QUERY_TARGETAUDIENCE_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取单个客户群详细信息
#输入:单个客户群id
#输出:单个客户群详情
def get_customer_group_detail(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['obj'] = []
    group_id = request.GET['group_id']
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        obj = session.query(TargetAudience).filter_by(id=group_id).one()
        try:
            group_location = session.query(DimChinaProvinceCityDistrict).filter_by(id = obj.location).one().name
        except :
            group_location = "无"
        try :
            favourite_nonfuel_products = ""
            pos_id_list = json.loads(obj.favourite_products)
            for pos_id in pos_id_list :
                try :
                    good = session.query(StoreItem).filter_by(comp_id=comp_id,pos_id=pos_id).one()
                except Exception,e:
                    ajax_logger.error(str(e))
                    continue
                favourite_nonfuel_products = favourite_nonfuel_products + good.name + ";"
        except Exception,e:
            ajax_logger.error(str(e))
            favourite_nonfuel_products = ''
        rsdic["obj"].append(dict(
                id = obj.id,
                group_name = obj.group_name,
                group_location = group_location,
                gender = obj.gender,
                from_age = obj.from_age,
                to_age = obj.to_age,
                career = obj.career,
                prefer_cost_map = obj.prefer_cost,
                prefer_time_map = obj.prefer_time,
                prefer_pump_type_map = obj.prefer_pump_type,
                prefer_fuel_cost_map = obj.prefer_fuel_cost,
                prefer_nonfuel_cost_map = obj.prefer_nonfuel_cost,
                pump_timeout = obj.pump_timeout,
                description = obj.description,
                user_list = json.loads(obj.user_list),
                favourite_nonfuel_products = favourite_nonfuel_products
            ))
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))



#我的油站数据读取
#输入：用户id
#输出：用户油站基本信息
def my_station(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['objs'] = []
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        objs = session.query(Station).filter_by(comp_id=comp_id).all()
        for obj in objs:
            rsdic['objs'].append(dict(
                name =obj.name,
                address = obj.address,
                site_tel = obj.site_tel
                ))
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))



#删除客户群
#输入:单个客户群id
#输出:删除状态
def delete_customer_group(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    group_id = request.GET['group_id']
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    #检查用户是否为管理员用户
    try :
        gcompany_membership = session.query(GCompanyMembership).filter_by(comp_id=comp_id,
            user_id=user.id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.QUERY_USER_COMP_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    if not gcompany_membership.role == 2 :
        rsdic['ret'] = Status.HAS_NO_ACCESS
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    try:
        session.query(TargetAudience).filter_by(comp_id=comp_id,id=group_id).delete()
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.DELETE_TARGETAUDIENCE_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    finally :
        return HttpResponse(json.dumps(rsdic))

#取得用户画像
#输入: 用户类型,用户卡号
#输出: 用户画像
def get_user_profile(request):
    rsdic = {}
    rsdic['ret']=Status.OK
    user = get_current_user(request)
    comp_id = user.comp_id 
    try:
        cardnum=request.GET['cardnum']
        session=request.get_session()
        obj=session.query(CustomerProfile).filter_by(vcard_id=cardnum).one()
        rsdic['id']=obj.id
        rsdic['area_type'] = obj.area_type
        try:
            # 0:油站 1:行政区划
            if obj.area_type == 1:
                profiling_area = session.query(DimChinaProvinceCityDistrict).filter_by(id = int(obj.profiling_area)).one().name
                rsdic['profiling_area'] = profiling_area
            elif obj.area_type == 0:
                profiling_area = session.query(StationProfile).filter_by(comp_id = comp_id,site_code=obj.profiling_area).one().site_code
                rsdic['profiling_area'] = profiling_area
            else :
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = '用户所属油站或行政区划错误'
                ajax_logger.error(str(rsdic['info']))
                return HttpResponse(json.dumps(rsdic))
        except Exception,e :
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = '查询用户所属油站或行政区划失败'
            return HttpResponse(json.dumps(rsdic))
        rsdic['cardnum']=int(obj.vcard_id)
        rsdic['prefer_time']=obj.prefer_time
        rsdic['prefer_pump_type']=obj.prefer_pump_type
        rsdic['prefer_fuel_cost']=obj.prefer_fuel_cost
        rsdic['prefer_nonfuel_cost']=obj.prefer_nonfuel_cost
        try:
            rsdic['fuel_products']=json.loads(obj.fuel_products)
        except Exception,e:
            rsdic['fuel_products']=[]
        #用户最喜爱的非油品
        try:
            try :
                favourite_nonfuel_products=json.loads(obj.favourite_nonfuel_products)
            except :
                favourite_nonfuel_products = []
            oil_card_fav_nonfuel_list = get_profile_from_oil_card(request,cardnum,"favourite_nonfuel_products")
            favourite_nonfuel_products.extend(oil_card_fav_nonfuel_list)
            favourite_nonfuel_products = list(set(favourite_nonfuel_products))
            rsdic['favourite_nonfuel_products'] = []
            obj.favourite_nonfuel_products = json.dumps(favourite_nonfuel_products)
            for product_id in favourite_nonfuel_products :
                try:
                    product_name = session.query(StoreItem).filter_by(comp_id = comp_id,pos_id = product_id).one().name
                    rsdic['favourite_nonfuel_products'].append(product_name)
                except :
                    try :
                        session.query(StoreItem).filter_by(comp_id = comp_id ,name = product_id).one()
                        rsdic['favourite_nonfuel_products'].append(product_id)
                    except :
                        pass
        except Exception,e:
            rsdic['favourite_nonfuel_products']=[]
        #推荐用户购买的非油品
        try:
            try :
                recommended_nonfuel_products = json.loads(obj.recommended_nonfuel_products)
            except Exception ,e:
                recommended_nonfuel_products = []
            oil_card_rec_nonfuel_list = get_profile_from_oil_card(request,cardnum,"recommended_nonfuel_products")
            recommended_nonfuel_products.extend(oil_card_rec_nonfuel_list)
            recommended_nonfuel_products = list(set(recommended_nonfuel_products))
            obj.recommended_nonfuel_products = json.dumps(recommended_nonfuel_products)
            rsdic['recommended_nonfuel_products']= []
            for product_id in recommended_nonfuel_products:
                try :
                    product_name = session.query(StoreItem).filter_by(comp_id = comp_id,pos_id = product_id).one().name
                    rsdic['recommended_nonfuel_products'].append(product_name)
                except :
                    try :
                        session.query(StoreItem).filter_by(comp_id = comp_id,name = product_id).one()
                        rsdic['recommended_nonfuel_products'].append(product_id)
                    except :
                        pass
        except Exception,e:
            rsdic['recommended_nonfuel_products']=[]
        try:
            rsdic['grouped']=json.loads(obj.grouped)
        except Exception,e:
            rsdic['grouped']=[]
        rsdic['avg_charge_period']=obj.avg_charge_period
        rsdic['efficiency']=obj.efficiency,
        rsdic['prominence']=obj.prominence,
        rsdic['total_fuel_amount']=obj.total_fuel_amount,
        rsdic['total_purchase_amount']=obj.total_purchase_amount,
        rsdic['total_nonfuel_purchase_amount']=obj.total_nonfuel_purchase_amount,
        rsdic['best_promotion_mode']=obj.best_promotion_mode
        try :
            session.commit()
        except Exception,e:
            ajax_logger.error(str(e))
            rsdic['ret']=Status.UNKNOWNERR
            rsdic['info']= '存储用户画像结果失败'
    except Exception,e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.USERNOTEXIST
        rsdic['info']= Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic))

#取得加油站用户分组
#输入: 用户类型
#输出: 用户群组聚合信息,最喜爱的商品
def get_user_group(request):
    rsdic = {}
    rsdic['ret']=Status.OK
    try:
        user_source=int(request.GET['user_source'])
        s=request.get_session()
        objs=s.query(TargetAudience).filter_by(user_source=user_source)
        all_group=[]
        for obj in objs:
            all_group.append({
                'users':json.loads(obj.user_list),
                'items':json.loads(obj.favourite_products)
            })
        rsdic['groups']=all_group
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#新建大客户
#输入:用户名,大客户参数
#输出:创建状态
def create_big_customer(request):
    rsdic = {}
    rsdic['ret']=Status.OK
    username = request.session.get('username',None)
    #用户名不存在
    if not username :
        rsdic['ret'] = status.UNKNOWNERR
        rsdic['info'] = status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    else :
        user = get_current_user(request)
        source_id= user.id
        customer_cardnum = request.GET['customer_cardnum']
        customer_name = request.GET['customer_name']
        customer_type = request.GET['customer_type']
        slave_card_nb = request.GET['slave_card_nb']
        session = request.get_session()
        try:
            obj = BigCustomerProfile(
                    user_source = int(customer_type),
                    source_id = source_id,
                    master_cardnum = customer_cardnum,
                    name = customer_name,
                    nb_slave_cards = slave_card_nb
                )
            session.add(obj)
            session.commit()
        except Exception,e :
            ajax_logger.error(str(e))
            rsdic['ret']=Status.UNKNOWNERR
            rsdic['info']=Status().getReason(rsdic['ret'])
            return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取用户类型
def get_user_source_name(customer_type):
    if customer_type == "1" :
        return "中石油"
    elif customer_type == "2" :
        return "中石化"
    elif customer_type == "3" :
        return "中海油"
    elif customer_type == "4" :
        return "壳牌"
    elif customer_type == "5" :
        return "中化"
    else :
        ajax_logger.error(customer_type)
        return ""

#获取大客户信息
#输入: 大客户卡号
#输出:  大客户信息
def big_customer_manage(request):
    rsdic = {}
    rsdic['ret']=Status.OK
    try:
        #get args
        user = get_current_user(request)
        source_id= user.id
        cardnum=int(request.GET['cardnum'])
        #get obj
        session = request.get_session()
        obj=session.query(BigCustomerProfile).filter_by(master_cardnum=cardnum).one()
        rsdic['user_source']=obj.user_source
        rsdic['source_id']=obj.source_id
        rsdic['master_cardnum']=str(obj.master_cardnum)
        rsdic['create_time']=str(obj.create_time).split(".")[0]
        rsdic['name']=obj.name
        rsdic['prepaid_amount']=obj.prepaid_amount
        rsdic['current_balance']=obj.current_balance
        rsdic['nb_slave_cards']=obj.nb_slave_cards
        rsdic['contribution']=obj.contribution
        rsdic['score']=obj.score
        rsdic['score_rank']=obj.score_rank
        # rsdic['pump_range']=obj.pump_range
        rsdic['pump_range']= '暂无'
        rsdic['last_month_sale']=obj.last_month_sale
        slaveObj = session.query(CustomerRelation).filter_by(master_cardnum=obj.master_cardnum).all()
        rsdic['slaveObj']=[]
        for  row in slaveObj:
            try :
                    slaveItem=session.query(CustomerProfile).filter_by(cardnum=int(row.slave_cardnum)).one()
            except :
                    continue
            obj = {}
            obj['cardnum'] = str(slaveItem.cardnum)
            obj['user_name'] = slaveItem.user_name
            obj['curr_balance'] = str(slaveItem.curr_balance)
            rsdic['slaveObj'].append(obj)

    except Exception, e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#更新活动状态
#输入: 无
#输出: 更新状态
def update_activity_status(request) :
    rsdic = {}
    rsdic['ret'] = Status.OK
    try :
        s=request.get_session()
        objs=s.query(Promotion).all()
        for obj in objs :
            #0:活动状态已完成 1:活动进行中
            if obj.status == 0 :
                continue
            else :
                start_time=stringToTimeStamp(str(obj.start_time))
                end_time=stringToTimeStamp(str(obj.end_time))
                now_time=stringToTimeStamp(str(datetime.datetime.now()).split(".")[0])
                if now_time >= end_time :
                    s.query(Promotion).filter_by(id = obj.id).update({"status":0})
                    s.commit()
                elif start_time <=now_time and now_time < end_time :
                    s.query(Promotion).filter_by(id = obj.id).update({"status":1})
                    s.commit()
                else :
                    pass
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "更新活动状态失败"
    return HttpResponse(json.dumps(rsdic))

#获取活动列表
#输入: 无
#输出:  当前正在进行的活动列表
def show_activity(request):
    rsdic={}
    rsdic['ret']=Status.OK
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        #当前时间
        now_time=datetime.datetime.now()
        #get obj
        s=request.get_session()
        obj=s.query(Promotion).filter_by(comp_id=comp_id).order_by('start_time').all()
        obj.reverse()
        rsdic['obj']=[]
        for row in obj:
            if row.status == 1 :
                duration_time=stringToTimeStamp(str(now_time).split('.')[0])-stringToTimeStamp(str(row.start_time).split('.')[0])
                remain=stringToTimeStamp(str(row.end_time))-stringToTimeStamp(str(now_time).split('.')[0])
                schedule=float(duration_time)/float((duration_time+remain))
                participants=s.query(PromotionEffect).filter_by(promotion_id=row.id).first()
                obj = {}
                obj['id'] = row.id
                obj['name'] = row.name
                obj['start_time'] = str(row.start_time)
                obj['end_time'] = str(row.end_time)
                obj['activity_duration'] = duration_time
                if participants :
                    obj['participant_amount'] = str(participants.nb_participates)
                else :
                    obj['participant_amount'] = ""
                obj['total_fuel_purchase'] = participants.total_fuel_purchase 
                obj['activity_schedule'] = schedule
                obj['activity_remain'] = remain
                rsdic['obj'].append(obj)
            else :
                continue
    except Exception,e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取已完成活动列表
#输入: 无
#输出: 当前已完成活动列表
def completed_activity(request):
    rsdic={}
    rsdic['ret']=Status.OK
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        #get obj
        s=request.get_session()
        obj=s.query(Promotion).filter_by(comp_id=comp_id).all()
        rsdic['obj']=[]
        for row in obj:
            if not row.status:
                rsdic['obj'].append(dict(name=row.name))
            else :
                continue
    except Exception,e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取广告列表
#输入: 无
#输出:  广告列表
def get_advertisement_list(request):
    rsdic={}
    rsdic['ret']=Status.OK
    rsdic['obj']=[]
    try:
        s=request.get_session()
        user = get_current_user(request)
        comp_id = user.comp_id
        adv_list=s.query(Advertisement).filter_by(comp_id = comp_id).all()
        for row in adv_list:
            rsdic['obj'].append(dict(
                sha1=row.sha1,
                comp_id=row.comp_id,
                source_id=row.source_id,
                type=row.type,
                name=row.name,
                title = row.title,
                abstract=row.abstract,
                image_name = row.image_sha1
                ))
    except Exception, e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取广告统计信息
#输入: 无
#输出:  当前广告统计信息
def get_advertisement_information(request):
    rsdic={}
    rsdic['ret']=Status.OK
    rsdic['obj']=[]
    #广告统计图数据
    rsdic['advertisement_dash'] = {}
    #广告点击量统计
    rsdic['advertisement_dash']['count'] = {}
    try:
        session=request.get_session()
        user = get_current_user(request)
        comp_id = user.comp_id
        try :
            obj=session.query(Advertisement).filter_by(comp_id=comp_id,title=request.GET['name']).one()
        except Exception,e:
            rsdic['ret'] = Status.QUERY_ADVERTISE_ERROR
            rsdic['info'] = Status().getReason(rsdic['ret'])
            return HttpResponse(json.dumps(rsdic))
        #获取广告点击量统计数据
        sha1 = obj.sha1
        end_date = datetime.datetime.now()
        start_date = end_date- datetime.timedelta(days=30)
        sql = 'select count(*)  as count , action_time from gcustomer_useraction where sha1=\'%s\' and action_time>\'%s\' and action_time<\'%s\' group by action_time' %(sha1,start_date,end_date)
        countObjs = session.execute(sql)
        rsdic['advertisement_dash']['count']['categories'] = []
        rsdic['advertisement_dash']['count']['data'] = []
        for count_obj in countObjs :
            rsdic['advertisement_dash']['count']['categories'].append(str(count_obj.action_time).split(" ")[0])
            rsdic['advertisement_dash']['count']['data'].append(count_obj.count)
        rsdic['advertisement_dash']['count']['categories'].sort()
        statistic_data = cal_advert_statistics(sha1)
        #人群分布
        data_age = []
        data_gender = []
        data_career = []

        data_age_dict = statistic_data['data_age']
        data_gender_dict = statistic_data['data_gender']
        data_career_dict = statistic_data['data_career']

        for age_item in data_age_dict.keys() :
            data_age.append([age_item,data_age_dict[age_item]])

        for age_item in data_gender_dict.keys() :
            data_gender.append([age_item,data_gender_dict[age_item]])

        for age_item in data_career_dict.keys() :
            data_career.append([age_item,data_career_dict[age_item]])

        rsdic['obj'].append(dict(
            name=obj.name,
            title=obj.title,
            data_age = data_age,
            data_gender = data_gender,
            data_career = data_career,
            ))
    except Exception, e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#删除广告信息
#输入: 广告sha1
#输出: 删除状态
def delete_advertisement(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    sha1 = request.POST['sha1']
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    #检查用户是否为管理员用户
    try :
        gcompany_membership = session.query(GCompanyMembership).filter_by(comp_id=comp_id,
            user_id=user.id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.QUERY_USER_COMP_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    if not gcompany_membership.role == 2 :
        rsdic['ret'] = Status.HAS_NO_ACCESS
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    try:
        obj = session.query(Advertisement).filter_by(sha1=sha1).one()
        setting_obj = session.query(AdvertisementLaunchSetting).filter_by(advert_id=obj.id).one()
        session.delete(obj)
        session.delete(setting_obj)
        session.commit()
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "没有权限删除"
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取单个营销活动的数据
#输入:  单个营销活动的id
#输出:   单个营销活动的数据
def get_activity_data(request):
    rsdic={}
    rsdic['ret']=Status.OK
    rsdic['obj']=[]
    duration_time = 30
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        s=request.get_session()
        activityId=s.query(Promotion).filter_by(comp_id=comp_id,name=request.GET['name']).one().id
        obj=s.query(PromotionEffect).filter_by(promotion_id=activityId).one()
        rsdic['obj'].append(dict(
            name=request.GET['name'],
            cost=obj.cost,
            nb_participates=obj.nb_participates,
            activity_duration = duration_time,
            purchase=obj.total_fuel_purchase+obj.total_nonfuel_purcahse+obj.total_service_purcahse))
    except Exception, e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#get_main_customer_list
#输入: 站点代码
#输出: 油站信息
def get_main_customer_list(request):
    rsdic={}
    rsdic['ret']=Status.OK
    rsdic['obj']=[]
    rsdic['station']=[]
    rsdic['top_100_goods']=[]
    rsdic['bottom_100_goods']=[]
    rsdic['main_customer_list']=[]
    try:
        #获取该油站及其大客户信息
        user = get_current_user(request)
        comp_id = user.comp_id
        session = request.get_session()
        if request.GET.has_key("site") :
            try :
                station = session.query(Station).filter_by(comp_id = comp_id ,name=request.GET[u'site']).one()
                station_profile = session.query(StationProfile).filter_by(station_id=station.id).one()
            except Exception,e:
                rsdic['ret'] = Status.QUERY_SITE_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic))
            top_100_goods = station_profile.top_100_goods
            bottom_100_goods = station_profile.bottom_100_goods
            #油站信息概况
            rsdic['station'].append(dict(
                total_sales_amount=station_profile.total_sales_amount,
                total_nonfuel_sales_amount=station_profile.total_nonfuel_sales_amount,
                fuel_sales = station_profile.fuel_sales,
                rank=station_profile.rank,
                fuel_type = get_fuel_type(request,station.site_code)
                ))
            customerId_list=station_profile.top_100_customers
            for  customerId in  json.loads(customerId_list):
                obj = session.query(BigCustomerProfile).filter_by(vcard_id = customerId).first()
                if obj :
                    name = session.query(CustomerAccount).filter_by(cardnum = obj.vcard_id).one().nick
                    user_profile = session.query(CustomerProfile).filter_by(vcard_id = obj.vcard_id).one()
                    total_purchase_amount = user_profile.total_purchase_amount
                    total_nonfuel_purchase_amount = user_profile.total_nonfuel_purchase_amount
                    prepaid_amount = total_purchase_amount - total_nonfuel_purchase_amount
                    rsdic['obj'].append(dict(name=name,prepaid_amount=prepaid_amount))
            rsdic['top_100_goods']=json.loads(top_100_goods)
            rsdic['bottom_100_goods']=json.loads(bottom_100_goods)
        else :
            #获取该公司下排名前20的大客户
            try:
                main_customer_list = session.query(BigCustomerProfile).filter_by(comp_id=comp_id).order_by('contribution desc').all()
                if len(main_customer_list) >= 20:
                    main_customer_list = main_customer_list[0:20]
                else :
                    pass
                for obj in main_customer_list:
                    customer_relations = session.query(CustomerRelation).filter_by(comp_id = comp_id,master_cardnum=obj.vcard_id).all()
                    nb_slave_cards_list = [str(relation.slave_cardnum) for relation in customer_relations]
                    customer = session.query(CustomerAccount).filter_by(cardnum = obj.vcard_id).one()
                    user_profile = session.query(CustomerProfile).filter_by(vcard_id = obj.vcard_id).one()
                    total_purchase_amount = user_profile.total_purchase_amount
                    total_nonfuel_purchase_amount = user_profile.total_nonfuel_purchase_amount
                    prepaid_amount = total_purchase_amount - total_nonfuel_purchase_amount
                    rsdic['main_customer_list'].append(dict(
                            name = customer.nick,
                            master_cardnum = obj.vcard_id,
                            create_time = str(customer.time).split(".")[0],
                            contribution = obj.contribution,
                            current_balance = customer.balance,
                            nb_slave_cards = len(nb_slave_cards_list)
                        ))
            except Exception,e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = Status().getReason(rsdic['ret'])
    except Exception, e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#创建油站群
#输入: 用户类型,用户操作id,用户群参数
#输出: 创建状态
def create_station_group(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    user = get_current_user(request)
    comp_id = user.comp_id
    source_id = user.id
    group_name = request.GET['group_name']
    group_location = request.GET['group_location']
    total_sales_amount = request.GET['total_sales_amount']
    rank = request.GET['rank']
    group_info = request.GET['group_info']
    try:
        session = request.get_session()
        station_group = StationGroup(
                comp_id = comp_id,
                admin_id = source_id,
                group_name = group_name,
                group_location = group_location,
                total_sales_amount = total_sales_amount,
                rank = rank,
                group_info = group_info
            )
        station_sha1_list = cal_station_group_site_list(station_group)
        station_group.site_sha1_list = json.dumps(station_sha1_list)
        session.add(station_group)
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally :
        return HttpResponse(json.dumps(rsdic))

#获取油站群列表
#输入: 无
#输出: 油站群列表
def get_station_group_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['objs'] = []
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    try:
        station_groups = session.query(StationGroup).filter_by(comp_id=comp_id).all()
        for station_group in station_groups :
                group_creator = session.query(GCustomerUser).filter_by(id=station_group.admin_id).one().name
                rsdic['objs'].append(dict(
                        id = station_group.id,
                        group_name = station_group.group_name,
                        group_location = "",
                        total_sales_amount = station_group.total_sales_amount,
                        rank = station_group.rank,
                        group_info = station_group.group_info,
                        time = str(station_group.time).split(".")[0],
                        group_creator = group_creator
                    ))
    except Exception.e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取油站群
#输入: 油站群名称关键字
#输出:  油站群数据
def get_station_group_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['objs'] = []
    group_name = request.GET['group_name']
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        station_groups = session.query(StationGroup).filter_by(comp_id=comp_id).all()
        for station_group in station_groups :
            if group_name in station_group.group_name:
                group_creator = session.query(GCustomerUser).filter_by(id = station_group.admin_id).one().name
                rsdic['objs'].append(dict(
                        group_name = station_group.group_name,
                        group_location = "",
                        total_sales_amount = station_group.total_sales_amount,
                        rank = station_group.rank,
                        group_info = station_group.group_info,
                        time = str(station_group.time).split(".")[0],
                        group_creator = group_creator
                    ))
            else :
                continue
    except Exception.e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取油站群详细信息
#输入: 油站群名称
#输出: 油站群详情
def get_station_group_detail(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['obj'] = {}
    station_group_name = request.GET['station_group_name']
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        obj = session.query(StationGroup).filter_by(comp_id = comp_id,group_name=station_group_name).one()
        #群组的行政区划代码
        group_location = json.loads(obj.group_location)
        group_creator = session.query(GCustomerUser).filter_by(id=obj.admin_id).one().name
        #群组的行政区划名称
        group_location = session.query(DimChinaProvinceCityDistrict).filter_by(id=group_location['province']).one().name
        station_list = []
        station_site_code_list = json.loads(obj.site_sha1_list)
        for site_code in station_site_code_list :
            station = session.query(Station).filter_by(comp_id=comp_id,site_code=site_code).one()
            station_list.append(station.name)
        rsdic['obj'] = {
            'group_name':obj.group_name,
            'group_location':group_location,
            'total_sales_amount':obj.total_sales_amount,
            'rank':obj.rank,
            'group_info':obj.group_info,
            'time':str(obj.time).split(".")[0],
            'group_creator':group_creator,
            'station_list':station_list
        }
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#删除油站群
#输入: 油站群名称
#输出: 删除状态
def delete_station_group(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    group_name = request.GET['group_name']
    try:
        session = request.get_session()
        obj = session.query(StationGroup).filter_by(group_name = group_name).delete()
        session.commit()
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#获得主卡消费记录
#输入: 主卡卡号
#输出: 主卡消费记录
def get_consume_record(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['objs'] = []
    master_cardnum = request.GET['master_cardnum']
    try:
        session = request.get_session()
        if not master_cardnum :
            big_customer_list = session.query(BigCustomerProfile).all()
        else :
            big_customer_list = session.query(BigCustomerProfile).filter_by(master_cardnum = master_cardnum).all()
        if not big_customer_list :
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "大客户信息不存在"
            return HttpResponse(json.dumps(rsdic))
        else :
            for obj in big_customer_list:
                rsdic['objs'].append(dict(
                                name = obj.name,
                                master_cardnum =str(obj.master_cardnum),
                                current_balance = obj.current_balance,
                            ))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "暂无信息"
    return HttpResponse(json.dumps(rsdic))

#获得主卡对应的副卡的消费记录
#输入: 主卡卡号
#输出:  对应副卡消费记录
def get_slave_consume_record(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['objs'] = []
    master_cardnum = int(request.GET['master_cardnum'])
    #主卡号存在
    if master_cardnum :
        try:
            session = request.get_session()
            objs = session.query(CustomerRelation).filter_by(master_cardnum = master_cardnum).all()
            for obj in objs :
                slave_cardnum = obj.slave_cardnum
                try :
                    curr_balance = session.query(CustomerProfile).filter_by(cardnum = slave_cardnum).one().curr_balance
                except Exception,e:
                    continue
                    rsdic['ret'] = Status.UNKNOWNERR
                    rsdic['info'] = "暂无信息"
                    return HttpResponse(json.dumps(rsdic))
                rsdic['objs'].append(dict(
                        slave_cardnum = str(slave_cardnum),
                        curr_balance  = curr_balance
                    ))
        except Exception,e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "暂无信息"
        finally:
            return HttpResponse(json.dumps(rsdic))
    else :
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "暂无信息"
        return HttpResponse(json.dumps(rsdic))

#render_image
#输入: 图片sha1
#输出: 图片
def render_image(request):
    imagebinarydata = None
    if "img_sha1" in request.GET.keys():
        img_sha1 = str(request.GET['img_sha1'])
        try :
            import base64
            imagebinarydata = base64.b64decode(WheelFileImage.objects.filter(sha1=img_sha1).first().base64_content)
            response = HttpResponse(imagebinarydata,mimetype = 'image')
        except :
            try :
                    session = request.get_session()
                    import base64
                    imagebinarydata=base64.b64decode(session.query(FileImage).filter_by(sha1=img_sha1).one().image)
                    response = HttpResponse(imagebinarydata,mimetype = 'image')
            except :
                response = HttpResponse(None,mimetype = 'image/png')
        finally:
            return response
    else :
        try:
            image_sha1=request.GET['name']
            s=request.get_session()
            try :
                imagebinarydata = s.query(FileImage).filter_by(sha1=image_sha1).one().image
            except Exception,e:
                imagebinarydata = base64.b64decode(WheelFileImage.objects.filter(sha1=image_sha1).first().base64_content)
            import base64
            imagebinarydata = base64.b64decode(imagebinarydata)
            response = HttpResponse(imagebinarydata,mimetype = 'image')
        except Exception, e:
            print exception_stuck()
            ajax_logger.error(str(e))
        finally:
            return response

#添加商品
#输入: 商品参数
#输出: 添加状态
def create_commodity(request):
    rsdic = {}
    image_sha1 = request.POST['image_sha1']
    pos_id = request.POST['pos_id']
    commodity = request.POST['commodity']
    price = request.POST['price']
    session = request.get_session()
    try:
        obj = session.query(StoreItem).filter_by(pos_id=pos_id).first()
        if obj:
            rsdic['info'] = '商品已存在，请勿重复添加！'
            return HttpResponse(json.dumps({'message':rsdic['info'],'user_type':get_user_type(request)}))
        else :
            pass
    except Exception, e:
        session.rollback()
        ajax_logger.error(str(e))
        print e
    try:
        user = get_current_user(request)
        source_id = user.id
        comp_id = user.comp_id
        import hashlib
        sha1 = hashlib.sha1()
        sha1.update(str(pos_id))
        sha1.update(commodity)
        sha1.update(str(price))
        sha1.update(str(source_id))
        sha1.update(str(comp_id))
        sha1 = sha1.hexdigest()
        goods = StoreItem(
                        pos_id = pos_id,
                        name = commodity,
                        price = price,
                        source_id = source_id,
                        img_sha1 = image_sha1,
                        comp_id = comp_id,
                        sha1 = sha1
                    )
        session.add(goods)
        session.commit()
        rsdic['info'] = "商品信息成功添加！"
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "商品信息添加失败！"
    finally:
        return HttpResponse(json.dumps({'message':rsdic['info'],'user_type':get_user_type(request)}))

#自动导入商品数据
#输入:  文件名
#输出:  导入状态
def auto_create_commodity(request):
    rsdic = {}
    rsdic['ret'] = '1101'
    try:
        goods_file_name = request.FILES['goods_list'].name
        goods_file_data = request.FILES['goods_list'].file.read()
        base_dir = "gcustomer/media/goods_list/"
        time = datetime.datetime.today()
        time = time.strftime("%Y-%m-%d_%H:%M:%S")
        file_name = base_dir + goods_file_name + '_' + time
        f = open(file_name, 'w+')
        f.write(goods_file_data)
        f.close()
        rsdic['message'] = '文件上传成功!'
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['message'] = "文件上传失败！"
    finally:
        return render_to_response('gcustomer/add_store_items.html', {'message':rsdic['message'], 'user_type':get_user_type(request)})


#获取商品列表
#输入:  搜索关键字
#输出:   商品列表
def get_goods_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['obj'] = []
    search_string = request.GET['search_string']
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        s = request.get_session()
        goods = s.query(StoreItem).filter_by(comp_id=comp_id).all()
        for obj in goods:
            if str(search_string) in obj.name or search_string in str(obj.pos_id) :
                rsdic['obj'].append(dict(
                                sha1=obj.sha1,
                                pos_id=obj.pos_id,
                                name=obj.name,
                                price=obj.price,
                            ))
            else :
                continue
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    return HttpResponse(json.dumps(rsdic))

#获取商品详情
#输入: 商品sha1
#输出: 商品详情
def get_goods_detail(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    sha1 = request.GET['sha1']
    try:
        s = request.get_session()
        obj = s.query(StoreItem).filter_by(sha1=sha1).one()
        rsdic['obj'] = {
                'sha1':obj.sha1,
                'source_id':obj.source_id,
                'pos_id':obj.pos_id,
                'name':obj.name,
                'price':obj.price,
                'count':obj.count,
                'exchange_score':obj.exchange_score,
                'discount':obj.discount,
                'discount_info':obj.discount_info,
                'discount_end_time':str(obj.discount_end_time),
                'img_sha1':obj.img_sha1,
                'information':obj.information
            }
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#删除商品信息
#输入: 商品sha1
#输出:  删除状态
def delete_goods(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = "商品信息删除成功！"
    sha1 = request.POST['sha1']
    try:
        s = request.get_session()
        goods_obj = s.query(StoreItem).filter_by(sha1=sha1).one()
        s.delete(goods_obj)
        s.commit()
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "商品信息删除失败！"
    finally:
        return HttpResponse(json.dumps(rsdic))

#修改商品信息
#输入: 商品sha1 ,商品参数
#输出: 修改结果
def modify_goods_detail(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = "商品信息修改成功！"
    sha1 = request.POST['sha1']
    pos_id = request.POST['pos_id']
    name = request.POST['name']
    price = float(request.POST['price'])
    count = int(request.POST['count']),
    exchange_score = int(request.POST['exchange_score']),
    discount = float(request.POST['discount']),
    discount_info = request.POST['discount_info'],
    information = request.POST['information'],
    try:
        session = request.get_session()
        commodity = session.query(StoreItem).filter_by(sha1=sha1).one()
        commodity.pos_id = pos_id
        commodity.name = name
        commodity.price = price
        commodity.count = count
        commodity.exchange_score = exchange_score
        commodity.discount = discount
        commodity.discount_info = discount_info
        commodity.information = information
        session.commit()
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#创建广告
#输入:    广告参数
#输出:    创建状态
def create_advertisement(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = "上传广告成功"
    if not request.FILES:
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "请选择广告图片"
        return render_to_response('gcustomer/upload_advert.html',{'message':rsdic['info']})
    advert_title=request.POST['advert_title']
    advert_customer_name=request.POST['advert_customer_name']
    advert_image_name=request.FILES['advert_image'].name
    imagebinarydata=request.FILES['advert_image'].file.read()
    advert_content=request.POST['advert_content']
    #图片数据
    import hashlib
    sha1=hashlib.sha1()
    sha1.update(str(imagebinarydata))
    sha1=sha1.hexdigest()
    image_sha1 = sha1
    import base64
    imagebinarydata = base64.b64encode(imagebinarydata)
    user = get_current_user(request)
    comp_id = user.comp_id
    source_id = user.id
    try:
        s=request.get_session()
        title=s.query(Advertisement).filter_by(
            comp_id = comp_id,
            title=advert_title,
            name = advert_customer_name
            ).one().title
        if len(title):
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "不可以重复上传广告,上传失败!"
            return render_to_response('gcustomer/upload_advert.html',\
                {'message':rsdic['info'],'user_type':get_user_type(request)})
        else :
            pass
    except  :
        sha1=hashlib.sha1()
        sha1.update(str(comp_id)+str(advert_title))
        sha1=sha1.hexdigest()
        advertisement=Advertisement(
            sha1 = sha1,
            comp_id = comp_id,
            source_id = source_id,
            title=advert_title,
            name=advert_customer_name,
            abstract=advert_content,
            image_sha1 = image_sha1)
        s.add(advertisement)
        try:
            s.commit()
            try:
                advert = s.query(Advertisement).filter_by(
                        comp_id = comp_id,
                        source_id = source_id,
                        title=advert_title,
                        name=advert_customer_name,
                    ).one()
                advert_id = advert.id
            except Exception,e:
                s.rollback()
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "上传广告失败"
                return render_to_response('gcustomer/upload_advert.html',\
                    {'message':rsdic['info'],'user_type':get_user_type(request)})
            obj = AdvertisementLaunchSetting(comp_id = comp_id,advert_id = advert_id)
            s.add(obj)
            try:
                s.commit()
            except Exception,e:
                s.rollback()
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "存储广告周期设置信息失败"
                session.delete(advert)
                session.commit()
                return render_to_response('gcustomer/upload_advert.html',\
                    {'message':rsdic['info'],'user_type':get_user_type(request)})
            try:
                session = request.get_session()
                try:
                    session.query(FileImage).filter_by(sha1 = image_sha1).one()
                except :
                    imageObj = FileImage(
                            sha1 = image_sha1,
                            image = imagebinarydata ,
                            image_name = advert_image_name,
                            image_size = len(imagebinarydata),
                            author = user.name,
                            time = str(datetime.datetime.now())
                        )
                    session.add(imageObj)
                    session.commit()
                    return render_to_response('gcustomer/upload_advert.html',\
                        {'message':rsdic['info'],'user_type':get_user_type(request)})
            except Exception,e:
                session.rollback()
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "存储图片信息失败"
                return render_to_response('gcustomer/upload_advert.html',\
                    {'message':rsdic['info'],'user_type':get_user_type(request)})
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "上传广告失败!"
            return render_to_response('gcustomer/upload_advert.html',\
                {'message':rsdic['info'],'user_type':get_user_type(request)})
    return render_to_response('gcustomer/upload_advert.html',{'message':rsdic['info']})

#导入副卡信息
#输入: 文件名
#输出: 导入状态
def upload_cards_file(request):
    rsdic = {}
    rsdic['ret'] = "0001"
    cards_data_file_name = request.FILES['cards_data'].name
    cards_data = request.FILES['cards_data'].file.read()
    base_dir = "gcustomer/static/sheet/"
    time = datetime.datetime.today()
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    file_name = base_dir + cards_data_file_name + "-" + time
    try:
        f = open(file_name, "w+")
        f.write(cards_data)
        f.close()
        rsdic['message'] = "文件上传成功！"
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['message'] = "文件上传失败！"
    return render_to_response('gcustomer/create_customer.html',{'message':rsdic['message']})


#新建车后服务
#输入: 车后服务参数
#输出: 新建结果
def create_service_advertisement(request):
    import datetime
    rsdic = {}
    rsdic['ret'] = "0001"
    rsdic['info'] = []
    user = get_current_user(request)
    comp_id = user.comp_id
    source_id  = user.id
    image_sha1 = request.POST['image_sha1']
    info_type = int(request.POST['info_type'])
    price = float(request.POST['price'])
    create_time = datetime.datetime.now()
    #商品类型
    if info_type == 0:
        title = request.POST['title']
        from_province_code = request.POST['from_province_code']
        from_city_code = request.POST['from_city_code']
        dest_province_code = request.POST['dest_province_code']
        dest_city_code = request.POST['dest_city_code']
        phone_num = request.POST['phone_num']
        content = request.POST['content']

        try:
            s = request.get_session()
            from_province = s.query(DimChinaProvinceCityDistrict).filter_by(id=from_province_code).one().name
            from_city = s.query(DimChinaProvinceCityDistrict).filter_by(id=from_city_code).one().name
            dest_province = s.query(DimChinaProvinceCityDistrict).filter_by(id=dest_province_code).one().name
            dest_city = s.query(DimChinaProvinceCityDistrict).filter_by(id=dest_city_code).one().name
            from_city = from_province + from_city
            dest_city = dest_province + dest_city
            import hashlib
            sha1 = hashlib.sha1()
            sha1.update(str(source_id))
            sha1.update(title)
            sha1.update(str(info_type))
            sha1.update(content)
            sha1.update(str(create_time))
            sha1=sha1.hexdigest()
            goods_advertisement = ServiceInformation(
                source_id = source_id,
                title = title,
                info_type = info_type,
                from_city = from_city,
                dest_city = dest_city,
                create_time = create_time,
                phone_number = phone_num,
                content = content,
                img_sha1 = image_sha1 ,
                price = price,
                comp_id = comp_id,
                sha1 = sha1
            )
            s.add(goods_advertisement)
            s.commit()
            rsdic['info'] = "货运信息添加成功！"
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = "0000"
            rsdic['info'] = "货运信息添加失败！"
        finally:
            return HttpResponse(json.dumps(rsdic))
    elif info_type == 1:
        title = request.POST['title']
        address = request.POST['address']
        phone_num = request.POST['phone_num']
        business_scope = request.POST['business_scope']
        try:
            s = request.get_session()
            import hashlib
            sha1 = hashlib.sha1()
            sha1.update(str(source_id))
            sha1.update(title)
            sha1.update(str(info_type))
            sha1.update(business_scope)
            sha1.update(str(create_time))
            sha1=sha1.hexdigest()
            repair_advertisement = ServiceInformation(
                source_id = source_id,
                info_type = info_type,
                title = title,
                address = address,
                phone_number = phone_num,
                content = business_scope,
                img_sha1 = image_sha1 ,
                price = price,
                comp_id = comp_id,
                create_time = create_time,
                sha1 = sha1
            )
            s.add(repair_advertisement)
            s.commit()
            rsdic['info'] = "维修信息添加成功！"
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = "1102"
            rsdic['info'] = "维修信息添加失败！"
        finally:
            return HttpResponse(json.dumps(rsdic))
    elif info_type == 2:
        title = request.POST['title']
        address = request.POST['address']
        phone_num = request.POST['phone_num']
        business_scope = request.POST['business_scope']
        try:
            s = request.get_session()
            import hashlib
            sha1 = hashlib.sha1()
            sha1.update(str(source_id))
            sha1.update(title)
            sha1.update(str(info_type))
            sha1.update(business_scope)
            sha1.update(str(create_time))
            sha1=sha1.hexdigest()
            maintenance_advertisement=ServiceInformation(
                source_id = source_id,
                info_type = 2,
                title = title,
                address = address,
                phone_number = phone_num,
                content = business_scope,
                img_sha1 = image_sha1 ,
                price = price,
                comp_id = comp_id,
                create_time = create_time,
                sha1 = sha1
            )
            s.add(maintenance_advertisement)
            s.commit()
            rsdic['info'] = "保养信息添加成功！"
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = "0000"
            rsdic['info'] = "保养信息添加失败！"
            return HttpResponse(json.dumps(rsdic))
    else :
        ajax_logger.error(str(e))
        rsdic['ret'] = "0000"
        rsdic['info'] = "保养信息添加失败！"
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))


#获取油站信息
#Author:wangjianchang
#输入：查询关键字
#输出：相关的油站信息
def get_station_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['station_list'] = []
    keyword = request.GET['keyword']
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        station_list = session.query(Station).filter_by(comp_id = comp_id).all()
        for station in station_list:
            if keyword in station.name or keyword in str(station.site_code):
                rsdic['station_list'].append(dict(
                        name = station.name,
                        site_tel = station.site_tel,
                        address = station.address,
                        site_code = station.site_code,
                        sha1 = station.sha1
                    ))
            else:
                continue
    except  Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.QUERY_SITE_ERROR
        rsdic['info'] = Status.getReason(rsdic['ret'])
        rsdic['station_list'] = []
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#Author:wangjianchang
#获取详细信息
#输入：油站sha1
#输出：油站详细信息
def get_station_detail(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    sha1 = request.POST['sha1']
    try:
        session = request.get_session()
        record_obj = session.query(Station).filter_by(sha1 = sha1).one()
        record = {}
        record['site_code'] = record_obj.site_code
        record['name'] = record_obj.name 
        record['address'] = record_obj.address
        record['site_tel'] = record_obj.site_tel
        record['geo_x'] = record_obj.geo_x
        record['geo_y'] = record_obj.geo_y
        record['comment_score'] = record_obj.comment_score
        record['comment_count'] = record_obj.comment_count
        record['fuel_type'] = record_obj.fuel_type
        record['assist_type'] = record_obj.assist_type
        record['img_sha1'] = record_obj.img_sha1
        rsdic['obj'] = record
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.QUERY_SITE_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    return HttpResponse(json.dumps(rsdic))

#Author:wangjianchang
#新建油站
#输入：油站信息
#输出：新建油站结果
def create_station(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    user = get_current_user(request)
    comp_id = user.comp_id
    site_code = request.POST['site_code']
    name = request.POST['name']
    site_tel = request.POST['site_tel']
    address = request.POST['address']
    province = request.POST['province']
    city = request.POST['city']
    xiancode = request.POST['xiancode']
    location = province + city + xiancode + address
    import urllib2
    import json
    try:
        api_data = urllib2.urlopen("http://api.map.baidu.com/geocoder/v2/?address=%s&output=json&ak=C313lZw1Mqcwx5evyQCGOB6O" % location)
        json_data = json.load(api_data)
        geo_x = json_data['result']['location']['lat']
        geo_y = json_data['result']['location']['lng']
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    session = request.get_session()
    try:
        session.query(Station).filter_by(comp_id=comp_id,name =name).one()
        rsdic['ret'] = Status.SITE_HAS_EXIST
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    except :
        try:
            import hashlib
            sha1 = hashlib.sha1()
            sha1.update(str(comp_id))
            sha1.update(site_code)
            sha1 = sha1.hexdigest()

            station_obj = Station(
                comp_id = comp_id,
                site_code = site_code,
                name = name,
                location = location,
                site_tel = site_tel,
                address = address,
                sha1 = sha1,
                geo_x = geo_x,
                geo_y = geo_y
                )
            session.add(station_obj)
            try :
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.QUERY_SITE_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic))

            try:
                station = session.query(Station).filter_by(sha1 = sha1).one()
            except Exception,e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.QUERY_SITE_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic))

            station_id = station.id
            station_profile_obj = StationProfile(
                station_id = station_id,
                start_time = datetime.datetime.now(),
                end_time = datetime.date(2015,12,12),
                )
            session.add(station_profile_obj)
            try :
                session.commit()
            except Exception,e:
                session.delete(station)
                session.commit()
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.QUERY_SITE_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic))
        except Exception, e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.QUERY_SITE_ERROR
            rsdic['info'] = Status().getReason(rsdic['ret'])
            return HttpResponse(json.dumps(rsdic))
        return HttpResponse(json.dumps(rsdic))
        
#Author:wangjianchang
#删除油站
#输入:油站编码
#输出：油站删除操作
def delete_station(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    sha1 = request.POST['sha1']
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    try :
        station_obj = session.query(Station).filter_by(comp_id = comp_id,sha1 = sha1).one()
        station_profile_obj = session.query(StationProfile).filter_by(station_id = station_obj.id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    try:
        session.delete(station_obj)
        session.delete(station_profile_obj)
        session.commit()
        rsdic['info'] = Status().getReason(rsdic['ret'])
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))


#修改油站信息
#Author:wangjianchnag
#输入:油站sha1
#输出:油站信息修改
def modify_detail_station(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    session = request.get_session()
    sha1 = request.POST['sha1']
    site_code = request.POST['site_code']
    station_name = request.POST['name']
    address = request.POST['address']
    site_tel = request.POST['site_tel']
    geo_x = request.POST['geo_x']
    geo_y = request.POST['geo_y']
    try:
        station_obj = session.query(Station).filter_by(sha1 = sha1).one()
    except Exception, e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    station_obj.site_code = site_code
    station_obj.name = station_name
    station_obj.address = address
    station_obj.site_tel = site_tel
    station_obj.geo_x = geo_x
    station_obj.geo_y = geo_y
    try :
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取车后服务
#输入: 服务类型,查询关键字
#输出: 车后服务列表
def get_service_advertisement(request):
    rsdic = {}
    rsdic['ret'] = "0001"
    rsdic['obj'] = []
    info_type = int(request.GET['info_type'])
    keyword = request.GET['keyword']
    user = get_current_user(request)
    comp_id = user.comp_id
    if info_type==0:
        try:
            s = request.get_session()
            objects = s.query(ServiceInformation).filter_by(comp_id=comp_id,info_type=info_type).order_by().all()
            #查询
            obj_list = []
            for obj in objects :
                    if keyword in obj.title :
                        obj_list.append(obj)
                    else :
                        continue
            objects = obj_list
            for obj in objects:
                record = {}
                record['title'] = obj.title
                record['info_id'] = obj.id
                record['info_type'] = obj.info_type
                record['from_city'] = obj.from_city
                record['dest_city'] = obj.dest_city
                record['create_time'] = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
                record['phone_num'] = obj.phone_number
                record['content'] = obj.content
                record['price'] = obj.price
                if  not obj.price :
                    record['price'] = 0
                rsdic['obj'].append(record)
        except Exception, e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = Status().getReason(rsdic['ret'])
        finally:
            return HttpResponse(json.dumps(rsdic))
    elif info_type==1:
        try:
            s = request.get_session()
            objects = s.query(ServiceInformation).filter_by(comp_id=comp_id,info_type=info_type).order_by().all()
            #查询
            obj_list = []
            for obj in objects :
                    if keyword in obj.title :
                        obj_list.append(obj)
                    else :
                        continue
            objects = obj_list
            for obj in objects:
                record = {}
                record['info_id'] = obj.id
                record['info_type'] = obj.info_type
                record['title'] = obj.title
                record['create_time'] = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
                record['phone_num'] = obj.phone_number
                record['address'] = obj.address
                record['content'] = obj.content
                record['price'] = obj.price
                if  not obj.price :
                    record['price'] = 0
                else :
                    pass
                rsdic['obj'].append(record)
        except Exception, e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = Status().getReason(rsdic['ret'])
        finally:
            return HttpResponse(json.dumps(rsdic))
    elif info_type==2:
        try:
            s = request.get_session()
            objects = s.query(ServiceInformation).filter_by(comp_id=comp_id,info_type=info_type).order_by().all()
            #查询
            obj_list = []
            for obj in objects :
                    if keyword in obj.title :
                        obj_list.append(obj)
                    else :
                        continue
            objects = obj_list
            for obj in objects:
                record = {}
                record['info_id'] = obj.id
                record['info_type'] = obj.info_type
                record['title'] = obj.title
                record['create_time'] = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
                record['phone_num'] = obj.phone_number
                record['address'] = obj.address
                record['content'] = obj.content
                record['price'] = obj.price
                if  not obj.price :
                    record['price'] = 0
                rsdic['obj'].append(record)
        except Exception, e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = Status().getReason(rsdic['ret'])
        finally:
            return HttpResponse(json.dumps(rsdic))

#获取广告详细信息
#输入: 车后服务id
#输出: 车后服务详情
def get_detail_advertisement(request):
    rsdic = {}
    rsdic['ret'] ="0001"
    info_id = int(request.POST['info_id'])
    try:
        s = request.get_session()
        record_obj = s.query(ServiceInformation).filter_by(id=info_id).one()
        record = {}
        record['info_id'] = record_obj.id
        record['info_type'] = record_obj.info_type
        record['title'] = record_obj.title
        record['from_city'] = record_obj.from_city
        record['dest_city'] = record_obj.dest_city
        record['address'] = record_obj.address
        record['create_time'] = record_obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
        record['phone_num'] = record_obj.phone_number
        record['content'] = record_obj.content
        record['price'] = record_obj.price
        if  not record_obj.price :
            record['price'] = 0
        else :
            pass
        rsdic['obj'] = record
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    return HttpResponse(json.dumps(rsdic))

#修改车后服务详细信息
#输入:  车后服务类型,车后服务id
#输出:  修改状态
def modify_detail_advertisement(request):
    rsdic = {}
    rsdic['ret'] = "0001"
    info_id = int(request.POST['info_id'])
    info_type = int(request.POST['info_type'])
    if info_type==0:
        try:
            s = request.get_session()
            record = s.query(ServiceInformation).filter_by(id=info_id).one()
            record.title = request.POST['title']
            record.from_city = request.POST['from_city']
            record.dest_city = request.POST['dest_city']
            record.content = request.POST['content']
            record.phone_num = request.POST['phone_num']
            record.price = float(request.POST['price'])
            s.commit()
            rsdic['message'] = "修改成功！"
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['message'] = Status().getReason(rsdic['ret'])
    elif info_type==1:
        try:
            s = request.get_session()
            record = s.query(ServiceInformation).filter_by(id=info_id).one()
            record.title = request.POST['title']
            record.address = request.POST['address']
            record.content = request.POST['content']
            record.phone_num = request.POST['phone_num']
            record.price = float(request.POST['price'])
            s.commit()
            rsdic['message'] = "修改成功！"
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['message'] = Status().getReason(rsdic['ret'])
    elif info_type==2:
        try:
            s = request.get_session()
            record = s.query(ServiceInformation).filter_by(id=info_id).one()
            record.title = request.POST['title']
            record.address = request.POST['address']
            record.content = request.POST['content']
            record.phone_num = request.POST['phone_num']
            record.price = float(request.POST['price'])
            s.commit()
            rsdic['message'] = "修改成功！"
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['message'] = Status().getReason(rsdic['ret'])
    return HttpResponse(json.dumps(rsdic))

#删除车后服务
#输入: 车后服务id
#输出: 删除状态
def delete_goods_advertisement(request):
    rsdic = {}
    rsdic['ret'] = "0001"
    info_id = int(request.POST['info_id'])
    try:
        s = request.get_session()
        record_obj = s.query(ServiceInformation).filter_by(id=info_id).one()
        try:
            s.delete(record_obj)
            s.commit()
            rsdic['message'] = "delete successfully!"
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['message'] = Status().getReason(rsdic['ret'])
    except Exception, e:
        print e
    return HttpResponse(json.dumps(rsdic))

#上传图片
def upload_app_img(request):
    if not request.FILES :
            rsdic={'ret':'1103','info':'请选择图片!'}
            return render_to_response('gcustomer/upload_app_img.html',{'message':rsdic['info']})
    else :
            rsdic={'ret':'0001','info':'ok'}
            file_name = request.FILES['image'].name
            imagebinarydata = request.FILES['image'].file.read()
            import hashlib
            sha1=hashlib.sha1()
            sha1.update(str(imagebinarydata))
            sha1.update(str(datetime.datetime.now()))
            img_sha1=sha1.hexdigest()
            import base64
            imagebinarydata = base64.b64encode(imagebinarydata)
            obj = WheelFileImage(sha1 = img_sha1,base64_content=imagebinarydata,file_name=file_name)
            try :
                obj.save()
            except Exception,e:
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = Status().getReason(rsdic['ret'])
    return render_to_response('gcustomer/upload_app_img.html',{'message':rsdic['info']})

#Stirng to time
def string_to_time(timestr):
    timetemp=str(timestr).split("/")
    timelist=[]
    timelist.append(timetemp[2])
    timelist.append(timetemp[0])
    timelist.append(timetemp[1])
    return timelist

#创建营销活动
#输入: 活动参数
#流程: 获取活动参数 --> 创建营销活动 --> 在活动统计表中初始化活动信息 --> 优惠推送
#输出:  创建状态
def create_promotion_activity(request):
    rsdic={}
    rsdic['ret']=Status.OK
    rsdic['info']="创建成功!"
    try:
        #活动基本信息
        user = get_current_user(request)
        source_id= user.id
        comp_id=user.comp_id
        start_timelist=string_to_time(request.POST['start_time'])
        end_timelist=string_to_time(request.POST['end_time'])
        start_time=datetime.date(int(start_timelist[0]),int(start_timelist[1]),int(start_timelist[2]))
        end_time=datetime.date(int(end_timelist[0]),int(end_timelist[1]),int(end_timelist[2]))
        name=request.POST['activity_name']
        create_type=int(request.POST['create_type'])
        auto_create_option=request.POST['auto_create_option']

        #手动创建
        #行政区划
        area_type=int(str(request.POST['activity_range']))
        area=json.loads(request.POST['area'])

        #油站群id
        station_group_id = request.POST["station_group_id"]

        #计算油站列表
        group_id = None
        if not area == "" and area.has_key("district") :
            session = request.get_session()
            station_list = []
            #0:表示没有选择
            try :
                    stations = session.query(Station).all()
                    for station in stations :
                        location = json.loads(station.location)
                        if area['province'] == location['province'] \
                            or area['city'] == location['city'] or area['district'] == location['district']:
                            station_list.append(station.site_code)
                    group_id = station_list
            except Exception,e:
                    group_id = []
        else :
            group_id =  station_group_id

        #手动创建目标用户群
        target_audience=request.POST['target_audience']

        #触发类型
        trigger_type=int(request.POST['launch_type'])

        #沟通方式
        contact_approach=int(request.POST['communication_type'])

        #活动描述
        description=request.POST['description']

        #status
        startTime=stringToTimeStamp(str(start_time)+ ' ' +str(datetime.datetime.now()).split(' ')[1].split('.')[0])
        endTime=stringToTimeStamp(str(end_time)+" 23:59:59")
        nowTime=stringToTimeStamp(str(datetime.datetime.now()).split(".")[0])
        #1:活动状态为正在进行中
        if  endTime > nowTime :
            status = 1
        else :
            rsdic["info"] = "promotion activity time is wrong"
            return HttpResponse(json.dumps(rsdic))
        start_time = timeStampToString(startTime)
        end_time = timeStampToString(endTime)
        #get session
        session = request.get_session()
        promotion = None
        #创建优惠活动
        promotion = Promotion(
            comp_id=comp_id,
            source_id=source_id,
            create_type = int(create_type),
            auto_create_option = int(auto_create_option),
            start_time=start_time,
            end_time=end_time,
            name=name,
            area=json.dumps(area),
            station_group_id = station_group_id,
            area_type=area_type,
            trigger_type=trigger_type,
            target_audience=target_audience,
            contact_approach=contact_approach,
            description=description,
            status=status)
        #完成创建
        try:
            session.add(promotion)
            try:
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "活动创建失败,活动名重复"
                return HttpResponse(json.dumps(rsdic))
            promotion_id = promotion.id
        except Exception,e:
            session.rollback()
            ajax_logger.error(str(e))
            rsdic['info']="创建失败,活动名重复!"
            return  HttpResponse(json.dumps(rsdic))
        promotion =session.query(Promotion).filter_by(comp_id = comp_id,name=promotion.name).one()
        promotion_response = PromotionEffect(promotion_id=promotion.id,user_participates="")
        session.add(promotion_response)
        try:
            session.commit()
        except Exception,e :
            session.rollback()
            ajax_logger.error(str(e))
            rsdic['info']="创建失败,系统异常!"
            session.query(Promotion).filter_by(name=promotion.name).delete()
            session.commit()
            return  HttpResponse(json.dumps(rsdic))

        # 0:手动创建
        if create_type == 0:
            #send_promotion_goods_to_customer参数
            #优惠商品货物 存储优惠商品的字典
            promotion_goods = json.loads(request.POST['promotion_goods'])
            #优惠描述
            desc = description
            #目标客户群id
            user_group = target_audience

        else :
            #活动描述，如果是改善油站效率，那么描述里存放参与活动的站点的高峰期时段
            desc = ''
            if auto_create_option=='3':
                #优惠推送给加油流失客户人群的卡号列表
                promotion_goods = json.loads(request.POST['promotion_goods'])
                for promotion_good in promotion_goods :
                    if not promotion_good.has_key("site_code") :
                            promotion_good['site_code'] = get_comp_oil_loss_station_sha1s(request,comp_id)
                user_group = get_all_loss_oil_user(comp_id)['data']
                #没有加油流失客户
                if len(user_group) == 0 :
                    rsdic['ret'] = Status.NO_OIL_LOSS_USER
                    rsdic['info'] = Status().getReason(rsdic['ret'])
                    return HttpResponse(json.dumps(rsdic))
            #改善油站效率，即，避免用户在高峰期进行加油
            elif auto_create_option=='1':
                promotion_goods = json.loads(request.POST['promotion_goods'])
                for promotion_good in promotion_goods :
                    if not promotion_good.has_key("site_code") :
                            promotion_good['site_code'] = get_peak_period_station_list(request,comp_id)
                user_group = 0

            #清仓滞销非油品
            elif auto_create_option=='6':
                user_group = 0
                sites = get_all_site(comp_id)["ids"]
                promotion_goods = []
                good_list = []
                for site in sites:
                    goods = get_bottom_goods_by_site(site)
                    station_sha1 = session.query(Station).filter_by(id = site).one().sha1
                    try :
                        goods = json.loads(goods['goods'])
                    except Exception,e:
                        continue
                    for good in goods[0:10]:
                        try:
                            good_id = session.query(StoreItem).filter_by(comp_id=comp_id,pos_id = str(good['barcode'])).one().id
                            if not good_id in good_list :
                                good_list.append(good_id)
                                temp_site_code = []
                                temp_site_code.append(station_sha1)
                                promotion_goods.append({"type":"1","name":good_id,"discount":0.9,"site_code":temp_site_code})
                            else :
                                for temp_promotion_good in promotion_goods :
                                    if temp_promotion_good['name'] == good_id :
                                        temp_promotion_good['site_code'].append(station_sha1)
                                    else :
                                        continue
                        except Exception,e:
                            pass
                #根据用户画像聚合滞销商品的用户列表
                for promotion_good in promotion_goods :
                    temp_promotion_good_list = [promotion_good]
                    try :
                        user_group = get_user_list_with_bottom_goods(comp_id,temp_promotion_good_list)
                        if user_group == [] :
                            continue
                        send_status = send_promotion_goods_to_customer(request,user_group,temp_promotion_good_list,station_group_id=station_group_id,
                            delivery_type=trigger_type,desc=desc,start_time = start_time,duration=7,promotion_id=promotion_id)
                        if send_status == False :
                            promotion = session.query(Promotion).filter_by(id = promotion_id).one()
                            promotion_response = session.query(PromotionEffect).filter_by(promotion_id = promotion_id).one()
                            session.delete(promotion)
                            session.delete(promotion_response)
                            session.commit()
                            ajax_logger.error(str("推送失败"))
                            rsdic['ret'] = Status.UNKNOWNERR
                            rsdic['info'] = "推送失败"
                            return HttpResponse(json.dumps(rsdic))
                    except Exception,e:
                        continue
            #快销商品
            elif auto_create_option=='7':
                user_group = 0
                sites = get_all_site(comp_id)['ids']
                good_id_list = []
                promotion_goods = []
                good_list = []
                for site in sites:
                    goods = get_top_goods_by_site(site)
                    station_sha1 = session.query(Station).filter_by(id = site).one().sha1
                    try :
                        goods = json.loads(goods['goods'])
                    except Exception,e:
                        continue
                    for good in goods[0:10]:
                        try:
                            good_id = session.query(StoreItem).filter_by(comp_id= comp_id,pos_id = str(good['barcode'])).one().id
                            if not good_id in good_list :
                                good_list.append(good_id)
                                temp_site_code = []
                                temp_site_code.append(station_sha1)
                                promotion_goods.append({"type":"1","name":good_id,"discount":0.9,"site_code":temp_site_code})
                            else :
                                for temp_promotion_good in promotion_goods :
                                    if temp_promotion_good['name'] == good_id :
                                        temp_promotion_good['site_code'].append(station_sha1)
                                    else :
                                        continue
                        except Exception,e:
                            session.commit()
                            pass
            #其他情况暂时传给所有用户
            else:
                user_group = 0
    except Exception,e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])
    #如果优惠活动创建成功,则将营销活动划分到对应的人或是群组，将其存储到 UserTargedPromotion
    #就是将user_group , promotion_goods 信息存到UserTargedPromotion中
    finally:
        if rsdic['ret'] == '0001' and not auto_create_option == "6" :
            duration = 7
            #自动创建营销活动的推送
            if create_type == 0 :
                send_status = send_promotion_goods_target_audience(request,user_group,promotion_goods,station_group_id=station_group_id,
                delivery_type=trigger_type,desc=desc,start_time = start_time,duration=duration,promotion_id=promotion_id)
            else :
                send_status = send_promotion_goods_to_customer(request,user_group,promotion_goods,station_group_id=station_group_id,
                delivery_type=trigger_type,desc=desc,start_time = start_time,duration=duration,promotion_id=promotion_id)
            #send_status 推送状态
            if send_status == False :
                promotion = session.query(Promotion).filter_by(id = promotion_id).one()
                promotion_response = session.query(PromotionEffect).filter_by(promotion_id = promotion_id).one()
                session.delete(promotion)
                session.delete(promotion_response)
                session.commit()
                ajax_logger.error(str("推送失败"))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "推送失败"
        return HttpResponse(json.dumps(rsdic))

#删除营销活动
#输入: 活动id
#详情: 删除营销活动的同时,清除活动统计数据,活动相关的所有推送数据
#输出: 删除状态
def delete_promotion_activity(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    activity_id = request.GET['activity_id']
    session = request.get_session()
    user = get_current_user(request)
    comp_id = user.comp_id
    #检查用户是否为管理员用户
    try :
        gcompany_membership = session.query(GCompanyMembership).filter_by(comp_id=comp_id,
            user_id=user.id).one()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.QUERY_USER_COMP_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    if not gcompany_membership.role == 2 :
        rsdic['ret'] = Status.HAS_NO_ACCESS
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    try :
        try :
            activity = session.query(Promotion).filter_by(id = activity_id).one()
            activity_response = session.query(PromotionEffect).filter_by(promotion_id = activity_id).one()
            userTargedPromotion = session.query(UserTargetedPromotion).filter_by(promotion_id = activity_id).all()
            promotion_info = session.query(PromotionInfo).filter_by(promotion_id = activity_id).all()
        except Exception,e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "营销活动不存在!"
            return HttpResponse(json.dumps(rsdic))
        session.delete(activity)
        session.delete(activity_response)
        for obj in userTargedPromotion :
            session.delete(obj)
        for obj in promotion_info :
            session.delete(obj)
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "删除活动失败!"
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获得广告周期设置信息
#输入:  无
#输出:  所有广告的周期设置数据
def get_advert_cycle_setting_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['objs'] = []
    session = request.get_session()
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        objs = session.query(AdvertisementLaunchSetting).filter_by(comp_id=comp_id).all()
        for obj in objs :
            try:
                title = session.query(Advertisement).filter_by(id=obj.advert_id).one().title
                rsdic["objs"].append(dict(
                        title = title,
                        advert_id = obj.advert_id,
                        life_cycle = obj.life_cycle,
                        play_time = obj.play_time,
                        play_frequency = obj.play_frequency,
                        is_close = obj.is_close
                    ))
            except Exception, e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                rsdic['objs'] = []
    finally:
        return HttpResponse(json.dumps(rsdic))

#修改广告周期设置信息
#输入: 广告id
#输出: 修改状态
def modify_advert_cycle_setting_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['objs'] = []
    advert_id = int(request.POST['advert_id'])
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        s = request.get_session()
        obj = s.query(AdvertisementLaunchSetting).filter_by(comp_id=comp_id,advert_id=advert_id).one()
        obj.title = request.POST['title']
        obj.life_cycle = request.POST['life_cycle']
        obj.play_time = request.POST['play_time']
        obj.play_frequency = request.POST['play_frequency']
        s.commit()
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        rsdic['objs'] = []
    finally:
        return HttpResponse(json.dumps(rsdic))

#修改广告播放设置
def alter_advert_setting(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    advert_id = int(request.GET['advert_id'])
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        obj = session.query(AdvertisementLaunchSetting).filter_by(comp_id=comp_id,advert_id=advert_id).one()
        is_close = obj.is_close
        if is_close ==1 :
            is_close = 0
        else :
            is_close = 1
        obj.is_close = is_close
        session.commit()
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        rsdic['objs'] = []
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取油站的油品
#输入: 油站代号
#输出: 油站油品数据
def get_station_fuel(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    station_sha1_list = json.loads(request.GET['site_code'])
    rsdic['good_list'] = []
    session = request.get_session()
    try :
        #site_code存储油站列表
        good_name_list = []
        if type(station_sha1_list) == type([]) :
            for sha1 in station_sha1_list :
                code = session.query(Station).filter_by(sha1 = sha1).one().site_code
                fuel_list = get_fuel_type(request,code)
                for fuel in fuel_list :
                    if not fuel['name'] in  good_name_list:
                        good_name_list.append(fuel['name'])
                        rsdic['good_list'].append(fuel)
        else :
            rsdic['good_list'] = get_fuel_type(request,site_code)
    except Exception,e :
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        rsdic['good_list'] = []
    return HttpResponse(json.dumps(rsdic))

#获取营销活动的优惠商品数据
#输入: 优惠商品类型 , 油站群组范围
#输出:  商品列表
def get_promotion_goods_map(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['goods_list'] = []
    promotion_type = request.GET['promotion_type']
    #自动创建的场景 1:改善油站设备效率 3:改善加油流失客户
    auto_create_option = request.GET['auto_create_option']
    station_group_range = json.loads(request.GET['station_group_range'])
    #根据活动范围获取油站群组
    session = request.get_session()
    user = get_current_user(request)
    comp_id = user.comp_id
    station_list = []
    try :
        #手动创建油站范围不能为空  自动创建油站范围可以为空
        if station_group_range :
            if station_group_range['type'] == '0' and station_group_range.has_key("province"):
                            stations = session.query(Station).filter_by(comp_id=comp_id).all()
                            for station in stations :
                                location = json.loads(station.location)
                                if station_group_range['province'] == location['province'] \
                                    or station_group_range['city'] == location['city'] or station_group_range['district'] == location['district']:
                                    station_list.append(dict(
                                        sha1=station.sha1,
                                        name=session.query(Station).filter_by(sha1 = station.sha1).one().name
                                    ))
            elif  station_group_range['type'] == '0' and station_group_range.has_key("group_id") :
                        try:
                            obj_list = json.loads(session.query(StationGroup).filter_by(id = station_group_range['group_id'],\
                                comp_id=comp_id).one().site_sha1_list)
                            for obj in obj_list :
                                station_list.append(dict(
                                    sha1=obj,
                                    name=session.query(Station).filter_by(sha1 = obj).one().name
                                ))
                        except Exception.e:
                            station_list = []
        elif auto_create_option == '1':
            user = get_current_user(request)
            comp_id = user.comp_id
            station_sha1_list = get_peak_period_station_list(request,comp_id)
            if station_sha1_list == False :
                rsdic['ret'] = Status.QUERY_OIL_LOSS_STATION_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic))
            for station_sha1 in station_sha1_list :
                station_list.append(dict(
                sha1= station_sha1,
                name=session.query(Station).filter_by(sha1 = station_sha1).one().name
                ))
        elif auto_create_option == '3':
            user = get_current_user(request)
            comp_id = user.comp_id
            station_sha1_list = get_comp_oil_loss_station_sha1s(request,comp_id)
            if station_sha1_list == False :
                rsdic['ret'] = Status.QUERY_PEAK_PERIOD_STATION_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic))
            for station_sha1 in station_sha1_list :
                station_list.append(dict(
                sha1=station_sha1,
                name=session.query(Station).filter_by(sha1 =station_sha1).one().name
                ))
        else :
            pass
    except Exception,e:
        ajax_logger.error(str(e))
        print e
    #油品
    if promotion_type == '0':
        rsdic['station_list'] = station_list
        return HttpResponse(json.dumps(rsdic))
    #便利店商品
    elif promotion_type == '1':
        try:
            objs = session.query(StoreItem).filter_by(comp_id = comp_id).all()
            for obj in objs:
                rsdic['goods_list'].append(dict(
                    name=obj.name,
                    id = obj.id
                    ))
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = Status().getReason(rsdic['ret'])
        finally:
            return HttpResponse(json.dumps(rsdic))
    #车后服务
    elif promotion_type == '2':
        try:
            objs = session.query(ServiceInformation).filter_by(comp_id=comp_id).all()
            for obj in objs:
                rsdic['goods_list'].append(dict(
                    name=obj.title,
                    id=obj.id
                    ))
        except Exception, e:
            print e
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = Status().getReason(rsdic['ret'])
    else :
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取目标用户
#输入: 无
#输出:  目标有户群数据
def get_target_audience(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['obj'] = []
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        s = request.get_session()
        try:
            groups = s.query(TargetAudience).filter_by(comp_id=comp_id).all()
        except:
            groups = []
        for obj in groups:
            rsdic['obj'].append(dict(
                group_name = obj.group_name,
                id = obj.id
                ))
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#默认积分规则修改
#输入:  修改参数
#输出:  修改状态
def update_score_rule(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = '设置成功'
    base_point = float(request.GET['base_point'])
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        goods = session.query(StoreItem).filter_by(comp_id=comp_id).all()
        for good in goods :
            item_sha1 = good.sha1
            price = good.price
            try:
                goodScoreRelation = session.query(ItemScoreRule).filter_by(item_sha1 = item_sha1).one()
                goodScoreRelation.score_ratio = int(base_point * price)
                try:
                    session.add(goodScoreRelation)
                    session.commit()
                except Exception,e :
                    session.rollback()
                    ajax_logger.error(str(e))
                    rsdic['ret'] = Status.UNKNOWNERR
                    rsdic['info'] = "修改商品积分系数失败"
            except Exception,e:
                score_ratio = int(base_point * price)
                user_source = get_current_user(request).user_source
                goodScoreRelation = ItemScoreRule(
                        comp_id = comp_id,
                        item_sha1 = item_sha1,
                        score_ratio = score_ratio
                    )
                try:
                    session.add(goodScoreRelation)
                    session.commit()
                except Exception ,e:
                    session.rollback()
                    ajax_logger.error(str(e))
                    rsdic['ret'] = Status.UNKNOWNERR
                    rsdic['info'] = "添加商品积分系数失败"

    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取商品积分系数
#输入:  商品pos_id
#输出:  商品积分系数
def get_good_score_ratio(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    user = get_current_user(request)
    comp_id = user.comp_id
    if request.GET.has_key("pos_id"):
        pos_id = request.GET['pos_id']
        session = request.get_session()
        try:
            good = session.query(StoreItem).filter_by(comp_id=comp_id,pos_id = pos_id).one()
            obj = session.query(ItemScoreRule).filter_by(item_sha1 = good.sha1).one()
            rsdic['obj'] = {
                'good_id':good.id,
                'name' : good.name,
                'score_ratio':obj.score_ratio,
                'price':good.price
            }
        except Exception,e :
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['ret'] = "该商品不存在"
    else :
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['ret'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#修改商品积分系数
#输入: 商品id , 积分系数
#输出:  修改状态
def alter_good_score_ratio(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = "修改成功"
    good_id = int(request.GET['good_id'])
    score_ratio = int(request.GET['score_ratio'])
    user = get_current_user(request)
    comp_id = user.comp_id
    try:
        session = request.get_session()
        good = session.query(StoreItem).filter_by(id = good_id).one()
        goodScoreRelation = session.query(ItemScoreRule).filter_by(comp_id=comp_id,item_sha1 = good.sha1).one()
        goodScoreRelation.score_ratio = score_ratio
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "修改失败"
    finally:
        return HttpResponse(json.dumps(rsdic))

#修改用户等级积分系数
#输入: 修改参数
#输出: 修改状态
def alter_level_score_ratio(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = "提交成功"
    score_range_list = json.loads(request.GET['range_list'])
    score_ratio_list = json.loads(request.GET['ratio_list'])
    try:
        users = CustomerAccount.objects.all()
        session = request.get_session()
        i = 0
        for score_range in score_range_list:
            i = i + 1
            #更新等级范围
            userScoreRelation = session.query(UserScoreRule).filter_by(level=i).one()
            userScoreRelation.level_range = score_range
            try:
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "更新等级积分范围失败"
        for user in users:
            all_score = user.all_score
            i = 0
            for score_range in score_range_list:
                i = i + 1
                #score_range等级范围 是一个字符串
                if len(score_range.split(":")) == 2:
                    if all_score in range(int(score_range.split(":")[0]),int(score_range.split(":")[1])):
                        user.score_rank = i
                        user.save()
                        break
                else :
                    if i == 1:
                        if all_score in range(0,int(score_range.split(":")[0])):
                            user.score_rank = i
                            user.save()
                            break
                    elif i == 5 :
                        if all_score in range(int(score_range.split(":")[0]),10000):
                            user.score_rank = i
                            user.save()
                            break
        level = 0
        for ratio in score_ratio_list:
            level = level + 1
            try:
                level_ratio = session.query(UserScoreRule).filter_by(level = level).one()
                level_ratio.score_ratio = ratio
                try:
                    session.commit()
                except Exception,e:
                    ajax_logger.error(str(e))
                    rsdic['ret'] = Status.UNKNOWNERR
                    rsdic['info'] = "更新用户等级积分系数失败"
            except :
                userScoreRelation = UserScoreRule(
                        user_source = get_current_user(request).user_source,
                        level = level ,
                        score_ratio = int(ratio)

                    )
                session.add(userScoreRelation)
                try:
                    session.commit()
                except Exception,e:
                    ajax_logger.error(str(e))
                    rsdic['ret'] = Status.UNKNOWNERR
                    rsdic['info'] = "添加用户等级积分系数失败"


    except Exception,e:
        ajax_logger.error(str(e))
        rsdic[ret] = Status.UNKNOWNERR
        rsdic['info'] = "提交失败"
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取等级\积分信息
#输入:  无
#输出:  积分等级数据
def get_score_level_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['objs'] = []
    try:
        session = request.get_session()
        info_objs = session.query(UserScoreRule).order_by('level').all()
        for obj in info_objs:
            rsdic['objs'].append(dict(
                    id = obj.id,
                    user_source = obj.user_source,
                    level = obj.level,
                    score_ratio = obj.score_ratio,
                    level_range = obj.level_range
                ))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "获取积分规则信息失败"
    return HttpResponse(json.dumps(rsdic))

#获取可积分兑换商品
#输入:  无
#输出:  可积分兑换商品详情
def get_exchange_good_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['objs'] = []
    try:
        session = request.get_session()
        user = get_current_user(request)
        comp_id = user.comp_id
        goods = session.query(StoreItem).filter_by(comp_id=comp_id).all()
        for good in goods :
            #exchange_score为-1表示为不可积分兑换商品
            if good.exchange_score != -1:
                rsdic['objs'] .append(dict(
                        good_id = good.id,
                        pos_id = good.pos_id,
                        name = good.name,
                        exchange_score = good.exchange_score
                    ))
            else:
                continue
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "获取和积分兑换商品失败"
    finally:
        return HttpResponse(json.dumps(rsdic))

#获取会员商品详情
#输入: 商品pos_id
#输出:  会员商品列表
def get_member_good_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['objs'] = []
    pos_id = request.GET['pos_id']
    try:
        session = request.get_session()
        user = get_current_user(request)
        comp_id = user.comp_id
        #pos_id 商品的条形码
        if pos_id == "" :
            goods = session.query(StoreItem).filter_by(comp_id = comp_id).all()
            for good in goods :
                if good.member_option != -1:
                    rsdic['objs'] .append(dict(
                            good_id = good.id,
                            pos_id = good.pos_id,
                            name = good.name
                        ))
                else :
                    pass
        else :
            try :
                storeGood = session.query(StoreItem).filter_by(pos_id =pos_id,comp_id =comp_id).one()
                good = session.query(MemberDiscountInfo).filter_by(item_sha1 = storeGood.sha1,\
                    comp_id=comp_id).one()
                rsdic['objs'] .append(dict(
                            pos_id = storeGood.pos_id,
                            name = storeGood.name,
                            comp_id = good.comp_id,
                            ordinary_discount = good.ordinary_discount ,
                            gold_discount = good.gold_discount
                        ))
            except Exception,e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "查询会员商品失败"
                return HttpResponse(json.dumps(rsdic))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "获取会员商品失败"
    finally:
        return HttpResponse(json.dumps(rsdic))

#删除会员商品
#输入:  会员商品pos_id
#输出:  删除状态
def delete_member_good(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    member_pos_id = request.GET["member_pos_id"]
    user = get_current_user(request)
    comp_id = user.comp_id
    try :
        session = request.get_session()
        try :
                obj = session.query(StoreItem).filter_by(comp_id = comp_id,pos_id = member_pos_id).one()
                member_good = session.query(MemberDiscountInfo).filter_by(comp_id=comp_id,item_sha1=obj.sha1).one()
                obj.member_option = -1
                session.delete(member_good)
        except Exception,e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "会员商品不存在!"
                return HttpResponse(json.dumps(rsdic))
        session.commit()
    except Exception,e :
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "删除会员商品失败!"
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))


#获取用户积分详情
#输入: 卡号
#输出:  用户积分详情
def get_score_record_details(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['obj'] = []
    cardnum = request.GET['cardnum']
    try:
        session  = request.get_session()
        user = session.query(CustomerAccount).filter_by(cardnum=cardnum).one()
        rsdic['obj'].append(dict(
                user_id = user.id,
                cardnum = user.cardnum,
                name = user.name,
                score = user.score,
                score_rank = user.score_rank,
                all_score = user.all_score,
            ))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.USERNOTEXIST
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#上传图片
def jquery_upload_images(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    imagebinarydata = request.FILES['files'].read()
    name = request.FILES['files'].name
    size = request.FILES['files'].size
    import hashlib
    sha1=hashlib.sha1()
    sha1.update(str(imagebinarydata))
    sha1=sha1.hexdigest()
    image_sha1 = sha1
    import base64
    imagebinarydata = base64.b64encode(imagebinarydata)
    try :
        session = request.get_session()
        session.query(FileImage).filter_by(sha1 = sha1).one()
    except :
        user = get_current_user(request)
        imageObj = FileImage(
                            sha1 = sha1,
                            image = imagebinarydata ,
                            image_name = name,
                            image_size = size,
                            author = user.name,
                            time = str(datetime.datetime.now())
                        )
        session.add(imageObj)
        try :
                session.commit()
        except Exception,e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            return HttpResponse(json.dumps(rsdic))
    rsdic['image_sha1'] = sha1
    return HttpResponse(json.dumps(rsdic))

#添加可积分兑换商品
#输入: 商品pos_id
#输出:  添加状态
def add_exchange_score_good(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    user  = get_current_user(request)
    comp_id = user.comp_id
    if not request.GET.has_key("exchange_pos_id") :
            pos_id = request.GET['good_pos_id']
            exchange_score = request.GET['good_exchange_score']
            try :
                session = request.get_session()
                try :
                    good = session.query(StoreItem).filter_by(comp_id =comp_id,pos_id = pos_id).one()
                except Exception,e:
                    ajax_logger.error(str(e))
                    rsdic['ret'] = Status.UNKNOWNERR
                    rsdic['info'] = "商品不存在"
                    return HttpResponse(json.dumps(rsdic))
                #-1:表示不是可积分兑换商品
                if good.exchange_score != -1 :
                    rsdic['ret'] = Status.UNKNOWNERR
                    rsdic['info'] = "商品已存在于可积分兑换列表"
                    return HttpResponse(json.dumps(rsdic))
                else :
                    good.exchange_score = int(exchange_score)
                    session.commit()
                    rsdic['good_name'] = good.name
            except Exception,e :
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "添加可积分兑换商品失败"
    else :
        #从可积分兑换商品列表删除
        exchange_pos_id = request.GET["exchange_pos_id"]
        try :
                session = request.get_session()
                good = session.query(StoreItem).filter_by(comp_id = comp_id,pos_id = exchange_pos_id).one()
                good.exchange_score = -1
                try :
                    session.commit()
                except Exception,e:
                    ajax_logger.error(str(e))
                    rsdic['ret'] = Status.UNKNOWNERR
                    rsdic['info'] = "从可积分兑换商品列表删除失败"
                    return HttpResponse(json.dumps(rsdic))
        except Exception,e:
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "商品不存在"
                return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#添加会商品
#输入:  商品pos_id ,优惠参数
#输出:  添加状态
def add_member_good(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = "成功添加会员商品"
    user = get_current_user(request)
    comp_id = user.comp_id
    pos_id = request.GET['pos_id']
    ordinary_member_discount = request.GET['ordinary_member_discount']
    gold_member_discount = request.GET['gold_member_discount']
    try :
        session = request.get_session()
        try :
            obj = session.query(StoreItem).filter_by(comp_id=comp_id,pos_id= pos_id).one()
        except Exception,e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "商品不存在!"
            return HttpResponse(json.dumps(rsdic))
        #-1:表示不是会员商品
        if not obj.member_option == -1 :
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "已经是会员商品!"
            return HttpResponse(json.dumps(rsdic))
        else :
            obj.member_option = 0
            member_good = MemberDiscountInfo(
                    comp_id = comp_id,
                    item_sha1 = obj.sha1,
                    ordinary_discount = ordinary_member_discount,
                    gold_discount = gold_member_discount
                )
            session.add(member_good)
            try :
                session.commit()
            except Exception,e:
                print e
                ajax_logger.error(str(e))
                rsdic['ret'] = Status.UNKNOWNERR
                rsdic['info'] = "添加失败"
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "添加失败"
    return HttpResponse(json.dumps(rsdic))

#修改会员商品优惠
#输入:  商品pos_id ,优惠参数
#输出:  修改状态
def alter_good_member_discount(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = "修改优惠信息成功!"
    pos_id = request.GET['pos_id']
    ordinary_member_discount = request.GET['ordinary_member_discount']
    gold_member_discount = request.GET['gold_member_discount']
    user = get_current_user(request)
    comp_id = user.comp_id
    session =request.get_session()
    try :
        good = session.query(StoreItem).filter_by(comp_id=comp_id,pos_id=pos_id).one()
        good_member = session.query(MemberDiscountInfo).filter_by(comp_id=comp_id,item_sha1 = good.sha1).one()
        good_member.ordinary_discount = ordinary_member_discount
        good_member.gold_discount = gold_member_discount
        try :
            session.commit()
        except Exception,e:
            ajax_logger.error(str(e))
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "修改会员优惠信息失败!"
            return HttpResponse(json.dumps(rsdic))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "查询会员商品失败!"
    return HttpResponse(json.dumps(rsdic))

#获取行车轨迹
#输入: 卡号 , 时间范围
#输出:  位置点列表
def get_user_driving_trace(request):
    rsdic = {}
    rsdic['ret'] =Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    start_time = request.GET['start_time']
    end_time = request.GET['end_time']
    cardnum = request.GET['cardnum']
    rsdic['points'] = []
    try :
        pointTraces = WheelAccountLocation.objects.filter(user_id = cardnum).all()
        #行车轨迹点
        if len(pointTraces) < 3 :
            rsdic['ret'] = Status.UNKNOWNERR
            rsdic['info'] = "当前时段没有行车轨迹信息"
            return HttpResponse(json.dumps(rsdic))
        for point in pointTraces :
            rsdic['points'].append(dict(
                    longitude = point.geo_y,
                    latitude = point.geo_x
                ))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "获取行车轨迹信息失败"
        rsdic['points'] = []
    return HttpResponse(json.dumps(rsdic))

#营销活动列表
#输入:  营销活动id
#输出:   营销活动列表
def promotion_good_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['promotion_goods'] = []
    promotion_id = request.GET['promotion_id']
    user = get_current_user(request)
    comp_id = user.comp_id
    try :
        session = request.get_session()
        promotion_good_list = session.query(PromotionInfo).filter_by(promotion_id = promotion_id).all()
        for good in promotion_good_list :
            promotion_type = good.promotion_type
            obj_id = good.obj_id
            #0 油品，1 非油品，2车后服务
            if promotion_type == 0 :
                site_code = session.query(Station).filter_by(sha1=good.site_code).one().site_code
                station_name = session.query(Station).filter_by(sha1=good.site_code).one().name
                promotion_type = "油品优惠"
                try :
                    name = session.query(StationFuelType).filter_by(station = site_code,\
                        barcode = good.obj_id).one().description
                except :
                    name = ""
            elif promotion_type == 1 :
                try :
                    name = session.query(StoreItem).filter_by(id = obj_id).one().name
                    try :
                        station_name = session.query(Station).filter_by(sha1=good.site_code).one().name
                    except :
                        station_name = ""
                except :
                    name = ""
                promotion_type = "便利店商品优惠"
            elif promotion_type == 2 :
                try :
                    name = session.query(ServiceInformation).filter_by(id = obj_id).one().title
                    try :
                        station_name = session.query(Station).filter_by(sha1=good.site_code).one().name
                    except :
                        station_name = ""
                except :
                    name = ""
                promotion_type = "车后服务优惠优惠"
            else :
                pass
            rsdic['promotion_goods'].append(dict(
                    discount = good.discount,
                    site_code = station_name ,
                    obj_id = obj_id,
                    name = name,
                    promotion_type = promotion_type
                ))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = "获取商品优惠信息失败!"
    return HttpResponse(json.dumps(rsdic))

#获取营销活动推送的商品
#输入:  营销活动id
#输出:   营销活动推送的商品列表
def get_promotion_goods_lanch_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['objs'] = []
    promotion_id = int(request.GET['promotion_id'])
    try :
        session = request.get_session()
        userTargedPromotions = session.query(UserTargetedPromotion\
            ).filter_by(promotion_id = promotion_id).all()
        for userTargedPromotion in userTargedPromotions :
            #用户类型 user_id 0:表示所有用户
            if int(userTargedPromotion.user_type) == 1 and int(userTargedPromotion.user_id) == 0 :
                user_type = "所有用户推送"
                user_id  = "所有用户"
            elif int(userTargedPromotion.user_type) == 0 :
                user_type = "用户群组推送"
                try :
                    user_id = session.query(TargetAudience).filter_by(id = userTargedPromotion.user_id).one().group_name
                except Exception,e:
                    continue
            elif int(userTargedPromotion.user_type) == 1 and not userTargedPromotion.user_id == 0 :
                user_type = "单个用户推送"
                try :
                    user_id  = session.query(CustomerAccount).filter_by(cardnum = str(userTargedPromotion.user_id)).one().name
                    if not user_id :
                        user_id = "无"
                except Exception,e:
                    continue
            else :
                continue
            #0表示是油品，1表示是便利店商品， 2表示是车后服务，3是广告
            if userTargedPromotion.obj_type == 0 :
                obj_type = "油品"
                obj_id = userTargedPromotion.obj_id
            elif userTargedPromotion.obj_type == 1 :
                obj_type = "便利店商品"
                try :
                    obj_id = session.query(StoreItem).filter_by(id = userTargedPromotion.obj_id).one().pos_id
                except Exception,e:
                    continue
            elif userTargedPromotion.obj_type == 2 :
                continue
            elif userTargedPromotion.obj_type == 3 :
                continue
            else :
                continue
            rsdic['objs'].append(dict(
                    user_type = str(user_type),
                    user_id = str(user_id),
                    obj_type = str(obj_type),
                    obj_id = str(obj_id)
                ))
    except Exception,e:
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    return HttpResponse(json.dumps(rsdic))

#2015-7-17
#获取公司类型
#输入 : 无
#输出 : [{"value":1,"name":"中石油"},]
def get_comp_type(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['objs'] =  []
    try :
        comp_type = UserCardType().KEYS
        for key in comp_type.keys() :
            rsdic['objs'].append(dict(
                    value = comp_type[key],
                    name = key
                ))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.QUERY_COMPY_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        rsdic['data'] = []
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取公司列表
def get_comp_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['objs'] =  []
    session = request.get_session()
    try :
        comp_list = session.query(GCompany).all()
        for comp in comp_list :
            rsdic['objs'].append(dict(
                    value = comp.id,
                    name = comp.name
                ))
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.QUERY_COMPANY_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        rsdic['data'] = []
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#查询app用户
def get_app_user_setting(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    name = request.GET['name']
    rsdic['data'] = {}
    try :
        session = request.get_session()
        app_user = session.query(CustomerAccount).filter_by(name = name).one()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.USERNOTEXIST
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    rsdic['data']['name'] = name
    rsdic['is_pay_in_advance'] = app_user.is_pay_in_advance
    return HttpResponse(json.dumps(rsdic))

#修改app用户权限
def alter_app_user_settting(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    name = request.GET['name']
    is_pay_in_advance = int(request.GET['is_pay_in_advance'])
    try :
        session = request.get_session()
        app_user = session.query(CustomerAccount).filter_by(name = name).one()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.USERNOTEXIST
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    #是否是测试用户  0: 不是 1:是
    if is_pay_in_advance == 0:
        app_user.is_pay_in_advance = 1
    else :
        app_user.is_pay_in_advance = 0
    try :
        session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.ALERT_APP_USER_SETTING_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#查询退款订单
def get_refund_order_info(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['refund_order_list'] = []
    vcard_id  = request.GET['vcard_id']
    id_card  = request.GET['id_card']
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    #用户验证
    try :
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
    except Exception,e:
        rsdic['ret'] = Status.USERNOTEXIST
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    #验证用户身份
    if not user.id_card == id_card :
        rsdic['ret'] = Status.USER_ID_CARD_CHECK_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    #查询退款订单列表
    refund_order_list = session.query(CustomerAccountTransaction).filter_by(vcard_id = vcard_id,status = 5).all()
    if len(refund_order_list) == 0 :
        rsdic['ret'] = Status.HAS_NOT_REFUND_ORDER
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    #返回退款订单列表
    for refund_order in refund_order_list :
        try :
            if refund_order.station_sha1 :
                order_seller_name = session.query(Station).filter_by(sha1 = refund_order.station_sha1).one().name
            else :
                order_seller_name = '至察数据'
            try :
                refund_order.success_time = str(datetime.datetime.now())
                session.commit()
            except Exception,e:
                rsdic['ret'] = Status.ALTER_ORDER_STATUS_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic))
        except Exception,e:
            rsdic['ret'] = Status.QUERY_ORDER_ERROR
            rsdic['info'] = Status().getReason(rsdic['ret'])
            rsdic['data'] = []
            return HttpResponse(json.dumps(rsdic))
        rsdic['refund_order_list'].append(dict(
                order_sha1 = refund_order.sha1,
                order_purchase_time = '暂无',
                order_refund_submit_time = str(refund_order.application_time).split(".")[0],
                order_status = refund_order.status,
                order_seller_name = order_seller_name,
                order_item_name = refund_order.item_name,
                order_time = str(refund_order.time).split(".")[0],
                order_count = refund_order.item_count,
                order_type = refund_order.trans_type,
                order_money = refund_order.item_total,
            ))
    return HttpResponse(json.dumps(rsdic))

#确认退款
def confirm_order_refund(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['refund_order_list'] = []
    order_sha1 = request.GET['order_sha1']
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    #查询订单
    try :
        refund_order = session.query(CustomerAccountTransaction).filter_by(sha1 = order_sha1).one()
    except Exception,e:
        rsdic['ret'] = Status.QUERY_ORDER_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        rsdic['data'] = []
        return HttpResponse(json.dumps(rsdic))
    #将退款金额转入申请退款帐号的虚拟账户
    vcard_id = refund_order.vcard_id
    #验证用户账户信息
    try :
        app_user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
        account = session.query(CustomerCompInfo).filter_by(vcard_id = vcard_id,comp_id=0).one()
    except Exception,e:
        ajax_logger.error(str(e))
        result['ret'] = Status.QYERY_ACCOUNT_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    #修改用户虚拟卡余额和总账户余额 或积分账户
    if refund_order.trans_type == 4 :
        app_user.score = app_user.score + refund_order.item_total
    else :
        account.balance = account.balance + refund_order.item_total
        app_user.balance = app_user.balance  + refund_order.item_total
    #修改订单状态
    refund_order.status = 6
    refund_order.success_time = str(datetime.datetime.now())
    try :
        session.commit()
    except Exception,e:
        rsdic['ret'] = Status.REFUND_ORDER_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        rsdic['data'] = []
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#第三方支付完成修改订单状态并做相应的处理
def purchase_complete_by_the_third(request):
    #微信支付
    path_info = request.get_full_path()
    #if request.META.has_key("PATH_INFO") :
    #    path_info = request.META['PATH_INFO']
    ajax_logger.info("path_info:"+path_info)
    if path_info.find("out_trade_no") != -1 :
        out_trade_no = path_info.split("=")[1].strip()
        ajax_logger.info("wx_out_trade_no:"+str(out_trade_no))
    else :
            #支付宝支付
            #检查请求的方法类型
            if request.method == 'GET':
                #检查是否有out_trade_no
                if not request.GET.has_key("out_trade_no") :
                    ajax_logger.info("no out trade no")
                    return HttpResponse("fail")
                out_trade_no = request.GET['out_trade_no']
            elif request.method == 'POST':
                if not request.POST.has_key("out_trade_no") :
                    ajax_logger.info("no out trade no")
                    return HttpResponse("fail")
                out_trade_no = request.POST['out_trade_no']
            else :
                ajax_logger.info("request method error")
                return HttpResponse("fail")
    #打印回调参数
    ajax_logger.info("the_purchase_complete_by_the_third"+str(out_trade_no))
    try :
        session = request.get_session()
        order = session.query(CustomerAccountTransaction).filter_by(sessionid = out_trade_no).one()
    except Exception,e:
        ajax_logger.error(str(e))
        return HttpResponse("fail")
    #修改订单状态为已支付
    if order.status == 1 :
        return HttpResponse("success")
    else :
        order.status = 1
    try :
        session.commit()
        #修改用户积分
        if order.trans_type == 1 or order.trans_type == 2 or order.trans_type == 3  :
            #查询用户信息
            try :
                user = session.query(CustomerAccount).filter_by(cardnum = order.vcard_id).one()
            except Exception,e:
                ajax_logger.error(str(e))
                return HttpResponse("fail")
            user.score = user.score + int(order.item_total)
            user.all_score = user.all_score + int(order.item_total)
            try :
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                return HttpResponse("fail")
        #如果为充值,则做以下处理
        if order.trans_type == 0 :
            vcard_id = order.vcard_id
            comp_id = order.comp_id
            money = order.item_total
            #用户验证
            try :
                session = request.get_session()
                user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
            except Exception,e:
                ajax_logger.error(str(e))
                return HttpResponse("fail")
            #验证用户账户信息
            try :
                account = session.query(CustomerCompInfo).filter_by(vcard_id = vcard_id,
                    comp_id=comp_id).one()
            except Exception,e:
                ajax_logger.error(str(e))
                return HttpResponse("fail")
            #修改账户余额
            account.balance = account.balance  + money
            user.balance = user.balance + money
            try :
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
                return HttpResponse("fail")
    except Exception,e:
        ajax_logger.error(str(e))
        return HttpResponse("fail")
    return HttpResponse("success")

#获取公司订单列表
def get_comp_order_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['order_list'] = []
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    order_list = session.query(CustomerAccountTransaction).filter_by(comp_id = comp_id).order_by("time desc").all()
    try :
            for order in order_list :
                if order.status == 0:
                    status = '交易未支付'
                elif order.status == 1:
                    status = '等待取货'
                elif order.status == 2:
                    status = '交易完成'
                elif order.status == 3:
                    status = '交易关闭'
                elif order.status == 4:
                    status = '已预订'
                elif order.status == 5: 
                    status = '申请退款成功'
                elif order.status == 6 :
                    status = '退款成功'
                else:
                    status = '交易关闭'
                try :
                    station = session.query(Station).filter_by(sha1 = order.station_sha1).one()
                    address = station.name
                except Exception ,e:
                    try :
                            comp = session.query(GCompany).filter_by(id = comp_id).one()
                            address = comp.name
                    except Exception,e:
                            address = ''

                #部分显示移动端用户vcard_id
                vcard_id = order.vcard_id
                vcard_len = len(vcard_id)
                vcard_hide_string = vcard_id[0:3] + '***' + vcard_id[vcard_len-3:vcard_len]
                rsdic['order_list'].append(dict(
                        vcard_id = vcard_hide_string,
                        comp_id = order.comp_id,
                        trans_type = order.trans_type,
                        station_sha1 = order.station_sha1,
                        pump_id = order.pump_id,
                        item_sha1 = order.item_sha1,
                        good_name = order.item_name, 
                        item_count = order.item_count,
                        time = str(order.time).split(" ")[0],
                        sha1 = order.sha1,
                        seller_sha1 = order.seller_sha1,
                        worker_sha1 = order.worker_sha1,
                        promotion_id = order.promotion_id,
                        item_total = order.item_total,
                        status_flag = order.status,
                        sessionid = order.sessionid,
                        application_time = str(order.application_time).split(' ')[0],
                        success_time = str(order.success_time).split(' ')[0],
                        status = status,
                        station_name = address,
                    ))
    except Exception,e:
        rsdic['ret'] = Status.QUERY_ORDER_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#根据虚拟卡号查询移动用户订单列表
def search_order_by_vcard_id(request) :
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['order_list'] = []
    vcard_id = request.GET['vcard_id']
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    order_list = session.query(CustomerAccountTransaction).filter_by(comp_id = comp_id,
        vcard_id=vcard_id).order_by("time desc").all()
    try :
            for order in order_list :
                if order.status == 0:
                    status = '交易未支付'
                elif order.status == 1:
                    status = '等待取货'
                elif order.status == 2:
                    status = '交易完成'
                elif order.status == 3:
                    status = '交易关闭'
                elif order.status == 4:
                    status = '已预订'
                elif order.status == 5: 
                    status = '申请退款成功'
                elif order.status == 6 :
                    status = '退款成功'
                else:
                    status = '交易关闭'
                try :
                    station = session.query(Station).filter_by(sha1 = order.station_sha1).one()
                    address = station.name
                except Exception ,e:
                    try :
                            comp = session.query(GCompany).filter_by(id = comp_id).one()
                            address = comp.name
                    except Exception,e:
                            address = ''

                #部分显示移动端用户vcard_id
                vcard_id = order.vcard_id
                vcard_len = len(vcard_id)
                vcard_hide_string = vcard_id[0:3] + '***' + vcard_id[vcard_len-3:vcard_len]
                rsdic['order_list'].append(dict(
                        vcard_id = vcard_hide_string,
                        comp_id = order.comp_id,
                        trans_type = order.trans_type,
                        station_sha1 = order.station_sha1,
                        pump_id = order.pump_id,
                        item_sha1 = order.item_sha1,
                        good_name = order.item_name, 
                        item_count = order.item_count,
                        time = str(order.time).split(" ")[0],
                        sha1 = order.sha1,
                        seller_sha1 = order.seller_sha1,
                        worker_sha1 = order.worker_sha1,
                        promotion_id = order.promotion_id,
                        item_total = order.item_total,
                        status_flag = order.status,
                        sessionid = order.sessionid,
                        application_time = str(order.application_time).split(' ')[0],
                        success_time = str(order.success_time).split(' ')[0],
                        status = status,
                        station_name = address,
                    ))
    except Exception,e:
        rsdic['ret'] = Status.QUERY_ORDER_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取用户的最喜爱的商品
def get_app_user_favourite_goods(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['store_good_list'] = []
    favourite_nonfuel_product_list = []
    session = request.get_session()
    user = get_current_user(request)
    comp_id = user.comp_id 
    #获取与该公司关联的app用户
    app_account_list = get_associate_comp_vcardid_list(comp_id)
    for vcard_id in app_account_list :
        try :
            user_profile = session.query(CustomerProfile).filter_by(vcard_id=vcard_id).one()
        except Exception,e:
            ajax_logger.error(str(e))
            continue
        #获取用户最喜爱的商品列表
        if user_profile.favourite_nonfuel_products == '' :
            continue
        favourite_nonfuel_products = json.loads(user_profile.favourite_nonfuel_products)
        favourite_nonfuel_product_list.extend(favourite_nonfuel_products)
    favourite_nonfuel_product_list = list(set(favourite_nonfuel_product_list))
    #查询商品
    for pos_id in favourite_nonfuel_product_list :
        try :
            good = session.query(StoreItem).filter_by(comp_id=comp_id,pos_id = pos_id).one()
        except Exception,e:
            ajax_logger.error("当前系统没有该商品")
            continue
        rsdic['store_good_list'].append(dict(
                pos_id = pos_id,
                good_name = good.name
            ))
    return HttpResponse(json.dumps(rsdic))

#设置系统语言
def language_type_setting(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    language_type = int(request.GET['language_type'])
    try :
        #设置语言
        if language_type == 0 :
            request.session['django_language'] = 'en'
        else :
            request.session['django_language'] = 'zh-cn'
    except Exception,e:
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#意见反馈
#输入：暂无输入
#输出：用户的反馈信息
def get_user_feed_back(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['obj'] = []
    session = request.get_session()
    user = get_current_user(request)
    if not user.type == 3:
        rsdic['ret'] = Status.HAS_NO_ACCESS
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    try:
        #fbInfos = s.query(AppUserFeedBack).all()
        Utype = request.GET['Utype']
        if(Utype == "0"):
            fbInfos = AppUserFeedBack.objects.filter(type=0).all()

        elif(Utype == "1"):
            fbInfos = AppUserFeedBack.objects.filter(type=1).all()

        for fbInfo in fbInfos:
            rsdic['obj'].append(dict(
                                cardnum = fbInfo.vcard_id,
                                time = str(fbInfo.time).split(' ')[0],
                                content = fbInfo.content,
                                ))
    except Exception, e:
        print e
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
    return HttpResponse(json.dumps(rsdic))