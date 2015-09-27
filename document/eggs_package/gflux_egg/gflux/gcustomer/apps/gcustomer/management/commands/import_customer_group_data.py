#coding=utf-8
from sqlalchemy.sql import insert,select
from gcustomer import models
from gcustomer.models import *
from django.core.management.base import BaseCommand
import sys,pdb,json,datetime,os
from xml.dom import minidom
from gcustomer.models import CustomerGroup,CustomerProfile
from dash.core.backends.sql.models import get_dash_session_maker
from gcustomer.utils import *



class Command(BaseCommand):
	help = "import  customer group data."
	def handle(self,*args,**options):
		path = os.getcwd()+'/gcustomer/apps/gcustomer/management/commands/'
		try:
			fp = open(path+'test.txt','r')
			content = fp.read()
			xmldoc = minidom.parseString(content)
			root = xmldoc.documentElement
			groups_list = analyze_node(root,"groups")
			users_list = analyze_node(root,"users")
			fp.close()
			group_list = []
			user_list = []
			favourite_products = []
			groups = analyze_node(groups_list[0],'group')
			#用户画像数据
			customers = analyze_node(users_list[0],'user')																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																									
			for group in groups:
				group_id = group.getAttribute('id')
				users = analyze_node(analyze_node(group,"users")[0],"user")
				items = analyze_node(analyze_node(group,"items")[0],"item")
				for user in users:
					user_list.append(user.childNodes[0].data)
				for item in items:
					favourite_products.append(item.getAttribute('id'))
				create_session = get_dash_session_maker()
				session = create_session()
				customerGroup = CustomerGroup(
						id = group_id,
						#系统自动创建
						user_source=1,
            					source_id=3,
            					group_name = group_id,
            					user_list = json.dumps(user_list),
            					favourite_products = json.dumps(favourite_products)
					) 
				try:
					session.add(customerGroup)
					session.commit()
					user_list = []
					favourite_products = []
				except Exception,e:
					session.rollback()
			fav_items = []
			recommend_items = []
			grouped = []
			for user in customers :
				user_id = user.getAttribute('id')
				cardnum = user.getAttribute('card')
				favItems = analyze_node(analyze_node(user,"fav-items")[0],"item")
				recommendItems = analyze_node(analyze_node(user,"recommend-items")[0],"item")
				groupeds = analyze_node(analyze_node(user,"groups")[0],"group")
				for item in favItems :
					fav_items.append(item.getAttribute('id'))
				for item in recommendItems :
					recommend_items.append(item.getAttribute('id'))
				for group in groupeds :
					grouped.append(group.childNodes[0].data)
				create_session = get_dash_session_maker()
				session = create_session()
				customer_profile = CustomerProfile(
						id = user_id,
						user_source = 1,
						user_name = '',
						cardnum = cardnum,	
						favourite_nonfuel_products = json.dumps(fav_items),
						recommended_nonfuel_products = json.dumps(recommend_items)	,
						grouped = json.dumps(grouped)		
					)
				try :
					session.add(customer_profile)
					session.commit()
				except Exception,e:
					session.rollback()

		except  Exception,e:
			print e 
			return None

def analyze_node(parentNode,childNodeString):
	childNodes = []
	for node in parentNode.childNodes:
		if node.nodeType == 1 and node.nodeName == childNodeString:
			childNodes.append(node)
	return childNodes

