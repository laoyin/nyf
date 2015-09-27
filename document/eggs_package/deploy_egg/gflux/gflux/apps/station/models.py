# -*- coding: utf-8 -*-
from django.db import models
import hashlib,datetime
# Create your models here.
from sqlalchemy import (Column, Integer, BigInteger, Numeric, SmallInteger,
                        Float, String, DateTime, ForeignKey,UniqueConstraint,TEXT)
from dash.core.backends.sql import models as dash_models, star
from dash.core.types import enum
import json
from django.utils.translation import ugettext_lazy

# 缓存中统计分布的维度
all_type_args={
    'pump_daily_avg_report':['location'],
    'gun_pump_avg_report':['barcode','location'],
    'non_fuel_sales_avg_report':['location'],
    'non_fuel_sales_scale_report':['location'],
    'top10_non_fuel_sales_avg_report':['location'],
    'pump_hourly_avg_report':['location'],
    'pump_monthly_avg_report':['location'],
    'trans_count_avg_report':['barcode','location']
}

PumpType=enum(FILLOUT=(0,ugettext_lazy(u'加满')),FILLMONEY=(1,ugettext_lazy(u"定额")))
TransType = enum(FUEL=(0, ugettext_lazy(u'油品')), NON_FUEL=(1, ugettext_lazy(u'非油品')))
PaymentType = enum(ALL=(0, ugettext_lazy(u'任意')), UNION_PAY=(1, ugettext_lazy(u'银联卡')), VIP=(2, ugettext_lazy(u'加油卡')), CREDIT=(3, ugettext_lazy(u'信用卡')), CASH=(1000, ugettext_lazy(u'现金')))
CardType = enum(ALL=(0, ugettext_lazy(u'任意')), UNION_PAY=(1, ugettext_lazy(u'银联卡')), VIP=(2, ugettext_lazy(u'加油卡')), CREDIT=(3, ugettext_lazy(u'信用卡')))
DayPeriod = enum(ALL=(0, ugettext_lazy(u'全部')), MORNING=(1, ugettext_lazy(u'早')), NOON=(2, ugettext_lazy(u'中')), NIGHT=(3, ugettext_lazy(u'晚')))
HealthStatus = enum(BOTTLENECK=(0,ugettext_lazy(u'瓶颈')),LOYALTY=(1,ugettext_lazy(u'重复客户')),CUSTOMER=(2,ugettext_lazy(u'客单值')),AVG92=(3,ugettext_lazy(u'92/93#平均单车加油量')),
                    AVG95=(4,ugettext_lazy(u'95/97#平均单车加油量')),CRESTPERCENT=(5,ugettext_lazy(u'高峰期油枪效率')),FILLOUT92=(6,ugettext_lazy(u'92/93#加满率')),
                    FILLOUT95=(7,ugettext_lazy(u'95/97#加满率')),FILLOUT0=(8,ugettext_lazy(u'柴油加满率')),NOMALPERCENT=(9,ugettext_lazy(u'日常油非转化率')),
                    CRESTNONEANDFUELPERCENT=(10,ugettext_lazy(u'高峰期油非转化率')),NONE_ASSOC=(11,ugettext_lazy(u'非油品相关性')),FUEL_NONE_ASSOC=(12,ugettext_lazy(u'油品与非油品相关性')))

class FuelType(dash_models.Base, star.FactMixin) :
    """
    汽油类型  FUEL_92=(300585, u'92号油'),
    """
    __tablename__ = 'fuel_type'

    # 名称
    name = Column(String(32), nullable=False, index=True)
    # 交易数据中的数字编号
    numid = Column(String(32), nullable=False, index=True, unique=True)
    # 中文描述
    description = Column(String(256), nullable=False, index=True)

class FuelTypeRelation(dash_models.Base) :
    """
    油品编号与系统定义油品类型关系
    """
    __tablename__ = 'fuel_type_relation'

    #油品类型
    id=Column(BigInteger, primary_key=True)

    #中文名称
    name = Column(String(255), nullable=False, index=True, unique=True)

    #包含哪些油品编号
    #a json list
    barcodes = Column(TEXT, nullable=False)

