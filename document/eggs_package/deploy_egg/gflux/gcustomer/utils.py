#-*- coding: utf-8 -*-
import hashlib
import math
from gcustomer.models import *
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import Trans,FuelTypeRelation,StationFuelType
from gcustomer.models import *
from gcustomer.apps.jiachebao.models import *
import datetime,pdb,json,logging,gearman
from django.core.cache import cache
from django.conf import settings
from gcustomer.status  import *
from sqlalchemy.sql import select, and_, or_, func
from sqlalchemy import update

ajax_logger=logging.getLogger('ajax')

def compute_site_sha1(source_type, site_name) :
        s= hashlib.sha1()
        c=str(source_type)+"/"+site_name
        s.update(c)
        sha1=s.hexdigest()
        return sha1

#检查ajax请求方式，并检查是否是在线用户
def checkAjaxRequest(request,method):
    rsdic={}
    ret=Status.OK
    rsdic['ret']=ret
    rsdic['info']=Status().getReason(ret)
    if request.method !=method :
        #error
        ret=Status.REQMETHODERROR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return rsdic
    #check user status
    ret=checkUserOnlineStatus(request)
    if ret!=Status.LOGINSUCCESS:
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return rsdic
    return rsdic

#检查用户是否登录
def checkUserOnlineStatus(request,username=None):
    ajax_logger.info("username"+str(username))
    if username==None:
        username=request.session.get('username',None)
    #username check
    if username!=None:

        #session check
        connected_session_id=cache.get('%s_sessionid'%username)
        ajax_logger.info("session_id"+str(connected_session_id))
        sid=request.session.session_key
        #如果没有打开用户登陆保护
        if not settings.OPEN_USER_LOGIN_PROTECT:
            connected_session_id = sid
        if sid is None:
            request.session.save()
            sid=request.session.session_key

        #已经离线或未登陆
        if connected_session_id == None or sid==None:
            return Status.NOTLOGGEDIN

        #已再别处登陆
        elif connected_session_id!=sid:
            return Status.LOGINED_ON_OTHER_SIDE

        else:
            #更新缓存过期时间
            cache.set('%s_sessionid'%username,sid,settings.LOGIN_STATUS_KEEP)

            return Status.LOGINSUCCESS
    else:
        return Status.NOTLOGGEDIN


#params 经度纬度 return km
def distance(lng1,lat1,lng2,lat2):
    radlat1=math.radians(lat1)
    radlat2=math.radians(lat2)
    a=radlat1-radlat2
    b=math.radians(lng1)-math.radians(lng2)
    s=2*math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(radlat1)*math.cos(radlat2)*math.pow(math.sin(b/2),2)))
    earth_radius=6378.137
    s=s*earth_radius
    if s<0:
        return round(-s,2)
    else:
        return round(s,2)

#get fuel type
def get_fuel_type(request,site_code):
    site_fuel_type = []
    session = request.get_session()
    try:
        fuelObjects = session.query(StationFuelType).filter_by(station = site_code).all()
        for fuel in fuelObjects :
            name_list = []
            for obj in site_fuel_type : name_list.append(obj['name'])
            name = fuel.description
            if name.find('E') :
                name = '#' + str(filter(lambda x:x.isdigit(),name.split('E')[0]))
            else :
                name = '#' + str(filter(lambda x:x.isdigit(),name))
            if name in name_list :
                continue
            barcode = fuel.barcode
            price = fuel.price
            site_fuel_type.append(dict(
                    name = name.split(' ')[0],
                    barcode = barcode,
                    price = price
                ))
    except Exception,e:
        site_fuel_type = []
        return site_fuel_type
    return site_fuel_type


#计算高峰期时段显示
def cal_busy_time(peak_range):
    peak_range = json.loads(peak_range)
    peak_range_string = []
    peak_range_objs = peak_range['creat_list']
    for peak_range_obj in peak_range_objs :
        peak_range_string.append(str(peak_range_obj[0]) + '~' + str(peak_range_obj[1]))
    peak_range_string = str(peak_range_string)[2:len(str(peak_range_string))-2] + u'时'
    return peak_range_string

#计算是否是高峰期
def cal_is_busy(peak_range):
    peak_range = json.loads(peak_range)
    peak_range_objs = peak_range['creat_list']
    for peak_range_obj in peak_range_objs:
            if datetime.datetime.now().hour in range(peak_range_obj[0],peak_range_obj[1]):
                 return 1
    return 0

def cal_site_promotion(proObj,siteObj):
    promotions = []
    promotion = {}
    if proObj :
        for obj in proObj :
            promotion['name'] = obj.name
            promotion['discount_information'] = obj.discount_information
            promotion['start_time'] = str(obj.start_time).split(' ')[0]
            promotion['end_time'] = str(obj.end_time).split(' ')[0]
            promotions.append(promotion)
    return promotions

#获取的当前的user
def get_current_user(request):
    username = request.session.get('username',None)
    s = request.get_session()
    user = s.query(GCustomerUser).filter_by(name=username).first()
    return user

def get_user_type(request):
    user_type = get_current_user(request)
    if user_type :
        return user_type.type
    return 4

#计算单个用户是否为加油流失客户，距离最后一次加油日期如果超过七天，则视为加油流失客户,返回：0 流失客户  1 非流失客户
def cal_loss_oil_user(cardnum,site_code):
    try:
        #计算结果
        cardnum = cardnum['cardnum']
        site = site_code
        create_session = get_dash_session_maker(site)
        s = create_session()
        sql='select * from fact_trans where cardnum=\'%s\' and trans_type=0 order by timestamp desc limit(1);'%int(cardnum)
        ret=s.execute(sql).fetchall()
	if not ret:
	    return 1
        last_time=ret[0].timestamp
        now_time=datetime.datetime.now()
        subtract_time=(now_time-last_time).days
        s.close()

        #应该是不可能为空的,如果为空则假设该用户不属于流失客户
        if not ret :
            return 1

        #如果日期差大于7天，证明是加油流失客户，否则不属于流失客户
        if subtract_time>7:
            return 0
        else:
            return 1
    except Exception,e:
        print e


#计算所有的加油流失客户
def cal_all_loss_oil_user():
    result=[]
    try:
        create_session = get_dash_session_maker()
        s = create_session()

        #查询所有的驾车宝用户
        users = s.query(CustomerProfile).all()
        for user in users:
            rets = []

            try:
                #根据用户虚拟卡号查询所有绑定实体卡号的公司
                comps = s.query(CustomerCompInfo).filter_by(vcard_id=user.vcard_id).all()

                #查询虚拟卡在某个公司下的实体卡
                for comp in comps:
                    cardnums = json.loads(comp.card_list)

                    #查询该公司下的所有油站列表
                    stations = s.query(Station).filter_by(comp_id=comp.comp_id).all()
                    station_list = []

                    for station in stations:

                        #计算某张实体卡在某个公司下的所有加油站的流失情况
                        for cardnum in cardnums:
                            ret = cal_loss_oil_user(cardnum,station.site_code)

                            #如果是该油站的流失客户
                            if ret == 0:
                                rets.append(station.sha1)



            except:
                continue

            #更新数据库
            user.is_oil_loss_customer=json.dumps(rets)
            s.commit()

    except Exception,e:
        print e

