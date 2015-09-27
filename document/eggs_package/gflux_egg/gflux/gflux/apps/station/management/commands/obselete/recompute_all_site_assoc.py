# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management import call_command
from django.core.management.base import BaseCommand
from gflux.apps.station.sql_utils import *

class Command(BaseCommand):
    def handle(self,  *args, **options):
        print 'start'
        ret=get_all_stations()
        all_site=[x[0] for x in ret]
        for site in all_site:
            call_command('compute_item_assoc',interactive=False,period=0,site=site)
            call_command('compute_item_assoc',interactive=False,period=1,site=site)
            call_command('compute_item_assoc',interactive=False,period=2,site=site)
            call_command('compute_item_assoc',interactive=False,period=3,site=site)
        print 'end'
