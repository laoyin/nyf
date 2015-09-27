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
from gflux.apps.station.sql_utils import update_vip_pay
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Update VIP Type'
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):
        try:
            args={}
            args['site']=options['site']
            result=call_command('gearman_submit_job', 'update_vip_payment_type',
                json.dumps(args), foreground=False)
        except Exception,e:
            print e

        print 'end...'
