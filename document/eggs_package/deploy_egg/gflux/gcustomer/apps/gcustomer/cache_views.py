#coding=utf-8
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
from django.shortcuts import render_to_response
from gcustomer.models import *
from gcustomer.apps.jiachebao.models import *
from gflux.apps.station.models import FuelTypeRelation
from gflux.apps.common.models import Station
from gflux.util import *
import re, time, hashlib
from gcustomer.utils import *
from gcustomer.status  import *
#单个缓存个数
CACHE_COUNT = 2

CACHE_MAP = {
	"target_audience" : TargetAudience
}

#存入缓存
#输入:  缓存数据键值
#输出:  缓存数据
def download_in_cache(request,**options):
	rsdic = {}
	rsdic['ret'] = Status.OK
	rsdic['info'] = Status().getReason(rsdic['ret'])
	user = get_current_user(request)
	comp_id = user.comp_id
	#cache_key缓存键值
	if request.GET.has_key("cache_key") :
		cache_key = CACHE_MAP[request.GET['cache_key']]
		cache_key_string = str(cache_key).split("\'")[1]
		if cache.has_key(cache_key_string) :
			return HttpResponse(json.dumps(rsdic))
		session = request.get_session()
		try :
			objs = session.query(cache_key).filter_by(comp_id=comp_id).order_by('id').all()
		except Exception,e:
			ajax_logger.error(str(e))
			rsdic['ret'] = Status.UNKNOWNERR
			rsdic['info'] = "缓存客户群失败"
			return HttpResponse(json.dumps(rsdic))
		cache_level = len(objs) / CACHE_COUNT
		cache.set(cache_key_string,len(objs))
		if cache_level > 0 :
			for i in range(1,cache_level+2) :
			    cache.set(cache_key_string+str(i),objs[(i-1)*CACHE_COUNT:i*CACHE_COUNT])
		else:
			cache.set(cache_key_string+str(1),objs)
		return HttpResponse(rsdic)
	elif options.has_key("cache_key") :
		cache_key = options['cache_key']
		cache_key_string  = str(cache_key).split("\'")[1]
		session = request.get_session()
		try :
			objs = session.query(cache_key).filter_by(comp_id=comp_id).all()
		except Exception,e:
			ajax_logger.error(str(e))
			rsdic['ret'] = Status.UNKNOWNERR
			rsdic['info'] = Status().getReason(rsdic['ret'])
		cache_level = len(objs) / CACHE_COUNT
		cache.set(cache_key_string,len(objs))
		if cache_level > 0 :
			for i in range(1,cache_level+2) :
			    cache.set(cache_key_string+str(i),objs[(i-1)*CACHE_COUNT:i*CACHE_COUNT])
		else:
			cache.set(cache_key_string+str(1),objs)
		return objs

#获取指定缓存
#输入:  缓存数据键值
#输出:  指定缓存数据
def get_from_cache(request,cache_key) :
	cache_key_string  = str(cache_key).split("\'")[1]
	if cache.has_key(cache_key_string) :
		count = 1
		objs = []
		while not cache.get(cache_key_string+str(count)) == None :
			objs.extend(cache.get(cache_key_string+str(count)))
			count = count +1
		return objs
	else :
		return download_in_cache(request,cache_key=cache_key)

#更新缓存 status 0:删除cache_value 1:添加cache_value
#输入:   缓存数据键值,更新类型
#输出:  	无
def update_in_cache(request,cache_key,cache_value,status):
	cache_key_string  = str(cache_key).split("\'")[1]
	if cache.has_key(cache_key_string) :
		#更新缓存 status 0:删除cache_value 1:添加
		if status == 1:
			objs = get_from_cache(request,cache_key)
			objs.append(cache_value)
			delete_from_cache(request,cache_key)
			#更新
			cache_level = len(objs) / CACHE_COUNT
			cache.set(cache_key_string,len(objs))
			if cache_level > 0 :
				for i in range(1,cache_level+2) :
				    cache.set(cache_key_string+str(i),objs[(i-1)*CACHE_COUNT:i*CACHE_COUNT])
			else:
				cache.set(cache_key_string+str(1),objs)
		elif status == 0 :
			objs = get_from_cache(request,cache_key)
			temp_objs = []
			for obj in objs :
				if not obj.id == cache_value.id :
					temp_objs.append(obj)
			objs = temp_objs
			#更新
			cache_level = len(objs) / CACHE_COUNT
			cache.set(cache_key_string,len(objs))
			if cache_level > 0 :
				for i in range(1,cache_level+2) :
				    cache.set(cache_key_string+str(i),objs[(i-1)*CACHE_COUNT:i*CACHE_COUNT])
			else:
				cache.set(cache_key_string+str(1),objs)

	else :
		download_in_cache(request,cache_key=cache_key)


#删除指定缓存
#输入:  缓存数据键值
#输出:  无
def delete_from_cache(request,cache_key):
	cache_key_string  = str(cache_key).split("\'")[1]
	if cache.has_key(cache_key_string) :
		len = cache.get(cache_key_string)
		cache.delete(cache_key_string)
	for i in range(1,len+1) :
		cache.delete(cache_key_string+str(i))

#清空缓存
#输入:  无
#输出:  无
def clear_cache():
	cache.clear()


