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
            trans_count=20170001
            book=xlrd.open_workbook(options['file'],encoding_override='gb2312')
            sheets=book.sheets()
            #数据映射
            dim={}
            for sheet in sheets:
                nrows=sheet.nrows
                ncols=sheet.ncols
                for row_idx in xrange(nrows):
                    row=sheet.row_values(row_idx)
                    #忽略表头
                    if row_idx == 0:
                        for col_idx in xrange(ncols):
                            dim[row[col_idx]]=col_idx
                        continue
                    #最后一行的总计忽略掉
                    if row_idx==nrows-1:
                        return

                    with open(save_path+'/changjiangdao.txt','a') as lf:
                        site=eval(repr(row[dim['组织|名称'.decode()]])[1:]).decode('gbk','ignore')
                        #处理unicode编码，并去掉文字后面到空格
                        site = site.decode('unicode-escape').rstrip()+','
                        trans_type='1,'
                        cardnum='0,'
                        payment_type='1000,'
                        if dim.has_key('销售日期'.decode()):
                            timestamp = row[dim['销售日期'.decode()]]+','
                        else:
                            timestamp = row[dim['报表日期'.decode()]]+','
                        barcode=str(row[dim['商品|编码'.decode()]])+','
                        pay=str(row[dim['含税销售金额'.decode()]])+','
                        quantity=str(row[dim['销售数量'.decode()]])+','
                        desc=eval(repr(row[dim['商品|名称'.decode()]])[1:]).decode('gbk','ignore')
                        desc=desc.decode('unicode-escape')+','
                        if dim.has_key('售价'.decode()):
                            price=str(row[dim['售价'.decode()]])+','
                        else:
                            price=str(row[dim['发生售价'.decode()]])+','
                        unitname='个,'
                        pump_id='0,'
                        trans_id=str(trans_count)+'\n'
                        trans_count+=1

                        lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                        print 'ok'

        except Exception,e:
            print e




        print 'end...'
