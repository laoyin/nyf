# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb,xlrd,json,base64,logging
from django.conf import settings
from django.core.management import call_command
import django_gearman_commands
from gflux.apps.station.sql_utils import *
from gflux.apps.station.sql_utils import get_nb_guns_of_station,get_guns_id_by_site
from gflux.apps.station.sql_utils import update_station_info
from gflux.util import *

gearman_logger=logging.getLogger('gearman')

ajax_logger=gearman_logger

deleted_sha1=[]

def insert_csv_card_all_record_remove_pq(site, location, s, row):
    global deleted_sha1
    try:
        timestamp = guess_datetime(row[2])
        if timestamp==None:
            timestamp = guess_datetime(row[1])
        barcode = int(float(row[3]))
        if barcode < 400000:
            trans_type = TransType.FUEL
        else:
            trans_type = TransType.NON_FUEL
        cardnum = int(float(row[1]))
        if cardnum == 0:
            payment_type = PaymentType.CASH
        elif str(cardnum).startswith('9'):
            payment_type = PaymentType.VIP
        elif str(cardnum).startswith('6'):
            payment_type = PaymentType.UNION_PAY
        else:
            payment_type = PaymentType.CASH

        qty = int(float(row[4]))
        weight = float(row[7])

        desc=row[6].replace(u'昆仑好客','').replace(u'中国石油','').strip()
        if len(desc)==0:
            desc=u'unknow'

        date_hour=datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour)

        # 添加trans entry
        unitname=row[10].strip()
        trans_id=int(float(row[0]))
        if len(unicode(unitname))>16:
            ajax_logger.info("skip insert,unitname too long for trans_id:%s"%trans_id)
            return

        tran = {
            'site': site,
            'trans_type': trans_type,
            'trans_id': trans_id,
            'cardnum': cardnum,
            'payment_type': payment_type,
            'timestamp': timestamp,
            'datehour': date_hour,
            'barcode': barcode,
            'pay': float(row[5]) if trans_type == TransType.FUEL else float(row[9]),
            'quantity': weight if trans_type == TransType.FUEL else qty,
            'desc': desc,
            'price': row[8].strip(),
            'unitname': unitname,
            'pump_id': int(float(row[11])),
            'location':location
        }

        ins=Trans(**tran)

        #确定重复
        if ins.sha1 in deleted_sha1:
            return

        #check
        exists=s.query(Trans).filter_by(sha1=ins.sha1,site=ins.site,timestamp=ins.timestamp).count()
        if exists>0 and str(ins.timestamp)<='2014-09-01 22:55:09':
            s.query(Trans).filter_by(sha1=ins.sha1,site=ins.site,timestamp=ins.timestamp).delete()
            ajax_logger.info('delete dumplicate %s %s'%(ins.sha1,str(ins.timestamp)))
            deleted_sha1.append(ins.sha1)
            return

        if exists==0 and str(ins.timestamp)>'2014-09-01 22:55:09':
            ajax_logger.info('ERROR add %s %s %s'%(ins.sha1,str(ins.timestamp),ins.desc))
            s.add(ins)
    except Exception, e:
        ajax_logger.error("insert failure for:" + str(e) + " with data:" + str(row))

