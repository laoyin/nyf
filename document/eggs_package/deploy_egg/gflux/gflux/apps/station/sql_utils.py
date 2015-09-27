# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

from django.conf import settings
from datetime import datetime, timedelta
from dash.core import helper
from dash.core import fields
from dash.core import reports
from dash.core.types import enum
from dash.core.types import overrides
from dash.core.backends.sql.models import get_dash_session_maker
from models import Trans, TransType, PaymentType, CardType, DayPeriod,StationHealthStatus,\
    FuelType, Location, UserStation, User,StationFuelType,StationNoneFuelTop,HealthStatus,\
    FuelTypeRelation,StationDailyFuelSales,FuelTypeRelation,Card,StationItemAssoc,Tag
from dash.core.utils import uid,getPaymentTypeByCard,compute_trans_id,deserialize_trans_id
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from gflux.apps.common.models import Station, DimDateHour,SiteDayBatch,\
    DimChinaProvinceCityDistrict
from . import cubes
from django.core.cache import cache
from sqlalchemy.sql import select, and_, or_, func
from sqlalchemy import select as select_directly
from sqlalchemy import update
from sqlalchemy import delete
import math,json,copy,re
import pdb,traceback,logging
from gflux.apps.station.models import all_type_args,PumpType,StationDailyStat,StationMonthStat
from sqlalchemy.sql.expression import ClauseElement
from django.utils.translation import ugettext as _
from gflux.util import exception_stuck
import time,hashlib

DEFAULT_DATE = datetime(2013, 10, 21)

#set ajaxLogger
ajax_logger=logging.getLogger('ajax')

"""
工具方法 util
"""

#返回多站分析的区域范围行政区划号
def locate_china_location_id_from_request(request):
    #确定地区过滤器

    location_barcode=request.GET.get('china_location',None)
    location=None

    s=request.get_session()
    #未携带
    if location_barcode==None:
        #使用当前用户的省
        user=s.query(User).filter_by(name=request.session['username']).one()

        if user.district==0:
            return 0

        #县
        location=s.query(DimChinaProvinceCityDistrict).filter_by(id=user.district).one()

        while True:
            #判断当前等级
            if location.level!=1:
                location=s.query(DimChinaProvinceCityDistrict).filter_by(id=location.parent).one()
            else:
                break

        location_barcode=location.id

    else:
        try:
            location_barcode=int(location_barcode)
            if location_barcode==0:
                return 0
            location=s.query(DimChinaProvinceCityDistrict).filter_by(id=location_barcode).one()
        except:
            return 0

    return location_barcode

#返回油站名
def get_station_desc_by_name(name):
    s=get_dash_session_maker()()
    try:
        obj=s.query(Station).filter_by(name=name).one()
        name=obj.description
    except:
        name='ERROR'
    finally:
        s.close()
        return name


#返回地区名
def get_china_location_name_by_id(id):
    if id==0:
        return '中国'

    s=get_dash_session_maker()()
    try:
        obj=s.query(DimChinaProvinceCityDistrict).filter_by(id=id).one()
        name=obj.name
    except:
        name='ERROR'
    finally:
        s.close()
        return name


#取得系统的油品标号
def get_system_fuel_type():
    #初始化默认值
    all_fuel_types_dict=[]

    #读缓存
    try:
        cached=cache.get('system_fuel_type')
        all_fuel_types_dict=json.loads(cached)
    except:
        all_fuel_types_dict=[]

    #缓存失败读数据库
    if len(all_fuel_types_dict)==0:
        #创建sesion
        s=get_dash_session_maker()()
        all_fuel_type=s.query(FuelTypeRelation).all()

        for fuel_type in all_fuel_type:
            all_fuel_types_dict.append(dict(
                barcode=fuel_type.id,
                desc=fuel_type.name
            ))
        s.close()

        #更新cache
        cached=json.dumps(all_fuel_types_dict)
        cache.set('system_fuel_type',cached,settings.MEMCACHED_TIMEOUT)

    #构造结果
    ret=[]
    for info in all_fuel_types_dict:
        ret.append((info['barcode'],info['desc']))
    return ret

#获取上个自然月的开始和结束日期
def prev_bounds(when=None):
    from datetime import date, datetime, timedelta
    if not when:
        when = datetime.today()
    this_first = date(when.year, when.month, 1)
    prev_end = this_first - timedelta(days=1)
    prev_first = date(prev_end.year, prev_end.month, 1)
    return prev_first, prev_end

# 获取所有的油品类型

def get_all_fuel_types(tree_order=False):
    all_fuel_types_cache_data=read_all_fuel_types_from_cache('all_fuel_types')
    if all_fuel_types_cache_data!=None and len(all_fuel_types_cache_data)!=0 :
        return all_fuel_types_cache_data

    ret_fuel_types=[]

    sql=select([FuelType.name, FuelType.numid, FuelType.description]).select_from(FuelType.__table__)
    create_session = get_dash_session_maker()
    s = create_session()
    fuel_types = s.execute(sql)
    fuel_types = fuel_types.fetchall()

    #other cache
    fuel_des_cache_data={}
    all_fuel_barcodes_cache_data=[]

    for fuel_type in fuel_types :
        ret_fuel_types.append((fuel_type.numid, fuel_type.description))

        #update cache
        fuel_des_cache_data[str(fuel_type.numid)]=fuel_type.description
        all_fuel_barcodes_cache_data.append(int(fuel_type.numid))

    write_all_fuel_barcodes_in_cache('all_fuel_barcodes',all_fuel_barcodes_cache_data)
    write_fuel_descriptions_in_cache('fuel_descriptions',fuel_des_cache_data)

    if tree_order==False:
        ret_fuel_types.sort(key=lambda x: x[1], reverse=True)
    else :
        ret_fuel_types.sort(key=lambda x: x[0])

    #UPDATE CACHE
    all_fuel_types_cache_data=ret_fuel_types
    write_all_fuel_types_in_cache('all_fuel_types',all_fuel_types_cache_data)

    s.close()

    return ret_fuel_types

# 根据油品类型编号获取名称
# 如果没找到且指定了新的描述，则新加
def get_fuel_type_name(barcode,description=None):
    fuel_des_cache_data=read_fuel_descriptions_from_cache('fuel_descriptions')
    if fuel_des_cache_data==None:
        fuel_des_cache_data={}
    if fuel_des_cache_data.has_key(str(barcode)) :
        if fuel_des_cache_data[str(barcode)]!=None:
            return fuel_des_cache_data[str(barcode)]

    fuel_name=None
    create_session = get_dash_session_maker()
    s = create_session()
    fuel_sql=select_directly([FuelType.description]).where(FuelType.numid==str(barcode)).label('tao-gilbarco')
    rs=s.query(fuel_sql)

    ret=rs.first()
    if ret[0]!=None:
        fuel_name=ret[0]
    else:
        if description!=None:
            fuel_name=description
            s.execute(FuelType.__table__.insert(),[{'description':description,
                'name':description,'numid':str(barcode)}])
            s.commit()

            #delete cache
            delete_by_key_from_cache('all_fuel_barcodes')
	else:
	    obj = s.query(StationFuelType).filter_by(barcode=int(barcode)).first()
	    if obj!=None:
	        description = obj.description
	        fuel_name=description
                s.execute(FuelType.__table__.insert(),[{'description':description,
                    'name':description,'numid':str(barcode)}])
                s.commit()

                #delete cache
                delete_by_key_from_cache('all_fuel_barcodes')


    s.close()
    fuel_des_cache_data[str(barcode)]=fuel_name
    write_fuel_descriptions_in_cache('fuel_descriptions',fuel_des_cache_data)

    return fuel_name


#add new fule type to fueltype
def add_fuel_type_to_fueltype_table(barcode,description):
    get_fuel_type_name(barcode,description=description)

# 获取所有的油品类型编号
def get_all_fuel_barcodes():
    ret_fuel_barcodes=[]
    #检查缓存
    cache_data=read_all_fuel_barcodes_from_cache('all_fuel_barcodes')
    if cache_data!=None and len(cache_data)!=0:
        return cache_data

    # 重新计算
    sql = select([FuelType.numid]).select_from(FuelType.__table__)
    create_session = get_dash_session_maker()
    s = create_session()
    fuel_types = s.execute(sql)
    fuel_types = fuel_types.fetchall()

    for fuel_type in fuel_types :
        ret_fuel_barcodes.append(int(fuel_type.numid))

    ret_fuel_barcodes.sort(reverse=True)
    s.close()


    write_all_fuel_barcodes_in_cache('all_fuel_barcodes',ret_fuel_barcodes)

    return ret_fuel_barcodes

# 获取所有的加油站
def get_all_stations():

    ret_sites=[]

    sql = select([Station.name, Station.description]).select_from(Station.__table__)
    create_session = get_dash_session_maker()
    s = create_session()
    sites = s.execute(sql)
    sites = sites.fetchall()
    station_des_cache_data={}

    for site in sites :
        ret_sites.append((site.name, site.description))

        #update cache
        station_des_cache_data[site.name]=site.description
    write_station_descriptions_in_cache(station_des_cache_data)

    s.close()

    return ret_sites

# check加油站码
def check_staticons_code(name):
    #读取所有加油站的缓存
    cache_data=read_station_descriptions_from_cache()
    #如果缓存中存在，则返回TRUE，不存在从数据库判断
    if cache_data!=None:
        if cache_data.has_key(name):
            return True
    stationExist=True;
    sql = select([Station.name]).where(Station.name==name).select_from(Station.__table__)
    create_session = get_dash_session_maker()
    s = create_session()
    sites = s.execute(sql)
    sites = sites.fetchall()
    s.close()
    if len(sites)==0:
        stationExist=False
    return stationExist


# 获取一个油站的油枪数量

def get_nb_guns_of_station(site_name) :

    nb_guns=0

    create_session = get_dash_session_maker()
    s = create_session()

    sql=select_directly([Station.nb_guns]).where(Station.name==site_name).label('tao-gilbarco')
    rs=s.query(sql)
    ret=rs.first()
    if ret!=None:
        if ret[0]==None:
            #尝试过滤fact表
            create_session = get_dash_session_maker(site_name)
            s = create_session()
            cube = cubes.TransCube(s)
            conditions = [cube.d.pump_id>0,
                          cube.d.site == site_name]
            results = cube.aggregate(measures=['pump_count'],
                                     conditions=conditions,
                                     session=s)

            nb_guns=results[0]['pump_count']
        else :
            nb_guns=int(ret[0])

    s.close()

    return nb_guns

# 获取一个地点的油站数量

def get_nb_stations_of_location(location_id) :

    nb_sites=0

    create_session = get_dash_session_maker()
    s = create_session()

    sql=select_directly([Location.nb_sites]).where(Location.id==location_id).label('tao-gilbarco')
    rs=s.query(sql)
    ret=rs.first()
    s.close()
    if ret!=None:
        if ret[0]==None:
            nb_sites=0
        else :
            nb_sites=int(ret[0])

    return nb_sites

# 获取地点的所有加油站名
def get_all_sites_by_location_id(location_id):
    create_session = get_dash_session_maker()
    s = create_session()
    site_list=[]

    if location_id==0:
        sql = select([Station.name]).select_from(Station.__table__)
        sites = s.execute(sql).fetchall()

        for site in sites :
            site_list.append(site.name)

    else:
        sql=select_directly([Station.name]).where(Station.locid==location_id)

        sites = s.execute(sql).fetchall()

        for site in sites :
            site_list.append(site.name)

    s.close()

    return site_list

# 获取所有的地点

def get_all_locations(with_dict_info=False):
    all_locations_cache_data=read_all_locations_from_cache('all_locations')
    all_locations_with_dict_info_cache_data=read_all_locations_with_dict_info_from_cache('all_locations_with_dict_info')
    if ((all_locations_cache_data!=None and len(all_locations_with_dict_info_cache_data)!=0) and with_dict_info==False):
        return all_locations_cache_data
    elif all_locations_with_dict_info_cache_data!=None and len(all_locations_with_dict_info_cache_data)!=0 and with_dict_info:
        return all_locations_with_dict_info_cache_data

    ret_loc_names=[]
    ret_loc_names_with_dict_info=[]

    sql = select([Location.name, Location.id, Location.description]).select_from(Location.__table__)

    create_session = get_dash_session_maker()
    s = create_session()

    locs = s.execute(sql)
    locs = locs.fetchall()

    for loc in locs :
        ret_loc_names_with_dict_info.append(dict(
                id=loc.id,
                description=loc.description,
                name=loc.name))

        ret_loc_names.append((loc.id, loc.description))
    all_locations_cache_data=ret_loc_names
    write_all_locations_in_cache('all_locations',all_locations_cache_data)
    all_locations_with_dict_info_cache_data=ret_loc_names_with_dict_info
    write_all_locations_with_dict_info_in_cache('all_locations_with_dict_info',all_locations_with_dict_info_cache_data)

    s.close()

    if with_dict_info:
        return ret_loc_names_with_dict_info
    else:
        return ret_loc_names

# check地点码

def check_locations_code(name):
    locationExist=True

    sql = select([Location.name, Location.id]).where(Location.name==name).select_from(Location.__table__)

    create_session = get_dash_session_maker()
    s = create_session()

    locs = s.execute(sql)
    locs = locs.fetchall()
    s.close()
    if len(locs)==0 :
        locationExist=False

    return locationExist

# 根据图标数据取得高峰期时段
def get_peak_period(data):
    dict={}
    #检查数据
    if len(data['dataset'])==0:
        dict['crest_list']=[]
        dict['diff_value']=0

        period={}
        period['crest']=[]
        period['valley']=[]
        period['high']=[]
        period['low']=[]
        dict['period']=period
        return dict

    #去掉为0的值
    max_min_list=[]
    for count in data['dataset'][0]['data']:
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

    #求谷峰差率
    if min_data==0:
        dict['diff_value']=0
    else:
        dict['diff_value']=round(max_data/min_data,1)
    #计算每小时平均交易笔数
    crest_avg_count=0
    valley_avg_count=0
    last_count=data['dataset'][0]['data'][0]

    #默认值
    crest=[]
    crest_list=[]
    current_time=0
    valley_list=[]
    high_list=[]
    low_list=[]

    #0-8点的值
    first_data=sorted(data['dataset'][0]['data'][:8])
    first_min_data=first_data[0]
    first_max_data=first_data[7]

    #8-16点的值
    second_data=sorted(data['dataset'][0]['data'][8:16])
    second_min_data=second_data[0]
    second_max_data=second_data[7]

    #16-24点的值
    third_data=sorted(data['dataset'][0]['data'][16:24])
    third_min_data=third_data[0]
    third_max_data=third_data[7]

    v=(first_min_data+first_max_data+second_min_data+second_max_data+third_min_data+third_max_data)/6
    crest_avg_count=1.2*v
    valley_avg_count=0.6*v

    for count in data['dataset'][0]['data']:
        #高峰期
        #计算偏移量
        offset=count-crest_avg_count

        if offset>0:
            crest.append(current_time)
        elif valley_avg_count-count>0:
            valley_list.append(current_time)
        elif current_time==0:
            if data['dataset'][0]['data'][0]<data['dataset'][0]['data'][1]:
                high_list.append(0)
            else:
                low_list.append(0)
        elif last_count-count>0:
            low_list.append(current_time)
        else:
            high_list.append(current_time)

        last_count=count
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
    dict['crest_list']=crest_list
    period={}
    period['crest']=crest
    period['valley']=valley_list
    period['high']=high_list
    period['low']=low_list
    dict['period']=period

    return dict


# 获取一个站点的整数ID,如果不存在则增加该站点
# 这个函数的参数按照顺序依次是,站点代码,省,市,区,用户id,站点名称,是否创建
def get_station_id(station_name, province=0, city=0, district=0, user_id=None,site_desc=None,with_created_status=False):

    station_id=0

    # 检查是否存在
    create_session = get_dash_session_maker()
    s = create_session()

    sql=select_directly([Station.id]).where(Station.name==station_name).label('tao-gilbarco')
    rs=s.query(sql)
    ret=rs.first()

    if ret!=None and ret[0]!=None:
        station_id=int(ret[0])
        if with_created_status:
            return station_id,False
        return station_id

    # 获取当前最大id
    succ=False
    sql=select_directly([func.max(Station.id)]).label('tao-gilbarco')
    rs=s.query(sql)
    ret=rs.first()
    if ret!=None and ret[0]!=None:
        station_id=int(ret[0])+1
    else :
        station_id=1

    # 存储该站点
    new_sites=[]
    site_dic = {
    	'name':station_name,
        'id':station_id,
        'description':site_desc if site_desc!=None else station_name,
        'province':province,
        'city':city,
        'district':district,
    }
    new_sites.append(site_dic)

    try:
      	s.execute(Station.__table__.insert(), new_sites)
        s.commit()
        succ=True
    except Exception,e:
        s.rollback()
        ajax_logger.error(str(e))

    # 创建用户油站所属关系
    if user_id!=None and succ:
        site,created=get_or_create(s,UserStation,user_id=user_id,station=station_name)
        s.commit()

    s.close()
    if with_created_status:
        return station_id,True
    return station_id

