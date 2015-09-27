# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb,json,datetime,xlwt,xlrd
from django.http import *
from django.conf import settings
from django.db.models import Q
from models import *
import xlrd,base64,logging
from sqlalchemy import *
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from django.core.management.base import BaseCommand
from gflux.apps.common.models import *
from gflux.apps.station.models import *
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from gflux.util import *
from sqlalchemy.sql import select, and_,or_,not_
from sqlalchemy import func,update
import csv,re
from django.core.management import call_command
from django.core.cache import cache
from django.utils import timezone
from sql_utils import get_location_id,get_station_id,\
get_user_fuel_type_by_name,check_staticons_code,check_locations_code,get_or_create,\
checkFuelTypeRelationNameAndId,write_station_descriptions_in_cache,read_station_descriptions_from_cache,\
get_site_desc_by_name


ajax_logger=logging.getLogger('ajax')

#登陆请求
def checkLoginAjaxRequest(request):
    #初始化返回值
    rsdic={}
    ret=Status.OK
    rsdic['ret']=ret
    rsdic['info']=Status().getReason(ret)
    try:

        #取得参数
        username=request.POST['username']
        password=request.POST['password']

        #用户名密码检查
        s = request.get_session()
        user=s.query(User).filter_by(name=username,password=password).first()
        #用户在线状态检查
        ret=checkUserOnlineStatus(request,username=username)
        if ret==Status.LOGINED_ON_OTHER_SIDE:
            rsdic['ret']=ret
            rsdic['info']=Status().getReason(ret)
            return

        #成功登陆
        request.session['username']=username
        request.session['type']=user.type
        request.session['company_name']=user.company
        request.session['django_language']=settings.LANGUAGES[user.language][0]
        sid=request.session.session_key
        if sid is None:
            request.session.save()
            sid=request.session.session_key
        request.session['sessionid'] = sid

        #init cache for user
        get_user_fuel_type_by_name(username)
        cache.set('%s_sessionid'%username,sid,settings.LOGIN_STATUS_KEEP)


    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret,error=str(e))

    finally:
        return HttpResponse(json.dumps(rsdic))

# check register
def checkRegisterAjaxRequest(request):
    rsdic={}
    rsdic['ret']='1101'

    username=request.POST['username']
    password=request.POST['password']
    email=request.POST['email']
    company=request.POST['company']
    district=request.POST['district']
    if re.match(r'^[a-zA-Z0-9]{3,16}$',username) == None:
        rsdic['info']= _(u'用户名格式错误')
        return HttpResponse(json.dumps(rsdic))

    if len(password)<6 or len(password)>16 :
        rsdic['info']= _(u'请输入长度在6到16位之间的密码')
        return HttpResponse(json.dumps(rsdic))

    #if re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]{1,}$',company) == None:
    #    rsdic['info']= _(u'公司名称只能包含汉字、字母和数字')
    #    return HttpResponse(json.dumps(rsdic))

    try:

            s=request.get_session()
            user = s.query(User).filter_by(name = username).first()
            if user :
                rsdic['ret']='1111'
                rsdic['info']=_(u'注册失败,用户名已存在')
                return HttpResponse(json.dumps(rsdic))
            user = s.query(User).filter_by(email = email).first()
            if user :
                rsdic['ret']='1111'
                rsdic['info']=_(u'注册失败,邮箱已注册')
                return HttpResponse(json.dumps(rsdic))
            user = User(name=username, password=password,email=email,company=company,type=0,district=district)
            s.add(user)
            s.commit()
            rsdic['ret']='1101'
            rsdic['info'] = '注册成功'

            #发送邮件
            try :
                call_command('gearman_submit_job','send_email',json.dumps({
                'to':['mengtao@tmlsystem.com','steven.yang@gilbarco.com','niyoufa@tmlsystem.com'],
                #'to':'zhouyong@tmlsystem.com',
                'content':'%(username)s with email:%(email)s from company:%(company)s register success!'%({
                'username':username,
                'email':email,
                'company':company
                }),
                'subject':'%(username)s register success'%({'username':username})
                }),foreground=False)
            except Exception,e:
                rsdic['ret'] = '1101'
                rsdic['info'] = '注册成功'
    except Exception,e:
        rsdic['ret']='1111'
        rsdic['info']=_(u'注册失败')
        #print e
    return HttpResponse(json.dumps(rsdic))

#修改密码
def UpdatePassword(request):
    #检查登陆情况
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #get args
        old_password=request.POST['old_password']
        new_password=request.POST['new_password']

        #get obj
        s=request.get_session()
        obj=s.query(User).filter_by(name=request.session['username']).one()
        if obj.password!=old_password:
            rsdic['ret']='0003'
            rsdic['info']=status_collection['0003']
            return

        obj.password=new_password
        s.commit()
    except Exception,e:
        #print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#增加用户站点
def AddUserStation(request):
    #检查登陆情况
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #get args
        user_id=int(request.POST['user_id'])
        site_name=request.POST['site_name']

        #get obj
        s=request.get_session()
        us=UserStation(user_id=user_id,station=site_name)
        s.add(us)
        s.commit()
    except Exception,e:
        #print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#删除用户的站点
def RemoveUserStation(request):
    #检查登陆情况
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #get args
        user_id=int(request.POST['user_id'])
        site_name=request.POST['site_name']

        #get obj
        s=request.get_session()
        obj=s.query(UserStation).filter_by(user_id=user_id,station=site_name).one()
        s.delete(obj)
        s.commit()
    except Exception,e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#取得用户的站点列表
def GetUserStation(request):
    #检查登陆情况
    rsdic=checkAjaxRequest(request,'GET')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #get args
        user_id=int(request.GET['user_id'])

        #get obj
        s=request.get_session()
        objs=s.query(UserStation).filter_by(user_id=user_id)

        #get data
        data=[]
        for obj in objs:
            site=s.query(Station).filter_by(name=obj.station).one()
            data.append(dict(
                desc=site.description,
                name=site.name
            ))
        rsdic['data']=data
    except Exception,e:
        print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#取得站点的油品类型
