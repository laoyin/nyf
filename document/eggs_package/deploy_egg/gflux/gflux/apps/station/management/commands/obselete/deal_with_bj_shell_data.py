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
from dash.core.utils import getPaymentTypeByCard
import hashlib
import xlrd
import random
from xlrd import xldate_as_tuple

class Command(BaseCommand):
    help = 'Deal with Data'
    option_list = BaseCommand.option_list + (
        make_option('--file',help="set file path",type="string"),
        make_option('--save_path',help="save file path",type="string"),
    )

    def handle(self,  *args, **options):
        print 'start...'
        save_path=options['save_path']
        try:
            book=xlrd.open_workbook(options['file'],encoding_override='gb2312')
            sheets=book.sheets()
            for sheet in sheets:
                nrows=sheet.nrows
                for row_idx in xrange(nrows):
                    #忽略前5行表头
                    if row_idx == 0 or row_idx == 1 or row_idx == 2 or row_idx == 3 or row_idx == 4:
                        continue
                    row=sheet.row_values(row_idx)
                    with open(save_path+'/beijingqiaopai.txt','a') as lf:
                        site='北京小营,'
                        pump_id=str(row[8])
                        if pump_id == '0.0' or pump_id == '0':
                            pump_id = '0,'
                            trans_type = '1,'
                            unitname='个,'
                        else:
                            pump_id = pump_id[:-2]+','
                            trans_type = '0,'
                            unitname='公升,'
                        payment_type=row[5]
                        if payment_type == '现金':
                            cardnum='0,'
                            payment_type='1000,'
                        elif payment_type == '信用卡':
                            payment_type='3,'
                            #信用卡由于卡号为空随机生成,以100000开头为标示
                            cardnum='100000'+str(random.randint(1000000000, 9999999999))+','
                        elif payment_type == '壳牌车队卡':
                            payment_type='2,'
                            #加油卡由于卡号为空随机生成,以200000开头为标示
                            cardnum='200000'+str(random.randint(1000000000, 9999999999))+','
                        else:
                            cardnum='0,'
                            payment_type='1000,'
                        #处理从excel中取到的时间
                        timestamps=datetime(*xldate_as_tuple(row[0],0))
                        year=timestamps.year
                        month=timestamps.month
                        day=timestamps.day
                        timestamps2=xlrd.xldate_as_tuple(row[1],0)
                        hour=timestamps2[3]
                        minute=timestamps2[4]
                        second=timestamps2[5]
                        timestamp = str(year)+'-'+str(month)+'-'+str(day)+' '+str(hour)+':'+str(minute)+':'+str(second)+','

                        #没有条形码,根据商品名称生成sha1
                        barcode_sha1=hashlib.sha1()
                        barcode_sha1.update(row[9])
                        barcode=int(barcode_sha1.hexdigest()[:6],16)
                        barcode=str(barcode)+','
                        pay=str(row[12])+','
                        quantity=str(row[11])+','
                        desc=row[9]+','
                        price=str(row[10])+','
                        trans_id=str(int(row[15]))+'\n'
                        lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                        print 'ok'


        except Exception,e:
            print e
        print 'end...'
