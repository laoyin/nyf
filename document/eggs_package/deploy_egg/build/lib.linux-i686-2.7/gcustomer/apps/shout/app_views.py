# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb,json,datetime,logging,hashlib
from django.http import *
from django.conf import settings
from django.shortcuts import render_to_response

from gcustomer.apps.jiachebao.models import *

status_collection={
    '0000':'Not logged in',
    '0001':'Login success',
    '0002':'user does not exist',
    '0003':'password error',
    '0006':'用户已存在',
    '0001':'Everything is OK',
    '1111':'An error has occurred. Please try again!',
}

class Status :
    NOTLOGGEDIN     =   '0000'
    OK              =   '0001'
    LOGINSUCCESS    =   '0001'
    USERNOTEXIST    =   '0002'
    PASSWORDERROR   =   '0003'
    USEREXIST    =   '0006'
    UNKNOWNERR      =   '1111'

    def getReason(self, code,error=None):
        if error==None:
            return status_collection[code]
        else:
            return 'Info:%s,Error:%s'%(
                status_collection[code],
                error
            )

def login(request,username,password):
    result={}
    try:
      user=CustomerAccount.objects.filter(name=username,password=password).get()
      # 更新request session参数
      request.session.set_expiry(0)
      request.session['username'] = username
      sid=request.session.session_key
      if sid is None:
        request.session.save()
        sid=request.session.session_key
      dic = {}
      dic['user_name'] = user.name
      dic['user_sha1'] = user.sha1
      dic['sessionid'] = sid
      dic['avarta_sha1'] = user.avarta_sha1        
      dic['lilei'] = user.nick
      dic['score'] = user.average_score
      dic['career'] = user.career
      result['data'] = dic
      result['ret'] = Status.LOGINSUCCESS
      result['info'] = Status().getReason(result['ret'])
    except Exception,e:
      result['ret'] = Status.USERNOTEXIST
      result['info'] = Status().getReason(result['ret'])
    return result 

def register(request,name,password,nick,career,avarta_sha1):
    result = {}
    user_sha1 = hashlib.sha1()
    user_sha1.update(name+password)
    sha1 = user_sha1.hexdigest()
    user = CustomerAccount(
      name = name,
      sha1 = sha1,
      password = password,
      nick = nick,
      career = career,
      avarta_sha1 = avarta_sha1
    )
    try:
      user.save()
      result['ret'] = Status.OK
      result['info'] = Status().getReason(result['ret'])
      result['data'] = {}
    except Exception,e:
      result['ret'] = Status.USEREXIST
      result['info'] = Status().getReason(result['ret'])
    return result

def anonymous_login(request,imei_code,mac_address,sim_number,device_type):
    result = {}
    result['data'] = {} 
    try : 
      anonymous = WheelDevice.objects.filter(imei_code=imei_code).get()
      result['ret'] = Status.OK
      result['info'] = Status().getReason(result['ret'])
      result['data']['sessionid'] = request.session.session_key
    except Exception,e:
      anonymous_user=WheelDevice(
      		imei_code=imei_code,
      		mac_address=mac_address,
      		sim_number=sim_number,
      		device_type=device_type,
      	)
      try:
      	anonymous_user.save()
      	result['ret'] = Status.OK
      	result['info'] = Status().getReason(result['ret'])
      	result['data']['sessionid'] = request.session.session_key
      except Exception,e:
      	result['ret'] = '1'
      	result['info'] = 'error'
      	result['data']['sessionid'] = request.session.session_key
    return result

def logout(request,session_id):
    result = {}
    result['ret'] = Status.OK
    result['info'] = Status().getReason(result['ret'])
    result["data"] = {}
    return result