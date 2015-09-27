#coding=utf-8
from django.core.management.base import BaseCommand
from django.conf import settings
from gcustomer.models import *
from gcustomer.apps.jiachebao import *
from dash.core.backends.sql.models import *
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm import sessionmaker
from datetime import *
import sys, pdb
from gcustomer.utils import *


class Command(BaseCommand):
    help = 'calculate promotion info status'

    def handle(self, *args, **options):
    	session = get_dash_session_maker()()
    	promotion_info_list = session.query(PromotionInfo).all()
    	for promotion_info in promotion_info_list :
    		try :
    			promotion = session.query(Promotion).filter_by(id = promotion_info.promotion_id).one()
    		except Exception,e:
    			continue
    		if promotion.status == 0 :
    			promotion_info.status = 0 
    		else :
    			promotion_info.status = 1
    	try :
    		session.commit()
    	except Exception,e:
    		session.rollback()
