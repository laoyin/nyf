# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

from django.utils import timezone
from django.conf import settings
from django.core.cache import cache

import pdb,json,datetime,time,traceback,StringIO,decimal

status_collection={
    '0000':'Not logged in',
    '0001':'Login success',
    '0002':'user does not exist',
    '0003':'password error',
    '0004':'Cookie is expired',
    '0005':'Request method error',
    '0006':'Name has Existed',
    '0007':'Logined on other side',
    '1101':'Everything is OK',
    '1111':'An error has occurred. Please try again!',
}

class Status :
    NOTLOGGEDIN     =   '0000'
    LOGINSUCCESS    =   '0001'
    USERNOTEXIST    =   '0002'
    PASSWORDERROR   =   '0003'
    COOKIREEXPIRED  =   '0004'
    REQMETHODERROR  =   '0005'
    NAMEEXISTED     =   '0006'
    OK              =   '1101'
    UNKNOWNERR      =   '1111'
    LOGINED_ON_OTHER_SIDE =   '0007'

    def getReason(self, code,error=None):
        if error==None:
            return status_collection[code]
        else:
            return 'Info:%s,Error:%s'%(
                status_collection[code],
                error
            )

def json_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return ISOFormat(obj)
    elif isinstance(obj,decimal.Decimal):
        return int(obj)
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

#YYYY-MM-DD HH:MM:SS+HH:MM
def DatetimeISOFormat(datetime_obj):
    if datetime_obj==None:
        return '1970-01-01 00:00:00+00:00'
    elif not isinstance(datetime_obj,datetime.datetime):
        return '1970-01-01 00:00:00+00:00'

    elif datetime_obj.tzinfo is None:
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S+00:00")
    else:
        string=datetime_obj.strftime("%Y-%m-%d %H:%M:%S%z")
        return string[:-2]+':'+string[-2:]

def NowTime():
    return DatetimeISOFormat(timezone.now())


#打印异常堆栈
def exception_stuck():
    vf = StringIO.StringIO()
    traceback.print_exc(file=vf)
    return '\n%s\n'%vf.getvalue()

#检查用户是否登录
def checkUserOnlineStatus(request,username=None):
    if username==None:
        username=request.session.get('username',None)

    #username check
    if username!=None:

        #session check
        connected_session_id=cache.get('%s_sessionid'%username)
        sid=request.session.session_key

        #如果没有打开用户登陆保护
        if not settings.OPEN_USER_LOGIN_PROTECT:
            connected_session_id=sid

        if sid is None:
            request.session.save()
            sid=request.session.session_key

        #已经离线或未登陆
        if connected_session_id==None or sid==None:
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
    
