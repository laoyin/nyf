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
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
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
        
        #get data
        waits=[]
        
        with open(options['file']) as fd:
            print 'start...'
            file_mod=None
            batch_counter=0
            for row in fd:
                if not row.startswith('0,08,'):
                    continue
                    
                try:
                    #批量提交
                    if batch_counter==10000:
                        print 'finish 10000 row'
                        self.s.commit()
                        batch_counter=0
                        
                    batch_counter+=1
                    print batch_counter
                    
                    
                    row=row.strip(' \r\n').decode('gb2312').split(',')
                    row=[x.strip('"') for x in row]
                    
                    #商品信息
                    if int(row[6])==1 and int(row[7]) in [2,14]:
                        ins=self.insert_record(row)
                        if ins is not None:
                            waits.append(ins)
                            
                    #结算信息
                    elif int(row[6])==0 and int(row[7])==7:
                        if row[8]==u'现金':
                            payment_type = PaymentType.CASH
                        elif row[8]==u'壳牌车队卡':
                            payment_type = PaymentType.VIP
                        elif row[8]==u'信用卡':
                            payment_type = PaymentType.CREDIT
                        else:
                            payment_type = PaymentType.CASH
                        #将等待的doc赋值提交
                        for wait in waits:
                            wait.payment_type=payment_type
                            self.s.add(wait)
                        waits=[]
                        
                except Exception,e:
                    print e
                    
            self.s.commit()
            self.s.close()
            
        print 'end...'
        
    def insert_record(self,row):
        try:
            timestamp = guess_datetime(row[2])
            if int(row[7])==2:
                trans_type = TransType.FUEL
                barcode = int(re.findall(u'(?<=\s{1})(\d+)#汽油',row[8])[0])
            else:
                trans_type = TransType.NON_FUEL
                barcode = int(row[13])
                
            cardnum =0
            tran = {
                'site': self.site,
                'trans_type': trans_type,
                'trans_id': int(row[4]),
                'cardnum': cardnum,
                'payment_type': PaymentType.CASH,
                'timestamp': timestamp,
                'datehour': datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour),
                'barcode': barcode,
                'pay': float(row[11]),
                'quantity': float(row[10]),
                'desc': row[8].strip(),
                'price': row[9].strip(),
                'unitname': 'unknow',
                'pump_id': int(row[13]) if trans_type==TransType.FUEL else 0,
                'location':self.location
            }
            return Trans(**tran)
        except Exception, e:
            print 'insert error:',e,'data:',row
            return None