# 更新油站的信息

def update_station_info(name, description, locid, nb_guns, phone,
                        address, brand, distance,guns_id):

    create_session = get_dash_session_maker()
    s = create_session()

    # description
    if description!=None:
        stmt = update(Station).where(Station.name==name).\
                values(description=description)
        try:
            s.execute(stmt)
            s.commit()
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))

    # locid
    if locid!=None:
        stmt = update(Station).where(Station.name==name).\
                values(locid=locid)
        try:
            s.execute(stmt)
            s.commit()
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))

    # nb_guns
    if nb_guns!=None:
        stmt = update(Station).where(Station.name==name).\
                values(nb_guns=nb_guns)
        try:
            s.execute(stmt)
            s.commit()
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))

    # phone
    if phone!=None:
        stmt = update(Station).where(Station.name==name).\
                values(phone=phone)
        try:
            s.execute(stmt)
            s.commit()
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))

    # address
    if address!=None:
        stmt = update(Station).where(Station.name==name).\
                values(address=address)
        try:
            s.execute(stmt)
            s.commit()
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))

    # brand
    if brand!=None:
        stmt = update(Station).where(Station.name==name).\
                values(brand=brand)
        try:
            s.execute(stmt)
            s.commit()
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))

    # distance
    if distance!=None:
        stmt = update(Station).where(Station.name==name).\
                values(distance=distance)
        try:
            s.execute(stmt)
            s.commit()
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))

    #更新油枪号
    if guns_id!=None and guns_id!=[]:
        stmt = update(Station).where(Station.name==name).\
                values(id_guns=json.dumps(guns_id),nb_guns=len(guns_id))
        try:
            s.execute(stmt)
            s.commit()
        except Exception,e:
            s.rollback()
            ajax_logger.error(str(e))

    s.close()

# 获取一个用户ID的所有油站名称

def get_user_stations_by_id(user_id=1):

    ret_sites=[]
    station_descriptions_cache_data=read_station_descriptions_from_cache()
    if station_descriptions_cache_data==None:
        station_descriptions_cache_data={}
    # 获取对应的站点名称

    names=[]
    create_session = get_dash_session_maker()
    s = create_session()
    sql=select([UserStation.station]).where(UserStation.user_id==user_id)
    rs=s.execute(sql)
    sites=rs.fetchall()
    if len(sites)==0:
        return []

    for site in sites:
        names.append(site.station)

    # 获取对应的油站信息

    for name in names:
        if station_descriptions_cache_data.has_key(name):
            ret_sites.append((name, station_descriptions_cache_data[name]))

        else:
            sql = select_directly([Station.description]).where(Station.name==name).label('tao-gilbarco')
            rs=s.query(sql)
            ret=rs.first()
            if ret!=None and ret[0]!=None:
                ret_sites.append((name, ret[0]))
                station_descriptions_cache_data[name]=ret[0]
    write_station_descriptions_in_cache(station_descriptions_cache_data)

    s.close()

    return ret_sites

# 获得用户加油站的油机通道分布
def get_user_station_description_by_name(station_name=None):
    #初始值
    ret={'machines':[],'passages':[]}

    if station_name==None:
        return ret

    #查询数据库

    #创建session
    create_session = get_dash_session_maker()
    s = create_session()

    try:
        obj=s.query(Station).filter_by(name=station_name).one()
        ret.update(json.loads(obj.machine_passage))
    except Exception,e:
        pass
    finally:
        #关闭session
        s.close()

        return ret

# 获取一个用户名称的所有油站名称

def get_user_stations_by_name(user_name=None,with_dict_info=False):
    ret_sites=[]
    if user_name==None:
        return ret_sites
    station_descriptions_cache_data=read_station_descriptions_from_cache()
    if station_descriptions_cache_data==None:
        station_descriptions_cache_data={}
    create_session = get_dash_session_maker()
    s = create_session()

    # 获取用户ID
    try :
        sql=select([User.id]).where(User.name==user_name).label('tao-gilbarco')
        rs=s.query(sql)
        ret=rs.first()
    except:
        return ret_sites
    user_id=ret[0]

    # 获取对应的站点名称
    names=[]
    sql=select([UserStation.station]).where(UserStation.user_id==user_id)
    rs=s.execute(sql)
    sites=rs.fetchall()
    if len(sites)==0:
        return []

    for site in sites:
        names.append(site.station)

    # 获取对应的油站信息
    for name in names:
        if station_descriptions_cache_data.has_key(name) :
            desc=station_descriptions_cache_data[name]
            if with_dict_info:
                ret_sites.append(dict(
                    name=name,
                    description=desc
                ))
            else:
                ret_sites.append((name, desc))
        else :
            sql = select_directly([Station.description]).where(Station.name==name).label('tao-gilbarco')
            rs=s.query(sql)
            ret=rs.first()
            if ret!=None and ret[0]!=None:
                if with_dict_info:
                    ret_sites.append(dict(
                            name=name,
                            description=ret[0]
                            ))
                else:
                    ret_sites.append((name, ret[0]))
            station_descriptions_cache_data[name]=ret[0]
    s.close()
    write_station_descriptions_in_cache(station_descriptions_cache_data)
    return ret_sites

# 获取一个用户name的账户类型

def get_user_account_type_by_name(user_name):

    user_type=0

    # 获取用户TYPE
    try :
        create_session = get_dash_session_maker()
        s = create_session()
        sql=select([User.type]).where(User.name==user_name).label('tao-gilbarco')
        rs=s.query(sql)
        ret=rs.first()
        s.close()
    except:
        return user_type

    return ret[0]

#get enable_advanced_features
def get_enable_advanced_features_by_name(user_name):

    enable_advanced_features=0

    # 获取用户TYPE
    try :
        create_session = get_dash_session_maker()
        s = create_session()
        sql=select([User.enable_advanced_features]).where(User.name==user_name).label('tao-gilbarco')
        rs=s.query(sql)
        ret=rs.first()
        s.close()
    except:
        return enable_advanced_features

    return ret[0]

# 检查帐号类型是否允许访问某个portal

def check_if_user_is_allowed_to_portal(portal_class, user_type) :

    from gflux.apps.station import ui_portal

    if isinstance(portal_class,type):
        type_val=portal_class
    else:
        type_val=type(portal_class)

    if type_val==ui_portal.StationPortal :
        return user_type>=1
    elif type_val==ui_portal.IndexPortal :
        return user_type>=3
    elif type_val==ui_portal.AdminPortal :
        return user_type>=4
    elif type_val==ui_portal.UploadPortal :
        return user_type>=2

    return user_type>=0

#获得每个加油站的非油品top10
def get_station_none_fuel_top10_by_name(site_name):
    ret=[]
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        sql=select([StationNoneFuelTop.top]).where(StationNoneFuelTop.station==site_name).label('tao-gilbarco')
        rs=s.query(sql)
        ret=json.loads(rs.first()[0])
        s.close()
    except Exception,e:
        ajax_logger.error(str(e))
    finally:
        return ret

#更新每个加油站的非油品top10
def set_station_none_fuel_top10(site_name,top):
    try:
        create_session = get_dash_session_maker()
        s = create_session()
	#obj = s.query(StationNoneFuelTop).filter_by(station=site_name).one()
	#obj.top = json.dumps(top)
        obj,created=get_or_create(
            s,StationNoneFuelTop,
            station=site_name,
            defaults={
                'top':json.dumps(top)
            }
        )
        s.commit()
        s.close()
    except Exception,e:
        #print exception_stuck()
        ajax_logger.error(str(e))

#更新用户的非油品top10
def update_user_none_fuel_top10(user_name=None,site_name=None):
    if user_name==None and site_name==None:
        return []
    create_session = get_dash_session_maker()
    s = create_session()
    if site_name==None:
        # 获取用户ID
        try :
            sql=select([User.id]).where(User.name==user_name).label('tao-gilbarco')
            rs=s.query(sql)
            ret=rs.first()
        except:
            return []

        user_id=ret[0]

        # 获取对应的站点名称
        sql=select([UserStation.station]).where(UserStation.user_id==user_id)
        rs=s.execute(sql)
        sites=rs.fetchall()
        s.close()
        if len(sites)==0:
            return []
        # 分析站点都在哪些shard上
        all_site=[site.station for site in sites]
    else:
        all_site=[site_name]

    for site in all_site:

        create_session_func=get_dash_session_maker(site)
        s=create_session_func()
        sql='SELECT sum(fact_trans.pay) AS pay, max(fact_trans."desc") AS "desc", fact_trans.barcode AS barcode FROM fact_trans WHERE fact_trans.trans_type = 1 AND fact_trans.site = \'%s\' GROUP BY fact_trans.barcode ORDER BY pay desc  LIMIT 10;'%(site)

        ret_non_fuel_types=[]
        #results = cube.aggregate(measures=['pay'],
         #                        drilldown=['barcode'],
          #                       details=['desc'],
           #                      conditions=conditions,
            #                     order='pay desc',
             #                    limit=10,
              #                   session=s)
	results=s.execute(sql)

        for result in results:
            ret_non_fuel_types.append({'barcode':result.barcode,
            'desc':result.desc,'pay':result.pay})
        s.close()
        #update cache
        set_station_none_fuel_top10(site,ret_non_fuel_types)

#获取用户所有非油品的top10销售额产品
#TODO：此函数需要优化, 每个用户的非油类型需要离线计算并缓存
def get_user_none_fuel_type_by_name(user_name=None):
    if user_name==None:
        return []
    user_none_fuel_top10_cache_data=read_user_none_fuel_top10_from_cache('%s_user_none_fuel_top10'% user_name)
    if user_none_fuel_top10_cache_data==None :
        user_none_fuel_top10_cache_data={}
    else:
        return user_none_fuel_top10_cache_data[user_name]
    create_session = get_dash_session_maker()
    s = create_session()
    # 获取用户ID
    try :
        sql=select([User.id]).where(User.name==user_name).label('tao-gilbarco')
        rs=s.query(sql)
        ret=rs.first()
    except:
        return []

    user_id=ret[0]

    # 获取对应的站点名称
    sql=select([UserStation.station]).where(UserStation.user_id==user_id)
    rs=s.execute(sql)
    sites=rs.fetchall()
    s.close()
    if len(sites)==0:
        return []

    # 分析站点都在哪些shard上
    ret_non_fuel_types=[]
    already_barcodes=[]
    for site in sites:
        tmp=get_station_none_fuel_top10_by_name(site.station)
        for t in tmp:
            if t['barcode'] in already_barcodes:
                continue
            already_barcodes.append(t['barcode'])
            ret_non_fuel_types.append(t)

    #sort
    ret_non_fuel_types.sort(key=lambda x:x['pay'],reverse=True)
    ret_non_fuel_types=ret_non_fuel_types[:10]

    total_top=[]
    for result in ret_non_fuel_types:
        total_top.append((result['barcode'],result['desc']))

    user_none_fuel_top10_cache_data[user_name]=total_top
    write_user_none_fuel_top10_in_cache('%s_user_none_fuel_top10'%user_name,user_none_fuel_top10_cache_data)
    return total_top

# 从Django表格中读取事先计算好的站点油品类型
def get_station_fuel_types_by_name(site_name=None,with_dict_info=False) :

    ret_fuel_types=[]

    if site_name==None:
        return []

    create_session = get_dash_session_maker()
    s = create_session()
    sql=select([StationFuelType.barcode,StationFuelType.description]).where(StationFuelType.station==site_name)
    rs=s.execute(sql)
    fuels=rs.fetchall()
    s.close()

    for fuel in fuels:
        if with_dict_info:
            ret_fuel_types.append({
                'barcode':fuel.barcode,
                'desc':fuel.description
                })
        else:
            ret_fuel_types.append((fuel.barcode, fuel.description))

    return ret_fuel_types

# 将站点油品类型缓存到Django表格中
def set_station_fuel_type(site_name, barcode, desc) :
    try:
        create_session = get_dash_session_maker()
        s = create_session()
        dim={}
        dim['barcode']=barcode
        dim['description']=desc
        dim['station']=site_name
        s.execute(StationFuelType.__table__.insert(), dim)
        s.commit()
        s.close()
    except Exception, e:
        ajax_logger.error(str(e))

# 更新指定用户或所有用户的站点油品类型并存储到django中
def update_station_fuel_types_from_fact_trans(user_name=None,site_name=None):
    #没有指定油站
    if site_name==None:

        #检查是否指定用户
        sites=[]
        create_session = get_dash_session_maker()
        s = create_session()

        #没有指定用户,取得所有的站
        if user_name==None:
            sites=s.query(UserStation).all()

        else :
            # 取得改用户的所有站
            user=s.query(User).filter_by(name=user_name).one()
            sites=s.query(UserStation).filter_by(user_id=user.id)

        s.close()
        all_site=[site.station for site in sites]

        #没有任何站点需要被更新
        if len(all_site)==0:
            return

    else:
        all_site=[site_name]

    # 分析站点都在哪些shard
    shard_sites={}
    shard_funcs={}
    for site in all_site:
        shard_id,create_session_func=get_dash_session_maker(site, True)
        if shard_sites.has_key(shard_id) :
            names=shard_sites[shard_id]
            names.append(site)
            shard_sites[shard_id]=names
        else :
            shard_sites[shard_id]=[site]
        shard_funcs[shard_id]=create_session_func

    # 处理每个shard上的站点的油品类型，批量处理
    cur_fuel_types={}
    for shard_id in shard_sites.iterkeys():
        create_session=shard_funcs[shard_id]
        s=create_session()
        names=shard_sites[shard_id]
        sql=select_directly([Trans.barcode,func.min(Trans.desc),Trans.site]).where(and_(Trans.site.in_(names),Trans.pump_id>0)).group_by(Trans.barcode,Trans.site)
        rs=s.execute(sql).fetchall()
        for ret in rs:
            set_station_fuel_type(ret[2], ret[0], ret[1])

            #add fuel type to fueltype table
            add_fuel_type_to_fueltype_table(ret[0],ret[1])

        s.close()

#获取用户的所有油品类型barcode
def get_user_fuel_type_by_name(user_name=None):
    ret_fuel_types=[]
    if user_name==None:
        return ret_fuel_types
    user_fuel_types_dict_cache_data=read_user_fuel_types_dict_from_cache('%s_user_fuel_types_dict' %user_name)
    if user_fuel_types_dict_cache_data==None:
        user_fuel_types_dict_cache_data={}
    else:
        return user_fuel_types_dict_cache_data[user_name]


    # 获取用户ID
    try :
        create_session = get_dash_session_maker()
        s = create_session()
        sql=select([User.id]).where(User.name==user_name).label('tao-gilbarco')
        rs=s.query(sql)
        ret=rs.first()
        s.close()
    except:
        return ret_fuel_types

    user_id=ret[0]

    # 获取对应的站点名称
    create_session = get_dash_session_maker()
    s = create_session()
    sql=select([UserStation.station]).where(UserStation.user_id==user_id)
    rs=s.execute(sql)
    sites=rs.fetchall()
    s.close()

    if len(sites)==0:
        return []

    already_fuel_types={}
    for site in sites:
        fuel_types=get_station_fuel_types_by_name(site.station,with_dict_info=True)
        for fuel_type in fuel_types:
            if already_fuel_types.has_key(fuel_type['barcode']):
                continue
            already_fuel_types[fuel_type['barcode']]=1
            ret_fuel_types.append(fuel_type)

    #sort
    ret_fuel_types.sort(key=lambda x :x['barcode'])

    sorted_ret=[]

    for ret_fuel_type in ret_fuel_types:
        sorted_ret.append((ret_fuel_type['barcode'],ret_fuel_type['desc']))
    user_fuel_types_dict_cache_data[user_name]=sorted_ret
    write_user_fuel_types_dict_in_cache('%s_user_fuel_types_dict'% user_name,user_fuel_types_dict_cache_data)
    return sorted_ret

# 获取一个地点的整数ID，如果不存在则增加该地点

def get_location_id(loc_name, loc_description):

    s = get_dash_session_maker()()
    sql=select_directly([Location.id]).where(or_(Location.description==loc_description,
                                                 Location.name==loc_name))
    rs=s.execute(sql).fetchall()

    if len(rs)!=0:
        loc_id=int(rs[0][0])
    else :

        # 获取当前最大id
        sql=select_directly([func.max(Location.id)]).label('tao-gilbarco')
        rs=s.query(sql)
        ret=rs.first()
        if ret!=None and ret[0]!=None:
            max_id=int(ret[0])+1
        else :
            max_id=1

        # 设置最大id
        loc_dic={
            'name':loc_name,
            'description':loc_description,
            'nb_sites':0,
            'id':max_id,
        }
        loc=Location(**loc_dic)
        s.add(loc)
        s.commit()
        loc_id=max_id
        delete_by_key_from_cache('all_locations')
        delete_by_key_from_cache('all_locations_with_dict_info')

    s.close()

    return loc_id