#获取某个油站公司的流失客户
def get_all_loss_oil_user(comp_id):
    result={}
    result['data']=[]
    try:
        create_session = get_dash_session_maker()
        session = create_session()

        #查询关联该油站公司的用户画像
        comp_info_list =  session.query(CustomerCompInfo).filter_by(comp_id=comp_id).all()
        for comp_info in comp_info_list :
            #判断该用户是否是该油站的流失客户
            try :
                user = session.query(CustomerProfile).filter_by(vcard_id = comp_info.vcard_id).one()
            except Exception ,e:
                ajax_logger.error(e)
                return result
            if user.is_oil_loss_customer :
                result['data'].append(user.vcard_id)
    except Exception,e:
        ajax_logger.error(e)
        print e
        return result
    return result

#将营销活动划分到对应的人或是群组，将其存储到UserTargedPromotion,并将商品的优惠信息存储到PromotionInfo
def send_promotion_goods_to_customer(request,user_group,promotion_goods,**options):
    try:
        #当前操作用户
        user = get_current_user(request)
        comp_id = user.comp_id
        session = request.get_session()
        promotion_id = options["promotion_id"]
        promotion = session.query(Promotion).filter_by(id =promotion_id).one()
        try :
                #自动推送中给加油流失客户推送,清仓滞销
                if type(user_group) == type([]) :
                    for cardnum in user_group:
                        user = session.query(CustomerProfile).filter_by(vcard_id=cardnum).one()
                        # 取出活动的所有优惠商品
                        #给流失客户推送对应油站该加油用户经常加的油品类型,
                        for promotion_info in promotion_goods:
                            goods_id = promotion_info['name']
                            good_type = promotion_info['type']
                            discount = float(promotion_info['discount'])
                            # 更新到用户活动表中
                            obj = UserTargetedPromotion(
                                promotion_id = promotion_id,
                                user_type = 1,
                                user_id = int(cardnum),
                                obj_type = int(good_type),
                                obj_id = int(goods_id),
                                desc = options['desc'],
                                delivery_type = int(options['delivery_type'])
                            )
                            session.add(obj)
                    for promotion_info in promotion_goods:
                        #将优惠商品存入PromotionInfo
                        for code in promotion_info['site_code'] :
                            try :
                                    promotion_info_good = session.query(PromotionInfo).filter_by(
                                                  promotion_id = promotion_id,
                                                   promotion_type = int(good_type),
                                                   obj_id = int(goods_id),
                                                   discount = discount,
                                                   site_code = code,
                                                   status = 1,
                                        ).one()
                            except  Exception,e:
                                    promotion_info_obj = PromotionInfo(
                                                   promotion_id = promotion_id,
                                                   promotion_type = int(good_type),
                                                   obj_id = int(goods_id),
                                                   discount = discount,
                                                   site_code = code,
                                                   status = 1,
                                    )
                                    session.add(promotion_info_obj)
                    try:
                        session.commit()
                        #调用消息服务器发送我的专享消息
                        try :
                                #对用户群中每一个对象发送消息
                                user_sha1_list = []
                                for user in user_group :
                                    user_sha1_list.append(user)
                                push_my_sale_message(user_sha1_list,promotion,int(good_type))
                        except Exception,e:
                                ajax_logger.error("push_my_sale_message:"+str(e))
                    except Exception,e:
                        session.rollback()
                        return False

                #自动推送中给所有用户推的优惠商品
                elif user_group == 0:
                    promotionObj = session.query(Promotion).filter_by(id = promotion_id).one()
                    for promotion_info in promotion_goods:
                        goods_id = promotion_info['name']
                        good_type= promotion_info['type']
                        discount = float(promotion_info['discount'])
                        if promotion_info.has_key("site_code") :
                                site_code = promotion_info['site_code']
                        else :
                            site_code = ""
                        # 更新到用户活动表中
                        #增加非油品销售额  根据用户画像精准推送
                        if promotionObj.create_type == 1 and promotionObj.auto_create_option == -1 :
                            all_user_list = session.query(CustomerAccount).all()
                            #精准推送计数
                            count = 0
                            for user in all_user_list :
                                cardnum = user.cardnum
                                if cardnum :
                                    try :
                                        customer = session.query(CustomerProfile).filter_by(vcard_id = user.cardnum).one()
                                    except Exception,e:
                                        continue
                                else :
                                    continue
                                recommended_nonfuel_products = json.loads(customer.recommended_nonfuel_products)
                                good_name = session.query(StoreItem).filter_by(id = goods_id).one().name
                                if goods_id in recommended_nonfuel_products  or good_name in recommended_nonfuel_products:
                                        obj = UserTargetedPromotion(
                                            promotion_id = promotion_id,
                                            user_type = 1,
                                            user_id = customer.cardnum,
                                            obj_type = int(good_type),
                                            obj_id = int(goods_id),
                                            desc = options['desc'],
                                            delivery_type = int(options['delivery_type'])
                                            )
                                        session.add(obj)
                                        count = count + 1
                            #没有给任何用户精准推送,则给所有用户推送
                            if count == 0 :
                                obj = UserTargetedPromotion(
                                    promotion_id = promotion_id,
                                    user_type = 1,
                                    user_id =user_group,
                                    obj_type = int(good_type),
                                    obj_id = int(goods_id),
                                    desc = options['desc'],
                                    delivery_type = int(options['delivery_type'])
                                    )
                                session.add(obj)
                        else :
                            obj = UserTargetedPromotion(
                                    promotion_id = promotion_id,
                                    user_type = 1,
                                    user_id =user_group,
                                    obj_type = int(good_type),
                                    obj_id = int(goods_id),
                                    desc = options['desc'],
                                    delivery_type = int(options['delivery_type'])
                                    )
                            session.add(obj)
                        #将优惠商品存入PromotionInfo
                        if type(site_code) == type([]) :
                                for code in site_code :
                                    promotion_info = PromotionInfo(
                                                   promotion_id = promotion_id,
                                                   promotion_type = int(good_type),
                                                   obj_id = int(goods_id),
                                                   discount = discount,
                                                   site_code = code,
                                                   status = 1,
                                    )
                                    session.add(promotion_info)
                                    try:
                                        session.commit()
                                        #调用消息服务器发送我的专享消息
                                        try :
                                                user_list = session.query(CustomerAccount).all()
                                                #对用户群中每一个对象发送消息
                                                user_sha1_list = []
                                                for user in user_list :
                                                        user_sha1_list = user.cardnum
                                                push_my_sale_message(user_sha1_list,promotion,int(good_type))
                                        except Exception,e:
                                            ajax_logger.error("push_my_sale_message:"+str(e))
                                    except Exception,e:
                                        session.rollback()
                                        return False

                        else :
                            promotion_info = PromotionInfo(
                                               promotion_id = promotion_id,
                                               promotion_type = int(good_type),
                                               obj_id = int(goods_id),
                                               discount = discount,
                                               site_code = site_code,
                                               status = 1,
                                )
                            session.add(promotion_info)
                            try:
                                session.commit()
                                #调用消息服务器发送我的专享消息
                                try :
                                        user_list = session.query(CustomerAccount).all()
                                        #对用户群中每一个对象发送消息
                                        user_sha1_list = []
                                        for user in user_list :
                                                user_sha1_list = user.cardnum
                                        push_my_sale_message(user_sha1_list,promotion,int(good_type))
                                except Exception,e:
                                    ajax_logger.error("push_my_sale_message:"+str(e))
                            except Exception,e:
                                session.rollback()
                                return False
        except Exception,e :
            session.rollback()
            return False
    except Exception,e :
        session.rollback()
        return False
    return True

