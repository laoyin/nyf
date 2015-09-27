# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import Trans
from gflux.apps.station.sql_utils import compute_station_monthbatch
from sqlalchemy.sql import select, and_, or_, func
import pdb
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, **options):
        site='BJBJBJ'#'CN_JL_CC_PUQING'
        #计算月度高峰期和月度全时段平均进站车辆数
        compute_station_monthbatch(site,2013,4)

        #导数据
        f=open('/tmp/pq_gcustomer_trans_data.txt','w')

        #建立数据会话
        create_session = get_dash_session_maker(site)
        s = create_session()
        start_time='2014-12-01 00:00:00'
        end_time='2014-12-31 23:59:59'

        try:
            sql = select([
                Trans.site,Trans.cardnum,Trans.timestamp,Trans.trans_id,
                Trans.trans_type,Trans.barcode,Trans.price,Trans.quantity,Trans.pay,
                Trans.desc
            ]).select_from(Trans.__table__).where(
                and_(Trans.cardnum>0,Trans.site==site,Trans.quantity>0,
                        Trans.timestamp>=start_time,Trans.timestamp<=end_time)
            ).order_by('trans_id asc')
            trans_ret = s.execute(sql)
            trans = trans_ret.fetchall()

            def writeData(tmp,tmp_data):

                if tmp is None or len(tmp_data)==0:
                    return

                buy_list=[]
                for data in tmp_data:
                    buy_list.append('%(desc)s\r%(barcode)s\r%(trans_type)s\r%(price)s\r%(quantity)s\r%(pay)s'%({
                        'desc':data.desc,
                        'barcode':data.barcode,
                        'trans_type':data.trans_type,
                        'price':data.price,
                        'quantity':data.quantity,
                        'pay':data.pay
                    }))

                f.write('%(trans_id)s,%(timestamp)s,%(cardnum)s,{%(buying)s}\n'%({
                    'trans_id':tmp.trans_id,
                    'timestamp':tmp.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'cardnum':tmp.cardnum,
                    'buying':'\t'.join(buy_list)
                }))

            tmp=None
            tmp_data=[]

            for tran in trans:
                if tmp is None:
                    tmp=tran
                    tmp_data.append(tran)
                    continue

                if tmp.trans_id!=tran.trans_id:
                    writeData(tmp,tmp_data)

                    #清空
                    tmp=None
                    tmp_data=[]
                else:
                    tmp=tran
                    tmp_data.append(tran)

        except Exception,e:
            print 'except:%s'%str(e)

        finally:
            s.close()

        f.close()
