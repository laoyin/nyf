#coding=utf-8
from gcustomer.models import * 
from gcustomer.apps.jiachebao.models import *
import json,pdb
from django.http import * 
import logging
from gcustomer.status  import * 
ajax_logger=logging.getLogger('ajax')

#获取副卡信息列表
#输入: 主卡号 , 起始索引,结束索引
#输出:  副卡信息列表
def get_slave_card(request):
	result = {}
	result["Result"] = "OK" 
	result["Records"] = []
	main_cardnum = int(request.GET['main_cardnum'])
	jtStartIndex = int(request.GET['jtStartIndex'])
	jtPageSize = int(request.GET['jtPageSize'])
	# sortString , sortType = tuple (jtSorting.split(" "))
	s = request.get_session()
	try :
		cards = s.query(CustomerRelation).filter_by(master_cardnum = main_cardnum).all()
		i = 0 
		for card in cards :
			i = i + 1
			try :
				obj = s.query(CustomerProfile).filter_by(cardnum = card.slave_cardnum).one()
			except Exception,e:
				continue
			result['Records'].append(dict(
					id = i ,
					cardnum = str(obj.cardnum),
					user_name = obj.user_name,
					car_num = str(obj.car_num),
					curr_balance = obj.curr_balance,
					main_cardnum = str(obj.main_cardnum)
				))
		result['Records'] = result['Records'][jtStartIndex:jtStartIndex+jtPageSize]
	except Exception,e:
		print e 
		ajax_logger.error(str(e))
		result["Result"] = "OK"
		result['Record'] = []
	if not result['Records'] :
		result["Result"] = "OK"
		result['Record'] = []
		return HttpResponse(json.dumps(result))
	return HttpResponse(json.dumps(result))

#添加副卡信息
#输入: 主卡号 , 副卡参数
#输出:  副卡信息
def create_slave_card(request):
	result = {}
	result["Result"] = "OK" 
	result["Record"] = []
	main_cardnum = int(request.GET['main_cardnum'])
	s = request.get_session()
	try :
		big_customer = s.query(BigCustomerProfile).filter_by(master_cardnum = main_cardnum).one()
		s.add_all([ 
			CustomerProfile(
				user_source = big_customer.user_source,
				main_cardnum = big_customer.master_cardnum,
				#副卡号应该是系统已有的 
				cardnum = request.POST['cardnum'],
				car_num = request.POST['car_num'],
				user_name = request.POST['user_name'],
				curr_balance = request.POST['curr_balance']
			),
			CustomerRelation(
				user_source = big_customer.user_source,
				master_cardnum = big_customer.master_cardnum,
				slave_cardnum = request.POST['cardnum']
			)
			 ])
		s.commit()
	except Exception,e:
		s.rollback()
		ajax_logger.error(str(e))
		result['Result'] = 'ERROR'
		result['Record'] = "大客户不存在"
		return HttpResponse(json.dumps(result))
	i = len(s.query(CustomerRelation).filter_by(master_cardnum = main_cardnum).all())
	result['Record'].append(dict(
			id = i,
			cardnum = str(request.POST['cardnum']),
			name = request.POST['user_name'],
			car_num = str(request.POST['car_num']),
			curr_balance = request.POST['curr_balance']
		))
	return HttpResponse(json.dumps(result))

#修改副卡信息
#输入:  副卡号
#输出: 副卡信息
def update_slave_card(request):
	result = {}
	result["Result"] = "OK"
	# filter 
	cardnum = request.POST['cardnum']
	if cardnum :
		try :
			data = {}
			for key in request.POST.keys():
				data[key]  = request.POST[key]
			session = request.get_session()
			obj = session.query(CustomerProfile).filter_by(cardnum = cardnum).update(data)
			session.commit()
		except Exception,e:
			print e 
			ajax_logger.error(str(e))
			result["Result"] = "ERROR"
			result["Message"] = "database has no this record"
	else :
		result["Result"] = "ERROR"
		result["Message"] = "database has no this record"
	return HttpResponse(json.dumps(result))

#删除副卡
#输入:  主卡卡号
#输出:  删除状态
def delete_slave_card(request):
	result = {}
	result["Result"] = "OK"
	main_cardnum = request.GET['main_cardnum']
	cardnum = request.POST['cardnum']
	session = request.get_session()
	try :
		slave_card = session.query(CustomerRelation).filter_by(master_cardnum = main_cardnum,slave_cardnum = cardnum).first()
	except Exception,e:
		ajax_logger.error(str(e))
		result['Result'] = "ERROR"
		result['Message'] = "副卡信息不存在"
	if slave_card :
		session.delete(slave_card)
		session.query(CustomerProfile).filter_by(cardnum = cardnum).delete()
		session.commit()
	return HttpResponse(json.dumps(result))
