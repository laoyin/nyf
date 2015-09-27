# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import Trans
from datetime import datetime
from optparse import make_option
import sys,pdb,re,json
from gflux.apps.station.sql_utils import update_user_none_fuel_top10
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Update VIP Type'
    option_list = BaseCommand.option_list + (
        make_option('--user',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):
        try:
            self.user=options['user']
            update_user_none_fuel_top10(self.user,'FZ_BM')
            update_user_none_fuel_top10(self.user,'FZ_WY')
            update_user_none_fuel_top10(self.user,'FZ_LY')
            update_user_none_fuel_top10(self.user,'FZ_CT')
            update_user_none_fuel_top10(self.user,'FZ_LF')
            update_user_none_fuel_top10(self.user,'FZ_QT')

        except Exception,e:
            print e

        print 'end...'
