# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import Session
from gflux.apps.station.models import Trans, TransType, PaymentType
from datetime import datetime
from optparse import make_option
import sys,pdb,re

def guess_datetime(s):
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d','%Y-%m-%dT%H:%M:%S.000Z']:
        try:
            return datetime.strptime(s, fmt)
        except:
            pass
    return None

class Command(BaseCommand):
    help = 'Import Trans from CSV'
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
        make_option('--file',help="set file path",type="string"),
        make_option('--location',help="set location",type="string"),
    )

    def handle(self,  *args, **options):
        #get site name
        self.site=options['site'].strip().upper()
        self.s = Session()
        self.location=int(options['location'])

        with open(options['file']) as fd:
            print 'start...'
            file_mod=None
            batch_counter=0
            for row in fd:
                #取得数据
                row=row.replace('\t',' ')
                row=re.findall('\S+',row)

                #判断是否有效数据
                if len(row)!=21:
                    continue

                try:
                    #批量提交
                    if batch_counter==10000:
                        print 'finish 10000 row'
                        self.s.commit()
                        batch_counter=0

                    batch_counter+=1
                    print batch_counter

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
            timestamp = guess_datetime('%sT%sZ'%(row[10],row[11]))
            trans_type = TransType.FUEL
            
            tran = {
                'site': self.site,
                'trans_type': trans_type,
                'trans_id': int(row[1]),
                'cardnum': 0,
                'payment_type': PaymentType.CASH,
                'timestamp': timestamp,
                'datehour': datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour),
                'barcode': int(row[3]),
                'pay': float(row[8]),
                'quantity': float(row[7]),
                'desc': row[4].strip(),
                'price': float(row[5]),
                'unitname': '公升',
                'pump_id': int(row[2]),
                'location':self.location
            }
            return Trans(**tran)
        except Exception, e:
            print 'insert error:',e,'data:',row
            return None
