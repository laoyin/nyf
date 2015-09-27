# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb  ,json,datetime,logging
from django.http import *
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.core.management import call_command
from django.core.cache import cache
from django.utils import timezone
from gcustomer.models import *
from gflux.util import *
import re
from django.core.mail import send_mail
from django.conf import settings
from gcustomer.status  import * 
from gcustomer.utils import *
ajax_logger=logging.getLogger('ajax')


#check login
def check_login(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    try:
        #取得参数
        username = request.POST['username']
        password = request.POST['password']
        language = int(request.POST['language'])
        data = login(request,username,password,language)
        if data['ret'] == Status.OK :
            if data['type'] < 1 :
                ret=Status.UNKNOWNERR
                rsdic['ret']=ret
                rsdic['info']='等待管理员审核!'
                return HttpResponse(json.dumps(rsdic))
            # 更新request session参数
            request.session.set_expiry(0)
            request.session['username'] = username
            sid=request.session.session_key
            if sid is None:
                request.session.save()
                sid=request.session.session_key
            rsdic['info'] = "ok"
        elif data['ret'] == Status.PASSWORDERROR :
            rsdic['ret'] = data['ret']
            rsdic['info'] = Status().getReason(rsdic['ret'])
            return HttpResponse(json.dumps(rsdic))
        else:
            rsdic['ret'] = data['ret']
            rsdic['info'] = "用户名不存在!"
    except Exception,e:
        ret=Status.UNKNOWNERR
        rsdic['ret']=ret
        rsdic['info']=Status().getReason(ret,error=str(e))
    finally:
        return HttpResponse(json.dumps(rsdic))

#登录
def login(request,username,password,language):
    result = {}
    #获取md5字符串
    password = md5_data(password)
    try:
        session = request.get_session()
        user=session.query(GCustomerUser).filter_by(name=username).one()
        if not user.password == password :
            result['ret'] = Status.PASSWORDERROR
            return result
        #设置语言
        if language == 0 :
            request.session['django_language'] = 'en'
        else :
            request.session['django_language'] = 'zh-cn'
        result['ret'] = Status.OK
        result['sessionid'] = request.session.session_key
        user_comp_memship = session.query(GCompanyMembership).filter_by(user_id =user.id).one()
        if user.type == 3 :
            result['type'] = user_comp_memship.role
        else :
            result['type'] = user.type
    except Exception, e:
        print e
        result['ret'] = Status.UNKNOWNERR
        result['info'] = Status().getReason(result['ret'])
        return result
    return result

#注册
def register(request,register_type,comp_id,username,password,email,comp_name,comp_type,district):
    result = {}
    # 检查用户传入的参数的合法性
    if re.match(r'^[a-zA-Z0-9]{3,16}$',username) == None:
        result['ret'] = Status.REGISTER_ERROR
        result['info'] = '用户名格式出错!'
        return result

    if len(password)<6 or len(password)>16 :
        result['ret'] = Status.REGISTER_ERROR
        result['info'] = '请输入6至16为密码!'
        return result

    session = request.get_session()
    #注册公司信息
    if register_type == "0" :
        try :
            company = session.query(GCompany).filter_by(id=int(comp_id)).one()
        except Exception,e:
            ajax_logger.error(str(e))
            result['ret'] = Status.QUERY_COMP_INFO_ERROR
            result['info'] = Status().getReason(result['ret'])
            return result
        comp_id = int(comp_id)
    else :
            try :
                company = session.query(GCompany).filter_by(user_source=comp_type,name=comp_name).one()
                comp_id = company.id
            except :
                #计算公司sha1
                import hashlib
                sha1=hashlib.sha1()
                sha1.update(str(comp_type)+str(comp_name))
                sha1=sha1.hexdigest()
                company = GCompany(
                        user_source = int(comp_type),
                        name = comp_name,
                        sha1 = sha1
                    )
                session.add(company)
                try :
                    session.commit()
                    comp_id = company.id
                except Exception,e :
                    ajax_logger.error(str(e))
                    session.rollback()
                    result['ret'] = Status.REGISTER_COMPANY_ERROR
                    result['info'] = Status().getReason(result['ret'])
                    return result
    #检查用户名和邮箱
    user = session.query(GCustomerUser).filter_by(name = username).first()
    if user :
        result['ret'] = Status.REGISTER_ERROR
        result['info'] = '用户名已注册!'
        return result 
    user = session.query(GCustomerUser).filter_by(email = email).first()
    if user :
        result['ret'] = Status.REGISTER_ERROR
        result['info'] = '邮箱已注册过了!'
        return result 
    #注册用户
    if not comp_id == 0 :
        uesr_type = 3
    else :
        user_type = 4
    #md5加密
    password = md5_data(password)
    user = GCustomerUser(
        comp_id = comp_id,
        name=username,
        password=password,
        email=email,
        type=uesr_type,
        district=district
        )
    session.add(user)
    try :
        session.commit()
        user = session.query(GCustomerUser).filter_by(comp_id = comp_id,name = username).one()
        company_membership = GCompanyMembership(
            comp_id = comp_id , 
            user_id = user.id ,
            role = 0
        )
        session.add(company_membership)
        session.commit()
    except Exception,e:
        session.rollback()
        ajax_logger.error(str(e))
        result['ret'] = Status.REGISTER_ERROR
        result['info'] = Status().getReason(result['ret'])
        return result
    result['ret'] = Status.OK
    result['info'] = '创建成功,等待管理员审核!'
    result['sessionid'] = request.session.session_key
    result['user'] = user
    return result

#注册验证
def check_register(request):
    rsdic={}
    rsdic['ret'] = Status.OK
    register_type = request.POST['register_type']
    comp_id = request.POST['comp_id']
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    company = request.POST['company']
    comp_type = request.POST['comp_type']
    district = request.POST['district']
    data = register(request,register_type,comp_id,username,password,email,company,comp_type,district)
    rsdic['ret'] = data['ret']
    rsdic['info'] = data['info']
    emailContext = u"""
                        register success
                        now login : http://wheel.marketcloud.com.cn:8000/gcustomer
    """
    try:
        if rsdic['ret'] == Status.OK :
            send_mail(u'register',emailContext,settings.EMAIL_HOST_USER,[email],fail_silently = False)
    except Exception,e:
        ajax_logger.error(str(e))
        print e
    finally:
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

#get_china_location
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

#获取系统用户
def get_system_user_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])    
    rsdic['users'] = []
    try :
        session = request.get_session()
        #comp_id 为0 默认为系统用户
        system_user_list = session.query(GCustomerUser).filter_by(comp_id=0).all()
        for user in system_user_list :
            rsdic['users'].append(dict(
                    id = user.id,   
                    name = user.name ,
                    type = user.type ,
                    time = str(user.time),
                    comp_id = user.comp_id
                ))
    except Exception,e:
        rsdic['ret'] = Status.OK
        rsdic['info'] = Status().getReason(rsdic['ret'])    
        return HttpResponse(json.dumps(rsdic),mimetype = "application/json")
    return HttpResponse(json.dumps(rsdic),mimetype = "application/json")

