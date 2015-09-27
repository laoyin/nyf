# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from optparse import make_option
from gflux.apps.station.models import User
from gflux.apps.station.sql_utils import *
import sys,pdb,os,re,datetime
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Re Compute Fuel Daybatch'

    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):
        site_name = options['site'].upper()
        from datetime import datetime
        start_date=datetime(2015,1,1)
        end_date=datetime(2015,7,31)
        compute_fuel_daybatch(site_name,start_date,end_date)
