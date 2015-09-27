# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,xlrd,json,base64,logging
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from gflux.apps.station.sql_utils import import_sp_excel
from gflux.apps.station.sql_utils import get_nb_guns_of_station
from gflux.apps.station.sql_utils import update_station_info
from gflux.util import *
from optparse import make_option

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
        make_option('--file',help="set file path",type="string"),
        make_option('--username',help="string",type="string"),
        make_option('--location',help="set location name like SC-CN",type="string"),
        make_option('--location_desc',help="set location desc like 四川",type="string"),
        make_option('--userid',help="set location desc like 四川",type="int"),
    )
    def handle(self,  *args, **options):
        try:
            #import
            import_sp_excel(
                options['site'],
                options['file'],
                options['location'],
                options['location_desc'],
                options['userid'],
                options['username'])
        except Exception,e:
            print exception_stuck()