#获取石油公司用户列表
def get_all_comp_user_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    rsdic['users'] = []
    user = get_current_user(request)
    user_type = user.type 
    comp_id = user.comp_id
    try :
        session = request.get_session()
        #comp_id 3 : 石油公司用户
        if user_type == 4:
            comp_user_list = session.query(GCustomerUser).filter_by(type = 3).all()
        else : 
            comp_user_list = session.query(GCustomerUser).filter_by(comp_id = comp_id,type = 3).all()
        for user in comp_user_list :
            try :
                comp_mem_ship  = session.query(GCompanyMembership).filter_by(user_id = user.id).one()
            except Exception,e:
                rsdic['ret'] = Status.QUERY_USER_COMP_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                rsdic['users'] = []
                return HttpResponse(json.dumps(rsdic),mimetype = "application/json")
            user_role = comp_mem_ship.role
            comp_id = user.comp_id
            try :
                company_name = session.query(GCompany).filter_by(id = comp_id).one().name
            except :
                company_name = ""
            rsdic['users'].append(dict(
                    id = user.id,   
                    name = user.name ,
                    type = user_role ,
                    time = str(user.time),
                    company_name = company_name
                ))
    except Exception,e:
        rsdic['ret'] = Status.OK
        rsdic['info'] = Status().getReason(rsdic['ret'])    
        return HttpResponse(json.dumps(rsdic),mimetype = "application/json")
    return HttpResponse(json.dumps(rsdic),mimetype = "application/json")