#手动创建的营销活动的推送
def send_promotion_goods_target_audience(request,user_group,promotion_goods,**options) :
    #当前操作用户
    user = get_current_user(request)
    comp_id = user.comp_id
    session = request.get_session()
    promotion_id = options["promotion_id"]
    promotion = session.query(Promotion).filter_by(id =promotion_id).one()
    user_group = int(user_group)
    customer_group_id = user_group
    for promotion_info in promotion_goods:
        goods_id = promotion_info['name']
        good_type= promotion_info['type']
        discount = float(promotion_info['discount'])
        if promotion_info.has_key("site_code") :
                site_code = promotion_info['site_code']
        else :
                site_code = ""

        # 更新到活动用户表中
        obj = UserTargetedPromotion(
                promotion_id = promotion_id,
                user_type = 0,
                user_id = user_group,
                obj_type = int(good_type),
                obj_id = int(goods_id),
                desc = options['desc'],
                delivery_type = int(options['delivery_type'])
            )
        session.add(obj)
        # 更新到活动商品表中
        if type(site_code) == type([]) :
                for code in site_code :
                    if code :
                        promotion_info = PromotionInfo(
                                       promotion_id = promotion_id,
                                       promotion_type = int(good_type),
                                       obj_id = int(goods_id),
                                       discount = discount,
                                       site_code = code,
                                       status = 1,
                        )
                        session.add(promotion_info)
        else :
            promotion_info = PromotionInfo(
                               promotion_id = promotion_id,
                               promotion_type = int(good_type),
                               obj_id = int(goods_id),
                               discount = discount,
                               site_code = site_code,
                               status = 1,
                )
            session.add(promotion_info)
    try :
        session.commit()
        #调用消息服务器发送我的专享消息
        try :
                try :
                    user_list = json.loads(session.query(TargetAudience).filter_by(comp_id = comp_id,
                        id=user_group).one().user_list)
                except Exception,e:
                        result['ret'] = Status.MESSAGESERVERPUSHERROR
                        result['info'] = Status().getReason(result['ret'])
                        return False
                #对用户群中每一个对象发送消息
                user_sha1_list = user_list
                push_my_sale_message(user_sha1_list,promotion,int(good_type))
        except Exception,e:
            ajax_logger.error("push_my_sale_message:"+str(e))
    except Exception,e:
        session.rollback()
        return False
    return True

#推送我的专享消息(后面会将其集成到message_service中)
def push_my_sale_message(user_sha1_list,promotion,good_type):
    from gcustomer.message_server.service.message_service import *
    #对用户群中每一个对象发送消息
    for user_sha1 in user_sha1_list :
            MessageService.PushMysaleMessage({
                          "user_sha1":user_sha1,
                         "promotion_title":promotion.name,
                         "promotion_content":promotion.description,
                         "promotion_sha1":promotion.sha1,
                         "promotion_type":int(good_type)
                         })
    return True


#根据油站的编码获取一个月的数据，按照小时划分出来
def get_month_data_group_by_hour(site_code):
    data=[]
    for i in range(24):
        data.append(0)

    #计算的时间以当前时间到一个月以前作为统计
    end_date = datetime.datetime.now()
    start_date = end_date- datetime.timedelta(days=30)

    create_session = get_dash_session_maker(site_code)
    s = create_session()

    sql_get_date = 'select timestamp from fact_trans where site=\'%s\' order by timestamp desc limit(1);'%site_code
    dates = s.execute(sql_get_date)

    for date in dates:
        end_date = date.timestamp
        start_date = end_date- datetime.timedelta(days=30)

    sql = 'select count(*) as trans_count,extract(hour from timestamp) \
          as hour from fact_trans where site=\'%s\' and \
          timestamp>\'%s\' and timestamp<\'%s\' group by extract(hour from timestamp) order by extract(hour from timestamp);'%(site_code,start_date,end_date)
    rets=s.execute(sql)
    for ret in rets:
        data[int(ret[1])] = ret[0]
    return data

#计算高峰期时段
def cal_peak_period(data):
    #去掉为0的值
    max_min_list=[]
    for count in data:
        if count!=0:
            max_min_list.append(count)
    #获取最大的三个值
    max_list=sorted(max_min_list)[-3:]

    #获取最小的六个值
    min_list=sorted(max_min_list)[:6]
    max_data=0
    min_data=0
    for value in max_list:
        max_data+=value
    max_data=max_data/3
    for value in min_list:
        min_data+=value
    min_data=min_data/6

    #默认值
    crest=[]
    crest_list=[]
    current_time=0

    #0-8点的值
    first_data=sorted(data[:8])
    first_min_data=first_data[0]
    first_max_data=first_data[7]

    #8-16点的值
    second_data=sorted(data[8:16])
    second_min_data=second_data[0]
    second_max_data=second_data[7]

    #16-24点的值
    third_data=sorted(data[16:24])
    third_min_data=third_data[0]
    third_max_data=third_data[7]

    v=(first_min_data+first_max_data+second_min_data+second_max_data+third_min_data+third_max_data)/6
    crest_avg_count=1.2*v

    for count in data:
        #高峰期
        #计算偏移量
        offset=count-crest_avg_count

        if offset>0:
            crest.append(current_time)
        current_time+=1

    time=0
    temp=[]
    for item in crest:
        if time==0:
            temp.append(crest[time])
            time+=1
            continue
        if crest[time]-crest[time-1]>1:
            temp.append(crest[time-1]+1)
            crest_list.append(temp)
            temp=[]
            temp.append(crest[time])

        if time==len(crest)-1:
            temp.append(crest[time]+1)
            crest_list.append(temp)
        time+=1

    return crest_list

#获取油站近一个月高峰期时段
def get_crest_period_one_month(site_code):
    crest_list = []
    data = get_month_data_group_by_hour(site_code)
    crest_list = cal_peak_period(data)
    return crest_list

#获取该公司下所有的油站
def get_all_site(comp_id):
    result = {}

    #油站的sha1
    result_sha1_list = []

    #油站的id
    result_id_list = []
    try:
        create_session = get_dash_session_maker()
        s = create_session()

        #查询该公司下的所有站点
        stations = s.query(Station).filter_by(comp_id = comp_id).all()
        for station in stations:
            result_sha1_list.append(station.sha1)
            result_id_list.append(station.id)

        result['sha1s'] = result_sha1_list
        result['ids'] = result_id_list
    except Exception,e :
        session.rollback()

    finally:
        return result

#获取该公司下所有油站的编码
def get_all_site_code():
    result = []
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        sites = s.query(StationProfile).all()
        for site in sites:
            result.append((site.site_code).strip())
    except Exception,e :
        session.rollback()

    finally:
        return result

#根据油站sha1获取油站编码
def get_site_code_by_sha1(sha1s):
    result = []
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        for sha1 in sha1s:
            info = {}
            site = s.query(StationProfile).filter_by(site_sha1=sha1).one()
            info['site_code'] = site.site_code
            info['site_sha1'] = site.site_sha1
            result.append(json.dumps(info))
    except Exception,e :
        session.rollback()

    finally:
        return result

#批量计算油站的高峰期
def cal_peak_period_by_sites_group():

    try:
        create_session = get_dash_session_maker()
        s = create_session()

        #获取所有的油站
        stations = s.query(Station).all()
        for station in stations:

            #油站编码
            site = station.site_code

            #获取近一个月的高峰期时段
            crest_list = get_crest_period_one_month(site.strip())
            try:
                obj = s.query(StationProfile).filter_by(station_id=station.id).one()

                obj.peak_range = json.dumps(crest_list)
                s.commit()
            except:
                continue

    except Exception,e :
        print e