def GetStationFuelType(request):
    #检查登陆情况
    rsdic=checkAjaxRequest(request,'GET')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #get args
        site=request.GET['site']

        #get obj
        s=request.get_session()
        objs=s.query(StationFuelType).filter_by(station=site)

        #get data
        data=[]
        for obj in objs:
            data.append(dict(
                barcode=obj.barcode,
                name=obj.description
            ))
        rsdic['fuel_types']=data
    except Exception,e:
        ajax_logger.error(exception_stuck())
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#高级图表
def ProfessionalAnalysis(request):
    #检查登陆情况
    rsdic=checkAjaxRequest(request,'GET')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        from gflux.apps.station import cubes
        from gflux.apps.station.sql_utils import get_all_fuel_barcodes
        from gflux.apps.station.sql_utils import get_fuel_type_name
        from datetime import datetime, timedelta

        cube = cubes.TransCube()
        conditions=[cube.d.trans_type==TransType.FUEL]

        #get args
        site=request.GET['site']
        conditions.append(cube.d.site == site)

        #L加油量 T出油时间 P销售额
        count_type=request.GET['count_type']
        vertical=[]
        if count_type=='L':
            vertical.append('quantity')
        elif count_type=='T':
            vertical.append('quantity')
        elif count_type=='P':
            vertical.append('pay')

        date=request.GET['date']
        date=datetime.strptime(date,'%Y-%m-%d')
        start_date=request.GET['start_date']
        start_date=datetime.strptime(start_date,'%Y-%m-%d')
        end_date=request.GET['end_date']
        end_date=datetime.strptime(end_date,'%Y-%m-%d')

        #ONE单天 MULTI范围
        time_type=request.GET['time_type']
        if time_type=='ONE':
            conditions.append(cube.d.datehour >= date)
            conditions.append(cube.d.datehour <date+timedelta(days=1))
        elif time_type=='MULTI':
            conditions.append(cube.d.datehour >= start_date)
            conditions.append(cube.d.datehour < end_date+timedelta(days=1))

        #hour小时 day天 week周 month月
        base_time=request.GET['base_time']
        drilldown=[]
        categories=[]
        if base_time=='hour':
            drilldown.append('hour')
            categories=['%02d:00 - %02d:00' % (i, i + 1) for i in xrange(0, 24)]

        elif base_time=='day':
            drilldown.append('year')
            drilldown.append('month')
            drilldown.append('day')
            curr_date = start_date
            while curr_date <= end_date:
                categories.append(curr_date.strftime("%Y-%m-%d"))
                curr_date += timedelta(days=1)

        elif base_time=='week':
            drilldown.append('week')
            curr_date = start_date
            while curr_date <= end_date:
                categories.append(curr_date.strftime("%W"))
                curr_date += timedelta(days=7)

        elif base_time=='month':
            drilldown.append('year')
            drilldown.append('month')
            curr_date = start_date
            while curr_date <= end_date:
                categories.append(curr_date.strftime("%Y-%m"))
                curr_date += timedelta(days=31)

        #可选 key:
        #pay_type,fuel_type,pump_type,passages,machines,levels
        option={}
        for key,value in request.GET.iteritems():
            if key.startswith('option_value'):
                option[key[16:-1]]=value

        for key,value in option.iteritems():
            if key=='pay_type':
                conditions.append(cube.d.payment_type==value)
            elif key=='fuel_type':
                conditions.append(cube.d.barcode==value)
            elif key=='pump_type':
                conditions.append(cube.d.pump_type==value)
            elif key=='passages':
                s=request.get_session()
                obj=s.query(Station).filter_by(name=site).one()
                passages=json.loads(obj.machine_passage)['passages']
                for passage in passages:
                    if passage['name']==value:
                        conditions.append(cube.d.pump_id.in_(passage['value']))
                        break
            elif key=='machines':
                s=request.get_session()
                obj=s.query(Station).filter_by(name=site).one()
                machines=json.loads(obj.machine_passage)['machines']
                for machine in machines:
                    if machine['name']==value:
                        conditions.append(cube.d.pump_id.in_(machine['value']))
                        break
            elif key=='levels':
                s=request.get_session()
                obj=s.query(Station).filter_by(name=site).one()
                levels=json.loads(obj.machine_passage)['level']
                for level in levels:
                    if level['name']==value:
                        conditions.append(cube.d.pump_id.in_(level['value']))
                        break

        #曲线分组:fuel-type,pump,pay-type,pump-type,passages,machines,levels
        series_category=request.GET.getlist('series_category[]')
        for cat in series_category:
            if cat=='fuel-type':
                drilldown.append('barcode')
            elif cat=='pump':
                drilldown.append('pump_id')
            elif cat=='pay-type':
                drilldown.append('payment_type')
            elif cat=='pump-type':
                drilldown.append('pump_type')
            elif cat=='passages':
                drilldown.append('pump_id')
            elif cat=='machines':
                drilldown.append('pump_id')
            elif cat=='levels':
                drilldown.append('pump_id')

        #get data
        results = cube.aggregate(
            session_factory=request.get_session,
            measures=vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=['id'])

        #曲线分组
        fuel_type_name={}
        pay_type_name={
            1:'银联卡',
            2:'加油卡',
            3:'信用卡',
            1000:'现金'
        }
        pump_type_name={
            0:'加满',
            1:'定额'
        }
        guns=[]
        if 'passages' in series_category:
            s=request.get_session()
            obj=s.query(Station).filter_by(name=site).one()
            passages=json.loads(obj.machine_passage)['passages']
            for passage in passages:
                for gun in passage['value']:
                    if int(gun) not in guns:
                        guns.append(int(gun))
        elif 'machines' in series_category:
            s=request.get_session()
            obj=s.query(Station).filter_by(name=site).one()
            machines=json.loads(obj.machine_passage)['machines']
            for machine in machines:
                for gun in machine['value']:
                    if int(gun) not in guns:
                        guns.append(int(gun))
        elif 'levels' in series_category:
            s=request.get_session()
            obj=s.query(Station).filter_by(name=site).one()
            levels=json.loads(obj.machine_passage)['level']
            for level in levels:
                for gun in level['value']:
                    if int(gun) not in guns:
                        guns.append(int(gun))

        stats = {}

        results_stack=[results]

        #已经处于一种曲线中
        already_in_series=[]

        while len(results_stack)>0:

            #由于油枪分组存在可能
            #一条结果可能是两种分类都有份
            #所以需要记录二次结果,以便二次划分曲线名
            extend_results=[]
            results=results_stack.pop()
            for result in results:
                series_cat=''

                #如果用户选择了油枪分组,不在分组中的数据直接扔掉
                if 'passages' in series_category:
                    if int(result['pump_id']) not in guns:
                        continue
                elif 'machines' in series_category:
                    if int(result['pump_id']) not in guns:
                        continue
                elif 'levels' in series_category:
                    if int(result['pump_id']) not in guns:
                        continue

                #确定曲线名字
                for cat in series_category:
                    if cat=='fuel-type':

                        #取得油品描述
                        if fuel_type_name.has_key(result['barcode']):
                            label=fuel_type_name[result['barcode']]
                        else:
                            label=get_fuel_type_name(result['barcode'])
                            fuel_type_name[result['barcode']]=label

                        series_cat+=' 油品类型:%s'%label

                    elif cat=='pump':
                        series_cat+=' 油枪号:%s'%result['pump_id']

                    elif cat=='pay-type':

                        #取得支付方式描述
                        label=pay_type_name[result['payment_type']]
                        series_cat+=' 支付方式:%s'%label

                    elif cat=='pump-type':

                        #取得加油方式描述
                        label=pump_type_name[result['pump_type']]
                        series_cat+=' 加油方式:%s'%label

                    elif cat=='passages':
                        passages=json.loads(obj.machine_passage)['passages']

                        #是否已经添加曲线名
                        already_cated=False

                        for passage in passages:

                            #多通道可能,计算当前结果和曲线名的sha1
                            passage_sha1=hashlib.sha1()
                            passage_sha1.update(str(result['id']))
                            if str(result['pump_id']) in passage['value']:
                                passage_sha1.update(passage['name'])
                                passage_sha1.update(str(passage['value']))
                                passage_sha1=passage_sha1.hexdigest()

                                #如果sha1表明已经存在过了,则continue
                                if passage_sha1 in already_in_series:
                                    continue

                                if already_cated:

                                    #添加到二次结果供分析
                                    extend_results.append(result)
                                    break

                                else:
                                    series_cat+=' 通道:%s'%passage['name']
                                    already_in_series.append(passage_sha1)
                                    already_cated=True


                    elif cat=='machines':
                        machines=json.loads(obj.machine_passage)['machines']

                        #是否已经添加曲线名
                        already_cated=False

                        for machine in machines:

                            #多通道可能,计算当前结果和曲线名的sha1
                            passage_sha1=hashlib.sha1()
                            passage_sha1.update(str(result['id']))
                            if str(result['pump_id']) in machine['value']:
                                passage_sha1.update(machine['name'])
                                passage_sha1.update(str(machine['value']))
                                passage_sha1=passage_sha1.hexdigest()

                                #如果sha1表明已经存在过了,则continue
                                if passage_sha1 in already_in_series:
                                    continue

                                if already_cated:

                                    #添加到二次结果供分析
                                    extend_results.append(result)
                                    break

                                else:
                                    series_cat+=' 油机:%s'%machine['name']
                                    already_in_series.append(passage_sha1)
                                    already_cated=True

                    elif cat=='levels':
                        levels=json.loads(obj.machine_passage)['level']

                        #是否已经添加曲线名
                        already_cated=False

                        for level in levels:

                            #多通道可能,计算当前结果和曲线名的sha1
                            passage_sha1=hashlib.sha1()
                            passage_sha1.update(str(result['id']))
                            if str(result['pump_id']) in level['value']:
                                passage_sha1.update(level['name'])
                                passage_sha1.update(str(level['value']))
                                passage_sha1=passage_sha1.hexdigest()

                                #如果sha1表明已经存在过了,则continue
                                if passage_sha1 in already_in_series:
                                    continue

                                if already_cated:
                                    #添加到二次结果供分析
                                    extend_results.append(result)
                                    break

                                else:
                                    series_cat+=' 油位:%s'%level['name']
                                    already_in_series.append(passage_sha1)
                                    already_cated=True


                stats.setdefault(series_cat, {})

                cat=''
                if base_time=='hour':
                    cat='%02d:00 - %02d:00'%(result['hour'],result['hour']+1)
                elif base_time=='day':
                    cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
                elif base_time=='week':
                    cat='%d'%result['week']
                elif base_time=='month':
                    cat='%d-%02d'%(result['year'], result['month'])

                cat_value=0
                if count_type=='L':
                    cat_value=round(result['quantity'], 2)
                elif count_type=='T':
                    cat_value=round(result['quantity']/40,0)
                elif count_type=='P':
                    cat_value=round(result['pay'], 2)


                #如果存在结果,则求和
                if stats[series_cat].has_key(cat):
                    stats[series_cat][cat] += cat_value
                else:
                    stats[series_cat][cat] = cat_value

            #需要进行二次分析
            if len(extend_results)>0:
                results_stack.append(extend_results)

        items = stats.items()
        data = {
            "categories": categories,
            "dataset": []
        }

        for series, stat in items:
            opt = {"data": [], "name": series}

            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)
            data["dataset"].append(opt)

        rsdic.update(data)
    except Exception,e:
        #print exception_stuck()
        ajax_logger.error(str(e))
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#取得station的最新最旧时间
def GetStationLatestEarliestDate(request):
    #检查登陆情况
    rsdic=checkAjaxRequest(request,'GET')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #取得session
        s=request.get_session()

        #取得station名
        site=request.GET['site']

        #取得station 对象
        station=s.query(Station).filter_by(name=site).one()


        if station.latest_date is not None:
            rsdic['latest_date']=station.latest_date.strftime('%Y-%m-%d')
            rsdic['lastest_second_date']=(station.latest_date+ datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
            rsdic['latest_month_date']=(station.latest_date+ datetime.timedelta(days=-31)).strftime('%Y-%m-%d')
            rsdic['latest_year_date']=(station.latest_date+ datetime.timedelta(days=-366)).strftime('%Y-%m-%d')
            rsdic['latest_quarter_date']=(station.latest_date+ datetime.timedelta(days=-90)).strftime('%Y-%m-%d')
        else:
            rsdic['latest_date']=None
            rsdic['lastest_second_date']=None
            rsdic['latest_month_date']=None
            rsdic['latest_year_date']=None
            rsdic['latest_quarter_date']=None
        if station.earliest_date is not None:
            rsdic['earliest_date']=station.earliest_date.strftime('%Y-%m-%d')
        else:
            rsdic['earliest_date']=None

    except Exception,e:
        ajax_logger.error(exception_stuck())
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype="application/json")

