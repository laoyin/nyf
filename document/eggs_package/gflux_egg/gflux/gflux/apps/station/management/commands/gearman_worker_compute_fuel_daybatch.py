# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,xlrd,json,base64,logging
from django.conf import settings
from django.core.management import call_command
import django_gearman_commands
from gflux.apps.station.sql_utils import *
from gflux.util import *

gearman_logger=logging.getLogger('gearman')

class Command(django_gearman_commands.GearmanWorkerBaseCommand):
    @property
    def task_name(self):
        return 'compute_fuel_daybatch'

    def do_job(self, job_data):
        try:
            args=json.loads(job_data)

            with open(args['log_file'],'at') as lf:
                lf.write('===new task===\n[%s]start compute fuel daybatch site:%s\'s data...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

            #import
            start_date=guess_datetime(args['start_date'])
            end_date=guess_datetime(args['end_date'])

            compute_fuel_daybatch(args['site'],start_date,end_date)

            with open(args['log_file'],'at') as lf:
                lf.write('[%s]end compute fuel daybatch site:%s\'s data...\n===finish task===\n'%(
                    NowTime(),args['site']
                ))
                lf.close()
        except Exception,e:
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]handle task error:%s\n===finish task===\n'%(
                    NowTime(),str(e)
                ))
                lf.close()
            gearman_logger.error('gearman error: '+str(e))
            gearman_logger.error('stack:'+exception_stuck())

#test
from gflux.apps.station.sql_utils import *
from datetime import datetime
start_date=datetime(2013,1,1)
end_date=datetime(2014,12,31)
compute_fuel_daybatch('JQ_GAOTA',start_date,end_date)