#根据油站的sha1获取高峰期的值
def get_peak_period_by_sites_group(sites):
    result = {}
    try:
        for site in sites:
            create_session = get_dash_session_maker()
            s = create_session()
            obj = s.query(StationProfile).filter_by(site_code=site).one()
            result[obj.site] = obj.peak_range
    except Exception,e :
        session.rollback()

    finally:
        return json.dumps(result)

#获取所有用户的卡号
def get_all_user_cardnum():
    result = []
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        objs = s.query(CustomerProfile).all()
        for obj in objs:
            result.append(obj.cardnum)
    except Exception,e :
        session.rollback()

    finally:
        return result

#获取群组里的油站sha1列表
def get_sites_by_group_id(group_id):
    #result = []
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        objs = s.query(StationGroup).filter_by(id=group_id).one()
        result = json.loads(objs.site_sha1_list)
    except Exception,e :
        session.rollback()
    finally:
        return result

#获取非油品的销售后10名
def get_none_fuel_last_10():
    sites = get_all_site_code()
    try:
         #计算的时间以当前时间到一个月以前作为统计
        end_date = datetime.datetime.now()
        start_date = end_date- datetime.timedelta(days=30)
        s2=get_dash_session_maker()()

        for site in sites:
            result = []
            # create_session = get_dash_session_maker(site)
            create_session = get_dash_session_maker(site)
            s = create_session()

            sql_get_date = 'select timestamp from fact_trans where site=\'%s\' order by timestamp desc limit(1);'%site
            dates = s.execute(sql_get_date)

            for date in dates:
                end_date = date.timestamp
                start_date = end_date- datetime.timedelta(days=30)
            sql = 'select "desc",sum(quantity) as sum,barcode from fact_trans where site=\'%s\' and trans_type=1 and \
                  timestamp>\'%s\' and timestamp<\'%s\' group by "desc" ,barcode order by sum(quantity) limit(10)'%(site,start_date,end_date)
            rets=s.execute(sql)
            for ret in rets:
                info = {
                    'barcode':ret.barcode,
                    'desc':ret.desc,
                    'sum':ret.sum
                }
                result.append(info)
            objs=s2.query(StationProfile).filter_by(site_code=site).all()
	    for obj in objs:
                obj.bottom_100_goods = json.dumps(result)
                s2.add(obj)
        s2.commit()
    except Exception,e :
        s.rollback()
    finally:
        return True

#获取非油品销售的top10
def get_none_fuel_top_10():
    sites = get_all_site_code()
    try:
         #计算的时间以当前时间到一个月以前作为统计
        end_date = datetime.datetime.now()
        start_date = end_date- datetime.timedelta(days=30)
        s2=get_dash_session_maker()()

        for site in sites:
            result = []
            create_session = get_dash_session_maker(site)
            s = create_session()

            sql_get_date = 'select timestamp from fact_trans where site=\'%s\' order by timestamp desc limit(1);'%site
            dates = s.execute(sql_get_date)

            for date in dates:
                end_date = date.timestamp
                start_date = end_date- datetime.timedelta(days=30)
            sql = 'select "desc",sum(quantity) as sum,barcode from fact_trans where site=\'%s\' and trans_type=1 and \
                  timestamp>\'%s\' and timestamp<\'%s\' group by "desc",barcode order by sum(quantity) desc limit(10)'%(site,start_date,end_date)
            rets=s.execute(sql)
            for ret in rets:
                info = {
                    'barcode':ret.barcode,
                    'desc':ret.desc,
                    'sum':ret.sum
                }
                result.append(info)
            objs=s2.query(StationProfile).filter_by(site_code=site).all()
            for obj in objs:
	        obj.top_100_goods = json.dumps(result)
                s2.add(obj)
        s2.commit()
    except Exception,e :
        session.rollback()
    finally:
        return True

#检查用户群属性,防止创建两个完全相同的用户群
def check_target_audience(**dict_obj):
    session = get_dash_session_maker()()
    #基本属性
    comp_id = dict_obj['comp_id']
    group_location = dict_obj['group_location']
    career = dict_obj['career']
    gender = dict_obj['gender']
    from_age = int(dict_obj['from_age'])
    to_age = int(dict_obj['to_age'])
    #行为特性
    prefer_cost_map = dict_obj['prefer_cost_map']
    prefer_time_map = dict_obj['prefer_time_map']
    prefer_pump_type_map = dict_obj['prefer_pump_type_map']
    prefer_fuel_cost_map = dict_obj['prefer_fuel_cost_map']
    prefer_nonfuel_cost_map = dict_obj['prefer_nonfuel_cost_map']
    pump_timeout = dict_obj['pump_timeout']
    favourite_nonfuel_products = dict_obj['favourite_nonfuel_products']

    try :
        session.query(TargetAudience).filter_by(
            comp_id=comp_id,location=group_location,
            career = career,gender = gender,
            from_age = from_age,to_age=to_age,
            prefer_cost = prefer_cost_map,
            prefer_time = prefer_time_map,
            prefer_pump_type= prefer_pump_type_map,
            prefer_fuel_cost = prefer_fuel_cost_map,
            prefer_nonfuel_cost = prefer_nonfuel_cost_map,
            pump_timeout = pump_timeout,
            favourite_products = favourite_nonfuel_products
        ).one()
    except  Exception,e:
        return True
    return False