#获取位置描述信息
def get_location_desc_by_id(loc_name):
    s = get_dash_session_maker()()
    sql=select_directly([Location.description]).where(Location.name==loc_name)
    rs=s.execute(sql).fetchall()

    loc_dec = None

    if len(rs)!=0:
        loc_dec=rs[0][0]

    return loc_dec

#获取油站描述信息
def get_site_desc_by_name(name):
    s = get_dash_session_maker()()
    sql=select_directly([Station.description]).where(Station.name==name)
    rs=s.execute(sql).fetchall()

    site_dec = None

    if len(rs)!=0:
        site_dec=rs[0][0]

    return site_dec


#计算每天油站汇总数据
def compute_station_daybatch(site_name,start_date,end_date):
    #create session
    src_session=get_dash_session_maker(site_name)()
    des_session=get_dash_session_maker()()

    try:

        #油站情况
        station=des_session.query(Station).filter_by(name=site_name).one()

        #compute
        curr_date=start_date
        while curr_date <= end_date:
            futher_date=curr_date+timedelta(days=1)
            pre_mon_curr_date=curr_date-relativedelta(months=1)
            pre_mon_futher_date=futher_date-relativedelta(months=1)

            #油品销量
            sql='select sum(quantity) as quantity_fuel from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\' and trans_type=%s;'%(
                curr_date.strftime('%Y-%m-%d'),futher_date.strftime('%Y-%m-%d'),
                site_name,TransType.FUEL
            )
            quantity_fuel=0
            rets=src_session.execute(sql)
            for ret in rets:
                if ret.quantity_fuel!=None:
                    quantity_fuel=ret.quantity_fuel

            #非油品销量
            sql='select sum(quantity) as quantity_nonefuel from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\' and trans_type=%s;'%(
                curr_date.strftime('%Y-%m-%d'),futher_date.strftime('%Y-%m-%d'),
                site_name,TransType.NON_FUEL
            )
            quantity_nonefuel=0
            rets=src_session.execute(sql)
            for ret in rets:
                if ret.quantity_nonefuel!=None:
                    quantity_nonefuel=ret.quantity_nonefuel

            #非油品对油品比例
            nonefuel_percent=0
            if quantity_fuel==0:
                nonefuel_percent=0
            else:
                nonefuel_percent=quantity_nonefuel*100/quantity_fuel

            #上月油品销量
            sql='select sum(quantity) as quantity_fuel from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\' and trans_type=%s;'%(
                pre_mon_curr_date.strftime('%Y-%m-%d'),pre_mon_futher_date.strftime('%Y-%m-%d'),
                site_name,TransType.FUEL
            )
            pre_mon_quantity_fuel=0
            rets=src_session.execute(sql)
            for ret in rets:
                if ret.quantity_fuel!=None:
                    pre_mon_quantity_fuel=ret.quantity_fuel

            #油品环比
            fuel_mom_percent=0
            if pre_mon_quantity_fuel==0:
                fuel_mom_percent=0
            else:
                fuel_mom_percent=(quantity_fuel-pre_mon_quantity_fuel)*100/pre_mon_quantity_fuel

            #上月非油品销量
            sql='select sum(quantity) as quantity_nonefuel from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\' and trans_type=%s;'%(
                pre_mon_curr_date.strftime('%Y-%m-%d'),pre_mon_futher_date.strftime('%Y-%m-%d'),
                site_name,TransType.NON_FUEL
            )
            pre_mon_quantity_nonefuel=0
            rets=src_session.execute(sql)
            for ret in rets:
                if ret.quantity_nonefuel!=None:
                    pre_mon_quantity_nonefuel=ret.quantity_nonefuel

            #非油品环比
            nonefuel_mom_percent=0
            if pre_mon_quantity_nonefuel==0:
                nonefuel_mom_percent=0
            else:
                nonefuel_mom_percent=(quantity_nonefuel-pre_mon_quantity_nonefuel)*100/pre_mon_quantity_nonefuel

            #高峰期平均出油量
            peak_fuel_avg_gun=0

            #交易笔数情况
            sql='SELECT count(DISTINCT fact_trans.trans_id) AS trans_count, dim_datehour.hour AS hour, \
            sum(quantity) as quantity_count \
            FROM fact_trans JOIN dim_datehour ON dim_datehour.id = fact_trans.datehour \
            WHERE fact_trans.site =\'%s\' AND fact_trans.datehour >=\'%s\' AND \
            fact_trans.datehour <\'%s\' AND fact_trans.trans_type =%s GROUP BY dim_datehour.hour'%(
                site_name,curr_date.strftime('%Y-%m-%d'),futher_date.strftime('%Y-%m-%d'),
                TransType.FUEL
            )
            rets=src_session.execute(sql)

            #数据整理
            trans_count={
                'categories':[
                    '0 - 1', '1 - 2', '2 - 3', '3 - 4', '4 - 5', '5 - 6', '6 - 7',
                    '7 - 8', '8 - 9', '9 - 10', '10 - 11', '11 - 12', '12 - 13',
                    '13 - 14', '14 - 15', '15 - 16', '16 - 17', '17 - 18', '18 - 19',
                    '19 - 20', '20 - 21', '21 - 22', '22 - 23', '23 - 24'
                ],
                'dataset': [{
                    'data': [],
                    'name': 'test'}
                ]
            }
            trans_dict={}
            for ret in rets:
                trans_dict[ret.hour]=ret.quantity_count
            for idx in xrange(24):
                trans_count['dataset'][0]['data'].append(trans_dict.get(idx,0))

            peak_rets=get_peak_period(trans_count)

            #高峰期列表
            peak_list=peak_rets['period']['crest']

            #总的小时数和油量,以及最大峰值
            total_hours=0
            total_fuel=0
            peak_fuel_biggest=0
            for peak in peak_list:
                total_hours+=1
                total_fuel+=trans_dict[peak]
                if trans_dict[peak]>peak_fuel_biggest:
                    peak_fuel_biggest=trans_dict[peak]

            peak_fuel_count=total_fuel
            peak_hour_num=total_hours
            if total_hours==0 or station.nb_guns==0:
                peak_fuel_avg_gun=0
            else:
                peak_fuel_avg_gun=total_fuel/total_hours/station.nb_guns

            #加油卡消费比例
            vip_pay_percent=0
            sql='select sum(pay) as pay, payment_type from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\' group by payment_type;'%(
                curr_date.strftime('%Y-%m-%d'),futher_date.strftime('%Y-%m-%d'),
                site_name
            )
            rets=src_session.execute(sql)
            total_pay=0
            vip_pay=0
            for ret in rets:
                if ret.payment_type==PaymentType.VIP:
                    vip_pay+=ret.pay
                total_pay+=ret.pay

            pay_amout=total_pay
            vip_pay_amout=vip_pay
            if total_pay==0:
                vip_pay_percent=0
            else:
                vip_pay_percent=vip_pay*100/total_pay

            #加满率
            fuel_fillout_percent=0
            sql='select count(DISTINCT trans_id) as count, pump_type from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\' and trans_type=%s group by pump_type;'%(
                curr_date.strftime('%Y-%m-%d'),futher_date.strftime('%Y-%m-%d'),
                site_name,TransType.FUEL
            )
            rets=src_session.execute(sql)
            fillout_count=0
            total_count=0
            for ret in rets:
                if ret.pump_type==PumpType.FILLOUT:
                    fillout_count+=ret.count
                total_count+=ret.count

            fuel_trans_count=total_count
            fuel_fillout_count=fillout_count
            if total_count==0:
                fuel_fillout_percent=0
            else:
                fuel_fillout_percent=fillout_count*100/total_count

            #客单值
            single_customer_pay=0
            sql='select count(DISTINCT trans_id) as customer_num from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\';'%(
                curr_date.strftime('%Y-%m-%d'),futher_date.strftime('%Y-%m-%d'),
                site_name
            )
            rets=src_session.execute(sql)
            customer_num=0
            for ret in rets:
                if ret.customer_num!=None:
                    customer_num+=ret.customer_num

            if customer_num==0:
                single_customer_pay=0
            else:
                single_customer_pay=total_pay/customer_num

            #存储结果
            obj=StationDailyStat(date=curr_date,site=site_name)
            obj.compute_sha1()

            #check exists
            exists=des_session.query(StationDailyStat).filter_by(sha1=obj.sha1).count()
            if exists>0:
                obj=des_session.query(StationDailyStat).filter_by(sha1=obj.sha1).one()
            else:
                des_session.add(obj)

            #update
            obj.quantity_fuel=quantity_fuel
            obj.quantity_nonefuel=quantity_nonefuel
            obj.peak_fuel_avg_gun=peak_fuel_avg_gun
            obj.peak_fuel_count=peak_fuel_count
            obj.peak_hour_num=peak_hour_num
            obj.peak_fuel_biggest=peak_fuel_biggest
            obj.pre_mon_quantity_fuel=pre_mon_quantity_fuel
            obj.pre_mon_quantity_nonefuel=pre_mon_quantity_nonefuel
            obj.vip_pay_percent=vip_pay_percent
            obj.pay_amout=pay_amout
            obj.vip_pay_amout=vip_pay_amout
            obj.fuel_fillout_percent=fuel_fillout_percent
            obj.fuel_trans_count=fuel_trans_count
            obj.fuel_fillout_count=fuel_fillout_count
            obj.nonefuel_percent=nonefuel_percent
            obj.single_customer_pay=single_customer_pay

            try:
                des_session.commit()
            except Exception,e:
                ajax_logger.error('session commit error:%s'%str(e))
                des_session.rollback()

            #下一天
            curr_date += timedelta(days=1)

    except Exception,e:
        ajax_logger.error('compute station daybatch error:%s'%str(e))

    finally:
        src_session.close()
        des_session.close()

#计算每月油站汇总数据
def compute_station_monthbatch(site_name,year,month):
    #check args

    try:
        year=int(year)
        month=int(month)
        if month not in [1,2,3,4,5,6,7,8,9,10,11,12]:
            raise Exception('cmopute station monthbatch with incorrect args')
    except Exception,e:
        ajax_logger.error(str(e))
        return

    #create session
    frac_session=get_dash_session_maker(site_name)()
    src_session=get_dash_session_maker()()
    des_session=get_dash_session_maker()()

    try:
        import datetime
        #油站情况
        station=des_session.query(Station).filter_by(name=site_name).one()

        ajax_logger.debug('begin check avg_cars:%s'%str(str(datetime.datetime.now())))
        #全时段平均进站车辆
        sql='select count(distinct(fact_trans.trans_id)) as trans_count, dim_datehour.hour as hour from fact_trans join dim_datehour ON dim_datehour.id = fact_trans.datehour where \
            fact_trans.trans_type=0 and dim_datehour.year=%s and dim_datehour.month=%s and site=\'%s\' group by dim_datehour.hour order by dim_datehour.hour'%(
                year,month,site_name
            )
        all_hour_in_car={}
        all_hour_in_car_list=[]
        rets=frac_session.execute(sql)
        for ret in rets:
            all_hour_in_car[int(ret.hour)]=ret.trans_count
        ajax_logger.debug('end check avg_cars:%s'%str(str(datetime.datetime.now())))
        #数据整理
        trans_count={
            'categories':[
                '0 - 1', '1 - 2', '2 - 3', '3 - 4', '4 - 5', '5 - 6', '6 - 7',
                '7 - 8', '8 - 9', '9 - 10', '10 - 11', '11 - 12', '12 - 13',
                '13 - 14', '14 - 15', '15 - 16', '16 - 17', '17 - 18', '18 - 19',
                '19 - 20', '20 - 21', '21 - 22', '22 - 23', '23 - 24'
            ],
            'dataset': [{
                'data': [],
                'name': 'test'}
            ]
        }

        for hour in xrange(24):
            all_hour_in_car_list.append(int(all_hour_in_car.get(hour,0)/30))
            trans_count['dataset'][0]['data'].append(all_hour_in_car.get(hour,0))

        peak_rets=get_peak_period(trans_count)

        #高峰期列表
        peak_list=peak_rets['period']['crest']

        ajax_logger.debug('begin check oil_quantity:%s'%str(str(datetime.datetime.now())))
        #加油量趋势
        #油品销量
        if int(month) in [1,3,5,7,8,10,12]:
            day = 31
        elif int(month) in [2]:
            day = 28
        else:
            day = 30

        start_date = str(year) + '-' + str(month) + '-1 00:00:00'
        end_date = str(year) + '-' + str(month) + '-' + str(day) + ' 23:59:59'
        sql='select sum(total_quantity) as total_quantity,sum(total_pay) as total_pay from station_daily_fuel_sales where \
            date>=\'%s\' and date<=\'%s\' and site=\'%s\''%(start_date,end_date,site_name)
        total_quantity=0
        total_pay=0
        rets=src_session.execute(sql)
        for ret in rets:
            if ret.total_quantity!=None:
                total_quantity=ret.total_quantity
            if ret.total_pay!=None:
                total_pay=ret.total_pay
        ajax_logger.debug('end check oil_quantity:%s'%str(str(datetime.datetime.now())))

        ajax_logger.debug('begin check none_oil_quantity,peak_peroid_oil,cardnum,fillout:%s'%str(str(datetime.datetime.now())))
        #油品销量,非油品销量,高峰期平均出油率,加油卡消费比例,加满率,客单值
        sql='select sum(quantity_fuel) as quantity_fuel,sum(quantity_nonefuel) as quantity_nonefuel, \
            sum(peak_fuel_avg_gun) as peak_fuel_avg_gun,sum(peak_hour_num) as peak_hour_num,\
            sum(peak_fuel_count) as peak_fuel_count,sum(pay_amout) as pay_amout,sum(vip_pay_amout) as vip_pay_amout, \
            sum(fuel_trans_count) as fuel_trans_count,sum(fuel_fillout_count) as fuel_fillout_count, \
            sum(single_customer_pay) as single_customer_pay from station_daily_stat where \
            date>=\'%s\' and date<=\'%s\' and site=\'%s\''%(start_date,end_date,site_name)

        #油品销量
        quantity_fuel=0

        #非油品销量
        quantity_nonefuel=0

        #高峰期平均出油率
        peak_fuel_avg_gun=0
        peak_fuel_count=0
        peak_hour_num=0


        #加油卡消费比例
        vip_pay_percent=0
        pay_amout=0
        vip_pay_amout=0

        #加满率
        fuel_trans_count=0
        fuel_fillout_count=0
        fillout_count=0
        total_count=0

        #加满率
        fuel_fillout_percent=0

        #客单值
        single_customer_pay=0
        customer_num=0



        rets=src_session.execute(sql)
        for ret in rets:
            if ret.quantity_fuel!=None:
                quantity_fuel=ret.quantity_fuel
            if ret.quantity_nonefuel!=None:
                quantity_nonefuel=ret.quantity_nonefuel
            if ret.peak_fuel_avg_gun!=None:
                peak_fuel_avg_gun=ret.peak_fuel_avg_gun
            if ret.peak_hour_num!=None:
                peak_hour_num=ret.peak_hour_num
            if ret.peak_fuel_count!=None:
                peak_fuel_count=ret.peak_fuel_count
            if ret.pay_amout!=None and ret.vip_pay_amout!=None:
                if ret.pay_amout==0:
                    vip_pay_percent=0
                else:
                    vip_pay_percent=ret.vip_pay_amout*100/ret.pay_amout
            if ret.fuel_trans_count!=None and ret.fuel_fillout_count!=None:
                if ret.fuel_trans_count==0:
                    fuel_fillout_percent=0
                else:
                    fuel_fillout_percent=ret.fuel_fillout_count*100/ret.fuel_trans_count
        ajax_logger.debug('end check none_oil_quantity,peak_peroid_oil,cardnum,fillout:%s'%str(str(datetime.datetime.now())))

        ajax_logger.debug('start check customer:%s'%str(str(datetime.datetime.now())))
        sql='select count(DISTINCT trans_id) as customer_num from fact_trans where \
            timestamp>=\'%s\' and timestamp<=\'%s\' and site=\'%s\';'%(start_date,end_date,site_name)
        rets=frac_session.execute(sql)
        for ret in rets:
            if ret.customer_num!=None:
                customer_num+=ret.customer_num

        if customer_num==0:
            single_customer_pay=0
        else:
            single_customer_pay=total_pay/customer_num
        ajax_logger.debug('end check customer:%s'%str(str(datetime.datetime.now())))


        #非油品对油品比例
        nonefuel_percent=0
        if quantity_fuel==0:
            nonefuel_percent=0
        else:
            nonefuel_percent=quantity_nonefuel*100/quantity_fuel


        #上月油品销量,上月非油品销量
        if int(month)==1:
            pre_month=12
            pre_year=int(year)-1
        else:
            pre_month=int(month)-1
            pre_year=year

        if int(pre_month) in [1,3,5,7,8,10,12]:
            pre_day = 31
        elif int(pre_month) in [2]:
            pre_day = 28
        else:
            pre_day = 30

        pre_start_date = str(pre_year) + '-' + str(pre_month) + '-1 00:00:00'
        pre_end_date = str(pre_year) + '-' + str(pre_month) + '-' + str(pre_day) + ' 23:59:59'

        ajax_logger.debug('start check oildevnoneoil:%s'%str(str(datetime.datetime.now())))

        #环比计算
        sql='select sum(quantity_fuel) as quantity_fuel,sum(quantity_nonefuel) as quantity_nonefuel \
            from station_daily_stat where \
            date>=\'%s\' and date<=\'%s\' and site=\'%s\';'%(pre_start_date,pre_end_date,site_name)

        pre_mon_quantity_fuel=0
        pre_mon_quantity_nonefuel=0
        rets=src_session.execute(sql)
        for ret in rets:
            if ret.quantity_fuel!=None:
                pre_mon_quantity_fuel=ret.quantity_fuel
            if ret.quantity_nonefuel!=None:
                pre_mon_quantity_nonefuel=ret.quantity_nonefuel


        #油品环比
        fuel_mom_percent=0
        if pre_mon_quantity_fuel==0:
            fuel_mom_percent=0
        else:
            fuel_mom_percent=(quantity_fuel-pre_mon_quantity_fuel)*100/pre_mon_quantity_fuel


        #非油品环比
        nonefuel_mom_percent=0
        if pre_mon_quantity_nonefuel==0:
            nonefuel_mom_percent=0
        else:
            nonefuel_mom_percent=(quantity_nonefuel-pre_mon_quantity_nonefuel)*100/pre_mon_quantity_nonefuel

        ajax_logger.debug('end check oildevnoneoil:%s'%str(str(datetime.datetime.now())))
        #存储结果
        obj=StationMonthStat(year=year,month=month,site=site_name)
        obj.compute_sha1()

        #check exists
        exists=des_session.query(StationMonthStat).filter_by(sha1=obj.sha1).count()
        if exists>0:
            obj=des_session.query(StationMonthStat).filter_by(sha1=obj.sha1).one()
        else:
            des_session.add(obj)

        #update
        obj.peak_hour_list=json.dumps(peak_list)
        obj.all_hour_avg_car=json.dumps(all_hour_in_car_list)
        obj.total_quantity=total_quantity
        obj.quantity_fuel=quantity_fuel
        obj.quantity_nonefuel=quantity_nonefuel
        obj.peak_fuel_avg_gun=peak_fuel_avg_gun
        obj.peak_fuel_count=peak_fuel_count
        obj.peak_hour_num=peak_hour_num
        obj.pre_mon_quantity_fuel=pre_mon_quantity_fuel
        obj.pre_mon_quantity_nonefuel=pre_mon_quantity_nonefuel
        obj.vip_pay_percent=vip_pay_percent
        obj.pay_amout=pay_amout
        obj.vip_pay_amout=vip_pay_amout
        obj.fuel_fillout_percent=fuel_fillout_percent
        obj.fuel_trans_count=fuel_trans_count
        obj.fuel_fillout_count=fuel_fillout_count
        obj.nonefuel_percent=nonefuel_percent
        obj.single_customer_pay=single_customer_pay
        obj.nonefuel_mom_percent=nonefuel_mom_percent
        obj.fuel_mom_percent=fuel_mom_percent
        obj.total_pay=total_pay

        try:
            des_session.commit()
        except Exception,e:
            ajax_logger.error('session commit error:%s'%str(e))
            des_session.rollback()

    except Exception,e:
        ajax_logger.error('compute station monthbatch error:%s'%str(e))

    finally:
        src_session.close()
        des_session.close()

