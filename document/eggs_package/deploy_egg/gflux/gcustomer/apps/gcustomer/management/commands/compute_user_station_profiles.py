
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.sql_utils import get_or_create,get_all_stations
from gflux.apps.station.models import TransType, PumpType
from optparse import make_option
from gcustomer.models import *
import pdb,json
from gflux.apps.station.models import Trans
from sqlalchemy.sql import select, and_, or_, func
import pdb
from django.core.management.base import BaseCommand
from optparse import make_option
from sqlalchemy.sql import select, and_, or_, func, update
from sqlalchemy import select as select_directly

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--user_source',help="指定集团值，请参考UserCardType的定义"),
        make_option('--site', help="指定site值，如果不指定，则是所有的站点"),
    )

    def handle(self, **options):

        start_time='2010-12-01 00:00:00'
        end_time='2015-12-31 23:59:59'        
        sites=[]
        if options.has_key('site') and options['site']!=None :
            sites.append(options['site'])
        else :
            # 获取该用户的所有关联site名称
            station_infos=get_all_stations()
            for info in station_infos:
                sites.append(info[0])

        user_source=1
        if options.has_key('user_source') and options['user_source']!=None :
            user_source=int(options['user_source'])

        # 对每一个油站进行分析
        for site in sites: 

            # 建立数据会话
            create_session = get_dash_session_maker(site)
            s = create_session()

            # 对每个station，获取所有的用户列表 
            users={}
            user_total_purchase_amounts={} 		# 记录每个用户的总金额
            user_total_nonfuel_purchase_amounts={} 	# 记录每个用户的非油品总金额
            user_total_fuel_amounts={} 			# 记录每个用户的加油量
            user_promotion_times={} 			# 记录用户接受促销的次数
            try:

                # 遍历该站点的所有交易数据，统计每个用户的消费总金额，非油品总金额和油品数量
                sql = select([
                        Trans.site,Trans.cardnum,Trans.timestamp,Trans.trans_id,
                        Trans.trans_type,Trans.barcode,Trans.price,Trans.quantity,Trans.pay,
                        Trans.desc,Trans.pump_type
                        ]).select_from(Trans.__table__).where(
                    and_(Trans.cardnum>0,Trans.site==site,Trans.quantity>0,
                         Trans.timestamp>=start_time,Trans.timestamp<=end_time)
                    ).order_by('trans_id asc')
                trans_ret = s.execute(sql)
                transactions = trans_ret.fetchall()

                for trans in transactions:
                    # 更新总金额和消费次数
                    if users.has_key(trans.cardnum) :
                        users[trans.cardnum]+=1
                        user_total_purchase_amounts[trans.cardnum]+=trans.pay
                    else :
                        users[trans.cardnum]=1
                        user_total_purchase_amounts[trans.cardnum]=0
                    
                    # 如果此次消费金额为０
                    if trans.pay==0:
                        if user_promotion_times.has_key(trans.cardnum) :
                            user_promotion_times[trans.cardnum]+=1
                        else :
                            user_promotion_times[trans.cardnum]=1                        

                    # 更新非油品总金额和油品数量                    
                    if trans.trans_type==TransType.FUEL:
                        if user_total_nonfuel_purchase_amounts.has_key(trans.cardnum) :
                            user_total_nonfuel_purchase_amounts[trans.cardnum]+=trans.pay
                        else :
                            user_total_nonfuel_purchase_amounts[trans.cardnum]=trans.pay
                    else :
                        if user_total_fuel_amounts.has_key(trans.cardnum) :
                            user_total_fuel_amounts[trans.cardnum]+=trans.quantity
                        else :
                            user_total_fuel_amounts[trans.cardnum]=trans.quantity
            except Exception, e :
                print 'exception:%s'%str(e)
                
            # 对用户根据金额总数排序
            user_array=sorted(user_total_purchase_amounts.items(), key=lambda x:x[1], reverse=True)
            user_prominence={}
            nb_users=len(user_array)
            idx=0

            # 根据用户总金额来计算用户的排名权重
            for user in user_array:
                user_prominence[user[0]]=100-(idx*100+0.0001)/nb_users
                idx+=1

            # 对每一个用户，查询其所有的交易记录，按照先后时间排序
            idx=0
            for user in users:
                
                # 获取该用户的所有交易记录
                sql = select([
                        Trans.site,Trans.cardnum,Trans.timestamp,Trans.trans_id,
                        Trans.trans_type,Trans.barcode,Trans.price,Trans.quantity,Trans.pay,
                        Trans.desc, Trans.pump_type
                        ]).select_from(Trans.__table__).where(
                    and_(Trans.cardnum==user,Trans.site==site,Trans.quantity>0,
                         Trans.timestamp>=start_time,Trans.timestamp<=end_time)
                    ).order_by('trans_id asc')

                trans_ret = s.execute(sql)
                trans_array = trans_ret.fetchall()

                #初始化统计分析的结果

                # 加油时间倾向 prefer_time
                #0  无; 1  早; 2  中; 3  晚
                prefer_time_stat={}
                prefer_time_stat[1]=0
                prefer_time_stat[2]=0
                prefer_time_stat[3]=0
                prefer_time_stat[4]=0

        	# 加满率 prefer_pump_type
        	#0  无;1  加满;2  定额
                prefer_pump_type_stat={}
                prefer_pump_type_stat[1]=0
                prefer_pump_type_stat[2]=0

        	# 加油额 prefer_fuel_cost
        	#0  无规律;1  加很多;2  加很少;3  一般
                prefer_fuel_cost_stat={}
                prefer_fuel_cost_stat[1]=0
                prefer_fuel_cost_stat[2]=0
                prefer_fuel_cost_stat[3]=0

        	# 非油品销售量 prefer_nonfuel_cost
        	#0  无规律;1  买很多;2  买很少;3  一般
                prefer_nonfuel_cost_stat={}
                prefer_nonfuel_cost_stat[1]=0
                prefer_nonfuel_cost_stat[2]=0
                prefer_nonfuel_cost_stat[3]=0

        	#平均加油间隔, 平均间隔的天数，avg_charge_period
                user_charge_timestamps=[]

        	# 对油站的影响程度 efficiency
        	#0  无影响 1/3;1  一般   1/3-2/3;2  严重   2/3
                efficiency_stat={}
                efficiency_stat[1]=0
                efficiency_stat[2]=0

                prev_trans_id=None
                non_fuel_amount=0
                fuel_amount=0
                nb_transactions=0;

                # 扫描该用户的所有记录
                for trans in trans_array:

                    # 一次新的交易的开始
                    if trans.trans_id!=prev_trans_id :

                        # 用户有一次新的交易
                        nb_transactions+=1

                        # 追加加油日期
                        user_charge_timestamps.append(trans.timestamp)

                        # 更新对油站的影响程度(加油时间是否在查询得到的该站当天高峰期内)统计
                        # TODO

                        # 统计终结上一个交易的数据
                        if prev_trans_id!=None:

                            # 油品消费额
                            if fuel_amount<100:
                                prefer_fuel_cost_stat[1]+=1
                            elif fuel_amount<=300:
                                prefer_fuel_cost_stat[2]+=1
                            elif fuel_amount>0:
                                prefer_fuel_cost_stat[3]+=1

                            # 非油品销售额
                            if non_fuel_amount<100:
                                prefer_nonfuel_cost_stat[1]+=1
                            elif fuel_amount<=300:
                                prefer_nonfuel_cost_stat[2]+=1
                            elif non_fuel_amount>0:
                                prefer_nonfuel_cost_stat[3]+=1

                        # 更新消费时间统计
                        if trans.timestamp.hour>=5 and trans.timestamp.hour<11:
                            prefer_time_stat[1]+=1
                        elif trans.timestamp.hour>=11 and trans.timestamp.hour<17:
                            prefer_time_stat[2]+=1
                        elif trans.timestamp.hour>=17 and trans.timestamp.hour<23:
                            prefer_time_stat[3]+=1
                        else :
                            prefer_time_stat[4]+=1

                        # 更新加满率统计
                        if trans.trans_type==TransType.FUEL and trans.pay!=0:
                            if trans.pump_type==PumpType.FILLOUT:
                                prefer_pump_type_stat[1]+=1
                            else :
                                prefer_pump_type_stat[2]+=1

                        # 初始化加油额和非油品销售额
                        if trans.trans_type==TransType.FUEL:
                            fuel_amount=trans.pay
                        else :
                            non_fuel_amount=trans.pay
                                
                    # 同在一次交易内的其它物品
                    else :

                        # 更新加油额和非油品销售额
                        if trans.trans_type==TransType.FUEL:
                            fuel_amount+=trans.pay
                        else :
                            non_fuel_amount+=trans.pay

                    prev_trans_id=trans.trans_id

                # 根据统计得到消费时间倾向结果
                prefer_time=0
                for i in prefer_time_stat.keys():
                    if (prefer_time_stat[i]+0.0001)/nb_transactions>0.5:
                        prefer_time=i
                        break

                # 根据统计得到加满率结果
                prefer_pump_type=0
                for i in prefer_pump_type_stat.keys():
                    if (prefer_pump_type_stat[i]+0.0001)/nb_transactions>0.6:
                        prefer_pump_type=i
                        break

                # 根据统计得到加油额结果
                prefer_fuel_cost=0
                for i in prefer_fuel_cost_stat.keys():
                    if (prefer_fuel_cost_stat[i]+0.0001)/nb_transactions>0.6:
                        prefer_fuel_cost=i
                        break

                # 根据统计得到非油品购买行为结果
                prefer_nonfuel_cost=0
                for i in prefer_nonfuel_cost_stat.keys():
                    if (prefer_nonfuel_cost_stat[i]+0.0001)/nb_transactions>0.6:
                        prefer_nonfuel_cost=i
                        break

                # 根据统计得到平均加油间隔结果
                avg_charge_period=0
                if len(user_charge_timestamps)<=1:
                    avg_charge_period=0
                else :
                    avg_char_period=(user_charge_timestamps[-1]-user_charge_timestamps[0]).total_seconds()/86400/nb_transactions

                # 根据统计得到对油站的效率影响结果
                efficiency=0
                for i in efficiency_stat.keys():
                    if (efficiency_stat[i]+0.0001)/nb_transactions>0.6:
                        efficiency=i
                        break

                # 用户最适合的促销模式 best_promotion_mode
                # TODO

                # 写回该用户的信息到model数据库
                if user_total_fuel_amounts.has_key(user) :
                    total_fuel_amount=user_total_fuel_amounts[user]
                else :
                    total_fuel_amount=0
                if user_total_nonfuel_purchase_amounts.has_key(user) :
                    total_nonfuel_amount=user_total_nonfuel_purchase_amounts[user]
                else :
                    total_nonfuel_amount=0
                if user_total_purchase_amounts.has_key(user) :
                    total_purchase_amount=user_total_purchase_amounts[user]
                else :
                    total_purchase_amount=0

                # 查询用户的现有画像结果
                profile_sql=select_directly([CustomerProfile.cardnum]).where(and_(CustomerProfile.cardnum==user,CustomerProfile.user_source==user_source)).label('tao-gilbarco')
                rs=s.query(profile_sql)
                ret=rs.first()
                if ret[0]!=None:
                    stmt = update(CustomerProfile).where(CustomerProfile.cardnum==user).\
                        values(prefer_time=prefer_time,
                               prefer_pump_type=prefer_pump_type,
                               prefer_fuel_cost=prefer_fuel_cost,
                               prefer_nonfuel_cost=prefer_nonfuel_cost,
                               avg_charge_period=avg_charge_period,
                               efficiency=efficiency,
                               prominence=user_prominence[user],
                               total_fuel_amount=total_fuel_amount,
                               total_nonfuel_purchase_amount=total_nonfuel_amount,
                               total_purchase_amount=total_purchase_amount)
                    s.execute(stmt)
                else:
                    s.execute(CustomerProfile.__table__.insert(),[
                            {'site':site,
			     'cardnum':user,
			     'user_source':user_source,
			     'prefer_time':prefer_time,
                             'prefer_pump_type':prefer_pump_type,
                             'prefer_fuel_cost':prefer_fuel_cost,
                             'prefer_nonfuel_cost':prefer_nonfuel_cost,
                             'avg_charge_period':avg_charge_period,
                             'efficiency':efficiency,
                             'prominence':user_prominence[user],
                             'total_fuel_amount':total_fuel_amount,
                             'total_nonfuel_purchase_amount':total_nonfuel_amount,
                             'total_purchase_amount':total_purchase_amount}])

                idx+=1
                if idx%1000==0:
                    s.commit()
            s.commit()
            s.close()