#根据用户群属性计算用户列表
def cal_user_list_with_group_attribute(dict_obj):
    #用户cardnum列表
    user_list = []
    #群属性
    #基本属性
    comp_id = dict_obj['comp_id']
    group_location = dict_obj['group_location']
    career = dict_obj['career']
    gender = dict_obj['gender']
    from_age = int(dict_obj['from_age'])
    to_age = int(dict_obj['to_age'])
    #行为特性
    prefer_time_map = dict_obj['prefer_time_map']
    prefer_pump_type_map = dict_obj['prefer_pump_type_map']
    prefer_fuel_cost_map = dict_obj['prefer_fuel_cost_map']
    prefer_nonfuel_cost_map = dict_obj['prefer_nonfuel_cost_map']
    pump_timeout = dict_obj['pump_timeout']
    favourite_products = dict_obj['favourite_products']

    #聚合客户信息
    create_session = get_dash_session_maker()
    session = create_session()
    card_list = []
    temp_list = []
    #过滤所属地域
    objs = session.query(CustomerAccount).filter_by(location = int(group_location)).all()
    for obj in objs :
        if obj.cardnum :
            card_list.append(obj.cardnum)
    #过滤基本属性
    if not gender == -1 :
        for card in card_list :
            user = session.query(CustomerAccount).filter_by(cardnum = card).first()
            if user :
                if user.gender == int(gender):
                    temp_list.append(card)
        card_list = temp_list
        temp_list = []

    if  from_age and  to_age :
        for card in card_list :
            user = session.query(CustomerAccount).filter_by(cardnum = card).first()
            if user :
                if user.age in range(from_age,to_age):
                    temp_list.append(card)
        card_list = temp_list
        temp_list = []
    elif from_age:
        for card in card_list :
            user = session.query(CustomerAccount).filter_by(cardnum = card).first()
            if user :
                if user.age >= from_age :
                    temp_list.append(card)
        card_list = temp_list
        temp_list = []
    elif to_age :
        for card in card_list :
            user = session.query(CustomerAccount).filter_by(cardnum = card).first()
            if user.age < to_age :
                temp_list.append(card)
        card_list = temp_list
        temp_list = []

    if not prefer_time_map == '':
        for card in card_list:
            try :
                customer = session.query(CustomerProfile).filter_by(vcard_id = card).one()
            except Exception,e:
                continue
            if customer.prefer_time == int (prefer_time_map):
                temp_list.append(card)
        card_list = temp_list
        temp_list = []

    if not prefer_pump_type_map == '':
        for card in card_list:
            try :
                customer = session.query(CustomerProfile).filter_by(vcard_id = card).one()
            except Exception,e:
                continue
            if customer.prefer_pump_type == int (prefer_pump_type_map):
                temp_list.append(card)
        card_list = temp_list
        temp_list = []

    if not prefer_fuel_cost_map == '':
        for card in card_list:
            try :
                customer = session.query(CustomerProfile).filter_by(vcard_id = card).one()
            except Exception,e:
                continue
            if customer.prefer_fuel_cost == int (prefer_fuel_cost_map):
                temp_list.append(card)
        card_list = temp_list
        temp_list = []

    if not prefer_nonfuel_cost_map == '':
        for card in card_list:
            try :
                customer = session.query(CustomerProfile).filter_by(vcard_id = card).one()
            except Exception,e:
                continue
            if customer.prefer_nonfuel_cost == int (prefer_nonfuel_cost_map):
                temp_list.append(card)
        card_list = temp_list
        temp_list = []

    if not career == '' :
        for card in card_list :
            user = session.query(CustomerAccount).filter_by(cardnum = card).one()
            if user.career == career:
                temp_list.append(card)
        card_list = temp_list
        temp_list = []

    #返回计算结果
    user_list = card_list
    #过滤掉没有关联该公司的用户
    temp_user_list = []
    for cardnum  in user_list :
        try :
            comp_info_list = session.query(CustomerCompInfo).filter_by(vcard_id=cardnum).all()
            for comp_info in comp_info_list :
                if comp_info.comp_id == comp_id :
                    temp_user_list.append(comp_info.vcard_id)
                    break
        except Exception,e:
            continue
    user_list = temp_user_list
    #根据用户画像结果过滤
    user_list = filter_by_user_profile(user_list,favourite_products)
    return json.dumps(user_list)

#根据用户画像结果过滤
def filter_by_user_profile(user_list,product_list):
    temp_user_list = []
    session = get_dash_session_maker()()
    if product_list == "[]" :
        return user_list
    product_list = json.loads(product_list)
    for vcard_id in user_list :
        try :
            user = session.query(CustomerProfile).filter_by(vcard_id=vcard_id).one()
        except Exception,e:
            ajax_logger.error(str(e))
            continue
        if user.favourite_nonfuel_products == "" :
            continue
        user_favourite_products = json.loads(user.favourite_nonfuel_products)
        for favourite_product in product_list :
            if favourite_product in user_favourite_products :
                temp_user_list.append(vcard_id)
    user_list = temp_user_list
    return user_list

#根据油站sha1获取top10商品
def get_top_goods_by_site(station_id):
    result = {}
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        obj = s.query(StationProfile).filter_by(id=station_id).one()
        result['goods'] = obj.top_100_goods
    except Exception,e :
        session.rollback()
    finally:
        return result

#根据油站sha1获取bottom10商品
def get_bottom_goods_by_site(station_id):
    result = {}
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        obj = s.query(StationProfile).filter_by(id=station_id).one()
        result['goods'] = obj.bottom_100_goods
    except Exception,e :
        session.rollback()
    finally:
        return result

#通过油品id获取油品的描述信息
def get_fuel_desc_by_id(fuel_id):
    desc = ''
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        obj = s.query(FuelTypeRelation).filter_by(id=fuel_id).one()
        desc = obj.name
    except Exception,e :
        session.rollback()
    finally:
        return desc

def alter_user_score(request,order):
        user = CustomerAccount.objects.get(sha1 = order.user_sha1)
        session = request.get_session()
        #验证是否为绑定到卡号用户
        try :
            customer = session.query(CustomerProfile).filter_by(cardnum=user.cardnum).one()
        except :
            customer = None
        if customer :
                #修改用户积分
                #查询settings文件中用户选择的积分规则
                from django.conf import settings
                rule =  settings.INTEGRAL_OPTION[settings.USE_OPTION]
                #会员积分规则
                if settings.USE_OPTION == "0001" :
                    if order.order_type == 0 :
                        pass
                    elif order.order_type == 1:
                        score_change = order.item_total
                        user.score = user.score - score_change
                        user.save()
                    #购买油品
                    elif order.order_type == 2:
                        #累计油品消费 单位:升
                        pump_count = order.item_count
                        customer.total_fuel_amount = customer.total_fuel_amount  + pump_count
                        try:
                            session.commit()
                        except :
                            pass
                        score_change = int(pump_count)*rule.INTEGRAL_CHANGE["score_change"][user.score_rank]
                        user.score = user.score + score_change
                        user.all_score = user.all_score + score_change
                        user.save()
                    elif order.order_type == 3:
                        pass
                #普通积分规则
                elif settings.USE_OPTION == "0000" :
                        #商品优惠购买
                        if order.order_type == 0 :
                                try:
                                    user_ratio = session.query(UserScoreRule).filter_by(level = user.score_rank).one().score_ratio
                                    if order.item_type == 0:
                                        try:
                                            good_id = session.query(StoreItem).filter_by(sha1=order.item_sha1).one().id
                                        except Exception,e:
                                            pass
                                    elif order.item_type == 1:
                                        good_id = session.query(ServiceInformation).filter_by(sha1 = item_sha1).one().id
                                    good_ratio = session.query(ItemScoreRule).filter_by(good_id = good_id).one().score_ratio
                                except Exception,e :
                                    pass
                                score_change = int(user_ratio*good_ratio*order.item_count)
                                #修改用户当前积分并修改用户等级
                                user.score = user.score + score_change
                                user.all_score = user.all_score + score_change
                                if user.score_rank < 5:
                                    level_range = session.query(UserScoreRule).filter_by(level = user.score_rank+1).one().level_range
                                    if len(level_range.split(":")) == 2 :
                                        range_list = range(int(level_range.split(":")[0]),int(level_range.split(":")[1]))
                                        if user.all_score in range_list:
                                            user.score_rank = user.score_rank + 1
                                    else :
                                        range_list = range(int(level_range),10000)
                                        if user.all_score in range_list:
                                            user.score_rank = user.score_rank + 1
                                user.save()

                        #积分兑换
                        elif order.order_type == 1:
                                score_change = order.item_total
                                user.score = user.score - score_change
                                user.save()

                        #暂时返回的积分为购买金额的0.5倍
                        elif order.order_type == 2:
                                score_change = int(order.item_total * 0.5)
                                user.score = user.score + score_change
                                user.all_score = user.all_score + score_change
                                user.save()
                        elif order.order_type == 3:
                                score_change = int(order.item_total * 0.5)
                                user.score = user.score + score_change
                                user.all_score = user.all_score + score_change
                                user.save()
                return True
        else :
            return False