#计算每天油品汇总数据
def compute_fuel_daybatch(site_name,start_date,end_date):
    #生成查询语句
    def get_raw_sql(open_date,close_date,site_name,all_fuel_types):
        return 'select payment_type,sum(quantity) as total_quantity, \
        sum(pay) as total_pay from fact_trans where timestamp>=\'%s\' and \
        timestamp<\'%s\' and site=\'%s\' and barcode in (%s) group by payment_type;'%(
            open_date.strftime("%Y-%m-%d"),close_date.strftime("%Y-%m-%d"),
            site_name,','.join(all_fuel_types)
        )

    #create session
    src_session=get_dash_session_maker(site_name)()
    des_session=get_dash_session_maker()()

    try:
        #get all fuel type
        all_fuel_type=des_session.query(FuelTypeRelation).all()

        #compute
        curr_date=start_date
        while curr_date <= end_date:
            #所有的油品类型
            for fuel_type in all_fuel_type:
                all_fuel_types=[]

                try:
                    all_fuel_types=json.loads(fuel_type.barcodes)
                except:
                    ajax_logger.error('fuel_type_relation:%s barcodes must be json data'%fuel_type.id)
                    continue

                if len(all_fuel_types)==0:
                    continue
                else:
                    all_fuel_types=[str(x) for x in all_fuel_types]

                futher_date=curr_date+timedelta(days=1)
                rows=src_session.execute(get_raw_sql(curr_date,futher_date,
                    site_name,all_fuel_types))

                #保存结果
                for row in rows:
                    obj=StationDailyFuelSales(
                        date=curr_date,
                        site=site_name,
                        payment_type=int(row['payment_type']),
                        fuel_type=fuel_type.id,
                        total_quantity=float(row['total_quantity']),
                        total_pay=float(row['total_pay'])
                    )
                    obj.compute_sha1()

                    #check exists
                    exists=des_session.query(StationDailyFuelSales).filter_by(sha1=obj.sha1).count()
                    if exists>0:
                        #update
                        obj=des_session.query(StationDailyFuelSales).filter_by(sha1=obj.sha1).one()
                        obj.total_quantity=float(row['total_quantity'])
                        obj.total_pay=float(row['total_pay'])
                    else:
                        des_session.add(obj)

                #commit
                try:
                    des_session.commit()
                except Exception,e:
                    ajax_logger.error('session commit error:%s'%str(e))
                    des_session.rollback()

            #下一天
            curr_date += timedelta(days=1)

    except Exception,e:
        ajax_logger.error('compute fuel daybatch error:%s'%str(e))

    finally:
        src_session.close()
        des_session.close()

def compute_item_items(site_name=None):
    def compute(site_name):
        sm=get_dash_session_maker(site_name)
        s=sm()
        #新增指定加油站
        #将指定加油站数据选取出来，注意排除掉了item表中已经存在的数据（使用not exists）
        #然后将其分组插入
        sql='insert into item (id, barcode, price, "desc", unitname) select min(id), barcode, min(price), min("desc"), min(unitname) from fact_trans where site=\'%s\' and not exists (select * from item where item.barcode=fact_trans.barcode) group by barcode;'%site_name
        s.execute(sql)
        s.commit()
        s.close()

    if site_name==None:
        #取得当前所有站
        all_sites=get_all_stations()
        for site_name,site_desc in all_sites:
            compute(site_name)
    else:
        compute(site_name)

def guess_datetime(s):
    s=s.split('.')[0]
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
        try:
            return datetime.strptime(s, fmt)
        except:
            pass
    return None

#更新station 的最新和最旧时间
def update_station_latest_and_earliest_date(site):
    #创建sesson
    sm=get_dash_session_maker()
    s=sm()

    #取得station对象
    try:
        station=s.query(Station).filter_by(name=site).one()
    except:
        #not found
        s.close()
        return

    #创建流水session
    tsm=get_dash_session_maker(site_name=station.name)
    ss=tsm()

    #取得时间
    latest_time,earliest_time=ss.execute(
        'select max(timestamp),min(timestamp) from \
        fact_trans where site=:site;',{'site':site}).first()
    ss.close()

    #没数据
    if latest_time is None:
        s.close()
        return

    #update
    station.earliest_date=earliest_time
    station.latest_date=latest_time

    try:
        s.commit()
    except Exception,e:
        s.rollback()
        ajax_logger.error('update station latest and earliest date:%s'%str(e))

    s.close()

# 导入card和all分开的CSV格式的数据

def import_csv_card_all(site, all_file_path, card_file_path,
                        loc_name, loc_desc, user_id,user_name,station_id):
    #默认的数据开始结束时间
    start_date=None
    end_date=None

    #get site name
    site=site.strip().upper()

    shared_id,create_session = get_dash_session_maker(site_name=site,with_shard_id=True)
    s = create_session()


    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    #get data
    already_trans_ids=set()
    #print 'start...'

    #导入card文件中的数据
    batch_counter=0
    with open(card_file_path) as fd:
        for row in fd:
            try:
                #批量提交
                if batch_counter%10000==0:
                    #print 'added %d rows of card' % batch_counter
                    s.commit()

                row=row.strip(' \r\n').decode('gbk').split(',')

                #取得数据时间
                timestamp = guess_datetime(row[2])
                if timestamp==None:
                    timestamp = guess_datetime(row[1])

                #更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp

                insert_csv_card_all_record(site, location, s, row,station_id,shared_id)

                #add
                already_trans_ids.add(int(row[0]))
                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
        #print 'finished adding %d rows of card' % batch_counter

    # 导入all文件中的数据
    batch_counter=0
    with open(all_file_path) as fd:
        for row in fd:
            try:
                try:
                    row=row.strip(' \r\n').decode('gb2312').split(',')
                except:
                    row=row.strip(' \r\n').decode('gbk').split(',')

                #test already_trans_ids
               # if int(row[0]) in already_trans_ids:
                #    continue

                #批量提交
                if batch_counter%10000==0:
                    #print 'added %d rows of all' % batch_counter
                    s.commit()

                row.insert(1,'0')

                #取得数据时间
                timestamp = guess_datetime(row[2])
                if timestamp==None:
                    timestamp = guess_datetime(row[1])

                #更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp

                insert_csv_card_all_record(site, location, s, row,station_id,shared_id)

                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
        #print 'finished adding %d rows of all' % batch_counter

    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    return start_date,end_date

# 导入延长壳牌数据

def import_ycshell_card_all(site, all_file_path, card_file_path,
                        loc_name, loc_desc, user_id,user_name,station_id):
    #默认的数据开始结束时间
    start_date=None
    end_date=None

    #get site name
    site=site.strip().upper()

    shared_id,create_session = get_dash_session_maker(site_name=site,with_shard_id=True)
    s = create_session()


    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    #get data
    already_trans_ids=set()
    #print 'start...'

    #导入card文件中的数据
    batch_counter=0
    with open(card_file_path) as fd:
        for row in fd:
            try:
                #批量提交
                if batch_counter%10000==0:
                    #print 'added %d rows of card' % batch_counter
                    s.commit()

                row=row.strip(' \r\n').decode('gbk').split(',')

                #取得数据时间
                timestamp = guess_datetime(row[2])
                if timestamp==None:
                    timestamp = guess_datetime(row[1])

                #更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp

                import_ycshell_card_all_record(site, location, s, row,station_id,shared_id)

                #add
                already_trans_ids.add(int(row[0]))
                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
        #print 'finished adding %d rows of card' % batch_counter

    # 导入all文件中的数据
    batch_counter=0
    with open(all_file_path) as fd:
        for row in fd:
            try:
                try:
                    row=row.strip(' \r\n').decode('gb2312').split(',')
                except:
                    row=row.strip(' \r\n').decode('gbk').split(',')

                #test already_trans_ids
               # if int(row[0]) in already_trans_ids:
                #    continue

                #批量提交
                if batch_counter%10000==0:
                    #print 'added %d rows of all' % batch_counter
                    s.commit()

                row.insert(1,'0')

                #取得数据时间
                timestamp = guess_datetime(row[2])
                if timestamp==None:
                    timestamp = guess_datetime(row[1])

                #更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp

                import_ycshell_card_all_record(site, location, s, row,station_id,shared_id)

                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
        #print 'finished adding %d rows of all' % batch_counter

    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    return start_date,end_date

# 导入sp集团的excel数据

def import_sp_excel(site,file_path,loc_name, loc_desc, user_id,user_name):
    #get site name
    site=site.strip().upper()

    s = get_dash_session_maker(site_name=site)()

    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    batch_counter=0

    #get data
    #print 'start...'

    import xlrd

    book=xlrd.open_workbook(file_path)
    sheets=book.sheets()
    for sheet in sheets:
        nrows=sheet.nrows
        ncols=sheet.ncols

        #检查数据完整性
        if ncols!=10:
            raise Exception('sheet format not sp execl!')

        #数据映射
        dim={}
        for row_idx in xrange(nrows):
            try:
                row=sheet.row_values(row_idx)
                #第一行是列名,做数据映射
                if row_idx==0:
                    for col_idx in xrange(ncols):
                        dim[row[col_idx]]=col_idx

                        if row[col_idx]==u'油品':
                            dim['content']=col_idx
                        elif row[col_idx]==u'升数':
                            dim['litter']=col_idx
                        elif row[col_idx]==u'单价':
                            dim['price']=col_idx
                        elif row[col_idx]==u'金额':
                            dim['amount']=col_idx
                        elif row[col_idx]==u'交易时间':
                            dim['opetime']=col_idx
                        elif row[col_idx]==u'枪号':
                            dim['macno']=col_idx
                        elif row[col_idx]==u'员工号':
                            dim['openo']=col_idx
                        elif row[col_idx]==u'日结时间':
                            dim['accountdate']=col_idx
                        elif row[col_idx]==u'卡号':
                            dim['cardno']=col_idx
                    continue

                # 无效数据过滤
                if row[dim['litter']]==0:
                    continue
                #批量提交
                if batch_counter%10000==0:
                    #print 'added %d rows of all' % batch_counter
                    s.commit()

                insert_sp_excel_record(batch_counter,site, location, s, row,dim)

                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
        #print 'finished adding %d rows of all' % batch_counter

    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    #print 'end...'

# 导入ycshell集团的excel数据

def import_ycshell_excel(site,file_path,loc_name, loc_desc, user_id,user_name,station_id):

    #默认的数据开始结束时间
    start_date=None
    end_date=None

    #get site name
    site=site.strip().upper()

    shared_id,create_session = get_dash_session_maker(site_name=site,with_shard_id=True)
    s = create_session()

    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    batch_counter=0

    #get data
    #print 'start...'

    import xlrd

    book=xlrd.open_workbook(file_path)
    sheets=book.sheets()

    for sheet in sheets:
        nrows=sheet.nrows
        ncols=sheet.ncols
        a1=sheet.row_values(0)[0]

        #8月份数据
        if a1=='时间':

            #数据映射
            dim={}
            for row_idx in xrange(nrows):
                try:
                    row=sheet.row_values(row_idx)

                    #第一行是列名,做数据映射
                    if row_idx==0:
                        for col_idx in xrange(ncols):
                            if dim.has_key(row[col_idx]) and row[col_idx]=='品类':
                                dim['付款方式']=col_idx
                            else:
                                dim[row[col_idx]]=col_idx
                        continue

                    #批量提交
                    if batch_counter%10000==0:
                        #print 'added %d rows of all' % batch_counter
                        s.commit()

                    #取得数据时间
                    import datetime
                    timestamp=xlrd.xldate_as_tuple(row[dim['时间'.decode()]], 0)
                    timestamp=datetime.datetime(timestamp[0],timestamp[1],timestamp[2],timestamp[3],timestamp[4],timestamp[5])
                    if timestamp==None:
                        timestamp = guess_datetime(row[1])

                    #更新开始,结束时间
                    if start_date==None:
                        start_date=timestamp
                    if end_date==None:
                        end_date=timestamp

                    if timestamp<start_date:
                        start_date=timestamp
                    if timestamp>end_date:
                        end_date=timestamp

                    insert_ycshell_excel_record(site, location, s, row,dim,station_id,shared_id)

                    batch_counter+=1

                except Exception,e:
                    ajax_logger.error(str(e))

            s.commit()
            #print 'finished adding %d rows of all' % batch_counter

        #5月份数据
        elif a1=='销售日期':
            #数据映射
            dim={}
            for row_idx in xrange(nrows):
                try:
                    row=sheet.row_values(row_idx)
                    #第一行是列名,做数据映射
                    if row_idx==0:
                        for col_idx in xrange(ncols):
                            if dim.has_key(row[col_idx]) and row[col_idx]=='销售品类':
                                dim['结算方式']=col_idx
                            else:
                                dim[row[col_idx]]=col_idx
                        continue

                    # 无效数据过滤
                    if row[dim['销售日期'.decode()]]=='':
                        continue

                    #批量提交
                    if batch_counter%10000==0:

                        #print 'added %d rows of all' % batch_counter
                        s.commit()

                    #取得数据时间
                    import datetime,xlrd
                    timestamp=xlrd.xldate_as_tuple(row[dim['销售日期'.decode()]], 0)
        	    timestamp=datetime.datetime(timestamp[0],timestamp[1],timestamp[2],timestamp[3],timestamp[4],timestamp[5])
                    if timestamp==None:
                        timestamp = guess_datetime(row[1])

                    #更新开始,结束时间
                    if start_date==None:
                        start_date=timestamp
                    if end_date==None:
                        end_date=timestamp

                    if timestamp<start_date:
                        start_date=timestamp
                    if timestamp>end_date:
                        end_date=timestamp

                    insert_ycshell_excel_record2(batch_counter,site, location, s, row,dim,station_id,shared_id)

                    batch_counter+=1

                except Exception,e:
                    ajax_logger.error(str(e))
            s.commit()
            #print 'finished adding %d rows of all' % batch_counter

        #9月份数据
        elif a1=='消费时间':

            #该sheet没有用
            if sheets.index(sheet)==7 or sheets.index(sheet)==4:
                continue
            #数据映射
            dim={}
            for row_idx in xrange(nrows):
                try:
                    row=sheet.row_values(row_idx)

                    #第一行是列名,做数据映射
                    if row_idx==0:
                        for col_idx in xrange(ncols):
                            dim[row[col_idx]]=col_idx
                        continue

                    # 无效数据过滤
                    if row[dim['消费时间'.decode()]]=='':
                        continue

                     #批量提交
                    if batch_counter%10000==0:
                        #print 'added %d rows of all' % batch_counter
                        s.commit()

                    #取得数据时间
                    import datetime
                    timestamp=xlrd.xldate_as_tuple(row[dim['消费时间'.decode()]], 0)
        	    timestamp=datetime.datetime(timestamp[0],timestamp[1],timestamp[2],timestamp[3],timestamp[4],timestamp[5])
                    if timestamp==None:
                        timestamp = guess_datetime(row[1])

                    #更新开始,结束时间
                    if start_date==None:
                        start_date=timestamp
                    if end_date==None:
                        end_date=timestamp

                    if timestamp<start_date:
                        start_date=timestamp
                    if timestamp>end_date:
                        end_date=timestamp

                    insert_ycshell_excel_record3(batch_counter,site, location, s, row,dim,station_id,shared_id)
                    batch_counter+=1

                except Exception,e:
                    ajax_logger.error(str(e))
            s.commit()
            #print 'finished adding %d rows of all' % batch_counter

        else:
            continue

    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    return start_date,end_date