def import_csv_card_all_remove_pq(site, all_file_path, card_file_path,
                        loc_name, loc_desc, user_id,user_name):
    #get site name
    site=site.strip().upper()

    s = get_dash_session_maker(site_name=site)()

    #获取地点的ID
    location=get_location_id(loc_name, loc_desc)

    #get data
    already_trans_ids=set()
    #print 'start...'

    #导入card文件中的数据
    batch_counter=0
    with open(card_file_path) as fd:
        for row in fd:
            try:
                #批量提交
                if batch_counter%10000==0:
                    pass
                    #print 'added %d rows of card' % batch_counter
                    s.commit()

                row=row.strip(' \r\n').decode('gbk').split(',')

                insert_csv_card_all_record_remove_pq(site, location, s, row)

                #add
                already_trans_ids.add(int(row[0]))
                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
        #print 'finished adding %d rows of card' % batch_counter

    # 导入all文件中的数据
    batch_counter=0
    with open(all_file_path) as fd:
        for row in fd:
            try:
                try:
                    row=row.strip(' \r\n').decode('gb2312').split(',')
                except:
                    row=row.strip(' \r\n').decode('gbk').split(',')

                #test already_trans_ids
                if int(row[0]) in already_trans_ids:
                    continue

                #批量提交
                if batch_counter%10000==0:
                    pass
                    #print 'added %d rows of all' % batch_counter
                    s.commit()

                row.insert(1,'0')
                insert_csv_card_all_record_remove_pq(site, location, s, row)

                batch_counter+=1

            except Exception,e:
                ajax_logger.error(str(e))

        s.commit()
        #print 'finished adding %d rows of all' % batch_counter

    s.close()

    # 更新card_items数据
    # 暂时没有用到card表的数据，只和指数相关
    #compute_card_items(site)

    # 更新item_items数据

    compute_item_items(site)

    #更新用户油品类型缓存
    delete_by_key_from_cache('%s_user_fuel_types_dict'% user_name)
    update_station_fuel_types_from_fact_trans(site_name=site)

    #update nonefuel cache
    delete_by_key_from_cache('%s_user_none_fuel_top10'%user_name)
    update_user_none_fuel_top10(site_name=site)

    #删除所有油品缓存
    delete_by_key_from_cache('all_fuel_barcodes')

    #更新station的latest and earliest date
    update_station_latest_and_earliest_date(site)

class Command(django_gearman_commands.GearmanWorkerBaseCommand):
    @property
    def task_name(self):
        return 'import_data_remove_pq'

    def do_job(self, job_data):
        global deleted_sha1

        try:
            deleted_sha1=[]
            args=json.loads(job_data)

            with open(args['log_file'],'at') as lf:
                lf.write('===new task===\n[%s]start import site:%s\'s data...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

            #import
            import_csv_card_all_remove_pq(args['site'],
                                args['all_file'],
                                args['card_file'],
                                args['location'],
                                args['location_desc'],
                                args['userid'],
                                args['username'])

            with open(args['log_file'],'at') as lf:
                lf.write('[%s]end import site:%s\'s data...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

            #return
            #need update station info?
            """
            if args['need_update_station_info']:
                with open(args['log_file'],'at') as lf:
                    lf.write('[%s]start update site:%s info...\n'%(
                        NowTime(),args['site']
                    ))
                    lf.close()

                nb_guns=get_nb_guns_of_station(args['site'])
                guns_id=get_guns_id_by_site(args['site'])
                update_station_info(
                    args['site'],
                    args['site_desc'],
                    args['locid'],
                    nb_guns,
                    None,#phone
                    None,#address
                    None,#brand
                    None,#distance
                    guns_id
                    )

                with open(args['log_file'],'at') as lf:
                    lf.write('[%s]end update site:%s info...\n'%(
                        NowTime(),args['site']
                    ))
                    lf.close()

            """
            #计算相关性
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]start compute assoc on site:%s...\n'%(
                    NowTime(),args['site']
                ))
                lf.close()

            call_command('compute_item_assoc',interactive=False,period=0,site=args['site'])
            call_command('compute_item_assoc',interactive=False,period=1,site=args['site'])
            call_command('compute_item_assoc',interactive=False,period=2,site=args['site'])
            call_command('compute_item_assoc',interactive=False,period=3,site=args['site'])

            with open(args['log_file'],'at') as lf:
                lf.write('[%s]%s\n' %(NowTime(),args['import_flag_string']))
                lf.write('[%s]end compute assoc on site:%s...\n===finish task===\n'%(
                    NowTime(),args['site']
                ))
                lf.close()
        except Exception,e:
            with open(args['log_file'],'at') as lf:
                lf.write('[%s]%s\n' %(NowTime(),args['import_flag_string']))
                lf.write('[%s]handle task error:%s\n===finish task===\n'%(
                    NowTime(),str(e)
                ))
                lf.close()
            gearman_logger.error('gearman error: '+str(e))
            gearman_logger.error('stack:'+exception_stuck())