#获取app用户列表
def get_app_user_list(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['users'] = {}
    try:
        #get obj
        session=request.get_session()
        current_user = get_current_user(request)
        comp_id = current_user.comp_id
        user_objects = session.query(GasWorker).all()
        all_user_list = []
        for user in user_objects:
            if current_user.name == 'tao' :
                try : 
                    station = session.query(Station).filter_by(sha1 = user.station_sha1).one()
                    site_name = station.name
                    gas_comp_id = station.comp_id
                    try :
                            company_name = session.query(GCompany).filter_by(id = gas_comp_id).one().name
                    except :
                        company_name = ""
                except Exception,e:
                    continue
            else :
                try : 
                    station = session.query(Station).filter_by(sha1 = user.station_sha1).one()
                    site_name = station.name
                    gas_comp_id = station.comp_id
                    if not gas_comp_id == comp_id :
                        continue
                    try :
                            company_name = session.query(GCompany).filter_by(id = gas_comp_id).one().name
                    except :
                        company_name = ""
                except Exception,e:
                    continue
            dic = {}
            dic['id'] = user.id
            dic['name'] = user.name
            dic['sim_number'] = user.sim_number
            dic['site_name'] = site_name
            dic['password'] = user.password
            dic['device_type'] = user.device_type
            dic['time'] = str(user.time)
            dic['gender'] = user.gender
            dic['user_type'] = user.user_type
            dic['company_name'] = company_name
            all_user_list.append(dic)
        rsdic['users'] = all_user_list
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic),mimetype = "application/json")
    finally:
        return HttpResponse(json.dumps(rsdic),mimetype = "application/json")

#改变用户类型
def change_user_type(request):
    rsdic = {}
    rsdic['ret']=Status.OK
    try:
        # get params
        user_id = request.POST['user_id']
        type = request.POST['type']
        #get obj
        session=request.get_session()
        try :
            user_object = session.query(GCustomerUser).filter_by(id=user_id).one()
        except Exception,e:
            rsdic['ret'] = Status.QUERY_USER_ERROR
            rsdic['info'] = Status().getReason(rsdic['ret'])
            return HttpResponse(json.dumps(rsdic),mimetype = "application/json")
        #修改石油公司用户类型
        if user_object.type == 3 :
            try :
                user_mem_ship = session.query(GCompanyMembership).filter_by(user_id = user_object.id).one()
            except Exception,e:
                rsdic['ret'] = Status.QUERY_USER_COMP_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic),mimetype = "application/json")
            try :
                user_mem_ship.role = int(type)
                session.commit()
            except Exception,e:
                rsdic['ret'] = Status.ALERT_USER_ROLE_ERROR
                rsdic['info'] = Status().getReason(rsdic['ret'])
                return HttpResponse(json.dumps(rsdic),mimetype = "application/json")
        else :
            user_object.type = int(type)
            session.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype = "application/json")

#修改app用户类型
def change_app_user_type(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    try:
        user_id = request.POST['user_id']
        type = request.POST['type']
        s=request.get_session()
        user_object=s.query(GasWorker).filter_by(id=user_id).one()
        user_object.user_type = type
        s.commit()
    except Exception,e:
        ajax_logger.error(str(e))
        rsdic['ret'] = Status.UNKNOWNERR
        rsdic['info'] = Status().getReason(rsdic['ret'])

    finally:
        return HttpResponse(json.dumps(rsdic),mimetype = "application/json")

#修改密码
def alter_user_password(request):
    rsdic = {}
    rsdic['ret'] = Status.OK
    rsdic['info'] = Status().getReason(rsdic['ret'])
    session = request.get_session()
    password = request.GET['password']
    new_password = request.GET['new_password']
    re_new_password = request.GET['re_new_password']
    #获取md5字符串
    password = md5_data(password)
    new_password = md5_data(new_password)
    re_new_password = md5_data(re_new_password)
    #验证用户密码
    user = get_current_user(request)
    user_password = user.password
    if not user_password == password :
        rsdic['ret'] = Status.PRE_PASSWORD_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    if not new_password == re_new_password :
        rsdic['ret'] = Status.PASSWORDINCONSISTENT
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    user.password = new_password
    try :
        session.commit()
    except Exception,e:
        rsdic['ret'] = Status.ALTER_USER_ERROR
        rsdic['info'] = Status().getReason(rsdic['ret'])
        return HttpResponse(json.dumps(rsdic))
    return HttpResponse(json.dumps(rsdic))

