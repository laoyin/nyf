# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,xlrd,json,base64,logging
from django.conf import settings
from django.core.management import call_command
import django_gearman_commands
from gflux.util import *
from gflux.apps.station.sql_utils import update_vip_pay
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import Trans

gearman_logger=logging.getLogger('gearman')

class Command(django_gearman_commands.GearmanWorkerBaseCommand):
    @property
    def task_name(self):
        return 'update_vip_payment_type'

    def do_job(self, job_data):
        try:
            args=json.loads(job_data)

            #import
            site=args['site']
            count=0
            s = get_dash_session_maker(site)()
            results=s.query(Trans).filter_by(site=site).all()
            for result in results:
                cardnum=result.cardnum
                result.payment_type=update_vip_pay(cardnum)
                if count%10000==0:
                    s.commit()
                else:
                    s.add(result)
                count+=1
            s.commit()
            s.close()

        except Exception,e:
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]handle task error:%s\n===finish task===\n'%(
                    NowTime(),str(e)
                ))
                lf.close()
            gearman_logger.error('gearman error: '+str(e))
            gearman_logger.error('stack:'+exception_stuck())
