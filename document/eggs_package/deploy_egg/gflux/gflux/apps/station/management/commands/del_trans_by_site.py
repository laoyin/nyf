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
import hashlib
import xlrd
import random
from gflux.apps.station.sql_utils import delTransBySite

class Command(BaseCommand):
    help = 'Del Data'
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):
        print 'start...'
        site_name=options['site']
        try:
            delTransBySite(site_name)

        except Exception,e:
            print e




        print 'end...'
