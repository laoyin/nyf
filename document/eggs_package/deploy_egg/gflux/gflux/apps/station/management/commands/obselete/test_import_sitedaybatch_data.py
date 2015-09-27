# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.common.models import SiteDayBatch
from datetime import datetime
from optparse import make_option
import sys,pdb,re

class Command(BaseCommand):
    help = 'Import SiteDayBatch Data'
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
        make_option('--file',help="set file path",type="string")
    )

    def handle(self,  *args, **options):
        self.site=options['site'].strip().upper()
        self.s = get_dash_session_maker()
        with open(options['file']) as fd:
            print 'start...'
            batch_counter=0
            # 
            for row in fd:
                try:
                    #批量提交
                    if batch_counter==10000:
                        print 'finish 10000 row'
                        self.s.commit()
                        batch_counter=0

                    batch_counter+=1
                    print batch_counter

                    row=row.strip(' \r\n').decode('gb2312').split(',')

                    ins=self.insert_record(row)
                    if ins is None:
                        continue

                    self.s.add(ins)

                except Exception,e:
                    print e

            self.s.commit()
            self.s.close()

        print 'end...'

    def insert_record(self,row):
        try:
            item={
                'site': self.site,
                'day':row[0],
                'day_open':row[1],
                'day_close':row[2]
            }
            return SiteDayBatch(**item)

        except Exception, e:
            print 'insert error:',e,'data:',row
            return None