class Location(dash_models.Base, star.FactMixin) :
    __tablename__ = 'location'
    """
    加油站所在的地址
    """
    #名称
    name = Column(String(32), nullable=False, index=True)
    #描述
    description = Column(String(256), nullable=False, index=True)
    #站点数量
    nb_sites = Column(SmallInteger, nullable=False, default=0)

class StationDailyStat(dash_models.Base):
    """
    每个站每天的状态量
    """
    __tablename__="station_daily_stat"
    #sha1 主键 date+site
    sha1=Column(String(40),nullable=False,primary_key=True)
    #date
    date=Column(DateTime,ForeignKey('dim_datehour.id'),nullable=False,index=True)
    #site
    site=Column(String(255),nullable=False,index=True)
    #油品销量
    #区域时直接相加
    quantity_fuel=Column(Float, nullable=False, default=0)

    #非油品销量
    #区域时直接相加
    quantity_nonefuel=Column(Float, nullable=False, default=0)

    #高峰期平均出油量
    #高峰期总出油量/高峰期小时数/油枪数
    #区域时分别求分子分母和
    peak_fuel_avg_gun=Column(Float, nullable=False, default=0)
    #高峰期总出油量
    peak_fuel_count=Column(Float, nullable=False, default=0)
    #高峰期小时数
    peak_hour_num=Column(Float, nullable=False, default=0)

    #高峰期峰值
    #高峰期峰值出油量,峰值即是所有的高峰期点中最大的
    #不做,区域无意义
    peak_fuel_biggest=Column(Float, nullable=False, default=0)

    #油品环比百分数 销售量
    #区域时分别求分子分母和
    fuel_mom_percent=Column(Float, nullable=False, default=0)
    #上月同一天的 油品销售量
    pre_mon_quantity_fuel=Column(Float, nullable=False, default=0)

    #非油品环比百分数 销售量
    #区域时分别求分子分母和
    nonefuel_mom_percent=Column(Float, nullable=False, default=0)
    #上月同一天的 非油品销售量
    pre_mon_quantity_nonefuel=Column(Float, nullable=False, default=0)

    #加油卡消费比例
    #加油卡销售额/总销售额
    #区域时分别求分子分母和
    vip_pay_percent=Column(Float, nullable=False, default=0)
    #总销售额
    pay_amout=Column(Float, nullable=False, default=0)
    #加油卡销售额
    vip_pay_amout=Column(Float, nullable=False, default=0)

    #加满率
    #加满方式次数/总加油次数
    #区域时分别求分子分母和
    fuel_fillout_percent=Column(Float, nullable=False, default=0)
    #总加油次数
    fuel_trans_count=Column(Float, nullable=False, default=0)
    #加满次数
    fuel_fillout_count=Column(Float, nullable=False, default=0)

    #非油品对油品比例 销售量
    #区域分别求分子分母和
    #不做,单位都不一样,没意义
    nonefuel_percent=Column(Float, nullable=False, default=0)

    #客单值
    #总销售额/总客户数
    #区域直接相加
    single_customer_pay=Column(Float, nullable=False, default=0)

    def compute_sha1(self):
        #计算sha1
        import hashlib
        sha1=hashlib.sha1()
        sha1.update(str(self.date))
        sha1.update(self.site)
        self.sha1=sha1.hexdigest()

