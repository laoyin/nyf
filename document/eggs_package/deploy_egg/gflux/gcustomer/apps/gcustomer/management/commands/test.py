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
from gcustomer.apps.jiachebao.models import *
from dash.core.backends.sql.models import get_dash_session_maker


class Command(BaseCommand):
    help = 'compute_all_loss_customer'
    
    def handle(self,  *args, **options):
    	add_gcustomer__manage_group()
 
#初始化添加gcustomer用户组
def add_gcustomer__manage_group():
	session = get_dash_session_maker()()
	user_source = 1
	name = '北京中石油股份有限公司'
	group = GCompany(
			user_source = user_source,
			name = name,
		)
	session.add(group)
	try :
		session.commit()
	except Exception,e:
		session.rollback()
		print e 
		return 
	comp_id = session.query(GCompany).filter_by(user_source=user_source,name=name).one().id
	customer_list = session.query(GCustomerUser).all()
	for customer in customer_list :
		customer.comp_id = comp_id
		gcustomer_member_ship = GCompanyMembership(
				comp_id = comp_id,
				user_id = customer.id,
			)
		session.add(gcustomer_member_ship)
	try :
		session.commit()
	except Exception,e:
		session.rollback()
		print e
		return 