#验证身份证的合法性,code为身份证前17位，check_code为身份证最后一位，即校验位
def check_card_id(code,check_code):

    #17位系数
    Wi = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]

    #最后一位校验数
    Ti = ['1', '0', 'x', '9', '8', '7', '6', '5', '4', '3', '2']

    #check code ,位数为17位
    if (len(code) != 17):
            print "必须为17位的字符"
            return False

    #code的系数乘积和
    sum = 0
    for i in range(17):
        sum += int(code[i])*Wi[i]

    #计算得到的最后一位值，与给定的check_code进行对比，一致则验证成功，否则失败
    final_check_code = Ti[sum%11]
    if final_check_code != str(check_code).lower():
        return False

    return True

#根据身份证获取年龄性别
def get_age_sex_by_card_id(code):
    import datetime

    #性别，0为男性，1为女性
    sex = 0

    #身份证的年份
    id_year = int(code[6:10])

    #当前年份
    current_year = datetime.datetime.now().year

    #计算年龄
    age = current_year - id_year +1

    #性别标识位,男性为奇数，女性为偶数
    sex_flag = int(code[16])

    if sex_flag%2 == 0:
        sex = 1
    else:
        sex = 0

    info = {
        "age":age,
        "sex":sex
    }

    return info

#计算油站群的油站列表
def cal_station_group_site_list(station_group):
    station_sha1_list = []
    session = get_dash_session_maker()()
    station_list = session.query(Station).filter_by(comp_id = station_group.comp_id).all()
    area = json.loads(station_group.group_location)
    for station in station_list :
        location = json.loads(station.location)
        if area['province'] == location['province'] \
            or area['city'] == location['city'] or area['district'] == location['district']:
            station_sha1_list.append(station.site_code)
    return station_sha1_list

#获取当前gcustomer已注册的公司
def get_company_info():
    comp_list = []
    session = get_dash_session_maker()()
    companys = session.query(GCompany).all()
    for company in companys :
        comp_list.append(dict(
                comp_id = company.id,
                comp_name = company.name
            ))
    return comp_list

#获取公司的油站信息
def get_company_station_list(comp_id):
    staion_list = []
    session = get_dash_session_maker()()
    stations = session.query(Station).filter_by(comp_id=comp_id).all()
    for station in stations :
        staion_list.append(dict(
                station_sha1 = station.sha1,
                name = station.name
            ))
    return staion_list

#获取油站site code
#计算驾车宝用户热销商品top10和滞销bottom10
def cal_station_items_top_bottom_10():
    try:

        #bottom商品列表
        bottom_items = []
        session = get_dash_session_maker()()

        #获取所有油站
        stations = session.query(Station).all()

        #根据油站分别计算top10和bottom10商品
        for station in stations:

	        #top油品、非有品、车后服务，存储结构：[{"barcode":"油品的barcode","type":0,"desc":"商品的描述"，"sum":31.9},{""},{}]
            top_list = []

            #查询top商品
            items = session.query(func.sum(CustomerAccountTransaction.item_count).label("total"),CustomerAccountTransaction.item_sha1,CustomerAccountTransaction.item_name)\
            .filter_by(comp_id=station.comp_id,trans_type=2)\
            .group_by(CustomerAccountTransaction.item_sha1,CustomerAccountTransaction.item_name).\
            order_by(func.sum(CustomerAccountTransaction.item_count)).all()

            #top10商品
            items_top10 = items[:10]


            #商品type为1
            for top in items_top10:
                try:
                    item_barcode = session.query(StoreItem).filter_by(sha1=top.item_sha1).one().pos_id
                    top_list.append({
                        'barcode':str(item_barcode),
                        'desc':top.item_name,
                        'sum':top.total,
                        'type':1
                    })
                except:
                    continue


            #查询车后服务
            services = session.query(func.sum(CustomerAccountTransaction.item_count).label("total"),CustomerAccountTransaction.item_sha1,CustomerAccountTransaction.item_name)\
            .filter_by(comp_id=station.comp_id,trans_type=3)\
            .group_by(CustomerAccountTransaction.item_sha1,CustomerAccountTransaction.item_name).\
            order_by(func.sum(CustomerAccountTransaction.item_count)).all()

            #top10车后服务，type为2
            services_top10 = services[:10]

            for service in services_top10:
                top_list.append({
                    'barcode':str(service.item_sha1),
                    'desc':service.item_name,
                    'sum':service.total,
                    'type':2
                })

            #查询油品top10
            fuel_session = get_dash_session_maker(station.site_code)()
            fuels = fuel_session.query(func.sum(Trans.quantity).label("total"),Trans.barcode,Trans.desc)\
            .filter_by(site=station.site_code,trans_type=0)\
            .group_by(Trans.barcode,Trans.desc).order_by(func.sum(Trans.quantity)).all()

            fuels_top10 = fuels[:10]

            for fuel in fuels_top10:
                top_list.append({
                    'barcode':str(fuel.barcode),
                    'desc':fuel.desc,
                    'sum':fuel.total,
                    'type':0
                })



            #更新油站画像的top10和bottom10
            smt = update(StationProfile).where(StationProfile.station_id==station.id).\
                    values(top_100_goods=json.dumps(top_list))
            session.execute(smt)
            session.commit()


    except Exception,e :
        session.rollback()
        ajax_logger.error(str(e))
    finally:
        return top_list

#计算驾车宝用户滞销bottom10
def cal_station_items_bottom_10():
    try:

        #bottom商品列表
        bottom_items = []
        session = get_dash_session_maker()()

        #获取所有油站
        stations = session.query(Station).all()

        #根据油站分别计算bottom10和bottom10商品
        for station in stations:

	        #bottom油品、非有品、车后服务，存储结构：[{"barcode":"油品的barcode","type":0,"desc":"商品的描述"，"sum":31.9},{""},{}]
            bottom_list = []

            #查询bottom商品
            items = session.query(func.sum(CustomerAccountTransaction.item_count).label("total"),CustomerAccountTransaction.item_sha1,CustomerAccountTransaction.item_name)\
            .filter_by(comp_id=station.comp_id,trans_type=2)\
            .group_by(CustomerAccountTransaction.item_sha1,CustomerAccountTransaction.item_name).\
            order_by(func.sum(CustomerAccountTransaction.item_count)).all()

            #bottom10商品
            items_bottom10 = items[-10:]


            #商品type为1
            for bottom in items_bottom10:
                try:
                    item_barcode = session.query(StoreItem).filter_by(sha1=bottom.item_sha1).one().pos_id
                    bottom_list.append({
                        'barcode':str(item_barcode),
                        'desc':bottom.item_name,
                        'sum':bottom.total,
                        'type':1
                    })
                except:
                    continue

            #查询油品bottom10
            fuel_session = get_dash_session_maker(station.site_code)()
            fuels = fuel_session.query(func.sum(Trans.quantity).label("total"),Trans.barcode,Trans.desc)\
            .filter_by(site=station.site_code,trans_type=0)\
            .group_by(Trans.barcode,Trans.desc).order_by(func.sum(Trans.quantity)).all()

            fuels_bottom10 = fuels[-10:]

            for fuel in fuels_bottom10:
                bottom_list.append({
                    'barcode':str(fuel.barcode),
                    'desc':fuel.desc,
                    'sum':fuel.total,
                    'type':0
                })



            #更新油站画像的bottom10和bottom10
            smt = update(StationProfile).where(StationProfile.station_id==station.id).\
                    values(bottom_100_goods=json.dumps(bottom_list))
            session.execute(smt)
            session.commit()


    except Exception,e :
        session.rollback()
        ajax_logger.error(str(e))
    finally:
        return bottom_list