class StationMonthStat(dash_models.Base):
    """
    每个站每月的指标
    """
    __tablename__ = 'station_month_stat'
    #sha1 主键
    #month+site
    sha1=Column(String(40),nullable=False,primary_key=True)
    #year
    year=Column(SmallInteger,nullable=False,index=True)
    #month
    month=Column(SmallInteger,nullable=False,index=True)
    #site
    site=Column(String(255),nullable=False,index=True)
    #total quantity
    total_quantity = Column(Float, nullable=False)
    #油品销量
    quantity_fuel=Column(Float, nullable=False, default=-1)

    #非油品销量
    quantity_nonefuel=Column(Float, nullable=False, default=-1)

    #高峰期平均出油量
    peak_fuel_avg_gun=Column(Float, nullable=False, default=-1)
    #高峰期总出油量
    peak_fuel_count=Column(Float, nullable=False, default=-1)
    #高峰期小时数
    peak_hour_num=Column(Float, nullable=False, default=-1)

    #高峰期峰值
    #高峰期峰值出油量,峰值即是所有的高峰期点中最大的
    peak_fuel_biggest=Column(Float, nullable=False, default=-1)

    #高峰期时段
    #json list
    peak_hour_list=Column(TEXT,default=json.dumps([]))

    #全时段平均车流量
    #json list
    all_hour_avg_car=Column(TEXT,default=json.dumps([0 for x in xrange(24)]))

    #油品环比百分数 销售量
    fuel_mom_percent=Column(Float, nullable=False, default=-1)
    #上月 油品销售量
    pre_mon_quantity_fuel=Column(Float, nullable=False, default=-1)

    #非油品环比百分数 销售量
    nonefuel_mom_percent=Column(Float, nullable=False, default=-1)
    #上月 非油品销售量
    pre_mon_quantity_nonefuel=Column(Float, nullable=False, default=-1)

    #加油卡消费比例
    #加油卡销售额/总销售额
    #区域时分别求分子分母和
    vip_pay_percent=Column(Float, nullable=False, default=-1)
    #总销售额
    pay_amout=Column(Float, nullable=False, default=-1)
    #加油卡销售额
    vip_pay_amout=Column(Float, nullable=False, default=-1)

    #加满率
    #加满方式次数/总加油次数
    #区域时分别求分子分母和
    fuel_fillout_percent=Column(Float, nullable=False, default=-1)
    #总加油次数
    fuel_trans_count=Column(Float, nullable=False, default=-1)
    #加满次数
    fuel_fillout_count=Column(Float, nullable=False, default=-1)

    #非油品对油品比例 销售量
    nonefuel_percent=Column(Float, nullable=False, default=-1)

    #客单值
    single_customer_pay=Column(Float, nullable=False, default=-1)

    #total pay
    total_pay = Column(Float, nullable=False,default=0)

    def compute_sha1(self):
        #计算sha1
        import hashlib
        sha1=hashlib.sha1()
        sha1.update(str(self.year))
        sha1.update(str(self.month))
        sha1.update(self.site)
        self.sha1=sha1.hexdigest()



class StationDailyFuelSales(dash_models.Base):
    """
    每个站每天每种油品每种支付方式的交易量和金额
    """
    __tablename__ = 'station_daily_fuel_sales'
    #sha1 主键
    #date+site+paytype+fuel_type
    sha1=Column(String(40),nullable=False,primary_key=True)
    #date
    date=Column(DateTime,ForeignKey('dim_datehour.id'),nullable=False,index=True)
    #site
    site=Column(String(255),nullable=False,index=True)
    #paytype
    payment_type = Column(SmallInteger, nullable=False, index=True, default=0)
    #fuel_type
    #我们自己定义的标准的barcode
    fuel_type=Column(Integer, nullable=False, index=True)
    #total quantity
    total_quantity = Column(Float, nullable=False)
    #total pay
    total_pay = Column(Float, nullable=False)

    def compute_sha1(self):
        #计算sha1
        import hashlib
        sha1=hashlib.sha1()
        sha1.update(str(self.date))
        sha1.update(self.site)
        sha1.update(str(self.payment_type))
        sha1.update(str(self.fuel_type))
        self.sha1=sha1.hexdigest()

