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

gearman_logger=logging.getLogger('gearman')

class Command(BaseCommand):
    help = 'compute_assoc_by_site'

    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):

        site=options['site'].upper()
        call_command('compute_item_assoc',interactive=False,period=0,site=site)
        call_command('compute_item_assoc',interactive=False,period=1,site=site)
        call_command('compute_item_assoc',interactive=False,period=2,site=site)
        call_command('compute_item_assoc',interactive=False,period=3,site=site)