def get_site_code(staion_sha1):
    session = get_dash_session_maker()()
    try :
        station = session.query(Station).filter_by(sha1=station_sha1).one()
    except Exception,e:
        ajax_logger.error(str(e))
        return None
    site_code = station.site_code
    return site_code

#生成充值订单
def create_charge_order(vcard_id,comp_id,money):
    session = get_dash_session_maker()()
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
            time = str(datetime.datetime.now())
        )
    try :
        session.add(order)
        session.commit()
    except Exception,e:
        return False
    return True

#获取当前用关联的石油公司
#输入:驾车宝用户虚拟卡号
#驾车宝用户关联的石油公司帐号comp_id列表
def get_associated_oil_company(vcard_id):
    comp_id_list = []
    try :
            session = get_dash_session_maker()()
            comp_list = session.query(CustomerCompInfo).filter_by(vcard_id=vcard_id).all()
            for comp in comp_list :
                comp_id_list.append(comp.comp_id)
    except Exception,e:
            ajax_logger.error(str(e))
            comp_id_list = []
            return comp_id_list
    return comp_id_list

#密码加密
def md5_data(password):
    if type(password) == type("")  or type(password) == type(u"") :
        import hashlib
        m = hashlib.md5()
        m.update(password)
        return m.hexdigest()
    else :
        return password

#在调试模式下,记录app端的输入日志
def  app_input_log_record(request) :
    if settings.DEBUG == True :
        if request.method == 'GET':
            ajax_logger.info(request.GET)
        elif request.method == 'POST':
            ajax_logger.info(request.POST)
        else :
            ajax_logger.info(request.method)
    else :
        return

#在调试模式下,记录app端的输出日志
def app_output_log_record(response):
    if settings.DEBUG == True :
        ajax_logger.info(response.content)
    else :
        return

#获取石油公司用户角色
def get_user_role(request):
    user = get_current_user(request)
    session = request.get_session()
    if user.type == 3 :
        comp_id = user.comp_id
        user_comp_memship = session.query(GCompanyMembership).filter_by(user_id=user.id,comp_id=comp_id).one()
        return user_comp_memship.role
    else :
        return user.type

#从石油公司实体卡消费计算虚拟卡画像
def get_profile_from_oil_card(request,cardnum,profile_type):
    session = request.get_session()
    try :
        session.query(CustomerAccount).filter_by(cardnum=cardnum).one()
    except Exception,e:
        ajax_logger.info(request.method)
        return []
    user = get_current_user(request)
    comp_id = user.comp_id
    account_comp_info = session.query(CustomerCompInfo).filter_by(comp_id = comp_id,
        vcard_id=cardnum).one()
    oil_card_list = json.loads(account_comp_info.card_list)
    nonfuel_products = []
    if profile_type == "favourite_nonfuel_products" :
        for oil_card in oil_card_list :
            try :
                oil_card_obj = UserCardProfilingResult.objects.get(cardnum = oil_card['cardnum'])
            except Exception,e:
                ajax_logger.info(request.method)
                continue
            goods = json.loads(oil_card_obj.favourite_nonfuel_products)
            nonfuel_products.extend(goods)
    elif profile_type == "recommended_nonfuel_products" :
        for oil_card in oil_card_list :
            try :
                oil_card_obj = UserCardProfilingResult.objects.get(cardnum = oil_card['cardnum'])
            except Exception,e:
                ajax_logger.info(request.method)
                continue
            goods = json.loads(oil_card_obj.recommended_nonfuel_products)
            nonfuel_products.extend(goods)
    nonfuel_products = list(set(nonfuel_products))
    return nonfuel_products


#获取公司的加油流失客户的油站信息
def get_comp_oil_loss_station_sha1s(request,comp_id):
    station_list = []
    vcard_list = []
    session = request.get_session()
    try :
        comp_info_objects = session.query(CustomerCompInfo).filter_by(comp_id=comp_id).all()
    except Exception,e:
        ajax_logger.error(str(e))
        return False
    for obj in comp_info_objects :
        vcard_list.append(obj.vcard_id)
    for vcard_id in vcard_list :
        try :
            vcard_profile = session.query(CustomerProfile).filter_by(vcard_id = vcard_id).one()
        except Exception,e:
            ajax_logger.error(str(e))
            continue
        is_oil_loss_customer = json.loads(vcard_profile.is_oil_loss_customer)
        if is_oil_loss_customer :
            station_list.extend(is_oil_loss_customer)
    station_list = list(set(station_list))
    if not station_list :
        return False
    return station_list

#获取高峰期油站列表
def get_peak_period_station_list(request,comp_id):
    station_list = []
    session = request.get_session()
    try :
        station_objects = session.query(Station).filter_by(comp_id = comp_id).all()
    except Exception,e:
        ajax_logger.error(str(e))
        return False
    for obj in station_objects :
        try :
            station_profile = session.query(StationProfile).filter_by(station_id = obj.id).one()
        except Exception,e:
            ajax_logger.error(str(e))
            return False
        if station_profile.peak_range :
            station_list.append(obj.sha1)
    if not station_list :
        return False
    return station_list

#时间转换
#时间字符串转化为时间戳
def stringToTimeStamp(timestr):
    timearray=time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    timestamp=int(time.mktime(timearray))
    return timestamp

#时间戳转换为时间字符串
def timeStampToString(timestamp):
    timeArray = time.localtime(timestamp)
    timestr = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return timestr

#当前时间生成timestramp
def timeToTimeStramp():
    import time
    import datetime
    now_time = str(datetime.datetime.now()).split(".")[0]
    time.strptime(now_time,'%Y-%m-%d %H:%M:%S')
    timestamp = time.mktime(time.strptime(now_time,'%Y-%m-%d %H:%M:%S'))
    return timestamp

#获取商品app统计数据
def get_user_action(request,sha1,promotion_id):
    session = request.get_session()
    check_count = 0
    pay_count = 0
    check_sql = 'select count(*)  as check_count  from gcustomer_useraction where action=\'%s\' and  sha1=\'%s\' and promotion_id=\'%s\' ' %(0,sha1,promotion_id)
    pay_sql = 'select count(*)  as pay_count  from gcustomer_useraction where  action=\'%s\' and sha1=\'%s\' and promotion_id=\'%s\' ' %(1,sha1,promotion_id)
    try :
            check_count_obj = session.execute(check_sql)
            check_count = check_count_obj.first().check_count
            pay_count_obj = session.execute(pay_sql)
            pay_count = pay_count_obj.first().pay_count
    except Exception,e:
            ajax_logger.error(str(e))
            check_count = 0
            pay_count = 0
            return check_count,pay_count
    return check_count,pay_count

#调用gearmand自动聚合新注册的app用户
def associate_user_to_group(comp_id,vcard_id):
    #新建gearmand客户端
    task_name = "associate_user_to_group"
    try :
        job_data = {"comp_id":comp_id,"vcard_id":vcard_id}
        client = gearman.GearmanClient(['127.0.0.1:4730'])
        client.submit_job(task_name,json.dumps(job_data),wait_until_complete=True,background=True)
    except Exception,e:
        ajax_logger.error("associate_user_to_group:"+str(e))
    return True

