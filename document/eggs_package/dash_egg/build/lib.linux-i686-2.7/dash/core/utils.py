# -*- coding: utf-8 -*-
from django.conf import settings
import re,time

def list_first_item(value):
    try:
        if not hasattr(value[0], '__iter__'):
            return [value[0]]
        else:
            return value[0]
    except Exception:
        return None

def float_equals(a, b):
    return abs(a - b) <= 1e-6

def uid(class_name):
    #将大写字母换成小写并在字母前加前缀_
    return re.sub(r'([A-Z])', r'_\1', class_name).lower()[1:]

#获取图表的功能描述信息
def get_dash_description(uid):
    data=dict(
        oil_sales_daily_trend_dash=\
        "显示油品销售额趋势,按照油品类型分别统计,不同的油品类型显示为不同的曲线,统计步长为每小时.\
        左上方饼图显示了油品销售额的百分比组成情况,趋势图使用了折线面积图,\
        多条曲线时数值叠加显示的方式进行渲染.",

        pump_daily_trend_dash=\
        "显示油品加油量趋势,按照油品类型分别统计,不同的油品类型显示为不同的曲线,统计步长为每小时.\
        左上方饼图显示了油品加油量的百分比组成情况,趋势图使用了折线面积图,\
        多条曲线时数值叠加显示的方式进行渲染.",

        trans_daily_trend_dash=\
        "显示进站车辆趋势,按照油品类型分别统计,不同的油品类型显示为不同的曲线,统计步长为每小时.\
        左上方饼图显示了进站车辆的百分比组成情况,趋势图使用了折线面积图,\
        多条曲线时数值叠加显示的方式进行渲染.",

        pump_car_daily_trend_dash=\
        "显示平均每车加油量趋势,按照油品类型分别统计,不同的油品类型显示为不同的曲线,统计步长为每小时.\
        左上方饼图显示了平均每车加油量的百分比组成情况,趋势图使用了折线面积图,\
        多条曲线时数值叠加显示的方式进行渲染.",

        oil_trend_dash=\
        "显示指定月加油量趋势,直接统计所有油品,统计步长为每天.趋势图使用了折线面积图进行渲染.",

        oil_mo_m_trend_dash=\
        "显示指定月加油量环比,直接统计所有油品,统计步长为每天.趋势图使用了平滑曲线图,\
        多条曲线时不叠加显示的方式进行渲染.",

        oil_yo_y_trend_dash=\
        "显示指定月加油量同比,直接统计所有油品,统计步长为每天.趋势图使用了平滑曲线图,\
        多条曲线时不叠加显示的方式进行渲染.",

        oil_trend_between_two_days_dash=\
        "对比显示两天的加油量,直接统计所有油品,统计步长为每小时.趋势图使用了平滑曲线图,\
        多条曲线时不叠加显示的方式进行渲染.",

        gun_pump_time_daily_trend_dash=\
        "显示油枪出油时间,按照油枪号分别统计,统计步长为每小时,趋势图使用了折线面积图,\
        多条曲线时数值叠加的方式进行渲染.",

        gun_machine_time_daily_trend_dash=\
        "显示油机出油时间(每出%s公升油换算为1分钟),按照油机分别统计,统计步长为每小时,\
        趋势图使用了折线面积图,多条曲线时数值叠加的方式进行渲染."%settings.PUMP_TRANS_TIME,

        passage_time_daily_trend_dash=\
        "显示通道出油时间(每出%s公升油换算为1分钟),按照通道分别统计,统计步长为每小时,\
        趋势图使用了折线面积图,多条曲线时数值叠加的方式进行渲染."%settings.PUMP_TRANS_TIME,

        station_peak_period_time_defined_dash=\
        "在全天的加油交易笔数曲线中，在0-8点，8-16点，\
        16-24点三个时段的每个时段中取一个交易笔数最高点和一个交易笔数最低点，\
        将此六个点的值相加除以6,得到一个平均值V,高峰期的定义为时段交易笔数大于等于1.2*V的集合.\
        负荷峰谷差异定义为取全天加油量最大的3个点，和最小的6个点，各自平均后用最大平均值除以最小平均值的结果.",

        goods_s_k_u_count_dash=\
        "总SKU数统计的是非油品商品种类数量,总销售额统计的是总的非油品销售额,\
        总客户数统计的是总的非油品交易笔数(即客流量,视为客户数),总客单值等于总销售额除以总客户数.",

        goods_sales_daily_trend_dash=\
        "显示非油品销售额趋势,直接统计所有非油品交易,统计步长为每小时,趋势图使用了折线面积图渲染.",

        goods_sales_per_people_daily_trend_dash=\
        "显示非油品销售客单值,直接统计所有非油品交易的金额和交易笔数(即客流量,视为客户数),\
        统计步长为每小时,趋势图使用了折线面积图渲染.",

        goods_rank_month_trend_dash=\
        "显示销售额最高的十种非油品商品.",

        goods_trend_dash=\
        "显示指定月非油品销售额趋势,直接统计所有非油品交易,统计步长为每天,趋势图使用了折线面积图渲染.",

        goods_mo_m_trend_dash=\
        "显示指定月非油品销售额环比,直接统计所有非油品交易,统计步长为每天,趋势图使用了平滑曲线图,\
        多条曲线时不叠加显示的方式进行渲染.",

        goods_yo_y_trend_dash=\
        "显示指定月非油品销售额同比,直接统计所有非油品交易,统计步长为每天,趋势图使用了平滑曲线图,\
        多条曲线时不叠加显示的方式进行渲染.",

        goods_trend_between_two_days_dash=\
        "对比显示两天的非油品销售额,直接统计所有非油品交易,统计步长为每小时.趋势图使用了平滑曲线图,\
        多条曲线时不叠加显示的方式进行渲染.",

        oil_goods_proportion_dash=\
        "显示指定月内非油品占油品的交易比例,各自统计油品和非油品交易笔数之后进行计算,统计步长为指定月内相同的小时值,\
        趋势图使用了折线面积图进行渲染.",

        oil_goods_assoc_dash=\
        "显示油品与非油品相关性,相关性结果为抽样离线计算的结果.",

        between_goods_assoc_dash=\
        "显示非油品之间的相关性,相关性结果为抽样离线计算的结果.",

        customer_v_i_p_counter_dash=\
        "显示当前总的VIP加油卡张数",

        customer_v_i_p_loyalty_proportion_dash=\
        "显示指定月忠诚客户占总VIP客户的比例,使用相同VIP加油卡加油两次即视为忠诚客户.",

        customer_v_i_p_cost_trend_proportion_dash=\
        "显示VIP客户消费趋势,上升或下降相应百分比的VIP客户数.",

        customer_v_i_p_monthly_loyalty_dash=\
        "显示近一年的忠诚客户比例趋势,统计所有的VIP卡交易笔数,统计步长为每月,趋势图使用了柱状图进行渲染.",

        customer_cost_trend_dash=\
        "显示指定月客户消费趋势,分别统计忠诚客户,VIP客户,所有客户的消费额,统计步长为每天,\
        趋势图使用了平滑曲线图,多条曲线时数值叠加显示的方式进行渲染."
    )
    data={}
    return data.get(uid,uid)