#获取用户信息
#type
#0          所有用户
#1          试用版用户
#2          普通版用户
#3          专业版用户
def checkUsersAjaxRequest(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    user_list=[]
    s = request.get_session()

    try:
        type=int(request.POST['type'])
        if type==-1:
            sql=select([User.name,User.time,User.company,User.type]).select_from(User.__table__)
            rs=s.execute(sql)
            users=rs.fetchall()
        elif type==1:
            sql=select([User.name,User.time,User.company,User.type]).where(User.type==1).select_from(User.__table__)
            rs=s.execute(sql)
            users=rs.fetchall()
        elif type==2:
            sql=select([User.name,User.time,User.company,User.type]).where(User.type==2).select_from(User.__table__)
            rs=s.execute(sql)
            users=rs.fetchall()
        elif type==3:
            sql=select([User.name,User.time,User.company,User.type]).where(User.type==3).select_from(User.__table__)
            rs=s.execute(sql)
            users=rs.fetchall()
        elif type==0:
            sql=select([User.name,User.time,User.company,User.type]).where(User.type==0).select_from(User.__table__)
            rs=s.execute(sql)
            users=rs.fetchall()

        if len(users)>0:
            for user in users:
                user_dist={}
                user_dist['name']=user.name
                user_dist['time']=str(user.time.year)+"-"+str(user.time.month)+"-"+str(user.time.day)
                user_dist['type']=user.type
                user_dist['company']=user.company
                user_list.append(user_dist)
        rsdic['data']=user_list
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))

    return HttpResponse(json.dumps(rsdic))