class Trans(dash_models.Base, star.FactMixin):
    """
    原始交易数据，导入脚本import_trans.py
    """
    __tablename__ = 'fact_trans'

    #sha1 唯一性约束
    #摘要值构成:
    #location+site+timestamp+trans_type+trans_id+pump_id+barcode+pay
    sha1=Column(String(40),nullable=False,index=True)
    #交易类型
    trans_type = Column(SmallInteger, nullable=False, index=True, default=0)
    #交易编号
    trans_id = Column(BigInteger, nullable=False, index=True)
    #加油站名
    site = Column(String(255), nullable=False, index=True)
    #刷卡卡号，现金则为0
    cardnum = Column(Numeric(20), nullable=False, index=True, default=0)
    #交易方式
    payment_type = Column(SmallInteger, nullable=False, index=True, default=0)
    #加油方式
    #仅对油品有效
    #0      加满要求,默认
    #1      定额
    pump_type=Column(SmallInteger,nullable=False,index=True,default=0)
    #地址, 目前是写死的，在导入数据时手工指定
    location = Column(SmallInteger, nullable=False, index=True, default=0)
    #油枪号， 导入的数据中有对油枪的编号，非系统自动生成
    pump_id = Column(SmallInteger, nullable=False, index=True)
    #条形码
    barcode = Column(BigInteger, nullable=False, index=True)
    #时间
    timestamp = Column(DateTime, nullable=False, index=True)
    datehour = Column(DateTime, ForeignKey('dim_datehour.id'), nullable=False, index=True)
    #交易数量
    quantity = Column(Float, nullable=False, index=True)
    #金额
    pay = Column(Float, nullable=False)
    #单价
    price = Column(Float, nullable=False)
    #商品名
    desc = Column(String(255), nullable=False)
    #商品单位
    unitname = Column(String(255), nullable=False)
    #第三级行政区划代码
    district=Column(Integer,nullable=False,index=True,default=0)

    def __init__(self,*args,**kwargs):
        super(Trans,self).__init__(*args,**kwargs)
        self.compute_sha1()
        self.compute_pump_type()

    def compute_pump_type(self):
        # if float(self.pay) in [50,100,200,300,400,500,600,700,800]:
        #     self.pump_type=1
        if float(self.pay) % 50 == 0 :
            self.pump_type=1

    def compute_sha1(self):
        #计算sha1
        import hashlib
        sha1=hashlib.sha1()
        sha1.update(str(self.location))
        sha1.update(self.site)
        sha1.update(str(self.timestamp))
        sha1.update(str(self.trans_type))
        sha1.update(str(self.trans_id))
        sha1.update(str(self.pump_id))
        sha1.update(str(self.barcode))
        sha1.update(str(self.pay))
        self.sha1=sha1.hexdigest()

class Card(dash_models.Base, star.FactMixin):
    """
    基于原始数据分析
    """
    __tablename__ = 'card'

    cardnum = Column(Numeric(20), nullable=False, index=True, default=0)
    site = Column(String(255), nullable=False, index=True)
    cardtype = Column(SmallInteger, nullable=False, index=True, default=-1)
    #客户忠诚度
    loyalty = Column(SmallInteger, nullable=False, index=True)

class Item(dash_models.Base):
    """
    基于原始数据分析
    """
    __tablename__ = 'item'

    id = Column(BigInteger, primary_key=True)
    barcode = Column(BigInteger, nullable=False, index=True)
    price = Column(Float, nullable=False)
    desc = Column(String(255), nullable=False)
    unitname = Column(String(255), nullable=False)

class StationItemAssoc(dash_models.Base):
    """
    针对某个站分析相关性
    """
    __tablename__ = 'station_item_assoc'

    id = Column(BigInteger, primary_key=True)
    site=Column(String(255), nullable=False, index=True)
    #时间段，早，中，晚
    period = Column(SmallInteger, nullable=False, index=True, default=0)
    item_from = Column(BigInteger, nullable=False, index=True)
    item_to = Column(BigInteger, nullable=False, index=True)
    #相关性
    weight = Column(Float, nullable=False, default=0.0)

class ItemAssoc(dash_models.Base):
    """
    基于原始数据分析,分析脚本compute_item_assoc.py
    """
    __tablename__ = 'item_assoc'

    id = Column(BigInteger, primary_key=True)
    #时间段，早，中，晚
    period = Column(SmallInteger, nullable=False, index=True, default=0)
    item_from = Column(BigInteger, nullable=False, index=True)
    item_to = Column(BigInteger, nullable=False, index=True)
    #相关性
    weight = Column(Float, nullable=False, default=0.0)


