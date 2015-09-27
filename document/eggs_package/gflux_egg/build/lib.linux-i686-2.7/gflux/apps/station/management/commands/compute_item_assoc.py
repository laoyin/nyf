# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import Trans, ItemAssoc, DayPeriod,StationItemAssoc
from gflux.apps.station.models import PumpType,TransType,PaymentType
from gflux.apps.common.models import DimDateHour
from gflux.apps.station.sql_utils import get_station_none_fuel_top10_by_name

from django.core.management.base import BaseCommand
from sqlalchemy.sql import select, and_
from scipy.sparse import coo_matrix
from sklearn.metrics.pairwise import pairwise_kernels
import numpy as np

from optparse import make_option
import time,random,pdb

# 以某个概率sampling_prob进行采样，如果选取该个体，则返回True

def should_include_under_random_probablity(sampling_prob=0.3):

    rand_num=random.randint(0,10000)

    if rand_num<10000*sampling_prob:
        return True
    else:
        return False

class Command(BaseCommand):
    """
    计算指定时段商品相关性
    """
    help = 'Train'

    #统计enum(ALL=(0, u'全部'), MORNING=(1, u'早'), NOON=(2, u'中'), NIGHT=(3, u'晚'))
    PERIOD_RANGE = {
        DayPeriod.ALL: (0, 24),
        DayPeriod.MORNING: (0, 10),
        DayPeriod.NOON: (10, 17),
        DayPeriod.NIGHT: (17, 24),
    }

    option_list = BaseCommand.option_list + (
        make_option('--period',help="specify time period to compute assoication: 0 for ALL, 1 for Morning, 2 for Noon and 3 for Night",type="string"),
        make_option('--site',help="指定site值，如果指定，那么存储相关性时就存储到station_item_assoc表")
    )

    def handle(self, **options):
        period=int(options['period'])
        start_hour, end_hour = self.PERIOD_RANGE[period]
        on_specifield_site=False

        #建立数据会话
        if options['site']==None:
            create_session = get_dash_session_maker()
        else :
            create_session = get_dash_session_maker(options['site'])
        s = create_session()

        #设置待计算变量
        #{user_id:{barcode:1}}
        dataset = {}

        #(barcode1,barcode2)
        item_ids = set()

        #以客户为中心的抽样过程
        def get_trans_from_sampling(trans):

            #总体样本数量
            count_all=len(trans)

            if count_all==0:
                return

            #抽样率=抽样目标/总体样本数量
            sampling_rate=(10000+0.000001)/count_all

            for tran in trans:
                #vip卡按卡号区分用户
                if tran.cardnum==PaymentType.VIP:
                    user_id="%s-%s"%(tran.site,str(tran.cardnum))

                #其余以交易号来区分
                else:
                    user_id = "%s-%s" % (tran.site,str(tran.trans_id))

                #如果此客户已经被采样过，则不用再次随机，直接命中
                if dataset.has_key(user_id):
                    pass

                #陌生客户需要随机采样
                else:
                    #未命中
                    if should_include_under_random_probablity(sampling_rate)==False:
                        continue

                dataset.setdefault(user_id, {})
                dataset[user_id].setdefault(tran.barcode, 0)
                dataset[user_id][tran.barcode] += 1
                item_ids.add(tran.barcode)

        #开始采样数据
        try:
            starttime = time.time()
            trans=[]

            if options['site']==None:
                sql = select([
                    Trans.site,Trans.cardnum,Trans.trans_id,
                    Trans.payment_type,Trans.barcode,DimDateHour.hour
                ]).select_from(Trans.__table__.join(DimDateHour.__table__)).where(
                    and_(Trans.quantity > 0,DimDateHour.hour >= start_hour,DimDateHour.hour < end_hour)#购买数量大于0的有效购买
                )
                trans_ret = s.execute(sql)
                trans = trans_ret.fetchall()
                get_trans_from_sampling(trans)

            else:
                on_specifield_site=True

                #第一次选取所有的油品
                sql = select([
                    Trans.site,Trans.cardnum,Trans.trans_id,
                    Trans.payment_type,Trans.barcode,DimDateHour.hour
                ]).select_from(Trans.__table__.join(DimDateHour.__table__)).where(
                    and_(Trans.trans_type==TransType.FUEL,Trans.site==options['site'],Trans.quantity > 0,DimDateHour.hour >= start_hour,DimDateHour.hour < end_hour)#购买数量大于0的有效购买
                )
                trans_ret = s.execute(sql)
                trans = trans_ret.fetchall()
                get_trans_from_sampling(trans)

                #取得top10
                none_fuel_top10=get_station_none_fuel_top10_by_name(options['site'])
                none_fuel_top10=[x['barcode'] for x in none_fuel_top10]

                #第二次选取top10非油品
                sql = select([
                    Trans.site,Trans.cardnum,Trans.trans_id,
                    Trans.payment_type,Trans.barcode,DimDateHour.hour
                ]).select_from(Trans.__table__.join(DimDateHour.__table__)).where(
                    and_(Trans.trans_type==TransType.NON_FUEL,Trans.barcode.in_(set(none_fuel_top10)),Trans.site==options['site'],Trans.quantity > 0,DimDateHour.hour >= start_hour,DimDateHour.hour < end_hour)#购买数量大于0的有效购买
                )
                trans_ret = s.execute(sql)
                trans = trans_ret.fetchall()
                get_trans_from_sampling(trans)

                #第三次选取非油品非top10交易
                sql = select([
                    Trans.site,Trans.cardnum,Trans.trans_id,
                    Trans.payment_type,Trans.barcode,DimDateHour.hour
                ]).select_from(Trans.__table__.join(DimDateHour.__table__)).where(
                    and_(Trans.trans_type==TransType.NON_FUEL,~Trans.barcode.in_(set(none_fuel_top10)),Trans.site==options['site'],Trans.quantity > 0,DimDateHour.hour >= start_hour,DimDateHour.hour < end_hour)#购买数量大于0的有效购买
                )
                trans_ret = s.execute(sql)
                trans = trans_ret.fetchall()
                get_trans_from_sampling(trans)

            print 'trans loaded: %s(s)' % (time.time() - starttime)

        except Exception,e:
            print 'trans load except:%s'%str(e)

        finally:
            s.close()

        starttime = time.time()
        #{user_id,cursor}
        #这里的cursor为keys排序之后的
        user_ids = dataset.keys()
        user_ids.sort()
        user_indices = dict([(user_id, index)
                             for index, user_id in enumerate(user_ids)])

        #{barcode,cursor}
        #这里的cursor为item——ids排序后的
        item_ids = list(item_ids)
        item_ids.sort()
        item_indices = dict([(item_id, index)
                             for index, item_id in enumerate(item_ids)])

        #[user_cursor1,user_cursor2]
        row = []
        #[barcode_cursor1,barcode_cursor2]
        col = []
        #[barcode_quantity1,barcode_quantity2]
        data = []

        for user_id, itemset in dataset.iteritems():
            #取得cursor
            user_index = user_indices[user_id]

            #取得user购买的商品
            if len(itemset)>1:
                print 'user:%s buy more than one good'%user_id

            for item_id, value in itemset.iteritems():
                row.append(user_index)

                #取得barcode cursor
                item_index = item_indices[item_id]
                col.append(item_index)

                data.append(value)

        print 'trans prepare to compute: %s(s)' % (time.time() - starttime)

        #使用科学计算库计算相关性
        ##############################
        starttime = time.time()

        M = coo_matrix((data, (row, col)),
            shape=(len(user_ids), len(item_ids)),
            dtype=np.float)
        print 'M shape:', M.shape

        X = M.tocsc()
        X = X.transpose()
        print 'X shape:', X.get_shape()

        R = pairwise_kernels(X, metric="cosine")
        print 'R shape:', R.shape

        R = coo_matrix(R)
        R = R.tocsr()
        print 'R shape:', R.get_shape()
        print 'R.data length:', len(R.data)

        print 'item assoc computed: %s(s)' % (time.time() - starttime)

        #结束计算，抽取计算结果
        #######################################
        assocs = []
        for i in xrange(0, R.get_shape()[0]):
            #barcode
            item_from = int(item_ids[i])

            start, end = R.indptr[i], R.indptr[i + 1]
            for j in xrange(start, end):
                #barcode
                item_to = int(item_ids[R.indices[j]])

                #同一种商品不需要计算相关性
                if item_from == item_to:
                    continue

                #获得相关性
                weight = round(float(R.data[j]), 6)
                if weight==0:
                    continue

                if on_specifield_site:
                    assocs.append({
                        'item_from': item_from,
                        'item_to': item_to,
                        'weight': weight,
                        'period': period,
                        'site':options['site']
                    })
                else:
                    assocs.append({
                        'item_from': item_from,
                        'item_to': item_to,
                        'weight': weight,
                        'period': period,
                    })

        #检查最后的结果
        if len(assocs)==0:
            print 'no assocs need to commit'
            return

        #更新数据库
        if options['site']==None:
            create_session = get_dash_session_maker()
        else :
            create_session = get_dash_session_maker(options['site'])
        s = create_session()

        try:
            if on_specifield_site:
                s.execute(StationItemAssoc.__table__.delete().where(and_(
                    StationItemAssoc.period == period,
                    StationItemAssoc.site==options['site']
                    )))
                s.execute(StationItemAssoc.__table__.insert(), assocs)
            else:
                s.execute(ItemAssoc.__table__.delete().where(ItemAssoc.period == period))
                s.execute(ItemAssoc.__table__.insert(), assocs)
            s.commit()
            print 'successfully committed %s assocs'%len(assocs)
        except Exception, e:
            print >> sys.stderr, "failed to commit: ", str(e)
        finally:
            s.close()
