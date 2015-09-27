# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,xlrd,json,base64,logging
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
import django_gearman_commands
from gflux.apps.station.sql_utils import *
from gflux.util import *

#计算每天油站汇总数据
def compute_station_daybatch_jiamanlv(site_name,start_date,end_date):
    #create session
    src_session=get_dash_session_maker(site_name)()
    des_session=get_dash_session_maker()()

    try:

        #油站情况
        station=des_session.query(Station).filter_by(name=site_name).one()

        #compute
        curr_date=start_date
        while curr_date <= end_date:
            futher_date=curr_date+timedelta(days=1)
            pre_mon_curr_date=curr_date-relativedelta(months=1)
            pre_mon_futher_date=futher_date-relativedelta(months=1)

            #加油卡消费比例
            vip_pay_percent=0
            sql='select sum(pay) as pay, payment_type from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\' group by payment_type;'%(
                curr_date.strftime('%Y-%m-%d'),futher_date.strftime('%Y-%m-%d'),
                site_name
            )
            rets=src_session.execute(sql)
            total_pay=0
            vip_pay=0
            for ret in rets:
                if ret.payment_type==PaymentType.VIP:
                    vip_pay+=ret.pay
                total_pay+=ret.pay

            pay_amout=total_pay
            vip_pay_amout=vip_pay
            if total_pay==0:
                vip_pay_percent=0
            else:
                vip_pay_percent=vip_pay*100/total_pay

            #加满率
            fuel_fillout_percent=0
            sql='select count(DISTINCT trans_id) as count, pump_type from fact_trans where timestamp>=\'%s\' and \
            timestamp<\'%s\' and site=\'%s\' and trans_type=%s group by pump_type;'%(
                curr_date.strftime('%Y-%m-%d'),futher_date.strftime('%Y-%m-%d'),
                site_name,TransType.FUEL
            )
            rets=src_session.execute(sql)
            fillout_count=0
            total_count=0
            for ret in rets:
                if ret.pump_type==PumpType.FILLOUT:
                    fillout_count+=ret.count
                total_count+=ret.count

            fuel_trans_count=total_count
            fuel_fillout_count=fillout_count
            if total_count==0:
                fuel_fillout_percent=0
            else:
                fuel_fillout_percent=fillout_count*100/total_count


            #存储结果
            obj=StationDailyStat(date=curr_date,site=site_name)
            obj.compute_sha1()

            #check exists
            exists=des_session.query(StationDailyStat).filter_by(sha1=obj.sha1).count()
            if exists>0:
                obj=des_session.query(StationDailyStat).filter_by(sha1=obj.sha1).one()
            else:
                des_session.add(obj)

            #update
            obj.vip_pay_percent=vip_pay_percent
            obj.pay_amout=pay_amout
            obj.vip_pay_amout=vip_pay_amout
            obj.fuel_fillout_percent=fuel_fillout_percent
            obj.fuel_trans_count=fuel_trans_count
            obj.fuel_fillout_count=fuel_fillout_count

            try:
                des_session.commit()
            except Exception,e:
                ajax_logger.error('session commit error:%s'%str(e))
                des_session.rollback()

            #下一天
            curr_date += timedelta(days=1)

    except Exception,e:
        ajax_logger.error('compute station daybatch error:%s'%str(e))

    finally:
        src_session.close()
        des_session.close()

class Command(BaseCommand):
    def handle(self,  *args, **options):
        from datetime import datetime
        print 'start'
        compute_station_daybatch_jiamanlv('FZ_LY',datetime(2013,11,1),datetime(2014,10,31))
        print 'finish FZ_LY'
        compute_station_daybatch_jiamanlv('FZ_QT',datetime(2013,11,1),datetime(2014,10,31))
        print 'finish FZ_QT'
        compute_station_daybatch_jiamanlv('FZ_WY',datetime(2013,11,1),datetime(2014,10,31))
        print 'finish FZ_WY'
        compute_station_daybatch_jiamanlv('FZ_CT',datetime(2013,11,1),datetime(2014,10,31))
        print 'finish FZ_CT'
        compute_station_daybatch_jiamanlv('FZ_BM',datetime(2013,11,1),datetime(2014,10,31))
        print 'finish FZ_BM'
        compute_station_daybatch_jiamanlv('FZ_LF',datetime(2013,11,1),datetime(2014,10,31))
        print 'finish FZ_LF'
        print 'end'
