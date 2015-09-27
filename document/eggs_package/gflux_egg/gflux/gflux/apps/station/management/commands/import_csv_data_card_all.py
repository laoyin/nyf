# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from gflux.apps.station.sql_utils import import_csv_card_all
from datetime import datetime
from optparse import make_option
import sys,pdb

class Command(BaseCommand):
    help = 'Import Trans from CSV ALL+CARD'
    
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
        make_option('--all_file',help="set file path",type="string"),
        make_option('--card_file',help="set file path",type="string"),
        make_option('--location_name',help="set location name like SC-CN",type="string"),
        make_option('--location_desc',help="set location desc like 四川",type="string"),
    )

    def handle(self,  *args, **options):

        # 最后一个参数设置为1,也就是缺省用户tao的整数id

        import_csv_card_all(options['site'],
                            options['all_file'],
                            options['card_file'],
                            options['location_name'],
                            options['location_desc'],
                            1,
                            'tao')
