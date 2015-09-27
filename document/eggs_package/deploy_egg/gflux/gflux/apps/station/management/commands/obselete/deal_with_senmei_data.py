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

class Command(BaseCommand):
    help = 'Deal with Data'
    option_list = BaseCommand.option_list + (
        make_option('--file',help="set file path",type="string"),
        make_option('--save_path',help="save file path",type="string"),
    )

    def handle(self,  *args, **options):

        #txt为油品,xls为非油品
        file_type=options['file'].split('.')[1]
        save_path=options['save_path']
        if '员工卡1' in options['file'].split('.')[0]:
            trans_count=20150001
        elif '员工卡2' in options['file'].split('.')[0]:
            trans_count=30150001
        elif '用户卡不限车号' in options['file'].split('.')[0]:
            trans_count=40150001
        elif '用户卡限车号' in options['file'].split('.')[0]:
            trans_count=50150001
        elif '五一' in options['file'].split('.')[0]:
            trans_count=60150001
        elif '六一' in options['file'].split('.')[0]:
            trans_count=70150001
        elif '北门' in options['file'].split('.')[0]:
            trans_count=80150001
        elif '长汀' in options['file'].split('.')[0]:
            trans_count=90150001
        elif '连潘' in options['file'].split('.')[0]:
            trans_count=10150001
        else:
            trans_count=11150001
        print 'start...'
        #油品
        if file_type=='txt':
            with open(options['file']) as fd:
                for row in fd:
                    try:
                        row=row.replace('\'','')
                        row=row.strip(' \r\n').decode('gb2312', 'ignore').split(',')

                        if row[0]==unicode("福州本部五一加油站"):
                            with open(save_path+'/五一.txt','a') as lf:
                                site=row[0]+','
                                trans_type=row[3]+','
                                cardnum=row[4]+','
                                payment_type=str(getPaymentTypeByCard(cardnum))+','
                                timestamp=row[1]+','
                                barcode_sha1=hashlib.sha1()
                                barcode_sha1.update(row[9])
                                barcode=int(barcode_sha1.hexdigest()[:6],16)
                                barcode=str(barcode)+','
                                pay=str(row[12])+','
                                quantity=str(row[11])+','
                                desc=row[9]+','
                                price=row[10]+','
                                unitname='公升,'
                                pump_id=str(row[8])+','
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1
                        elif row[0]==unicode("福州本部北门加油站"):
                            with open(save_path+'/北门.txt','a') as lf:
                                site=row[0]+','
                                trans_type=row[3]+','
                                cardnum=row[4]+','
                                payment_type=str(getPaymentTypeByCard(cardnum))+','
                                timestamp=row[1]+','
                                barcode_sha1=hashlib.sha1()
                                barcode_sha1.update(row[9])
                                barcode=int(barcode_sha1.hexdigest()[:6],16)
                                barcode=str(barcode)+','
                                pay=str(row[12])+','
                                quantity=str(row[11])+','
                                desc=row[9]+','
                                price=row[10]+','
                                unitname='公升,'
                                pump_id=str(row[8])+','
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1

                        elif row[0]==unicode("福州本部长汀路加油站"):
                            with open(save_path+'/长汀.txt','a') as lf:
                                site=row[0]+','
                                trans_type=row[3]+','
                                cardnum=row[4]+','
                                payment_type=str(getPaymentTypeByCard(cardnum))+','
                                timestamp=row[1]+','
                                barcode_sha1=hashlib.sha1()
                                barcode_sha1.update(row[9])
                                barcode=int(barcode_sha1.hexdigest()[:6],16)
                                barcode=str(barcode)+','
                                pay=str(row[12])+','
                                quantity=str(row[11])+','
                                desc=row[9]+','
                                price=row[10]+','
                                unitname='公升,'
                                pump_id=str(row[8])+','
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1

                        elif row[0]==unicode("福州本部泉塘加油站"):
                            with open(save_path+'/泉塘.txt','a') as lf:
                                site=row[0]+','
                                trans_type=row[3]+','
                                cardnum=row[4]+','
                                payment_type=str(getPaymentTypeByCard(cardnum))+','
                                timestamp=row[1]+','
                                barcode_sha1=hashlib.sha1()
                                barcode_sha1.update(row[9])
                                barcode=int(barcode_sha1.hexdigest()[:6],16)
                                barcode=str(barcode)+','
                                pay=str(row[12])+','
                                quantity=str(row[11])+','
                                desc=row[9]+','
                                price=row[10]+','
                                unitname='公升,'
                                pump_id=str(row[8])+','
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1

                        elif row[0]==unicode("福州本部连潘加油站"):
                            with open(save_path+'/连潘.txt','a') as lf:
                                site=row[0]+','
                                trans_type=row[3]+','
                                cardnum=row[4]+','
                                payment_type=str(getPaymentTypeByCard(cardnum))+','
                                timestamp=row[1]+','
                                barcode_sha1=hashlib.sha1()
                                barcode_sha1.update(row[9])
                                barcode=int(barcode_sha1.hexdigest()[:6],16)
                                barcode=str(barcode)+','
                                pay=str(row[12])+','
                                quantity=str(row[11])+','
                                desc=row[9]+','
                                price=row[10]+','
                                unitname='公升,'
                                pump_id=str(row[8])+','
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1

                        elif row[0]==unicode("福州本部六一加油站"):
                            with open(save_path+'/六一.txt','a') as lf:
                                site=row[0]+','
                                trans_type=row[3]+','
                                cardnum=row[4]+','
                                payment_type=str(getPaymentTypeByCard(cardnum))+','
                                timestamp=row[1]+','
                                barcode_sha1=hashlib.sha1()
                                barcode_sha1.update(row[9])
                                barcode=int(barcode_sha1.hexdigest()[:6],16)
                                barcode=str(barcode)+','
                                pay=str(row[12])+','
                                quantity=str(row[11])+','
                                desc=row[9]+','
                                price=row[10]+','
                                unitname='公升,'
                                pump_id=str(row[8])+','
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1
                    except Exception,e:
                        print e
                fd.close()

        #非油品
        elif file_type=='xls':
            try:
                book=xlrd.open_workbook(options['file'],encoding_override='gb2312')
                sheets=book.sheets()
                for sheet in sheets:
                    nrows=sheet.nrows
                    for row_idx in xrange(nrows):
                        #最后一行的总计忽略掉
                        if row_idx==nrows-1:
                            return
                        row=sheet.row_values(row_idx)
                        if eval(repr(row[2])[1:]).decode('gbk')=='福州北门加油站':
                            with open(save_path+'/北门.txt','a') as lf:
                                site=eval(repr(row[2])[1:]).decode('gbk','ignore')+','
                                trans_type='1,'
                                cardnum='0,'
                                payment_type='1000,'
                                hh=random.randint(0,23)
                                mm=random.randint(0,59)
                                ss=random.randint(0,59)
                                timestamp=str(row[0])+' '+str(hh)+':'+str(mm)+':'+str(ss)+','
                                barcode=str(row[5])[-9:]+','
                                pay=str(row[7])+','
                                quantity=str(row[6])+','
                                desc=eval(repr(row[4])[1:]).decode('gbk','ignore')+','
                                if int(row[6])==0:
                                    price='0,'
                                else:
                                    price=str(int(row[7])/int(row[6]))+','
                                unitname='个,'
                                pump_id='0,'
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1

                        elif eval(repr(row[2])[1:]).decode('gbk')=='福州五一加油站':
                            with open(save_path+'/五一.txt','a') as lf:
                                site=eval(repr(row[2])[1:]).decode('gbk','ignore')+','
                                trans_type='1,'
                                cardnum='0,'
                                payment_type='1000,'
                                hh=random.randint(0,23)
                                mm=random.randint(0,59)
                                ss=random.randint(0,59)
                                timestamp=str(row[0])+' '+str(hh)+':'+str(mm)+':'+str(ss)+','
                                barcode=str(row[5])[-9:]+','
                                pay=str(row[7])+','
                                quantity=str(row[6])+','
                                desc=eval(repr(row[4])[1:]).decode('gbk','ignore')+','
                                if int(row[6])==0:
                                    price='0,'
                                else:
                                    price=str(int(row[7])/int(row[6]))+','
                                unitname='个,'
                                pump_id='0,'
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1
                        elif eval(repr(row[2])[1:]).decode('gbk')=='福州六一加油站':
                            with open(save_path+'/六一.txt','a') as lf:
                                site=eval(repr(row[2])[1:]).decode('gbk','ignore')+','
                                trans_type='1,'
                                cardnum='0,'
                                payment_type='1000,'
                                hh=random.randint(0,23)
                                mm=random.randint(0,59)
                                ss=random.randint(0,59)
                                timestamp=str(row[0])+' '+str(hh)+':'+str(mm)+':'+str(ss)+','
                                barcode=str(row[5])[-9:]+','
                                pay=str(row[7])+','
                                quantity=str(row[6])+','
                                desc=eval(repr(row[4])[1:]).decode('gbk','ignore')+','
                                if int(row[6])==0:
                                    price='0,'
                                else:
                                    price=str(int(row[7])/int(row[6]))+','
                                unitname='个,'
                                pump_id='0,'
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1
                        elif eval(repr(row[2])[1:]).decode('gbk')=='福州连潘加油站':
                            with open(save_path+'/连潘.txt','a') as lf:
                                site=eval(repr(row[2])[1:]).decode('gbk','ignore')+','
                                trans_type='1,'
                                cardnum='0,'
                                payment_type='1000,'
                                hh=random.randint(0,23)
                                mm=random.randint(0,59)
                                ss=random.randint(0,59)
                                timestamp=str(row[0])+' '+str(hh)+':'+str(mm)+':'+str(ss)+','
                                barcode=str(row[5])[-9:]+','
                                pay=str(row[7])+','
                                quantity=str(row[6])+','
                                desc=eval(repr(row[4])[1:]).decode('gbk','ignore')+','
                                if int(row[6])==0:
                                    price='0,'
                                else:
                                    price=str(int(row[7])/int(row[6]))+','
                                unitname='个,'
                                pump_id='0,'
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1
                        elif eval(repr(row[2])[1:]).decode('gbk')=='福州长汀加油站':
                            with open(save_path+'/长汀.txt','a') as lf:
                                site=eval(repr(row[2])[1:]).decode('gbk','ignore')+','
                                trans_type='1,'
                                cardnum='0,'
                                payment_type='1000,'
                                hh=random.randint(0,23)
                                mm=random.randint(0,59)
                                ss=random.randint(0,59)
                                timestamp=str(row[0])+' '+str(hh)+':'+str(mm)+':'+str(ss)+','
                                barcode=str(row[5])[-9:]+','
                                pay=str(row[7])+','
                                quantity=str(row[6])+','
                                desc=eval(repr(row[4])[1:]).decode('gbk','ignore')+','
                                if int(row[6])==0:
                                    price='0,'
                                else:
                                    price=str(int(row[7])/int(row[6]))+','
                                unitname='个,'
                                pump_id='0,'
                                trans_id=str(trans_count)+'\n'

                                lf.write(site+trans_type+cardnum+payment_type+timestamp+barcode+pay+quantity+desc+price+unitname+pump_id+trans_id)
                                trans_count+=1


            except Exception,e:
                print e




        print 'end...'
