# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import *
from gflux.apps.common.models import *
import pdb,logging
from gflux.apps.station.sql_utils import guess_datetime
from optparse import make_option

class Command(BaseCommand):
    help = 'Fix PQDATA'
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
        make_option('--card_dir',help="file dir",type="string"),
        make_option('--all_dir',help="file dir",type="string"),
    )

    def handle(self,  *args, **options):
        ajax_logger=logging.getLogger('ajax')
        print 'start...'
        site=options['site']
        card_file_path=options['card_dir']
        all_file_path=options['all_dir']
        count=0
        try:
            s = get_dash_session_maker(site)()
            with open(card_file_path) as fd:
                for row in fd:
                    try:
                        row=row.strip(' \r\n').decode('gbk').split(',')
                        timestamp = guess_datetime(row[2])
                        if timestamp==None:
                            timestamp = guess_datetime(row[1])
                        barcode = int(float(row[3]))
                        if barcode < 400000:
                            trans_type = TransType.FUEL
                        else:
                            trans_type = TransType.NON_FUEL
                        trans_id = int(row[0])
                        pump_id = int(float(row[11]))
                        pay = float(row[5]) if trans_type == TransType.FUEL else float(row[9])
                        location = 8
                        import hashlib
                        sha1=hashlib.sha1()
                        sha1.update(str(location))
                        sha1.update(site)
                        sha1.update(str(timestamp))
                        sha1.update(str(trans_type))
                        sha1.update(str(trans_id))
                        sha1.update(str(pump_id))
                        sha1.update(str(barcode))
                        sha1.update(str(pay))
                        sha1=sha1.hexdigest()
                        rm = s.query(Trans).filter_by(sha1=sha1,site=site).delete()
                        s.commit()
                        if rm>0:
                            count+=1
                            print 'success delete card item trans_id: %d' %(count)
                    except Exception,e:
                        ajax_logger.error(str(e))
                        print e

            with open(all_file_path) as fd:
                for row in fd:
                    try:
                        try:
                            row=row.strip(' \r\n').decode('gb2312').split(',')
                        except:
                            row=row.strip(' \r\n').decode('gbk').split(',')
                        row.insert(1,'0')
                        timestamp = guess_datetime(row[2])
                        if timestamp==None:
                            timestamp = guess_datetime(row[1])
                        barcode = int(float(row[3]))
                        if barcode < 400000:
                            trans_type = TransType.FUEL
                        else:
                            trans_type = TransType.NON_FUEL
                        trans_id = int(row[0])
                        pump_id = int(float(row[11]))
                        pay = float(row[5]) if trans_type == TransType.FUEL else float(row[9])
                        location = 8
                        import hashlib
                        sha1=hashlib.sha1()
                        sha1.update(str(location))
                        sha1.update(site)
                        sha1.update(str(timestamp))
                        sha1.update(str(trans_type))
                        sha1.update(str(trans_id))
                        sha1.update(str(pump_id))
                        sha1.update(str(barcode))
                        sha1.update(str(pay))
                        sha1=sha1.hexdigest()
                        s.query(Trans).filter_by(sha1=sha1,site=site).delete()
                        s.commit()
                        if rm>0:
                            count+=1
                            print 'success delete card item %d' %(count)
                    except Exception,e:
                        ajax_logger.error(str(e))
                        print e
            print count
            #ajax_logger.info('delete count:%d'%count)
        except Exception,e:
            print e
            #ajax_logger.error('fail delete')
        print 'end...'
