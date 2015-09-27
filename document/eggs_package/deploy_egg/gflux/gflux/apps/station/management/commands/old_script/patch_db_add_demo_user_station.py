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
        demo_users=['gilbarco5','gilbarco6','gilbarco7']

        #demo_users=['smite']
        create_session = get_dash_session_maker()
    	s = create_session()

        #by site
        all_station_names=['CN_JL_CC_GUIGU','CN_JL_CC_CT','CN_JL_CC_GUANGGU',
            'CN_JL_CC_YT','CN_JL_CC_PD']

        for user in demo_users:
            user=s.query(User).filter_by(name=user).one()

            for station_name in all_station_names:
                new_user_station=UserStation(
                    user_id=user.id,
                    station=station_name
                )
                s.add(new_user_station)

            try:
                s.commit()
            except Exception,e:
                s.rollback()
                print e

        s.close()
        print 'finish all'