def insert_ycshell_excel_record(site, location, s, row,dim,site_id,shard_id):
    try:
        #油品
        if len(row)==8:
            trans_type=TransType.FUEL
            unitname='公升'
            pump_id=row[dim['品类'.decode()]][:2]
            payment_type=row[dim['付款方式']]
            desc=row[dim['品类'.decode()]][2:]
        #非油品
        elif len(row)==7:
            trans_type=TransType.NON_FUEL
            unitname='未知'
            pump_id=0
            payment_type=row[dim['付款方式'.decode()]]
            desc=row[dim['品类'.decode()]]
        else:
            raise Exception('trans type error.')

        if payment_type==u'现金':
            payment_type = PaymentType.CASH
        elif payment_type==u'壳牌车队卡':
            payment_type = PaymentType.VIP
        elif payment_type==u'信用卡':
            payment_type = PaymentType.CREDIT
        else:
            payment_type = PaymentType.CASH
        import xlrd,datetime
        #timestamp = guess_datetime(row[dim['时间']])
        timestamp=xlrd.xldate_as_tuple(row[dim['时间'.decode()]], 0)
        timestamp=datetime.datetime(timestamp[0],timestamp[1],timestamp[2],timestamp[3],timestamp[4],timestamp[5])
        date_hour=datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)
        date_time=time.mktime(timestamp.timetuple())
        import hashlib
        barcode_sha1=hashlib.sha1()
        barcode_sha1.update(desc)
        barcode=int(barcode_sha1.hexdigest()[:6],16)
        pay=float(row[dim['金额'.decode()]])
        quantity=float(row[dim['数量'.decode()]])
        price=float(row[dim['单价'.decode()]])
        trans_id=compute_trans_id(date_time,shard_id,site_id,int(pump_id),int(pay)%512)
        # 添加trans entry
        tran = {
            'site': site,
            'trans_type': trans_type,
            'trans_id': trans_id,
            'cardnum': 0,
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': barcode,
            'pay': pay,
            'quantity': quantity,
            'desc': desc,
            'price': price,
            'unitname': unitname,
            'pump_id': int(pump_id),
            'location':location
        }
        ins=Trans(**tran)

        #check
        exists=s.query(Trans.trans_id).filter_by(trans_id=trans_id).count()
        if exists>0:
            return
        s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))


def insert_ycshell_excel_record2(batch_counter,site, location, s, row,dim,site_id,shard_id):
    try:
        #油品
        if len(row)==8:
            trans_type=TransType.FUEL
            unitname='公升'
            payment_type=row[dim['结算方式'.decode()]]
            pump_id=row[dim['油枪号'.decode()]]
        #非油品
        elif len(row)==6:
            trans_type=TransType.NON_FUEL
            unitname='未知'
            payment_type=row[dim['结算方式']]
            pump_id=0
        else:
            raise Exception('trans type error.')

        if payment_type==u'现金':
            payment_type = PaymentType.CASH
        elif payment_type==u'壳牌车队卡':
            payment_type = PaymentType.VIP
        elif payment_type==u'信用卡':
            payment_type = PaymentType.CREDIT
        else:
            payment_type = PaymentType.CASH
        import xlrd,datetime
        timestamp=xlrd.xldate_as_tuple(row[dim['销售日期'.decode()]], 0)
        timestamp=datetime.datetime(timestamp[0],timestamp[1],timestamp[2],timestamp[3],timestamp[4],timestamp[5])
        date_time=time.mktime(timestamp.timetuple())
        date_hour=datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)
        import hashlib
        barcode_sha1=hashlib.sha1()
        barcode_sha1.update(row[dim['销售品类'.decode()]])
        barcode=int(barcode_sha1.hexdigest()[:6],16)
        pay=float(row[dim['消费总额'.decode()]])
        quantity=float(row[dim['消费数量'.decode()]])
        price=float(row[dim['销售单价'.decode()]])
        trans_id=compute_trans_id(date_time,shard_id,site_id,int(pump_id),int(pay)%512)
        # 添加trans entry
        tran = {
            'site': site,
            'trans_type': trans_type,
            'trans_id': trans_id,
            'cardnum': 0,
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': barcode,
            'pay': pay,
            'quantity': quantity,
            'desc': row[dim['销售品类'.decode()]],
            'price': price,
            'unitname': unitname,
            'pump_id': int(pump_id),
            'location':location
        }
        ins=Trans(**tran)

        #check
        exists=s.query(Trans.trans_id).filter_by(trans_id=trans_id).count()
        if exists>0:
            return

        s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))


def insert_ycshell_excel_record3(batch_counter,site, location, s, row,dim,site_id,shard_id):
    try:
        #油品
        if len(row)==9:
            trans_type=TransType.FUEL
            unitname='公升'
            pump_id=row[dim['消费品类'.decode()]][:2]
            desc=row[dim['消费品类'.decode()]][2:]
        #非油品
        elif len(row)==7:
            trans_type=TransType.NON_FUEL
            unitname='未知'
            pump_id=0
            desc=row[dim['消费品类'.decode()]]
        else:
            raise Exception('trans type error.')
        payment_type=row[dim['支付方式'.decode()]]
        if payment_type==u'现金':
            payment_type = PaymentType.CASH
        elif payment_type==u'壳牌车队卡':
            payment_type = PaymentType.VIP
        elif payment_type==u'信用卡':
            payment_type = PaymentType.CREDIT
        else:
            payment_type = PaymentType.CASH
        import xlrd,datetime
        timestamp=xlrd.xldate_as_tuple(row[dim['消费时间'.decode()]], 0)
        timestamp=datetime.datetime(timestamp[0],timestamp[1],timestamp[2],timestamp[3],timestamp[4],timestamp[5])
        date_time=time.mktime(timestamp.timetuple())
        date_hour=datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)
        import hashlib
        barcode_sha1=hashlib.sha1()
        barcode_sha1.update(desc)
        barcode=int(barcode_sha1.hexdigest()[:6],16)
        pay=float(row[dim['消费金额'.decode()]])
        quantity=float(row[dim['数量'.decode()]])
        price=float(row[dim['单价'.decode()]])
        trans_id=compute_trans_id(date_time,shard_id,site_id,int(pump_id),int(pay)%512)
        # 添加trans entry
        tran = {
            'site': site,
            'trans_type': trans_type,
            'trans_id': trans_id,
            'cardnum': 0,
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': barcode,
            'pay': pay,
            'quantity': quantity,
            'desc': desc,
            'price': price,
            'unitname': unitname,
            'pump_id': int(pump_id),
            'location':location
        }
        ins=Trans(**tran)

        #check
        exists=s.query(Trans.trans_id).filter_by(trans_id=trans_id).count()
        if exists>0:
            return

        s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))



def insert_sp_excel_record(trans_id,site, location, s, row,dim):
    try:
        trans_type=TransType.FUEL
        payment_type = PaymentType.CASH
        if row[dim['paymode']]=='IC卡':
            payment_type=PaymentType.VIP
        elif row[dim['paymode']]=='银行卡':
            payment_type=PaymentType.CREDIT
        #timestamp = guess_datetime(row[dim['opetime']])
        import xlrd,datetime
        timestamp=xlrd.xldate_as_tuple(row[dim['opetime']], 0)
        timestamp=datetime.datetime(timestamp[0],timestamp[1],timestamp[2],timestamp[3],timestamp[4],timestamp[5])
        #date_hour=datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)
        date_hour=datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)
        import hashlib
        barcode_sha1=hashlib.sha1()
        barcode_sha1.update(row[dim['content']])
        barcode=int(barcode_sha1.hexdigest()[:6],16)
        pay=float(row[dim['amount']])
        quantity=float(row[dim['litter']])
        price=float(row[dim['price']])
        # 添加trans entry
        tran = {
            'site': site,
            'trans_type': trans_type,
            'trans_id': trans_id,
            'cardnum': row[dim['cardno']],
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': barcode,
            'pay': pay,
            'quantity': quantity,
            'desc': row[dim['content']],
            'price': price,
            'unitname': '公升',
            'pump_id': int(row[dim['macno']]),
            'location':location
        }
        ins=Trans(**tran)

        #check
        exists=s.query(Trans).filter_by(sha1=ins.sha1,site=ins.site,timestamp=ins.timestamp).count()
        if exists>0:
            return


        s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))

def insert_csv_card_all_record(site, location, s, row,site_id,shard_id):
    try:
        timestamp = guess_datetime(row[2])
        if timestamp==None:
            timestamp = guess_datetime(row[1])
            #temp_time = str(row[1])
        #else:
            #temp_time = str(row[2])
        date_time=time.mktime(timestamp.timetuple())
        barcode = int(float(row[3]))
        if barcode < 400000:
            trans_type = TransType.FUEL
        else:
            trans_type = TransType.NON_FUEL
        cardnum = int(float(row[1]))

        #加油卡为以90或91开头的16位卡号
        payment_type=getPaymentTypeByCard(str(cardnum),'^90\w{14}|91\w{14}$')

        qty = int(float(row[4]))
        weight = float(row[7])

        desc=row[6].replace(u'昆仑好客','').replace(u'中国石油','').strip()
        if len(desc)==0:
            desc=u'unknow'

        date_hour=datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)

        # 添加trans entry
        unitname=row[10].strip()
        pay = float(row[5]) if trans_type == TransType.FUEL else float(row[9])
        #temp = temp_time+str(barcode)+str(pay)+str(int(float(row[11])))
        #trans_sha1=hashlib.sha1()
        #trans_sha1.update(temp)

        #time+barcode+pay+pump
        #trans_id=int(trans_sha1.hexdigest()[:6],16)

        if len(unicode(unitname))>16:
            ajax_logger.info("skip insert,unitname too long for trans_id:%s"%trans_id)
            return

        #trans_id=compute_trans_id(date_time,shard_id,site_id,int(float(row[11])),int(pay)%512)

        tran = {
            'site': site,
            'trans_type': trans_type,
            'trans_id': int(row[0]),
            'cardnum': cardnum,
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': barcode,
            'pay': pay,
            'quantity': weight if trans_type == TransType.FUEL else qty,
            'desc': desc,
            'price': row[8].strip(),
            'unitname': unitname,
            'pump_id': int(float(row[11])),
            'location':location
        }

        ins=Trans(**tran)

        #check
        exists=s.query(Trans.trans_id).filter_by(sha1=ins.sha1).count()
        if exists>0:
            return
        s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))

#插入延长壳牌数据
def import_ycshell_card_all_record(site, location, s, row,site_id,shard_id):
    try:
        timestamp = guess_datetime(row[2])
        if timestamp==None:
            timestamp = guess_datetime(row[1])
            #temp_time = str(row[1])
        #else:
            #temp_time = str(row[2])
        date_time=time.mktime(timestamp.timetuple())
        barcode = int(float(row[3]))
        if int(float(row[11])) > 0:
            trans_type = TransType.FUEL
        else:
            trans_type = TransType.NON_FUEL
        cardnum = int(float(row[1]))

        #加油卡为以90或91开头的16位卡号
        payment_type=getPaymentTypeByCard(str(cardnum),'^90\w{14}|91\w{14}$')

        qty = int(float(row[4]))
        weight = float(row[7])
        desc = row[6]
        if len(desc)==0:
            desc=u'unknow'

        date_hour=datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)

        # 添加trans entry
        unitname=row[10].strip()
        pay = float(row[5]) if trans_type == TransType.FUEL else float(row[9])


        if len(unicode(unitname))>16:
            ajax_logger.info("skip insert,unitname too long for trans_id:%s"%trans_id)
            return

        #trans_id=compute_trans_id(date_time,shard_id,site_id,int(float(row[11])),int(pay)%512)

        tran = {
            'site': site,
            'trans_type': trans_type,
            'trans_id': int(row[0]),
            'cardnum': cardnum,
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': barcode,
            'pay': pay,
            'quantity': weight if trans_type == TransType.FUEL else qty,
            'desc': desc,
            'price': row[8].strip(),
            'unitname': unitname,
            'pump_id': int(float(row[11])),
            'location':location
        }

        ins=Trans(**tran)

        #check
        exists=s.query(Trans.trans_id).filter_by(sha1=ins.sha1).count()
        if exists>0:
            return
        s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))

#导入森美数据
def import_senmei_data(site, file_path,loc_name, loc_desc, user_id,user_name):
    #默认的数据开始结束时间
    start_date=None
    end_date=None
    #get site name
    site=site.strip().upper()

    s = get_dash_session_maker(site_name=site)()

    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    batch_counter=0

    with open(file_path) as fd:
        for row in fd:
            try:
                #批量提交
                if batch_counter%10000==0:
                    #print 'added %d rows of card' % batch_counter
                    s.commit()

                row=row.strip(' \r\n').split(',')

                timestamp=time.strptime(row[4], "%Y-%m-%d %H:%M:%S")
                y,m,d,hh,mm,ss = timestamp[0:6]
                date_hour=datetime(y,m,d,hh,0,0)
                timestamp=datetime(y,m,d,hh,mm,ss)

                #更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp

                insert_senmei_record(site, location, s, row,timestamp,date_hour)

                batch_counter+=1
            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()

    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    #print 'end...'

    return start_date,end_date

def insert_senmei_record(site, location, s, row,timestamp,date_hour):
    try:

        # 添加trans entry
        tran = {
            'site': site,
            'trans_type': int(row[1]),
            'trans_id': row[12],
            'cardnum': row[2],
            'payment_type': row[3],
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': row[5],
            'pay': row[6],
            'quantity': row[7],
            'desc': row[8],
            'price': row[9],
            'unitname': row[10],
            'pump_id': int(row[11]),
            'location':location
        }
        ins=Trans(**tran)

        #check
        exists=s.query(Trans).filter_by(sha1=ins.sha1,site=ins.site,timestamp=ins.timestamp).count()
        if exists>0:
            return
        s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))


#导入中石化数据
def import_sinopec_data(site, file_path,loc_name, loc_desc, user_id,user_name,station_id):
    #默认的数据开始结束时间
    start_date=None
    end_date=None
    #get site name
    site=site.strip().upper()

    shared_id,create_session = get_dash_session_maker(site_name=site,with_shard_id=True)
    s = create_session()

    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    batch_counter=0

    with open(file_path) as fd:
        for row in fd:
            try:
                #批量提交
                if batch_counter%10000==0:
                    s.commit()
                row = row.replace('\'',"").split(',')
                row[1]=row[1].replace('.000','')
                row[1]=row[1].replace('.0','')
                timestamp=time.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                y,m,d,hh,mm,ss = timestamp[0:6]
                date_hour=datetime(y,m,d,hh,0,0)
                timestamp=datetime(y,m,d,hh,mm,ss)

                #更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp

                insert_sinopec_record(site, location, s, row , timestamp,date_hour,shared_id,station_id)
                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    #print 'end...'

    return start_date,end_date

