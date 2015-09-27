# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,xlrd,json,base64,logging
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from gflux.apps.station.sql_utils import import_ycshell_excel
from gflux.apps.station.sql_utils import get_nb_guns_of_station
from gflux.apps.station.sql_utils import update_station_info
from gflux.util import *

class Command(BaseCommand):
    def handle(self,  *args, **options):
        try:
            #import
            import_ycshell_excel(
                options['site'],
                options['file'],
                options['location'],
                options['location_desc'],
                options['userid'],
                options['username'])
        except Exception,e:
            print exception_stuck()
