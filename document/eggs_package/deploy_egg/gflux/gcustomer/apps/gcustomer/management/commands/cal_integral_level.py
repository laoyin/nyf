#coding=utf-8
from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from gcustomer.models import *
from gcustomer.apps.jiachebao.models import *
import sys, pdb
from django.conf import settings

class Command(BaseCommand):
    help = '计算会员等级'

    def handle(self, *args, **options):
    	session = get_dash_session_maker()()
    	try :	
    		#获取等级规则
		rule =  settings.INTEGRAL_OPTION[settings.USE_OPTION]
		#更新等级
		if settings.USE_OPTION == '0000' :
			try :
		    		score_rules = rule.USER_INTEGRAL_LEVEL
		    		#更新用户等级
		    		users = session.query(CustomerAccount).all()
		    		for user in users:
		    			all_score = user.all_score
		    			if all_score == 0 :
						user.score = 0
						user.score_rank = 0
						continue
		    			for score_rule in score_rules :
		    				if all_score <= score_rule['level_rule'][1] and all_score >= score_rule['level_rule'][0] :
		    					user.score_rank = score_rule['level_type']
		    					break
		    				else :
		    					continue
				session.commit()	
		    	except Exception,e:
		    		session.rollback()
		    		print e 
		    		print "更新用户等级失败"
			print "更新用户等级成功"
		elif settings.USE_OPTION == "0001" :
		 	try :
		 		#获取规则数据
		 		gasoline_ratio = rule.USER_INTEGRAL_LEVEL["rule"][rule.GASOLINE]
		 		diesel_ratio = rule.USER_INTEGRAL_LEVEL["rule"][rule.DIESEL]
		    		#更新用户等级
		    		users = CustomerAccount.objects.all()
		    		for user in users:
		    			if user.cardnum :
		    				try :
							customer = session.query(CustomerProfile).filter_by(cardnum = int(user.cardnum)).one()
						except Exception,e:
							continue
						ratio = customer.total_fuel_amount_1 +  customer.total_fuel_amount_2/(diesel_ratio/gasoline_ratio)
						if ratio >= (gasoline_ratio*2) :
							user.score_rank = rule.GOLD_MEMBER
							user.save()
						else :
							user.score_rank = rule.ORDINARY_MEMBER
							user.save()
					else :
						user.score_rank = rule.NON_MEMBER
						user.save()
			except Exception,e :
				print e
				print "更新会员等级失败"
    	except Exception,e:
    		print e 
