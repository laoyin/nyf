# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,xlrd,json,base64,logging
from django.conf import settings
from django.core.management import call_command
import django_gearman_commands
from gflux.apps.station.sql_utils import import_shell_data
from gflux.apps.station.sql_utils import get_nb_guns_of_station,get_guns_id_by_site
from gflux.apps.station.sql_utils import update_station_info
from gflux.util import *

gearman_logger=logging.getLogger('gearman')

class Command(django_gearman_commands.GearmanWorkerBaseCommand):
    @property
    def task_name(self):
        return 'import_shell_data'

    def do_job(self, job_data):
        try:
            args=json.loads(job_data)

            with open(args['log_file'],'at') as lf:
                lf.write('===new task===\n[%s]start import site:%s\'s data...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

            #import
            start_date,end_date=import_shell_data(args['site'],
                                args['file'],
                                args['location'],
                                args['location_desc'],
                                args['userid'],
                                args['username'],
                                args['station_id'])

            with open(args['log_file'],'at') as lf:
                lf.write('[%s]end import site:%s\'s data...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

            #need update station info?
            if args['need_update_station_info']:
                with open(args['log_file'],'at') as lf:
                    lf.write('[%s]start update site:%s info...\n'%(
                        NowTime(),args['site']
                    ))
                    lf.close()

                nb_guns=get_nb_guns_of_station(args['site'])
                guns_id=get_guns_id_by_site(args['site'])
                update_station_info(
                    args['site'],
                    args['site_desc'],
                    args['locid'],
                    nb_guns,
                    None,#phone
                    None,#address
                    None,#brand
                    None,#distance
                    guns_id
                    )

                with open(args['log_file'],'at') as lf:
                    lf.write('[%s]end update site:%s info...\n'%(
                        NowTime(),args['site']
                    ))
                    lf.close()

            #计算相关性
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]start compute assoc on site:%s...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

            call_command('compute_item_assoc',interactive=False,period=0,site=args['site'])
            call_command('compute_item_assoc',interactive=False,period=1,site=args['site'])
            call_command('compute_item_assoc',interactive=False,period=2,site=args['site'])
            call_command('compute_item_assoc',interactive=False,period=3,site=args['site'])

            with open(args['log_file'],'at') as lf:
                lf.write('[%s]%s\n' %(NowTime(),args['import_flag_string']))
                lf.write('[%s]end compute assoc on site:%s...\n===finish task===\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

            #离线计算油品每天销售
            args['start_date']=start_date.strftime('%Y-%m-%d')
            args['end_date']=end_date.strftime('%Y-%m-%d')
            call_command('gearman_submit_job', 'compute_fuel_daybatch',
                json.dumps(args), foreground=False)
            call_command('gearman_submit_job', 'compute_station_daybatch',
                json.dumps(args), foreground=False)
        except Exception,e:
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]%s\n' %(NowTime(),args['import_flag_string']))
                lf.write('[%s]handle task error:%s\n===finish task===\n'%(
                    NowTime(),str(e)
                ))
                lf.close()
            gearman_logger.error('gearman error: '+str(e))
            gearman_logger.error('stack:'+exception_stuck())
