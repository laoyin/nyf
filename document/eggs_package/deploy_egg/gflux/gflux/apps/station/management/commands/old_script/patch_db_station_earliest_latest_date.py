# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import *
from gflux.apps.common.models import *
import pdb

class Command(BaseCommand):
    def handle(self,  *args, **options):
        create_session = get_dash_session_maker()
    	s = create_session()

        #by site
        all_station=s.query(Station).all()

        all_counter=0
        for station in all_station:
            tmp_sm=get_dash_session_maker(site_name=station.name)
            ss=tmp_sm()
            site=station.name

            latest_time,earliest_time=ss.execute(
                'select max(timestamp),min(timestamp) from \
                fact_trans where site=:site;',{'site':site}).first()
            ss.close()

            #没数据
            if latest_time is None:
                continue

            #update
            station.earliest_date=earliest_time
            station.latest_date=latest_time

            try:
                s.commit()
            except Exception,e:
                s.rollback()
                print e


        s.close()
        print 'finish all'