#上传文件
def uploadFileAjaxRequest(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    from gflux.apps.station.models import Trans
    import hashlib,time,shutil
    try:
        uploaded=request

        creator=request.session['username']
        user_type=request.session['type']
        filename = request.GET[ 'qqfile' ]

        #计算临时文件名

        sha1=hashlib.sha1()
        sha1.update(creator)
        sha1.update(filename)
        sha1.update(str(time.time()))
        tmp_file_path='/tmp/'+sha1.hexdigest()+'.data'

        #read file
        with open(tmp_file_path,'wb') as f:
            data = uploaded.read( 1024 )
            while data:
                f.write(data)
                data = uploaded.read( 1024 )

            f.close()

        #检查用户已上传文件数
        s = request.get_session()
        nb_uploaded_file=s.query(func.count('*')).filter(File.creator == creator).scalar()
        if nb_uploaded_file>=settings.MAX_LIMIT_UPLOAD_FILE_FREE and user_type==1:
            raise Exception('免费用户最多上传%s个文件!'%settings.MAX_LIMIT_UPLOAD_FILE_FREE)

        elif nb_uploaded_file>=settings.MAX_LIMIT_UPLOAD_FILE_GENERAL and user_type==2:
            raise Exception('普通用户最多上传%s个文件!'%settings.MAX_LIMIT_UPLOAD_FILE_GENERAL)

        src_path=tmp_file_path
        dst_path=settings.BASE_DIR+'/file/'+creator+'/'+filename
        log_path=settings.BASE_DIR+'/file/'+creator+'/process.log'

        #判断文件夹是否存在
        if os.path.exists(settings.BASE_DIR+'/file/'+creator)==False:
            os.mkdir(settings.BASE_DIR+'/file/'+creator)

        #保存文件
        shutil.copyfile(src_path,dst_path)

        with open(log_path,'at') as lf:
            lf.write('[%s]success uploaded file:%s\n'%(
                NowTime(),filename
            ))
            lf.close()

        #save to db

        try:
            obj,created=get_or_create(s,File,file_name=filename,creator=creator)
            s.commit()
        except Exception,e:
            rsdic['ret']=Status.UNKNOWNERR
            rsdic['info']=str(e)
            #print >> sys.stderr, "save file info to database error:"+str(e)

    except Exception,e:
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=str(e)
        #print >> sys.stderr, "save file error:"+str(e)
    finally:
        return HttpResponse(json.dumps(rsdic))

def checkFilesAjaxRequest(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    file_list=[]
    try :
        s = request.get_session()
        sql=select([File.id,File.file_name,File.time,File.creator]).where(File.creator==request.session['username']).select_from(File.__table__)
        rs=s.execute(sql)
        files=rs.fetchall()
        if len(files)>0:
            for onefile in files:
                file_dist={}
                file_dist['id']=onefile.id
                file_dist['name']=onefile.file_name
                file_dist['time']=str(onefile.time.year)+"-"+str(onefile.time.month)+"-"+str(onefile.time.day)
                file_dist['creator']=onefile.creator
                file_list.append(file_dist)
        rsdic['data']=file_list
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))

    return HttpResponse(json.dumps(rsdic))


#更新用户类型
def UpdateUserType(request):
    try:
        #get args
        username=request.POST['user_name']
        usertype=request.POST['user_type']
        enable_advanced_features=int(request.POST['enable_advanced_features'])
        #更新用户类型
        s = request.get_session()
        s.query(User).filter(User.name == username).update({
          User.type: int(usertype),
          User.enable_advanced_features:enable_advanced_features
        })
        s.commit()
        #return success
        rsdic={
            'ret':'ok',
            'info':'success'
        }
        return HttpResponse(json.dumps(rsdic))
    except Exception,e:
        rsdic={
            'ret':'error',
            'info':'got error:'+str(e)
        }
        return HttpResponse(json.dumps(rsdic))

