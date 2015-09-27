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
                    #忽略表头
                    if row_idx == 0:
                        continue
                    #最后一行的总计忽略掉
                    if row_idx==nrows-1:
                        return
                    row=sheet.row_values(row_idx)
                    with open(save_path+'/changjiangdao.txt','a') as lf:
                        site=eval(repr(row[2])[1:]).decode('gbk','ignore')
                        #处理unicode编码，并去掉文字后面到空格
                        site = site.decode('unicode-escape').rstrip()+','
                        trans_type='0,'
                        cardnum=str(int(row[3]))+','
                        payment_type=row[5]
                        if payment_type=='员工卡正常记录':
                            payment_type='1000,'
                        elif payment_type=='本地卡正常记录':
                            payment_type='2,'
                        else:
                            payment_type='1000,'
                        #处理从excel中取到的时间
                        timestamps=datetime(*xldate_as_tuple(row[18],0))
                        year=timestamps.year
                        month=timestamps.month
                        day=timestamps.day
                        hour=timestamps.hour
                        minute=timestamps.minute
                        second=timestamps.second
                        if second<10:
                            second = '0'+str(second)
                        timestamp = str(year)+'-'+str(month)+'-'+str(day)+' '+str(hour)+':'+str(minute)+':'+str(second)+','
                        barcode_sha1=hashlib.sha1()
                        barcode_sha1.update(row[7])
                        barcode=int(barcode_sha1.hexdigest()[:6],16)
                        barcode=str(barcode)+','
                        pay=str(row[10])+','
                        quantity=str(row[8])+','
                        desc=eval(repr(row[7])[1:]).decode('gbk','ignore')
                        desc=desc.decode('unicode-escape')+','
                        price=str(row[9])+','
                        unitname='公升,'
                        pump_id=str(int(row[13]))+','
                        trans_id=str(int(row[15]))+'\n'

                        lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                        print 'ok'

        except Exception,e:
            print e




        print 'end...'