def insert_sinopec_record(site, location, s, row,timestamp,date_hour,shard_id,site_id):

    date_time=time.mktime(timestamp.timetuple())

    card_num = row[4]
    desc = row[8]

    #编码问题，后续需要解决
    #if '97' in desc:
        #desc = '97号车用汽油'
        #barcode = 300061
    #elif '92' in desc:
        #desc = '92号车用汽油'
        #barcode = 300585
    #elif '93' in desc:
        #desc = '93号车用汽油'
        #barcode = 300060
    #elif '95' in desc:
        #desc = '95号车用汽油'
        #barcode = 300586
    #elif '10' in desc:
        #desc = '-10号柴油'
        #barcode = 300602
    #elif '0' in desc:
        #desc = '0号车用柴油'
        #barcode = 300603
    #else:
        #barcode_sha1=hashlib.sha1()
        #barcode_sha1.update(desc)
        #barcode=int(barcode_sha1.hexdigest()[:6],16)
    import hashlib
    barcode_sha1=hashlib.sha1()
    barcode_sha1.update(desc)
    barcode=int(barcode_sha1.hexdigest()[:6],16)


    #交易编号，时间+商品名字+金额+油枪号生成sha1
    #trans_sha1=hashlib.sha1()
    #trans_sha1.update(row[1]+row[8].replace('\'','')+row[11].replace('\'','')+row[12].replace('\'',''))
    #trans_id=int(trans_sha1.hexdigest()[:6],16)
    trans_id=compute_trans_id(date_time,shard_id,site_id,int(row[12]),int(float(row[11]))%512)

    #'0000000000000000000'定义为现金交易
    if card_num == '0000000000000000000':
        payment_type = 1000
    else:
        #暂时得到的加油卡信息为以1开头的19位卡号
        payment_type=getPaymentTypeByCard(str(card_num),'^1\w{18}$')

    # 添加trans entry
    try:
        tran = {
            'site': site,
            'trans_type': 0,
            'trans_id': trans_id,
            'cardnum': int(row[4]),
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': barcode,
            'pay': row[11],
            'quantity': row[10],
            'desc': desc,
            'price': row[9],
            'unitname': '公升',
            'pump_id': int(row[12]),
            'location':location
        }

        ins=Trans(**tran)

        #check
        #check
        exists=s.query(Trans.trans_id).filter_by(trans_id=trans_id).count()
        if exists>0:
            return
        s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))


#导入北京壳牌数据
def import_shell_data(site, file_path,loc_name, loc_desc, user_id,user_name,station_id):
    #默认的数据开始结束时间
    start_date=None
    end_date=None
    #get site name
    site=site.strip().upper()

    shared_id,create_session = get_dash_session_maker(site_name=site,with_shard_id=True)
    s = create_session()

    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    batch_counter=0

    trans_id = 0
    tmp_row=[]
    payment_type = PaymentType.CASH

    with open(file_path) as fd:
        for row in fd:

            try:

                #批量提交
                if batch_counter%10000==0:
                    s.commit()

		if row.startswith('item_type') or row.startswith('--') or row.startswith('('):
		    continue
		row=row.decode('gb2312').split('__SEPERATER__')

		row[6] = row[6].replace('.000','').strip()
		timestamp = guess_datetime(row[6])

	        #更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp

                if trans_id != int(row[1]):
                    trans_id = int(row[1])
                    if trans_id!=0:
                        insert_shell_record(s,tmp_row,site,location,shared_id,station_id,payment_type)
                    batch_counter+=len(tmp_row)
                    tmp_row = []

                if int(row[0])==7:
                    if row[2].strip()==u'现金':
                        payment_type = PaymentType.CASH
                    elif row[2].strip()==u'壳牌车队卡':
                        payment_type = PaymentType.VIP
                    elif row[2].strip()==u'信用卡':
                        payment_type = PaymentType.CREDIT
                    else:
                        payment_type = PaymentType.CASH

                elif int(row[0]) in [2,14]:
                    tmp_row.append(row)

	    except Exception,e:
                ajax_logger.error(str(e))

        insert_shell_record(s,tmp_row,site,location,shared_id,station_id,payment_type)

        s.commit()
    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    #print 'end...'

    return start_date,end_date

#插入北京壳牌数据
def insert_shell_record(s,tmp_row,site,location,shared_id,station_id,payment_type):
    for row in tmp_row:
        try:
            timestamp = guess_datetime(row[6])
            date_time=time.mktime(timestamp.timetuple())

            #油品
            if int(row[0]) == 2:
                pump_desc = row[2].split('-')
                desc = pump_desc[1]
                pump_id = int(pump_desc[0])
                """
                  北京壳牌中，油品按照柴油和汽油分别计算油枪号,规则如下：
                  a.柴油：油枪号*10作为最终油枪号
                  b.汽油：1.95#汽油的油品代码设为1，油枪号为文本中的油枪号*10+1
                         2.92#汽油的油品代码设为2，油枪号为文本中的油枪号*10+2

                  如果是承德的站，油品需要做如下替换:
                  1.92#对应处理成93#
                  2.95#对应处理成97#

                """
                if desc.find('汽油')>-1:
                    pump_id = pump_id*10

                    if desc.find('92')>-1:
                        #承德站点
                        if site in ['SHELLCDZ']:
                            desc = "93#汽油"
                            barcode = 300656
                        pump_id = pump_id+2
                    else:
                        #承德站点
                        if site in ['SHELLCDZ']:
                            desc = "97#汽油"
                            barcode = 300657
                        pump_id = pump_id+1
                else:
                    pump_id = pump_id*10

                #如果不是承德的站，则barcode根据名字生成
                if desc not in ['93#汽油','97#汽油']:
                    import hashlib
                    barcode_sha1 = hashlib.sha1()
                    barcode_sha1.update(desc)
                    barcode = int(barcode_sha1.hexdigest()[:6],16)
                trans_type = TransType.FUEL
                unitname = '公升'

            #非油品
            else:
                pump_id = 0
                desc = row[2]
                barcode = row[7]
                unitname = '个'
                trans_type = TransType.NON_FUEL
            cardnum = 0
            if row[8].strip() != 'NULL':
                cardnum = row[8].replace('*','0')

            qty = int(float(row[4]))


            date_hour=datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)

            pay = float(row[5])

            price = float(row[3])


            trans_id=row[1]

            tran = {
                'site': site,
                'trans_type': trans_type,
                'trans_id': int(trans_id),
                'cardnum': int(cardnum),
                'payment_type': payment_type,
                'timestamp': timestamp,
                'datehour': date_hour,
                'barcode': int(barcode),
                'pay': pay,
                'quantity': qty,
                'desc': desc.strip(),
                'price': price,
                'unitname': unitname,
                'pump_id': pump_id,
                'location':location
            }
            ins=Trans(**tran)
            #check
            exists=s.query(Trans.trans_id).filter_by(trans_id=int(trans_id),sha1=ins.sha1).count()
            if exists>0:
                return
            s.add(ins)
        except Exception, e:
            ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))

#导入北京壳牌历史数据
def import_shell_history_data(site, file_path,loc_name, loc_desc, user_id,user_name,station_id):
    import xlrd
    #默认的数据开始结束时间
    start_date=None
    end_date=None
    history_end_date=None

    #get site name
    site=site.strip().upper()

    shared_id,create_session = get_dash_session_maker(site_name=site,with_shard_id=True)
    s = create_session()

    #导入历史数据前要先查询目前数据库的起始时间点，避免重复（因为历史数据的时间没有给出精确到秒）
    sql_get_strat_date = 'select timestamp from fact_trans where site=\'%s\' order by timestamp limit(1);'%site
    dates = s.execute(sql_get_strat_date)

    for date in dates:
        history_end_date = date.timestamp

    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    batch_counter=0

    import xlrd

    book=xlrd.open_workbook(file_path)
    sheets=book.sheets()

    for sheet in sheets:
        nrows=sheet.nrows
        for row_idx in xrange(nrows):
            try:
                row=sheet.row_values(row_idx)
                #第一行是列名
                if row_idx==0:
                    continue
                timestamp = xlrd.xldate_as_tuple(row[1]+row[2],0)
                timestamp=datetime(timestamp[0],timestamp[1],timestamp[2],timestamp[3],timestamp[4],timestamp[5])
                if timestamp==None:
                    timestamp = guess_datetime(row[1])

                #更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp
                #批量提交
                if batch_counter%10000==0:
                    s.commit()

                if history_end_date!=None:
                    if timestamp>=history_end_date:
                        continue

                insert_shell_history_record(batch_counter,site, location, s, row,timestamp)

                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()

    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据
    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    return start_date,end_date


#插入北京壳牌的历史数据
def insert_shell_history_record(batch_counter,site, location, s, row ,timestamp):
    try:
        trans_id = int(row[3])
        desc = row[10]
        date_hour = datetime(timestamp.year,timestamp.month,timestamp.day,timestamp.hour)
        try:
            if int(float(row[9]))==0:
                trans_type = TransType.NON_FUEL
                unitname = '个'
                pump_id = 0
            else:
                trans_type = TransType.FUEL
                unitname = '公升'
                pump_id = row[9]
                if desc.find('汽油')>-1:
                    pump_id=pump_id.replace('-','0')
                    pump_id=int(float(pump_id))
                    if desc.find('92')>-1:
                        desc='92#汽油'
                        barcode = 13748117
                        pump_id=int(float(pump_id.split('-')[0]))
                        pump_id=pump_id*10+2
                    elif desc.find('93')>-1:
                        desc='93#汽油'
                        barcode = 300656
                        pump_id=int(float(pump_id.split('-')[0]))
                        pump_id=pump_id*10+2
                    elif desc.find('95')>-1:
                        desc='95#汽油'
                        barcode = 10465763
                        pump_id=int(float(pump_id.split('-')[0]))
                        pump_id=pump_id*10+1
                    elif desc.find('97')>-1:
                        desc='97#汽油'
                        barcode = 300657
                        pump_id=int(float(pump_id.split('-')[0]))
                        pump_id=pump_id*10+1
                    else:
                        import hashlib
                        barcode_sha1 = hashlib.sha1()
                        barcode_sha1.update(desc)
                        barcode = int(barcode_sha1.hexdigest()[:6],16)
                else:
                    pump_id=pump_id.split('-')[0]+'0'
                    pump_id=int(float(pump_id))
        except:
            trans_type = TransType.FUEL
            unitname = '公升'
            pump_id = row[9]
            if desc.find('汽油')>-1:
                if desc.find('92')>-1:
                    pump_id=int(float(pump_id.split('-')[0]))
                    pump_id=pump_id*10+2
                    desc='92#汽油'
                    barcode = 13748117
                elif desc.find('93')>-1:
                    pump_id=int(float(pump_id.split('-')[0]))
                    pump_id=pump_id*10+2
                    desc='93#汽油'
                    barcode = 300656
                elif desc.find('95')>-1:
                    pump_id=int(float(pump_id.split('-')[0]))
                    pump_id=pump_id*10+1
                    desc='95#汽油'
                    barcode = 10465763
                elif desc.find('97')>-1:
                    pump_id=int(float(pump_id.split('-')[0]))
                    pump_id=pump_id*10+1
                    desc='97#汽油'
                    barcode = 300657
                else:
                    import hashlib
                    barcode_sha1 = hashlib.sha1()
                    barcode_sha1.update(desc)
                    barcode = int(barcode_sha1.hexdigest()[:6],16)
            else:
                pump_id=pump_id.split('-')[0]+'0'
                pump_id=int(float(pump_id))
                barcode = 10469401


        pay = float(row[13])
        qty = float(row[12])
        price = float(row[11])

        payment_type = row[4]

        if payment_type == '信用卡':
            payment_type = PaymentType.CREDIT
        elif payment_type == '壳牌车队卡':
            payment_type = PaymentType.VIP
        else:
            payment_type = PaymentType.CASH

        tran = {
            'site': site,
            'trans_type': trans_type,
            'trans_id': int(trans_id),
            'cardnum': 0,
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': int(barcode),
            'pay': pay,
            'quantity': qty,
            'desc': desc.strip(),
            'price': price,
            'unitname': unitname,
            'pump_id': pump_id,
            'location':location
        }
        ins=Trans(**tran)
        #check
        exists=s.query(Trans.trans_id).filter_by(sha1=ins.sha1).count()
        if exists>0:
            return
        s.add(ins)

    except Exception,e:
        ajax_logger.error(str(e))

#导入延长壳牌数据
def import_ycshell_data(site, file_path,loc_name, loc_desc, user_id,user_name,station_id):
    #默认的数据开始结束时间
    start_date=None
    end_date=None
    #get site name
    site=site.strip().upper()

    shared_id,create_session = get_dash_session_maker(site_name=site,with_shard_id=True)
    s = create_session()

    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    batch_counter=0

    #get data
    waits=[]

    with open(file_path) as fd:
        for row in fd:
	    if not row.startswith('0,08,'):
                    continue
            try:
                #批量提交
                if batch_counter%10000==0:
                    s.commit()


		row=row.strip(' \r\n').decode('gb2312').split(',')
                row=[x.strip('"') for x in row]

		timestamp = guess_datetime(row[2])

		#更新开始,结束时间
                if start_date==None:
                    start_date=timestamp
                if end_date==None:
                    end_date=timestamp

                if timestamp<start_date:
                    start_date=timestamp
                if timestamp>end_date:
                    end_date=timestamp

		#商品信息
                if int(row[6])==1 and int(row[7]) in [2,14]:
                    ins=insert_ycshell_record(s,row,site,location,shared_id,station_id)
		    if ins is not None:
                        waits.append(ins)
		#结算信息
                elif int(row[6])==0 and int(row[7])==7:
                    if row[8]==u'现金':
                        payment_type = PaymentType.CASH
                    elif row[8]==u'壳牌车队卡':
                        payment_type = PaymentType.VIP
                    elif row[8]==u'信用卡':
                        payment_type = PaymentType.CREDIT
                    else:
                        payment_type = PaymentType.CASH
                    #将等待的doc赋值提交
                    for wait in waits:
                        wait.payment_type=payment_type
                        s.add(wait)
                    waits=[]

	    except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

    #print 'end...'

    return start_date,end_date

#插入延长壳牌数据
def insert_ycshell_record(s,row,site,location,shard_id,site_id):
    try:
	timestamp = guess_datetime(row[2])
	date_time=time.mktime(timestamp.timetuple())
	if int(row[7])==2:
	    trans_type = TransType.FUEL
	    barcode = int(re.findall(u'(?<=\s{1})(\d+)#汽油',row[8])[0])
	    unitname='公升 20℃ '
	else:
	    trans_type = TransType.NON_FUEL
	    barcode = int(row[13])
	    unitname='个'

	trans_id=compute_trans_id(date_time,shard_id,site_id,int(row[13]) if trans_type==TransType.FUEL else 0,int(float(row[11]))%512)

	cardnum =0
	tran = {
	'site': site,
	'trans_type': trans_type,
	'trans_id': trans_id,
	'cardnum': cardnum,
	'payment_type': PaymentType.CASH,
	'timestamp': timestamp,
	'datehour': datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour),
	'barcode': barcode,
	'pay': float(row[11]),
	'quantity': float(row[10]),
	'desc': row[8].strip(),
	'price': row[9].strip(),
	'unitname': 'unknow',
	'pump_id': int(row[13]) if trans_type==TransType.FUEL else 0,
	'location':location
	}

	ins=Trans(**tran)

        #check
        exists=s.query(Trans.trans_id).filter_by(trans_id=trans_id).count()
        if exists>0:
            return None
	return ins
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))
	return None


#从缓存中读取油品编号
def read_all_fuel_barcodes_from_cache(key):
    value=cache.get(key)
    if value==None:
        data=None
    else:
        data=json.loads(value)
    return data

def write_all_fuel_barcodes_in_cache(key,value):
    cache.set(key,json.dumps(value),settings.MEMCACHED_TIMEOUT)

#从缓存中读取油站名称
def read_station_descriptions_from_cache():
    key='station_descriptions'
    value=cache.get(key)
    if value==None:
        data=None
    else:
        data=json.loads(value)
    return data

def write_station_descriptions_in_cache(value):
    key='station_descriptions'
    cache.set(key,json.dumps(value),settings.MEMCACHED_TIMEOUT)

#从缓存中读取油品名称
def read_fuel_descriptions_from_cache(key):
    value=cache.get(key)
    if value==None:
        data=None
    else:
        data=json.loads(value)
    return data

def write_fuel_descriptions_in_cache(key,value):
    cache.set(key,json.dumps(value),settings.MEMCACHED_TIMEOUT)