#计算广告统计数据
def cal_advert_statistics(sha1):
    session = get_dash_session_maker()()
    result = {}
    result['data'] = {}
    #年龄分布
    result['data_age'] = {}
    result['data_age']['20岁以下'] = 0
    result['data_age']['20-40岁'] = 0
    result['data_age']['40-60岁'] = 0
    result['data_age']['60岁以上'] = 0
    #性别分布
    result['data_gender'] = {}
    result['data_gender']['男'] = 0
    result['data_gender']['女'] = 0
    #职业分布
    result['data_career'] = {}
    result['data_career']['学生'] = 0
    result['data_career']['司机'] = 0
    result['data_career']['老师'] = 0
    result['data_career']['其他'] = 0
    #油品购买分布
    result['data_oil_pay'] = {}
    result['data_oil_pay']['5次以下'] = 0
    result['data_oil_pay']['5-10次'] = 0
    result['data_oil_pay']['10-15次'] = 0
    result['data_oil_pay']['15次以上'] = 0
    #查询
    sql = 'select *  from gcustomer_useraction where action=\'%s\' and  sha1=\'%s\' ' %(0,sha1)
    try :
        user_action_list = session.execute(sql)
        count = 0
        for user_action  in user_action_list :
            count = count + 1
            vcard_id = user_action.vcard_id
            user = session.query(CustomerAccount).filter_by(cardnum=vcard_id).one()
            #统计年龄
            if user.age in range(0,20) :
                result['data_age']['20岁以下'] = result['data_age']['20岁以下'] +1
            elif user.age in range(20,40) :
                result['data_age']['20-40岁'] = result['data_age']['20-40岁'] +1
            elif user.age in range(40,60) :
                result['data_age']['40-60岁'] = result['data_age']['40-60岁'] +1
            elif user.age in range(60,100) :
                result['data_age']['60岁以上'] = result['data_age']['60岁以上'] +1
            else :
                pass
            if user.gender == 0 :
                result['data_gender']['男'] = result['data_gender']['男'] + 1
            else :
                result['data_gender']['女'] = result['data_gender']['女'] +1
            if user.career == "学生" :
                result['data_career']['学生'] = result['data_career']['学生'] +1
            elif user.career == "司机" :
                result['data_career']['司机'] = result['data_career']['司机'] +1
            elif user.career == "老师" :
                result['data_career']['老师'] = result['data_career']['老师'] +1
            elif user.career == "其他" :
                result['data_career']['其他'] = result['data_career']['其他'] +1
            else :
                pass

        if not count == 0 :
            result['data_age']['20岁以下'] = float(result['data_age']['20岁以下']/float(count)) * 100
            result['data_age']['20-40岁'] = float(result['data_age']['20-40岁']/float(count)) * 100
            result['data_age']['40-60岁'] = float(result['data_age']['40-60岁']/float(count)) * 100
            result['data_age']['60岁以上'] = float(result['data_age']['60岁以上']/float(count)) * 100

            result['data_gender']['男'] = float(result['data_gender']['男'])/float(count) * 100
            result['data_gender']['女'] = float(result['data_gender']['女'])/float(count) * 100

            result['data_career']['学生'] = float(result['data_career']['学生'])/float(count) * 100
            result['data_career']['司机'] = float(result['data_career']['司机'])/float(count) * 100
            result['data_career']['老师'] = float(result['data_career']['老师'])/float(count) * 100
            result['data_career']['其他'] = float(result['data_career']['其他'])/float(count) * 100

    except Exception,e:
        ajax_logger.error(str(e))
    return result

#获取与公司关联的app用户vcard_id列表
def get_associate_comp_vcardid_list(comp_id):
    session = get_dash_session_maker()()
    vcard_id_list = []
    customer_comp_info_list = session.query(CustomerCompInfo).filter_by(comp_id=comp_id).all()
    for customer_comp_info in customer_comp_info_list :
        vcard_id_list.append(customer_comp_info.vcard_id)
    return vcard_id_list

#聚合滞销商品的用户列表
def get_user_list_with_bottom_goods(comp_id,promotion_goods):
    session = get_dash_session_maker()()
    user_list = get_associate_comp_vcardid_list(comp_id)
    product_list = []
    for promotion_good in promotion_goods :
        good_id = promotion_good['name']
        try :
            good = session.query(StoreItem).filter_by(comp_id=comp_id,id=good_id).one()
            product_list.append(str(good.pos_id))
        except Exception,e:
            ajax_logger.error(str(e))
            continue
    product_list = json.dumps(product_list)
    return filter_by_user_profile(user_list,product_list)

#判断某个用户是否可以聚合到某个公司的用户群
def check_user_associate_group(session,vcard_id,group):
    try :
        user = session.query(CustomerAccount).filter_by(cardnum = vcard_id).one()
        user_profile = session.query(CustomerProfile).filter_by(vcard_id = vcard_id).one()
    except Exception,e:
        return False
    #用户群的属性
    location = group.location
    career = group.career
    gender = group.gender
    from_age = group.from_age
    to_age = group.to_age
    prefer_time = group.prefer_time
    prefer_pump_type = group.prefer_pump_type
    prefer_fuel_cost = group.prefer_fuel_cost
    prefer_nonfuel_cost = group.prefer_nonfuel_cost
    favourite_products = json.loads(group.favourite_products)

    #过滤基本属性
    #性别
    if not gender == -1:
        if not user.gender == int(gender):
            return False
    #年龄
    if not from_age == 0 and not to_age == 0:
        if not user.age in range(from_age,to_age):
            return False
        elif not user.age >= from_age  and not user.age < to_age: 
            return False
    #职业
    if not career == '':
        if not user.career == career:
            return False
    #加油时间倾向
    if not prefer_time == '':
        if not user_profile.prefer_time == int (prefer_time):
            return False
    #加油量倾向
    if not prefer_pump_type == '':
        if not user_profile.prefer_pump_type == int (prefer_pump_type):
            return False
    #油品消费倾向
    if not prefer_fuel_cost == '':
        if not user_profile.prefer_fuel_cost == int (prefer_fuel_cost):
            return False
    #非油品消费倾向
    if not prefer_nonfuel_cost == '':
        if not user_profile.prefer_nonfuel_cost == int (prefer_nonfuel_cost):
            return False
    #最喜爱的非油品
    if not favourite_products == [] :
        try :
            user_favourite_products = user_profile.favourite_nonfuel_products
        except Exception,e:
            return False 
        for favourite_product in favourite_products :
            if not favourite_product in user_favourite_products :
                return False
    return True

#更新用户群的聚合属性
def update_target_audience_user_list():
    session = get_dash_session_maker()()
    #获取所有公司信息
    comp_list = session.query(GCompany).all()   
    for comp in comp_list :
        comp_id = comp.id
        group_list = session.query(TargetAudience).filter_by(comp_id = comp_id).all()
        for group in group_list :
            try :
                group_user_list = json.loads(group.user_list)
            except Exception,e:
                group_user_list = []
            #获得与该公司关联的用户列表
            vcard_id_list = get_associate_comp_vcardid_list(comp_id)
            for vcard_id in vcard_id_list :
                temp_session = get_dash_session_maker()()
                if check_user_associate_group(temp_session,vcard_id,group) :
                    if not vcard_id in group_user_list :
                        group_user_list.append(vcard_id)
                temp_session.close()
            group.user_list = json.dumps(group_user_list)
            try :
                session.commit()
            except Exception,e:
                ajax_logger.error(str(e))
        
#检查反馈意见长度和内容
def check_content(content):
    #意见反馈内容不超过100个字符
    if int(len(content)/3) > 300 or int(len(content)) < 0 :
        return 1 
    #意见反馈内容不可以提到共产党
    elif str(content).find('共产党') != -1 :
        return 2
    else :
        return 0