#coding=utf-8
import django_gearman_commands,json
from gcustomer.message_server.service.message_client import *
from dash.core.backends.sql.models import get_dash_session_maker
from gcustomer.models import *
from gcustomer.apps.jiachebao.models import * 
class Command(django_gearman_commands.GearmanWorkerBaseCommand):
   """Gearman worker performing 'associate user to group' job."""

   @property
   def task_name(self):
   	return 'associate_user_to_group'

   #job_data : {"comp_id":"1","vcard_id":"15996458299"}
   def do_job(self, job_data):
   	params = json.loads(job_data)
   	comp_id = params['comp_id']
   	vcard_id = params['vcard_id']
   	#获取公司的用户群
   	session = get_dash_session_maker()()
   	group_list = session.query(TargetAudience).filter_by(comp_id=comp_id).all()
   	for group in group_list :
   		try :
   			group_user_list = json.loads(group.user_list)
   		except Exception ,e:
   			continue
   		if not vcard_id in group_user_list :
   			if check_user_associate_group(session,vcard_id,group) :
   				group_user_list.append(vcard_id)
   				group.user_list = json.dumps(group_user_list)
   				try :
   					session.commit()
   				except Exception,e:
   					continue
   			else :
   				continue
   		else :
   			continue


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
	return True

