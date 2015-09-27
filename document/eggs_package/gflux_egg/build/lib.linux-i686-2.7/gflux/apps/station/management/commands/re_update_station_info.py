# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.common.models import SiteDayBatch
from datetime import datetime
from optparse import make_option
import sys,pdb,re
from dash.core.utils import getPaymentTypeByCard
from gflux.apps.station.sql_utils import get_nb_guns_of_station,get_guns_id_by_site,update_station_fuel_types_from_fact_trans,delete_by_key_from_cache
from gflux.apps.station.sql_utils import update_station_info
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import Trans

class Command(BaseCommand):
    help = 'Del Data'
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
        make_option('--user',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):
        print 'start...'
        site=options['site']
        user_name=options['user']
        try:
            #更新用户油品类型缓存
            delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
            update_station_fuel_types_from_fact_trans(site_name=site)


        except Exception,e:
            print e




        print 'end...'