#从缓存中读取所有油品类型
def read_all_fuel_types_from_cache(key):
    value=cache.get(key)
    if value==None:
        data=None
    else:
        data=json.loads(value)
    return data

def write_all_fuel_types_in_cache(key,value):
    cache.set(key,json.dumps(value),settings.MEMCACHED_TIMEOUT)

#从缓存中读取所有地点
def read_all_locations_from_cache(key):
    value=cache.get(key)
    if value==None:
        data=None
    else:
        data=json.loads(value)
    return data

def write_all_locations_in_cache(key,value):
    cache.set(key,json.dumps(value),settings.MEMCACHED_TIMEOUT)

def read_all_locations_with_dict_info_from_cache(key):
    value=cache.get(key)
    if value==None:
        data=None
    else:
        data=json.loads(value)
    return data

def write_all_locations_with_dict_info_in_cache(key,value):
    cache.set(key,json.dumps(value),settings.MEMCACHED_TIMEOUT)

#从缓存中根据用户读取油品类型
def read_user_fuel_types_dict_from_cache(key):
    value=cache.get(key)
    if value==None:
        data=None
    else:
        data=json.loads(value)
    return data

def write_user_fuel_types_dict_in_cache(key,value):
    cache.set(key,json.dumps(value),settings.MEMCACHED_TIMEOUT)

#从缓存中根据用户读取非油品top10
def read_user_none_fuel_top10_from_cache(key):
    value=cache.get(key)
    if value==None:
        data=None
    else:
        data=json.loads(value)
    return data

def write_user_none_fuel_top10_in_cache(key,value):
    cache.set(key,json.dumps(value),settings.MEMCACHED_TIMEOUT)

#缓存删除
def delete_by_key_from_cache(key):
    cache.delete(key)

def get_or_create(session, model, defaults={}, **kwargs):
    """
    插入新数据, 若数据已存在则返回已有记录. 若数据库存在唯一约束, 保证不会重复插入

    :param session: SQLAlchemy `Session`
    :param model: 数据表映射
    :param defaults: 新数据的参数默认值
    :param kwargs: 查询条件
    """
    try:
        query = session.query(model).filter_by(**kwargs)

        instance = query.first()

        if instance:
            return instance, False
        else:
            session.begin(nested=True)
            from sqlalchemy.exc import IntegrityError
            try:
                params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
                params.update(defaults)

                instance = model(**params)

                session.add(instance)
                session.commit()

                return instance, True
            except IntegrityError as e:
                session.rollback()
                instance = query.one()

                return instance, False
    except Exception as e:
        session.rollback()
        raise e


#根据油站名字获取油枪号
def get_guns_id_by_site(site):
    data=[]
    create_session = get_dash_session_maker(site)
    s = create_session()

    #查找油枪号
    sql = select([ Trans.pump_id]).\
        where(and_(Trans.site==site,Trans.trans_type==0)).group_by(Trans.pump_id)
    results = s.execute(sql)
    results = results.fetchall()
    for result in results:
        result=result.pump_id
        if result in data:
            continue
        data.append(result)
    s.close()
    return data

#获取用户名称下的所有站点的通道油机油位信息
def get_passage_machine_level_by_user_site(sites=None):
    if sites==None:
        return {}
    ret={}
    create_session = get_dash_session_maker()
    s = create_session()
    for site in sites:
        name=site['name']
        dict={}
        obj=s.query(Station).filter_by(name=name).one()
        if obj.machine_passage!=None:
            dict=json.loads(obj.machine_passage)
        ret[name]=dict
    s.close()
    return ret

#导入站点逻辑天
def import_sitedaybatch_data(site,file):
    site=site.strip().upper()
    s = get_dash_session_maker()
    with open(file) as fd:
        batch_counter=0
        for row in fd:
            try:
                #批量提交
                if batch_counter==10000:
                    print 'finish 10000 row'
                    s.commit()
                    batch_counter=0

                batch_counter+=1
                print batch_counter

                row=row.strip(' \r\n').decode('gb2312').split(',')

                ins=insert_sitedaybatch_record(site,row)
                if ins is None:
                    continue

                s.add(ins)

            except Exception,e:
                print e

        s.commit()
        s.close()

#站点逻辑天插入
def insert_sitedaybatch_record(site,row):
    try:
        item={
            'site': site,
            'day':row[0],
            'day_open':row[1],
            'day_close':row[2]
        }
        return SiteDayBatch(**item)

    except Exception, e:
        print 'insert error:',e,'data:',row
        return None

#根据输入日期得到逻辑天的起止时间
def getSiteDay(site,day):
    dict={}
    try:
        s=get_dash_session_maker()
        obj=s.query(SiteDayBatch).filter_by(site=site,day=day).one()
        dict['day_open']=obj.day_open
        dict['day_close']=obj.day_close
    except Exception, e:
        return None

    s.close()

    return dict

#检查油品编号与系统定义油品类型关系中是否已经存在油品类型或中文名称
#type:0 id和name都有更改,1 name有更改, 2 id有更改
def checkFuelTypeRelationNameAndId(type,id,name):
    #返回值:0:id已存在,1:name已存在,2:没有重复信息
    try:
        s=get_dash_session_maker()
        if type=='-1':
            s.close()
            return 2
        elif type=='0' or type=='3':
            obj=s.query(FuelTypeRelation).filter(or_(FuelTypeRelation.id==id,FuelTypeRelation.name==name)).all()

            #如果查询到了数据说明id或name有重复
            if len(obj)>0:
                #id重复
                if obj[0].id==int(id):
                    s.close()
                    return 0
                #name重复
                else:
                    s.close()
                    return 1
            else:
                s.close()
                return 2
        elif type=='1':
            obj=s.query(FuelTypeRelation).filter_by(name=name).all()

            #如果查询到了数据,说明name有重复
            if len(obj)>0:
                s.close()
                return 1
            else:
                s.close()
                return 2
        elif type=='2':
            obj=s.query(FuelTypeRelation).filter_by(id=id).all()

            #如果查询到了数据,说明id有重复
            if len(obj)>0:
                s.close()
                return 0
            else:
                s.close()
                return 2
    except Exception, e:
        s.close()
        return None

#获取年份
def get_years():
    ret_years=[]
    for i in range(1990,2016):
        ret_years.append((i,i))
    return ret_years

#获取月份
def get_months():
    ret_months=[]
    for i in range(1,13):
        ret_months.append((i,i))
    return ret_months

#更新支付类型
def update_vip_pay(cardnum):
    payment_type=getPaymentTypeByCard(str(cardnum),'^1000113\w{11}|1000413\w{11}|1000513\w{11}|1000613\w{11}$')
    return payment_type

#删除Trans表中的数据
def delTransBySite(site):
    try:
        create_session = get_dash_session_maker(site)
        s = create_session()
        des_session=get_dash_session_maker()()
        s.query(Trans).filter_by(site=site).delete()
        des_session.query(Card).filter_by(site=site).delete()
        des_session.query(StationItemAssoc).filter_by(site=site).delete()
        des_session.query(Station).filter_by(name=site).delete()
        des_session.query(UserStation).filter_by(station=site).delete()
        des_session.query(StationDailyStat).filter_by(site=site).delete()
        des_session.query(StationMonthStat).filter_by(site=site).delete()
        des_session.query(StationDailyFuelSales).filter_by(site=site).delete()
        s.commit()
        s.close()
        des_session.commit()
        des_session.close()
    except Exception,e:
        ajax_logger.error(str(e))

#通过油枪号获取通道和列道
def getChannelAndColumnByPump(site,pump_id):
    s=get_dash_session_maker()()
    dict={}
    result={}
    flag1=False
    flag2=False
    try:
        obj=s.query(Station).filter_by(name=site).one()
        if obj.machine_passage!=None:
            dict=json.loads(obj.machine_passage)

            if dict.has_key('passages') and dict.has_key('column'):

                #获取通道名字
                if dict.has_key('passages'):
                    for passage in dict['passages']:
                        if flag1:
                            break
                        if str(pump_id) in passage['value']:
                            result['passage']=passage['name']
                            flag1=True
                            break

                #获取列道名字
                if dict.has_key('column'):
                    for column in dict['column']:
                        if flag2:
                            break
                        if str(pump_id) in column['value']:
                            result['column']=column['name']
                            flag2=True
                            break

                if result.has_key('passage')==False or result.has_key('column')==False:
                    result={}

    except Exception,e:
            ajax_logger.error(str(e))
    finally:
        s.close()
        return result

#获取用户所有的区域信息
def getUserLocationInfo(request):
    try:
        locations = []
        sm=get_dash_session_maker()
        s=sm()
        #获取当前用户的id
        user=s.query(User).filter_by(name=request.session['username']).one()
        user_id = user.id

        stations = s.query(UserStation).filter_by(user_id=user_id).all()

        for station in stations:
            location = s.query(Station).filter_by(name=station.station).one()
            if location.province==0 or location.province in locations:
                continue
            locations.append(location.province)

    except Exception,e:
        ajax_logger.error(str(e))

    finally:
        sm.close()
        return locations

#获取用户标签信息
def getUserTags(user_name=None):
    try:
        ret_tags=[]
        if user_name==None:
            return ret_tags
        s=get_dash_session_maker()()

        #获取当前用户的id
        user=s.query(User).filter_by(name=user_name).one()
        user_id = user.id

        tags = s.query(Tag).filter_by(user_id=user_id).all()

        if len(tags)==0:
            ret_tags.append((0,'暂无标签'))

        for tag in tags:
            ret_tags.append((tag.id,tag.tag))
    except Exception,e:
        ajax_logger.error(str(e))

    finally:
        s.close()
        return ret_tags

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

