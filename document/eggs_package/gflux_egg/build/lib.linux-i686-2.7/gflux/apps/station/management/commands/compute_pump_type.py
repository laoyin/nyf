#coding=utf-8
from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.common import models as common_models
from dash.core.backends.sql.models import get_dash_session_maker
from optparse import make_option
import sys, pdb

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):
		# 建立数据会话
		sitename=options['site']
		create_session = get_dash_session_maker(site_name=sitename)	
		session = create_session()
		try :
			objs=session.query(models.Trans).filter_by(site=sitename).all()
			# session.close()
			for obj in objs :
				if obj.pay > 0 and obj.pay % 50 == 0 :
					session = create_session()
					session.query(models.Trans).filter(models.Trans.id == obj.id).update({"pump_type":1})
					session.commit()
					
		except Exception , e:
			session.rollback()
			session.close()
			print e
