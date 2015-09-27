# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,xlrd,json,base64,logging
from django.conf import settings
from django.core.management import call_command
import django_gearman_commands
from gflux.apps.station.sql_utils import import_sitedaybatch_data
from gflux.util import *

gearman_logger=logging.getLogger('gearman')

class Command(django_gearman_commands.GearmanWorkerBaseCommand):
    @property
    def task_name(self):
        return 'import_sitedaybatch_data'

    def do_job(self, job_data):
        try:
            args=json.loads(job_data)

            with open(args['log_file'],'at') as lf:
                lf.write('===new task===\n[%s]start import site:%s\'s daybatch data...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()
            #import
            import_sitedaybatch_data(args['site'],
                                args['file'])
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]end import site:%s\'s daybatch data...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

        except Exception,e:
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]%s\n' %(NowTime(),args['import_flag_string']))
                lf.write('[%s]handle task error:%s\n===finish task===\n'%(
                    NowTime(),str(e)
                ))
                lf.close()
            gearman_logger.error('gearman error: '+str(e))
            gearman_logger.error('stack:'+exception_stuck())