#计算所有的站的健康指标
def compute_health_result():
    import datetime
    from datetime import timedelta
    try:

        create_session = get_dash_session_maker()
        des_session=create_session()

        #查询所有油站
        stations = des_session.query(Station).all()

        #分别计算每个站的指标
        for station in stations:
            #站点名字
            site_name = station.name

            s = get_dash_session_maker(site_name)()

            #油品与非油品相关性初始值
            fuel_assoc_value = 0
            fuel_assoc_info = ''

            #非油品相关性初始值
            none_fuel_assoc_value = 0
            none_fuel_assoc_info = ''

            """
            计算油品和非油品相关性:油品和非油品相关数量临界值：5，8

            """

            #所有的油品barcode
            all_user_fuel_type=get_station_fuel_types_by_name(site_name)
            fuel_barcode_dict={}
            for item in all_user_fuel_type:
                fuel_barcode_dict[item[0]]=item[1]
            all_user_fuel_str=str(tuple(fuel_barcode_dict.keys())).replace('L','')

            #当前用户所有的非油品barcode
            all_user_none_fuel_type=get_user_none_fuel_type_by_name('tao')
            none_fuel_barcode_dict={}
            for item in all_user_none_fuel_type:
                none_fuel_barcode_dict[item[0]]=item[1]
            all_user_none_fuel_str=str(tuple(none_fuel_barcode_dict.keys())).replace('L','')

            #非油品之间的相关性
            none_fuel_assoc_sql="SELECT station_item_assoc.item_from,item.barcode FROM station_item_assoc "\
            "JOIN item ON station_item_assoc.item_to = item.barcode "\
            "WHERE site=\'%s\' and period = 0 and item_from in %s and item_to not in %s "% (site_name,all_user_none_fuel_str,all_user_fuel_str)

            none_fuel_assoc_rows = des_session.execute(none_fuel_assoc_sql)

            none_fuel_assoc_value = none_fuel_assoc_rows.rowcount

            if none_fuel_assoc_value < 5:
                none_fuel_assoc_info = '瘦弱'
            elif none_fuel_assoc_value < 8:
                none_fuel_assoc_info = '良好'
            else:
                none_fuel_assoc_info = '强壮'

            if fuel_assoc_value < 5:
                fuel_assoc_info = '瘦弱'
            elif fuel_assoc_value < 8:
                fuel_assoc_info = '良好'
            else:
                fuel_assoc_info = '强壮'




            #油品与非油品之间的相关性
            fuel_assoc_sql="SELECT station_item_assoc.item_from FROM station_item_assoc "\
                "JOIN item ON station_item_assoc.item_to = item.barcode "\
                "WHERE site=\'%s\' and period = 0 and item_from in %s and item_to not in %s"\
                % (site_name,all_user_fuel_str,all_user_fuel_str)

            fuel_assoc_rows = des_session.execute(fuel_assoc_sql)

            #选出加油量最大一天
            sql="SELECT sum(fact_trans.quantity) AS quantity ,dim_datehour.year, dim_datehour.month,dim_datehour.day FROM fact_trans JOIN dim_datehour ON dim_datehour.id = fact_trans.datehour "\
                 "WHERE fact_trans.site = '%s' "\
                 "AND fact_trans.trans_type = 0 GROUP BY dim_datehour.year, dim_datehour.month,dim_datehour.day ORDER BY quantity DESC LIMIT 1"%(site_name)

            rows = s.execute(sql)

            #获取最大加油量的日期
            for row in rows:
                max_time='%s-%s-%s'%(row['year'],row['month'],row['day'])
                max_time=datetime.datetime.strptime(max_time, "%Y-%m-%d")

                #初始化每天数据
                max_day_data = [0 for i in xrange(0, 24)]

                #获取第一条曲线
                temp_sql="SELECT sum(fact_trans.quantity) AS quantity, dim_datehour.hour AS hour "\
                    "FROM fact_trans JOIN dim_datehour ON dim_datehour.id = fact_trans.datehour "\
                    "WHERE fact_trans.site = '%s' AND fact_trans.datehour >= '%s'"\
                    " AND fact_trans.datehour < '%s' AND fact_trans.trans_type = 0 GROUP BY dim_datehour.hour"%(site_name,max_time.strftime("%Y-%m-%d"),(max_time+timedelta(days=1)).strftime("%Y-%m-%d"))

                temp_rows=s.execute(temp_sql)

                #存储第一条曲线每小时的加油量
                for temp_row in temp_rows:
                    max_day_data[temp_row['hour']]=temp_row['quantity']

            #获取该站的起止时间
            final_end_date = station.latest_date
            if not final_end_date:
                continue
            final_start_date = final_end_date - timedelta(days=31)
            start_date = final_start_date
            end_date = final_start_date

            month_counts = (final_end_date-final_start_date).days/30
            if (final_end_date-final_start_date).days%30 >0 :
                month_counts += 1

            for month_count in xrange(0,month_counts+1):
                start_date = end_date
                end_date = start_date + timedelta(days=30)

                #油品每天高峰期区间
                day_quantity_crest = []


                """
                计算油站每天是否存在瓶颈：1.选出加油量最大的一天交易作为第一条曲线
                                     2.遍历的每天的交易作为第二条曲线
                                     3.判断某天高峰期的区间内，两天的曲线是否出现交点，如果出现则为有瓶颈，否则没有瓶颈

                """

                #查询该站点所有油品的交易流水，按时间排序
                trans = s.query(Trans).filter(Trans.site==site_name,Trans.timestamp>=start_date,Trans.timestamp<=end_date).order_by('timestamp').all()


                #初始化数据
                start_time = datetime.datetime(start_date.year,start_date.month,start_date.day,0,0,0)
                time = datetime.datetime(start_date.year,start_date.month,start_date.day,0,0,0)

                day_data = []
                oil_trans_count = []
                none_oil_trans_count = []

                for i in xrange(0, 24):
                    day_data.append(0)

                    #油品每天的交易笔数按小时划分
                    oil_trans_count.append(0)

                    #非油品每天的交易笔数按小时划分
                    none_oil_trans_count.append(0)

                now_num = 0

                counts = len(trans)-1

                #非油品的消费的总额
                non_fuel_total_pay = 0.0

                #非油品的交易笔数
                non_fuel_trans_count = 0.0


                #客单值的初始值
                customer_value = 0.0

                #92/93单车加油量初始值
                single_92_quantity_value = 0.0

                #92/93交易笔数初始值
                fuel_92_trans_count = 0.0

                #95/97单车加油量初始值
                single_95_quantity_value = 0.0

                #95/97交易笔数初始值
                fuel_95_trans_count = 0.0

                #92/93加满率初始值
                pump_92_value=0.0

                #95/97加满率初始值
                pump_95_value=0.0

                #柴油加满率初始值
                pump_0_value=0.0

                #柴油交易笔数
                fuel_0_trans_count=0.0

                #92/93加满笔数初始值
                pump_92_trans_count = 0.0

                #95/97加满笔数初始值
                pump_95_trans_count = 0.0

                #柴油加满笔数初始值
                pump_0_trans_count = 0.0

                #高峰期油枪效率初始值
                crest_pump_time_percent = 0.0

                #根据每笔流水计算
                for tran in trans:
                    time = datetime.datetime(tran.datehour.year,tran.datehour.month,tran.datehour.day,0,0,0)

                    #非油品交易累计金额和交易笔数
                    if tran.trans_type == 1:
                        non_fuel_total_pay += tran.pay
                        non_fuel_trans_count += 1

                    #天数变化，计算上一天的指数
                    if time>start_time or now_num == counts:

                        #插入非油品相关性数据
                        try:
                            assco = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=11).one()
                            assco.info = none_fuel_assoc_info
                            assco.value = none_fuel_assoc_value
                            des_session.commit()
                        except:
                            obj = StationHealthStatus(site=site_name,date=start_time,type=11,desc=station.description,info=none_fuel_assoc_info,value=none_fuel_assoc_value)
                            des_session.add(obj)
                            des_session.commit()

                        #插入油品与非油品相关性数据
                        try:
                            assco = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=12).one()
                            assco.info = fuel_assoc_info
                            assco.value = fuel_assoc_value
                            des_session.commit()
                        except:
                            obj = StationHealthStatus(site=site_name,date=start_time,type=12,desc=station.description,info=fuel_assoc_info,value=fuel_assoc_value)
                            des_session.add(obj)
                            des_session.commit()

                        """
                        单车加油量：1.分别计算92/93和95/97的每天加油量
                                  2.分别统计92/93和95/97的每天交易笔数
                                  3.加油量/交易笔数（临界点 92/93：20，40 95/97：35，60）
                        """
                        if fuel_92_trans_count == 0:
                            single_92_value = 0.0
                            pump_92_value = 0
                        else:
                            single_92_value = round(single_92_quantity_value/fuel_92_trans_count,2)
                            pump_92_value = round(pump_92_trans_count/fuel_92_trans_count,2)
                        if fuel_95_trans_count == 0:
                            single_95_value = 0.0
                            pump_95_value = 0
                        else:
                            single_95_value = round(single_95_quantity_value/fuel_95_trans_count,2)
                            pump_95_value = round(pump_95_trans_count/fuel_95_trans_count,2)
                        if fuel_0_trans_count == 0:
                            pump_0_value = 0.0
                        else:
                            pump_0_value = round(pump_0_trans_count/fuel_0_trans_count,2)


                        """
                        加满率：1.分别统计92/93、95/97和柴油交易笔数
                              2.分别统计92/93、95/97和柴油加满交易笔数
                              3.计算加满率（临界值：92/93：0.5，0.6  95/97：0.6，0.7  柴油：0.8，0.9）
                        """

                        try:
                            pump_92 = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=6).one()
                            pump_92.value = pump_92_value*100
                            if pump_92_value < 50:
                                pump_92.info = '瘦弱'
                            elif pump_92_value < 60:
                                pump_92.info = '良好'
                            else:
                                pump_92_value.info = '强壮'
                                des_session.commit()
                        except:
                            if pump_92_value < 50:
                                info = '瘦弱'
                            elif pump_92_value < 60:
                                info = '良好'
                            else:
                                info = '强壮'
                            obj = StationHealthStatus(site=site_name,date=start_time,type=6,desc=station.description,info=info,value=pump_92_value*100)
                            des_session.add(obj)
                            des_session.commit()

                        try:
                            pump_95 = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=7).one()
                            pump_95.value = pump_95_value*100
                            if pump_95_value < 60:
                                pump_95.info = '瘦弱'
                            elif pump_95_value < 70:
                                pump_95.info = '良好'
                            else:
                                pump_95_value.info = '强壮'
                                des_session.commit()
                        except:
                            if pump_95_value < 60:
                                info = '瘦弱'
                            elif pump_95_value < 70:
                                info = '良好'
                            else:
                                info = '强壮'
                            obj = StationHealthStatus(site=site_name,date=start_time,type=7,desc=station.description,info=info,value=pump_95_value*100)
                            des_session.add(obj)
                            des_session.commit()

                        try:
                            pump_0 = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=8).one()
                            pump_0.value = pump_0_value*100
                            if pump_0_value < 80:
                                pump_0.info = '瘦弱'
                            elif pump_0_value < 90:
                                pump_0.info = '良好'
                            else:
                                pump_0_value.info = '强壮'
                                des_session.commit()
                        except:
                            if pump_0_value < 80:
                                info = '瘦弱'
                            elif pump_0_value < 90:
                                info = '良好'
                            else:
                                info = '强壮'
                            obj = StationHealthStatus(site=site_name,date=start_time,type=8,desc=station.description,info=info,value=pump_0_value*100)
                            des_session.add(obj)
                            des_session.commit()

                        #92/93加满笔数初始值
                        pump_92_trans_count = 0.0

                        #95/97加满笔数初始值
                        pump_95_trans_count = 0.0

                        #柴油加满笔数初始值
                        pump_0_trans_count = 0.0


                        try:
                            single_92 = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=3).one()
                            single_92.value = single_92_value
                            if single_92_value < 20:
                                single_92.info = '瘦弱'
                            elif single_92_value < 40:
                                single_92.info = '良好'
                            else:
                                single_92.info = '强壮'
                                des_session.commit()
                        except:
                            if single_92_value < 20:
                                info = '瘦弱'
                            elif single_92_value < 40:
                                info = '良好'
                            else:
                                info = '强壮'
                            obj = StationHealthStatus(site=site_name,date=start_time,type=3,desc=station.description,info=info,value=single_92_value)
                            des_session.add(obj)
                            des_session.commit()

                        try:
                            single_95 = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=4).one()
                            single_95.value = single_95_value
                            if single_95_value < 35:
                                single_95.info = '瘦弱'
                            elif single_95_value < 60:
                                single_95.info = '良好'
                            else:
                                single_95.info = '强壮'
                                des_session.commit()
                        except:
                            if single_95_value < 35:
                                info = '瘦弱'
                            elif single_95_value < 60:
                                info = '良好'
                            else:
                                info = '强壮'
                            obj = StationHealthStatus(site=site_name,date=start_time,type=4,desc=station.description,info=info,value=single_95_value)
                            des_session.add(obj)
                            des_session.commit()

                        #92/93单车加油量初始值
                        single_92_quantity_value = 0.0

                        #92/93交易笔数初始值
                        fuel_92_trans_count = 0.0

                        #95/97单车加油量初始值
                        single_95_quantity_value = 0.0

                        #95/97交易笔数初始值
                        fuel_95_trans_count = 0.0

                        #柴油交易笔数初始值
                        fuel_0_trans_count = 0.0



                        #计算上一天的客单值
                        if non_fuel_trans_count == 0:
                            customer_value = 0.0
                        else:
                            customer_value = round(non_fuel_total_pay/non_fuel_trans_count,2)


                        """
                        客单值：1.计算非油品每天总的消费金额
                              2.计算非油品每天的交易笔数
                              3.计算客单值：消费金额/消费笔数 （临界点：20，100）
                        """
                        try:
                            customer = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=2).one()
                            customer.value = customer_value
                            if customer_value < 20:
                                customer.info = '瘦弱'
                            elif customer_value < 100:
                                customer.info = '良好'
                            else:
                                customer.info = '强壮'
                                des_session.commit()
                        except:
                            if customer_value < 20:
                                info = '瘦弱'
                            elif customer_value < 100:
                                info = '良好'
                            else:
                                info = '强壮'
                            obj = StationHealthStatus(site=site_name,date=start_time,type=2,desc=station.description,info=info,value=customer_value)
                            des_session.add(obj)
                            des_session.commit()

                        #非油品的消费的总额
                        non_fuel_total_pay = 0.0

                        #非油品的交易笔数
                        non_fuel_trans_count = 0

                        #客单值的初始值
                        customer_value = 0.0


                        #计算上一天的高峰期
                        day_quantity_crest=cal_peak_period(day_data)

                        #初始化是否有瓶颈
                        has_bottleneck = False

                        #高峰期油品交易笔数
                        crest_oil_trans_count = 0.0

                        #高峰期非油品交易笔数
                        crest_none_oil_trans_count = 0.0

                        #查询高峰期时两条曲线是否有交点，如果有则存在瓶颈
                        for crest in day_quantity_crest:
                            for point in crest:
                                if point == 24:
                                    continue
                                if max_day_data[point]<day_data[point]:
                                    try:
                                        has_bottleneck = True
                                        health = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=0).one()
                                        if health.value == 1:
                                            health.value = -1
                                            health.info = '有瓶颈'
                                            des_session.commit()
                                    except:
                                        obj = StationHealthStatus(site=site_name,date=start_time,type=0,desc=station.description,info='有瓶颈',value=-1)
                                        des_session.add(obj)
                                        des_session.commit()
                                    break

                                #统计高峰期的出油量
                                crest_pump_time_percent += day_data[point]

                                #统计高峰期油品交易笔数
                                crest_oil_trans_count += oil_trans_count[point]

                                #统计高峰期非油品交易笔数
                                crest_none_oil_trans_count += none_oil_trans_count[point]

                        if not has_bottleneck:
                            try:
                                health = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=0).one()
                                if health.value == -1:
                                    health.value = 1
                                    health.info = '无瓶颈'
                                    des_session.commit()
                            except:
                                obj = StationHealthStatus(site=site_name,date=start_time,type=0,desc=station.description,info='无瓶颈',value=1)
                                des_session.add(obj)
                                des_session.commit()



                        #计算高峰期的出油时间，临界值为5，8
                        crest_pump_time_percent = round(crest_pump_time_percent/24/settings.PUMP_TRANS_TIME,0)
                        if crest_pump_time_percent < 5:
                            crest_pump_time_percent_info = '瘦弱'
                        elif crest_pump_time_percent < 8:
                            crest_pump_time_percent_info = '良好'
                        else:
                            crest_pump_time_percent_info = '强壮'

                        try:
                            crest_pump_time = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=5).one()
                            crest_pump_time.info = crest_pump_time_percent_info
                            crest_pump_time.value = crest_pump_time_percent
                            des_session.commit()
                        except:
                            obj = StationHealthStatus(site=site_name,date=start_time,type=5,desc=station.description,info=crest_pump_time_percent_info,value=crest_pump_time_percent)
                            des_session.add(obj)
                            des_session.commit()

                        oil_trans_num = 0.0
                        none_oil_trans_num = 0.0

                        for i in xrange(0,24):
                            oil_trans_num += oil_trans_count[i]

                        for i in xrange(0,24):
                            none_oil_trans_num += none_oil_trans_count[i]

                        #非高峰期油品交易笔数
                        normal_oil_trans_count = oil_trans_num - crest_oil_trans_count

                        #非高峰期非油品交易笔数
                        normal_none_oil_trans_count = none_oil_trans_num - crest_none_oil_trans_count

                        #计算非高峰期油非转化率，临界值：0.08，0.12
                        if normal_oil_trans_count == 0:
                            normal_none_fule_percent = 0.0
                        else:
                            normal_none_fule_percent = round(normal_none_oil_trans_count/normal_oil_trans_count,2)

                        if normal_none_fule_percent < 0.08:
                            normal_none_fule_percent_info = '瘦弱'
                        elif normal_none_fule_percent < 0.12:
                            normal_none_fule_percent_info = '良好'
                        else:
                            normal_none_fule_percent_info = '强壮'

                        try:
                            normal_percent = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=9).one()
                            normal_percent.value = normal_none_fule_percent*100
                            normal_percent.info = normal_none_fule_percent_info
                            des_session.commit()
                        except:
                            obj = StationHealthStatus(site=site_name,date=start_time,type=9,desc=station.description,info=normal_none_fule_percent_info,value=normal_none_fule_percent*100)
                            des_session.add(obj)
                            des_session.commit()

                        #计算高峰期油非转化率，临界值为：0.05,0.1
                        if crest_oil_trans_count == 0:
                            crest_none_fule_percent = 0.0
                        else:
                            crest_none_fule_percent = round(crest_none_oil_trans_count/crest_oil_trans_count,2)
                        if crest_none_fule_percent < 0.05:
                            crest_none_fule_percent_info = '瘦弱'
                        elif crest_none_fule_percent < 0.1:
                            crest_none_fule_percent_info = '良好'
                        else:
                            crest_none_fule_percent_info = '强壮'

                        try:
                            crest_percent = des_session.query(StationHealthStatus).filter_by(site=site_name,date=start_time,type=10).one()
                            crest_percent.value = crest_none_fule_percent*100
                            crest_percent.info = crest_none_fule_percent_info
                            des_session.commit()
                        except:
                            obj = StationHealthStatus(site=site_name,date=start_time,type=10,desc=station.description,info=crest_none_fule_percent_info,value=crest_none_fule_percent*100)
                            des_session.add(obj)
                            des_session.commit()

                        crest_pump_time_percent = 0.0

                        start_time = time

                        day_data = []
                        oil_trans_count =[]
                        none_oil_trans_count =[]

                        for i in xrange(0, 24):
                            day_data.append(0)

                            #油品每天的交易笔数按小时划分
                            oil_trans_count.append(0)

                            #非油品每天的交易笔数按小时划分
                            none_oil_trans_count.append(0)


                    #当天该站点每小时的加油量列表
                    if tran.trans_type == 0:
                        #计算一天按照小时统计的加油量
                        day_data[int(tran.datehour.hour)] += tran.quantity
                        oil_trans_count[int(tran.datehour.hour)] += 1
                        if tran.desc.find('92')>-1:
                            single_92_quantity_value += tran.quantity
                            fuel_92_trans_count += 1
                            #加满
                            if tran.pump_type == 0:
                                pump_92_trans_count += 1

                        elif tran.desc.find('93')>-1:
                            single_92_quantity_value += tran.quantity
                            fuel_92_trans_count += 1
                            #加满
                            if tran.pump_type == 0:
                                pump_92_trans_count += 1
                        elif tran.desc.find('95')>-1:
                            single_95_quantity_value += tran.quantity
                            fuel_95_trans_count += 1
                            #加满
                            if tran.pump_type == 0:
                                pump_95_trans_count += 1
                        elif tran.desc.find('97')>-1:
                            single_95_quantity_value += tran.quantity
                            fuel_95_trans_count += 1
                            #加满
                            if tran.pump_type == 0:
                                pump_95_trans_count += 1
                        else:
                            fuel_0_trans_count += 1
                            #加满
                            if tran.pump_type == 0:
                                pump_0_trans_count += 1

                    else:
                        none_oil_trans_count[int(tran.datehour.hour)] += 1

                    now_num+=1

                """
                计算忠诚客户比例：1.算出所有持卡用户的数量
                               2.算出持卡客户中的忠诚客户（一周内两次及以上的加油次数即为忠诚客户）
                               3.算出忠诚客户比例（临界点为40%和60%）
                """
                #忠诚客户初始值
                loyalty_cus = 0.0

                #总客户初始值
                all_cus = 0.0

                loyalty_sql = "select cardnum,datehour from fact_trans where payment_type<1000 and site='%s' and timestamp>='%s' and timestamp<'%s' group by cardnum,datehour order by datehour"%(site_name,start_date,end_date)
                loyalty_rows = s.execute(loyalty_sql)

                #初始化卡列表
                card_list = {}

                #初始化数据
                start_time = datetime.datetime(start_date.year,start_date.month,start_date.day)

                loyalty_counts = (loyalty_rows).rowcount-1
                now_loyalty_count = 0
                for loyalty_row in loyalty_rows:
                    #一周算一次重复率
                    time = datetime.datetime(loyalty_row['datehour'].year,loyalty_row['datehour'].month,loyalty_row['datehour'].day,0,0,0)
                    if (time-start_time).days >=7 or now_loyalty_count == loyalty_counts:
                        if int(all_cus) == 0:
                            value = 0.0
                        else:
                            value = round(loyalty_cus/all_cus,2)
                        all_cus = 0.0
                        loyalty_cus = 0.0
                        tmp_time = start_time
                        for idx in xrange(7):
                             try:
                                 if tmp_time > final_end_date:
                                     break
                                 health = des_session.query(StationHealthStatus).filter_by(site=site_name,date=tmp_time,type=1).one()
                                 health.value = value*100
                                 if value<40:
                                     health.info = '瘦弱'
                                 elif value<60:
                                     health.info = '良好'
                                 else:
                                     health.info = '强壮'
                                 des_session.commit()
                             except:
                                 if value<40:
                                     info = '瘦弱'
                                 elif value<60:
                                     info = '良好'
                                 else:
                                     info = '强壮'
                                 obj = StationHealthStatus(site=site_name,date=tmp_time,type=1,desc=station.description,info=info,value=value*100)
                                 des_session.add(obj)
                                 des_session.commit()
                             tmp_time = tmp_time + timedelta(days=1)
                        start_time = time
                    cardnum = str(loyalty_row['cardnum'])

                    if card_list.has_key(cardnum):
                        last_time = card_list[cardnum]

                        #7天内重复加油算作忠诚客户
                        if (time-last_time).days<7:
                            loyalty_cus += 1
                    else:
                        card_list[cardnum] = time
                    all_cus += 1

                    now_loyalty_count += 1

    except Exception,e:
        print e
        ajax_logger.error(str(e))