#根据卡号返回消费类型,1:普通银行卡,2:加油卡,3:信用卡,1000:现金
def getPaymentTypeByCard(card,card_fromat=None):
    if card_fromat!=None:
        reobj = re.compile(card_fromat)
        result = reobj.match(card)

        #加油卡
        if result:
            return 2

    #银行卡号最多为19位
    if len(card)>19:
        return 1000

    #银行卡至少为16位,信用卡至少为14位
    if len(card)>=14:

        #前六位为银行卡的BIN
        front=int(card[:6])

        #信用卡BIN分配如下:
        #威士卡（VISA）:400000—499999;万事达卡（MasterCard）:510000—559999;
        #运通卡（American Express）:340000—349999，370000—379999;
        #大来卡（DinersClub）:300000—305999，309500—309599,360000—369999，380000—399999;
        #JCB卡（JCB）:352800—358999
        if (front>=300000 and front<=305999) or (front>=309500 and front<=305999) or \
            (front>=360000 and front<=369999) or (front>=380000 and front<=399999) or \
            (front>=352800 and front<=358999) or (front>=340000 and front<=349999) or \
            (front>=370000 and front<=379999) or (front>=510000 and front<=559999) or \
            (front>=400000 and front<=499999):
            return 3

        else:
            if len(card)>=16:
                card_front=card[:1]
                #普通银行卡以6,9开头,多数为6
                if card_front=='6' or card_front=='9':
                    return 1
                else:
                    return 1000

    #现金
    return 1000

#序列化交易编号
def compute_trans_id(data_time,shard_id,site_id,gun_id,money) :

    # 交易时间,32位
    data_time=long(int(data_time))
    data_time=data_time<<32

    #服务器编号，6位，最多64台
    shard_id=shard_id<<26

    #油站编号,10位，最多每个服务器上1024个
    site_id=site_id<<16

    #油枪号，7位，一个油站最多128个
    gun_id=gun_id<<9

    #金额 9位
    result=data_time+shard_id+site_id+gun_id+money
    
    return result

#反序列化交易编号
def deserialize_trans_id(long_trans_id):
    num=long(long_trans_id)
    # 获取高32位的时间
    time=int(num>>32)
    # 获取低32 位
    num=num & 0xFFFFFFFF
    shard_id=num>>26
    #取出低26位
    num=num & 0x3FFFFFF
    site_id=num>>16
    #取出低16位
    num=num & 0xFFFF
    gun_id=num>>9
    #获取金额
    money=num & 0x1FF
    return (time, shard_id, site_id, gun_id, money)