#更新用户信息
def UpdateUserInfo(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    try:
        #get args
        username=request.session['username']
        district=request.POST['district']
        #更新用户类型
        s = request.get_session()
        s.query(User).filter(User.name == username).update({
          User.district: int(district)
        })
        s.commit()

        return HttpResponse(json.dumps(rsdic))
    except Exception,e:
        rsdic={
            'ret':'error',
            'info':'got error:'+str(e)
        }
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#用户登出
def LogoutRequest(request):
    rsdic={}
    ret=Status.OK
    rsdic['ret']=ret
    rsdic['info']=Status().getReason(ret)

    #logout in cache

    username=request.session.get('username',None)
    if username!=None:
        cache.delete('%s_sessionid'%username)

    #delete session
    for s in request.session.keys():
        del request.session[s]

    #delete cookie
    response = HttpResponse(json.dumps(rsdic))
    for c in request.COOKIES:
        if(c=='rmb'):
             continue
        response.set_cookie(c,max_age=0)
    response.set_cookie("username",username,max_age=60*60*24*30)
    return response

#打印出导入日志
def ShowImportDataProcess(request):
    try:
        #get args
        username = request.session['username']
        log_file=settings.BASE_DIR+'/file/'+username+'/process.log'
        content=''
        with open(log_file,'rt') as lf:
            content=lf.read()
            lf.close()
    except Exception,e:
        content=str(e)
    finally:
        return HttpResponse(content)

#数据自动导入
def ImportData(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    try:
        #get args
        s = request.get_session()
        data_type=request.POST.get('type','1')
        location=request.POST['location']
        location=location.strip().upper()
        site=request.POST['site']
        site=site.strip().upper()
        location_desc=request.POST['location_desc']
        site_desc=request.POST['site_desc']
        username = request.session['username']
        province = request.POST['province']
        city = request.POST['city']
        district = request.POST['district']
        import_flag_string=location+'@'+site+'@'+str(datetime.datetime.now().microsecond)
        rsdic['import_flag_string']=import_flag_string
        sql=select([User.id]).where(User.name==username).label('tao-gilbarco')
        rs=s.query(sql)
        ret=rs.first()

        args = {'need_update_station_info':False}
        #save location and station
        locid=get_location_id(location,location_desc)
        station_id,created=get_station_id(site,province=province,city=city,
            district=district,user_id=ret[0],site_desc=site_desc,
            with_created_status=True)
        if created:
            args['need_update_station_info']=True

        #gearman 参数
        args['locid']=locid
        args['station_id']=station_id
        args["site"] = site
        args['site_desc']=site_desc
        args['location']=location
        args['location_desc']=location_desc
        args['log_file']=settings.BASE_DIR+'/file/'+username+'/process.log'
        args['userid']=ret[0]
        args['username']=username

        #清理log
        with open(args['log_file'],'r+') as lf:
            lines=lf.readlines()
            nb_lines=len(lines)
            #截断
            if nb_lines>30:
                lines=lines[-30:]
                lf.truncate()
                lf.write(''.join(lines))

        if data_type=='1':

            allFileName=request.POST['all_file']
            cardFileName=request.POST['card_file']

            #check file exists
            args['all_file']=settings.BASE_DIR+'/file/'+username+'/'+allFileName
            args['card_file']=settings.BASE_DIR+'/file/'+username+'/'+cardFileName
            #检查是否导入完成
            args['import_flag_string']=import_flag_string

            if os.path.exists(args['all_file'])==False:
                raise Exception('all file not found on server!')

            if os.path.exists(args['card_file'])==False:
                raise Exception('card file not found on server!')

            result=call_command('gearman_submit_job', 'import_data',json.dumps(args), foreground=False)
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]success submit import site:%s\'s data task\n'%(
                    NowTime(),site
                ))
                lf.close()

        elif data_type=='0':
            fileName=request.POST['sp_file']
            args['file']=settings.BASE_DIR+'/file/'+username+'/'+fileName
            #检查是否导入完成
            args['import_flag_string']=import_flag_string
            if os.path.exists(args['file'])==False:
                raise Exception('all file not found on server!')
            results=call_command('gearman_submit_job', 'import_sp_excel_data',json.dumps(args), foreground=False)

            with open(args['log_file'],'at') as lf:
                lf.write('[%s]success submit import site:%s\'s data task\n'%(
                    NowTime(),site
                ))
                lf.close()

        elif data_type=='2':
            fileName=request.POST['ycshell_file']
            args['file']=settings.BASE_DIR+'/file/'+username+'/'+fileName
            #检查是否导入完成
            args['import_flag_string']=import_flag_string
            if os.path.exists(args['file'])==False:
                raise Exception('all file not found on server!')
            results=call_command('gearman_submit_job', 'import_ycshell_data',json.dumps(args), foreground=False)

            with open(args['log_file'],'at') as lf:
                lf.write('[%s]success submit import site:%s\'s data task\n'%(
                    NowTime(),site
                ))
                lf.close()

    except Exception,e:
        ajax_logger.error(str(e))
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
    finally:
        return HttpResponse(json.dumps(rsdic))

#删除File
def DeleteFile(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    try:
        obj_id=int(request.POST['id'])
        s = request.get_session()

        sql=select([File.creator]).where(File.id==obj_id).label('tao-gilbarco')
        rs=s.query(sql)
        ret=rs.first()
        if ret[0]!=request.session['username']:
            raise Exception('非法访问')

        #delete
        s.query(File).filter(File.id==obj_id).delete()
        s.commit()
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
    finally:
        return HttpResponse(json.dumps(rsdic))

#检测唯一性
def checkUnique(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    name = request.POST['name']
    checkType=int(request.POST['type'])
    try:
        #check station
        if checkType==1 :
            allSites=check_staticons_code(name)
            if allSites :
                rsdic['ret']=Status.UNKNOWNERR
        #check location
        elif checkType==2:
           allLocations= check_locations_code(name)
           if allLocations :
                rsdic['ret']=Status.UNKNOWNERR
    except Exception,e:
        rsdic['ret']=Status.UNKNOWNERR
        rsdic['info']=str(e)
    finally:
        return HttpResponse(json.dumps(rsdic))

#设置语言
def setLanguage(request):
    rsdic={}
    ret=Status.OK
    rsdic['ret']=ret
    rsdic['info']=Status().getReason(ret)
    idx=0
    for lan in settings.LANGUAGES:
        if lan[0]==request.POST['type']:
            break
        idx+=1
    language_type=idx
    user_name=request.session['username']
    s = request.get_session()
    stmt = update(User).where(User.name==user_name).\
            values(language=language_type)
    request.session['django_language']=settings.LANGUAGES[language_type][0]

    try:
        s.execute(stmt)
        s.commit()
        rsdic['info']=_(u'设置成功')
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))

    return HttpResponse(json.dumps(rsdic))

#根据站点获取相应的油枪号
def getGusIdBySite(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    try:
        #站点名字
        site_name=request.POST['site']

        #根据站点名字获取该站点的所有油枪号
        s=request.get_session()
        data=[]
        obj=s.query(Station).filter_by(name=site_name).one()
        if obj.id_guns!=None:
            data=json.loads(obj.id_guns)
        rsdic['data']=data
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))

    return HttpResponse(json.dumps(rsdic))

