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
    help = 'Deal with None Fuel Data'
    option_list = BaseCommand.option_list + (
        make_option('--file',help="set file path",type="string"),
        make_option('--save_path',help="save file path",type="string"),
    )

    def handle(self,  *args, **options):
        print 'start...'
        save_path=options['save_path']

        try:
            trans_count=30150001
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
                        site=eval(repr(row[1])[1:]).decode('gbk','ignore')
                        #处理unicode编码，并去掉文字后面到空格
                        site = site.decode('unicode-escape').rstrip()+','
                        trans_type='1,'
                        cardnum='0,'
                        payment_type='1000,'
                        timestamp = row[3]+','
                        barcode=str(row[11][0:11])+','
                        pay=str(row[38])+','
                        quantity=str(row[31])+','
                        desc=eval(repr(row[10])[1:]).decode('gbk','ignore')
                        desc=desc.decode('unicode-escape')+','
                        price=str(row[35])+','
                        unitname=row[12]+','
                        pump_id='0,'
                        trans_id=str(trans_count)+'\n'
                        trans_count+=1

                        lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                        print 'ok'

        except Exception,e:
            print e




        print 'end...'