class User(dash_models.Base):
    __tablename__ = 'station_user'
    id = Column(BigInteger,primary_key=True)
    time = Column(DateTime, nullable=False,default= datetime.datetime.now())
    type = Column(SmallInteger, nullable=False)
    name = Column(String(140), nullable=False)
    email = Column(String(140), nullable=False , unique=True)
    password = Column(String(32), nullable=False)
    company = Column(String(256))
    enable_advanced_features = Column(SmallInteger, nullable=False,default=0)
    #0:en 1:zh
    language = Column(SmallInteger,default=0)
    #第三级行政区划代码
    district=Column(Integer,nullable=False,index=True,default=110108)


class File(dash_models.Base):
    __tablename__ = 'station_file'

    id = Column(BigInteger,primary_key=True)
    #上传时间
    time = Column(DateTime,default= datetime.datetime.now() )
    #上传者
    creator = Column(String(40),nullable=False)
    #文件名字
    file_name = Column(String(140) ,nullable=False)

    __table_args__=( UniqueConstraint('creator','file_name'), )


class UserStation(dash_models.Base):
    __tablename__ = 'station_userstation'
    id = Column(BigInteger,primary_key=True)
    #用户id
    user_id = Column(SmallInteger, nullable=False,  default=0)
    #station 对应于Station字段中的name字段
    station = Column(String(140), nullable=False)
    #添加时间
    time = Column(DateTime, nullable=False,default= datetime.datetime.now())

    __table_args__=( UniqueConstraint('user_id','station'), )



class StationNoneFuelTop(dash_models.Base):
    __tablename__ = 'station_stationnonefueltop'

    id = Column(BigInteger,primary_key=True)
    #站点名
    station=Column(String(140), nullable=False,unique=True)
    #top
    top=Column(TEXT)



class StationFuelType(dash_models.Base):
    __tablename__ = 'station_stationfueltype'

    id = Column(BigInteger,primary_key=True)
    # 站点名
    station=Column(String(140))
    # 油品条形码
    barcode=Column(BigInteger, default=0)
    # 油品名称
    description=Column(String(256))
    #价格
    price = Column(Float,default=0.0)

    __table_args__=( UniqueConstraint('station','barcode'), )


#自定义标签表
class Tag(dash_models.Base):
    __tablename__ = 'tag'
    id = Column(BigInteger,primary_key=True)
    #用户id
    user_id = Column(SmallInteger, nullable=False,  default=0)
    #标签
    tag = Column(String(255), nullable=False)

    __table_args__=( UniqueConstraint('user_id','tag'), )

#用户油站与自定义标签关系表
class UserStationTagRelation(dash_models.Base):
    __tablename__ = 'user_station_tag_relation'
    id = Column(BigInteger,primary_key=True)
    #用户id
    user_id = Column(SmallInteger, nullable=False,  default=0)
    #station 对应于Station字段中的name字段
    station = Column(String(140), nullable=False)
    #标签的id
    tag_id = Column(BigInteger, ForeignKey('tag.id'),nullable=False)
    #站点描述信息
    station_desc = Column(String(255), nullable=False)

    __table_args__=( UniqueConstraint('user_id','station','tag_id'), )

#油站健康指标表
class StationHealthStatus(dash_models.Base):
    __tablename__ = 'station_health_status'
    id = Column(BigInteger,primary_key=True)
    #站点
    site = Column(String(140), nullable=False)
    #站点描述
    desc = Column(String(255), nullable=False)
    #时间
    date=Column(DateTime,nullable=False,index=True)
    #健康指标类型，0：瓶颈 1 重复客户 2 客单值 3 92/93#平均单车加油量 4 95/97#平均单车加油量
    #5 高峰期油枪效率 6 92/93#加满率 7 95/97#加满率 8 柴油加满率 9 日常油非转化率 10 高峰期油非转化率
    #11 非油品相关性 12 油品与非油品的相关性
    type = Column(SmallInteger,nullable=False)
    #健康指标信息
    info = Column(String(140), nullable=False)
    #健康指标值（type为0时，value:-1有瓶颈，1无瓶颈，其他为指标的临界值）
    value = Column(Float, nullable=False)