#增加\编辑通道油枪油位信息
def addChannelOrMachineAjax(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    channel={}
    dict={}

    #站点名
    site=request.POST['site']

    #新增信息的名字
    name=request.POST['name']

    #油枪号
    guns_id=request.POST.getlist('guns[]')

    #类型0:新增通道,1:编辑通道,2:新增油机,3:编辑油机,4:新增油位,5:编辑油位,6:新增列道，7:编辑列道
    request_type=request.POST['type']

    #新增的信息
    channel['name']=name
    channel['value']=guns_id

    s=request.get_session()
    obj=s.query(Station).filter_by(name=site).one()
    if obj.machine_passage!=None:
        dict=json.loads(obj.machine_passage)

    #根据类型进行相应的操作
    try:
        #增加通道
        if request_type=='0':
            if dict.has_key('passages'):
                dict['passages'].append(channel)
            else:
                dict['passages']=[channel]

        #编辑通道
        elif request_type=='1':
            passages=dict['passages']
            for passage in passages:
                if passage['name']==name:
                    passage['value']=guns_id
                    break

        #增加油机
        elif request_type=='2':
             if dict.has_key('machines'):
                 dict['machines'].append(channel)
             else:
                 dict['machines']=[channel]

        #编辑油机
        elif request_type=='3':
             machines=dict['machines']
             for machine in machines:
                 if machine['name']==name:
                     machine['value']=guns_id
                     break

        #增加油位
        elif request_type=='4':
            if dict.has_key('level'):
                dict['level'].append(channel)
            else:
                dict['level']=[channel]

        #编辑油位
        elif request_type=='5':
            levels=dict['level']
            for level in levels:
                if level['name']==name:
                    level['value']=guns_id
                    break

        #增加列道
        elif request_type=='6':
            if dict.has_key('column'):
                dict['column'].append(channel)
            else:
                dict['column']=[channel]

        #编辑列道
        elif request_type=='7':
            columns=dict['column']
            for column in columns:
                if column['name']==name:
                    column['value']=guns_id
                    break

        #更新数据库
        obj.machine_passage=json.dumps(dict)
        s.commit()

    except Exception,e:
        ajax_logger.error(exception_stuck())
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取通道,油位,油机信息
def getChannelAndMachineAjax(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    #获取通道,油位,油机信息
    try:
        #站点名字
        site=request.POST['site']
        s=request.get_session()
        obj=s.query(Station).filter_by(name=site).one()
        if obj.machine_passage!=None:
            rsdic['data']=json.loads(obj.machine_passage)
        else:
            rsdic['data']=[]
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#删除通道
def delChannelAjax(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #站点名字
        site=request.POST['site']

        #通道名字
        name=request.POST['name']
        dict={}
        passages=[]
        s=request.get_session()
        obj=s.query(Station).filter_by(name=site).one()
        if obj.machine_passage!=None:
            dict=json.loads(obj.machine_passage)
        for passage in dict['passages']:
            if passage['name']!=name:
                passages.append(passage)
        dict['passages']=passages
        obj.machine_passage=json.dumps(dict)
        s.commit()
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#删除油机
def delMachineAjax(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #站点名字
        site=request.POST['site']

        #油机名字
        name=request.POST['name']
        dict={}
        machines=[]
        s=request.get_session()
        obj=s.query(Station).filter_by(name=site).one()
        if obj.machine_passage!=None:
            dict=json.loads(obj.machine_passage)
        for machine in dict['machines']:
            if machine['name']!=name:
                machines.append(machine)
        dict['machines']=machines
        obj.machine_passage=json.dumps(dict)
        s.commit()
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#删除油位
def delLevelAjax(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #站点名字
        site=request.POST['site']

        #油位名字
        name=request.POST['name']
        dict={}
        levels=[]
        s=request.get_session()
        obj=s.query(Station).filter_by(name=site).one()
        if obj.machine_passage!=None:
            dict=json.loads(obj.machine_passage)
        for level in dict['level']:
            if level['name']!=name:
                levels.append(level)
        dict['level']=levels
        obj.machine_passage=json.dumps(dict)
        s.commit()
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#删除列道
def delColumnAjax(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        #站点名字
        site=request.POST['site']

        #油位名字
        name=request.POST['name']
        dict={}
        columns=[]
        s=request.get_session()
        obj=s.query(Station).filter_by(name=site).one()
        if obj.machine_passage!=None:
            dict=json.loads(obj.machine_passage)
        for column in dict['column']:
            if column['name']!=name:
                columns.append(column)
        dict['column']=columns
        obj.machine_passage=json.dumps(dict)
        s.commit()
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#检查通道,油机,油位名字的唯一性
def checkPassageMachineLevelName(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    try:
        name=request.POST['name']

        #0:通道  1:油机  2:油位  3:列道
        type=request.POST['type']
        site=request.POST['site']
        dict={}
        s=request.get_session()
        obj=s.query(Station).filter_by(name=site).one()
        if obj.machine_passage!=None:
            dict=json.loads(obj.machine_passage)

        #通道
        if type=='0':
            passages=[]
            if dict.has_key('passages'):
                passages=dict['passages']
                for passage in passages:
                    if passage['name']==name:
                        rsdic['ret']=Status.NAMEEXISTED
                        break
        elif type=='1':
            machines=[]
            if dict.has_key('machines'):
                machines=dict['machines']
                for machine in machines:
                    if machine['name']==name:
                        rsdic['ret']=Status.NAMEEXISTED
                        break

        elif type=='2':
            levels=[]
            if dict.has_key('level'):
                levels=dict['level']
                for level in levels:
                    if level['name']==name:
                        rsdic['ret']=Status.NAMEEXISTED
                        break

        #列道
        elif type=='3':
            columns=[]
            if dict.has_key('column'):
                columns=dict['column']
                for column in columns:
                    if column['name']==name:
                        rsdic['ret']=Status.NAMEEXISTED
                        break

    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#注册页面选择区县
def get_china_location(request):
    #初始化返回值
    rsdic={}
    ret=Status.OK
    rsdic['ret']=ret
    rsdic['info']=Status().getReason(ret)

    try:
        parent = int(request.POST['parent'])
        level = request.POST['level']
        s = request.get_session()
        citys = s.query(DimChinaProvinceCityDistrict).filter_by(parent=parent,level=level).all()
        dict_city = []
        for city in citys:
            temp = []
            temp.append(city.id)
            temp.append(city.name)
            dict_city.append(temp)
        rsdic['dict_city']=dict_city
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret,error=str(e))
    return HttpResponse(json.dumps(rsdic))

#根据油站名字获取描述信息
def getInfoBySiteName(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    try:
        site=request.POST['site_name']
        s=request.get_session()
        obj=s.query(Station).filter_by(name=site).one()

        #取得省的列表
        provinces = s.query(DimChinaProvinceCityDistrict)\
            .filter_by(level=1).all()

        #取得市的列表
        citys = s.query(DimChinaProvinceCityDistrict)\
            .filter_by(parent=obj.province,level=2).all()

        #取得區的列表
        districts = s.query(DimChinaProvinceCityDistrict)\
            .filter_by(parent=obj.city,level=3).all()

        #將省的信息添加中字典中
        rsdic['provinces']=[]
        for province in provinces:
            rsdic['provinces'].append({
            "id":province.id,"name":province.name})

        #將市的信息添加中字典中
        rsdic['citys']=[]
        for city in citys:
            rsdic['citys'].append({
            "id":city.id,"name":city.name})

        #將區的信息添加中字典中
        rsdic['districts']=[]
        for district in districts:
            rsdic['districts'].append({
            "id":district.id,"name":district.name})

        rsdic['data']=obj.description
        rsdic['province']=obj.province
        rsdic['district']=obj.district
        rsdic['city']=obj.city
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#根据油站名字获取描述信息
def saveStationInfo(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    try:

        #从前端取得站点的信息
        site=request.POST['site_name']
        description=request.POST['description']
        province=request.POST['province']
        city=request.POST['city']
        district=request.POST['district']

        #取得session,并通过站点名称来保存站点的信息
        s=request.get_session()
        obj=s.query(Station).filter_by(name=site).one()
        obj.description=description
        obj.province=province
        obj.city=city
        obj.district=district
        s.commit()

        #站点描述信息的缓存
        station_descriptions_cache_data=read_station_descriptions_from_cache()
        if station_descriptions_cache_data==None:
            station_descriptions_cache_data={}

        #对缓存进行更新
        if station_descriptions_cache_data.has_key(site) :
            station_descriptions_cache_data[site]=description
        write_station_descriptions_in_cache(station_descriptions_cache_data)
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#修改油品编号与系统定义油品类型关系
def editFuelTypeRelation(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))
    try:
        pre_id=request.POST['pre_id']
        next_id=request.POST['next_id']
        next_name=request.POST['next_name']
        next_barcodes=request.POST.getlist('next_barcodes[]')

        #type:0 id和name都有更改,1 name有更改, 2 id有更改 3 新增数据
        type=request.POST['type']
        if type=='3':
            result=checkFuelTypeRelationNameAndId(type,next_id,next_name)

            #id已存在
            if result==0:
                rsdic['type']=0
                return HttpResponse(json.dumps(rsdic))

            #name已存在
            elif result==1:
                rsdic['type']=1
                return HttpResponse(json.dumps(rsdic))

            #插入操作
            s=request.get_session()
            s.execute(FuelTypeRelation.__table__.insert(),[{'id':int(next_id),
                'name':next_name,'barcodes':json.dumps(next_barcodes)}])
            s.commit()

            #已新增
            rsdic['type']=3
        else:
            result=checkFuelTypeRelationNameAndId(type,next_id,next_name)

            #id已存在
            if result==0:
                rsdic['type']=0
                return HttpResponse(json.dumps(rsdic))

            #name已存在
            elif result==1:
                rsdic['type']=1
                return HttpResponse(json.dumps(rsdic))

            #更新操作
            s=request.get_session()
            obj=s.query(FuelTypeRelation).filter_by(id=pre_id).one()
            obj.id=int(next_id)
            obj.name=next_name
            obj.barcodes=json.dumps(next_barcodes)
            s.commit()

            #已更新
            rsdic['type']=2
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#删除一个油品编号与系统定义油品类型关系
def removeFuelTypeRelation(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:
        type_id=int(request.POST['type_id'])
        s=request.get_session()

        #根据id进行删除操作
        obj=s.query(FuelTypeRelation).filter_by(id=type_id).one()
        s.delete(obj)
        s.commit()
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取用户信息
def getUserInfo(request):
    rsdic=checkAjaxRequest(request,'POST')
    if rsdic['ret']!=Status.OK:
        return HttpResponse(json.dumps(rsdic))

    try:

        user_name=request.session['username']
        rsdic['username']=user_name
        s=request.get_session()

        #查找用户信息
        obj=s.query(User).filter_by(name=user_name).one()
        rsdic['type']=obj.type
        rsdic['district']=obj.district


        #根据区域代码获取省市区信息
        obj_district=s.query(DimChinaProvinceCityDistrict).filter_by(id=obj.district).one()
        if obj_district.parent!=0:
            obj_city=s.query(DimChinaProvinceCityDistrict).filter_by(id=obj_district.parent).one()
            rsdic['city']=obj_city.id
            obj_province=s.query(DimChinaProvinceCityDistrict).filter_by(id=obj_city.parent).one()
            rsdic['province']=obj_province.id
        else:
            rsdic['city']=0
            rsdic['province']=0

        #取得省的列表
        provinces = s.query(DimChinaProvinceCityDistrict)\
            .filter_by(level=1).all()

        #取得市的列表
        citys = s.query(DimChinaProvinceCityDistrict)\
            .filter_by(parent=obj_province.id,level=2).all()

        #取得區的列表
        districts = s.query(DimChinaProvinceCityDistrict)\
            .filter_by(parent=obj_city.id,level=3).all()

        #將省的信息添加中字典中
        rsdic['provinces']=[]
        for province in provinces:
            rsdic['provinces'].append({
            "id":province.id,"name":province.name})

        #將市的信息添加中字典中
        rsdic['citys']=[]
        for city in citys:
            rsdic['citys'].append({
            "id":city.id,"name":city.name})

        #將區的信息添加中字典中
        rsdic['districts']=[]
        for district in districts:
            rsdic['districts'].append({
            "id":district.id,"name":district.name})

    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#导出图表数据到xls表格
def exportTableToXls(request):
    rsdic={'message':0}
    categories=json.loads(request.POST['categories'])
    dataset=json.loads(request.POST['dataset'])
    filename=request.POST['title']
    if len(categories) and len(dataset):
        wb = xlwt.Workbook(encoding="utf-8")
        #添加excle表
        ws = wb.add_sheet('Sheet1')
        #从第一行写入数据表标题
        row_title=[]
        row_title.append(request.POST['title'])
        for obj in dataset:
            row_title.append(obj['name'])
        i=0
        for title_value in row_title:
            ws.write(0,i,title_value)
            i=i+1

        #写数据到表
        #从第二行开始按列写数据i=1
        i=1
        dataset_len=len(dataset)
        for key in categories:
            ws.write(i,0,key)
            i=i+1
        i=1
        j=0
        while dataset_len>0:
            for value in dataset[j]['data']:
                ws.write(i,j+1,value)
                i=i+1
            dataset_len=dataset_len-1
            j=j+1
            i=1
        #将数据存储到临时文件temp.xls供用户下载
        wb.save('/tmp/'+ filename + '.xls')
        rsdic={'message':1,'filename':filename}
    return HttpResponse(json.dumps(rsdic))

#下载导出的xls文件
def downloadXlsFile(request):
    #获取文件名
    filename=request.GET['filename']
    #读临时文件的数据
    data =xlrd.open_workbook('/tmp/'+filename)
    table = data.sheets()[0]
    #创建文件数据流
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')
    for row_index in range(table.nrows):
        for col_index in range(table.ncols):
            ws.write(row_index,col_index,table.cell(row_index,col_index).value)
    #定义response格式
    response = HttpResponse(content_type='application/vnd.ms-excel')
    Content_Disposition='attachment; filename='+str(filename)+'.xls'
    response['Content-Disposition'] =Content_Disposition
    wb.save(response)
    return response

#download_xls_file
def download_xls_file(request):
    #get data
    filename=request.GET['filename']
    xls_categories=request.GET['xls_categories']
    xls_dataset=request.GET['xls_dataset']
    obj_xls_categories=json.loads(xls_categories)
    obj_xls_dataset=json.loads(xls_dataset)
    #创建文件数据流
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')
    #write table title
    row_title=[]
    row_title.append('横坐标')
    for obj in obj_xls_dataset:
        row_title.append(obj['name'])
    i=0
    for title_value in row_title:
        ws.write(0,i,title_value)
        i=i+1

    #写数据到表
    #从第二行开始按列写数据i=1
    i=1
    dataset_len=len(obj_xls_dataset)
    for key in obj_xls_categories:
        ws.write(i,0,key)
        i=i+1
    i=1
    j=0
    while dataset_len>0:
        for value in obj_xls_dataset[j]['data']:
            ws.write(i,j+1,value)
            i=i+1
        dataset_len=dataset_len-1
        j=j+1
        i=1
    #定义response格式
    response = HttpResponse(content_type='application/vnd.ms-excel')
    #set filename end with .xls
    Content_Disposition='attachment; filename='+str(filename)+'.xls'
    response['Content-Disposition'] =Content_Disposition
    wb.save(response)
    return response

#新建标签
def addTag(request):
    try:
        rsdic=checkAjaxRequest(request,'POST')
        if rsdic['ret']!=Status.OK:
            return HttpResponse(json.dumps(rsdic))

        s=request.get_session()

        #获取当前用户的id
        user = s.query(User).filter_by(name=request.session['username']).one()
        user_id = user.id

        #标签名字
        tag_name = request.POST['tag_name']

        exists = s.query(Tag).filter_by(user_id=user_id,tag=tag_name).count()

        #判断该标签是否已经存在
        if exists>0:
            ret=Status.NAMEEXISTED
            rsdic['ret']=ret
            rsdic['info']=Status().getReason(ret)
            s.close()
            return HttpResponse(json.dumps(rsdic))
        else:
            tag = Tag(user_id=user_id,tag=tag_name)
            s.add(tag)
            s.commit()
            s.close()
    except Exception,e:
        s.close()
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        ajax_logger.error(str(e))
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取用户创建的所有标签
def getUserTags(request):
    try:
        rsdic=checkAjaxRequest(request,'POST')
        if rsdic['ret']!=Status.OK:
            return HttpResponse(json.dumps(rsdic))

        s=request.get_session()

        #获取当前用户的id
        user = s.query(User).filter_by(name=request.session['username']).one()
        user_id = user.id

        tags = s.query(Tag).filter_by(user_id=user_id).all()

        rsdic['tags']=[]
        for tag in tags:
            rsdic['tags'].append({
            "id":tag.id,"name":tag.tag})
        s.close()
    except Exception,e:
        s.close()
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        ajax_logger.error(str(e))
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#自定义标签关联油站
def removeTag(request):
    try:
        rsdic=checkAjaxRequest(request,'POST')
        if rsdic['ret']!=Status.OK:
            return HttpResponse(json.dumps(rsdic))

        #tag的id
        tag_id = int(request.POST['tag_id'])

        s=request.get_session()

        #查询所有关联该标签的油站，进行删除
        station_tags = s.query(UserStationTagRelation).filter_by(tag_id=tag_id).delete()

        s.commit()

        #删除标签
        tag = s.query(Tag).filter_by(id=tag_id).delete()

        s.commit()

        s.close()

    except Exception,e:
        s.close()
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        ajax_logger.error(str(e))
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#获取用户标签下的关联油站以及可选的油站
def getUserTagSites(request):
    try:
        #关联了该标签的油站
        tags_result = []

        #该标签下已有油站
        has_sites = []
        rsdic=checkAjaxRequest(request,'POST')
        if rsdic['ret']!=Status.OK:
            return HttpResponse(json.dumps(rsdic))

        s=request.get_session()

        #标签id
        tag_id = int(request.POST['tag_id'])

        #获取当前用户的id
        user = s.query(User).filter_by(name=request.session['username']).one()
        user_id = user.id

        tags = s.query(UserStationTagRelation).filter_by(tag_id=tag_id,user_id=user_id).all()

        #该标签下的所有油站
        for tag in tags:
            tmp = {}
            tmp['site'] = tag.station
            tmp['site_desc'] = tag.station_desc
            tags_result.append(tmp)
            has_sites.append(tag.station)
        rsdic['tags'] = tags_result
        rsdic['has_sites'] = has_sites

        s.close()
    except Exception,e:
        s.close()
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        ajax_logger.error(str(e))
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#对某个标签关联油站
def bandSiteForTag(request):
    try:
        rsdic=checkAjaxRequest(request,'POST')
        if rsdic['ret']!=Status.OK:
            return HttpResponse(json.dumps(rsdic))

        #tag的id
        tag_id = int(request.POST['tag_id'])

        s=request.get_session()

        #获取当前用户的id
        user = s.query(User).filter_by(name=request.session['username']).one()
        user_id = user.id

        #关联的油站
        site = request.POST['site']

        #站点描述
        site_desc = request.POST['site_desc']

        relation = UserStationTagRelation(user_id=user_id,tag_id=tag_id,station=site,station_desc=site_desc)
        s.add(relation)
        s.commit()
        s.close()

    except Exception,e:
        s.close()
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        ajax_logger.error(str(e))
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

#取消某标签下的油站
def removeSiteForTag(request):
    try:
        rsdic=checkAjaxRequest(request,'POST')
        if rsdic['ret']!=Status.OK:
            return HttpResponse(json.dumps(rsdic))

        #tag的id
        tag_id = int(request.POST['tag_id'])

        s=request.get_session()

        #获取当前用户的id
        user = s.query(User).filter_by(name=request.session['username']).one()
        user_id = user.id

        #关联的油站
        site = request.POST['site']

        #查询所有关联该标签的油站，进行删除
        station_tags = s.query(UserStationTagRelation).filter_by(tag_id=tag_id,user_id=user_id,station=site).delete()
        s.commit()
        s.close()
    except Exception,e:
        s.close()
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret)
        ajax_logger.error(str(e))
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))
