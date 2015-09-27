# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
import logging,pdb
from django.conf import settings
import django_gearman_commands
from gcustomer.utils import get_none_fuel_last_10,get_none_fuel_top_10
from gcustomer.models import *
from gflux.apps.station.models import *
from dash.core.backends.sql.models import get_dash_session_maker
import json,pdb

class Command(BaseCommand):
    help = '从目前交易的数据导入商品的数据'
    
    def handle(self,  *args, **options):
    	session = get_dash_session_maker()()
    	goods = session.query(Trans).filter_by(trans_type = 1).all()
    	store_good_list = []
    	temp_good_list = []
    	for good in goods :
    		if not good.barcode in temp_good_list :
    			store_good_list.append(dict(
					pos_id = good.barcode,
					name = good.desc,
					price = good.price
    				))
    			temp_good_list.append(good.barcode)

    	#写入到文件
    	f = open("/home/work/store_items.txt","w")
    	count = 0
    	for good in store_good_list :
    		f.write(str(good['pos_id']) + ":"+str(good['name']))
    		f.write('\n')
    		print str(good['pos_id']) + ":"+str(good['name'])
    		count = count + 1
        f.write(str(count))
        f.close()
    	print "total:" + str(count)
    	
    	#更新到后台商品管理
    	for good in store_good_list :
    		try :
	    		objs = session.query(StoreItem).filter_by(pos_id = str(good['pos_id'])).all()
	    		if len(objs) > 0 :
	    			print objs[0].name + "在系统中."
	    		else :
	    			good = StoreItem(
					           pos_id = good['pos_id'],
				                        name = good['name'],
				                        price = good['price'],
				                        user_source=1,
				                        source_id = 3,
				                        img_sha1 ="9329cec35570efd186bb60df1d905b31eec66463"
	    				)
	    			session.add(good)
	    	except Exception , e:
	    		pass
	try:
		session.commit()
	except Exception,e:
		session.rollback()
		print e
		return 

