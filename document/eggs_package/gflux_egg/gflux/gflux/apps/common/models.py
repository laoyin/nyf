# -*- coding: utf-8 -*-

from dash.core.backends.sql import models, star
from sqlalchemy import Column, String, Integer, DateTime,UniqueConstraint,BigInteger,TEXT

class DimChinaProvinceCityDistrict(models.Base):
    """
    中国三级行政区划
    省市区/县
    """
    __tablename__ = 'dim_chinaprovincecitydistrict'

    #区划代码
    id=Column(Integer,primary_key=True)

    #名称
    name=Column(String(256), nullable=False, index=True)

    #级别
    level=Column(Integer, nullable=False, index=True)

    #上级代码
    parent=Column(Integer, nullable=False, index=True)

class SiteDayBatch(models.Base):
    """
    油站逻辑天定义
    """
    __tablename__='sitedaybatch'

    #主键
    id = Column(BigInteger, primary_key=True)

    #加油站名
    site=Column(String(64), nullable=False, index=True)

    #现实日期
    day=Column(DateTime, nullable=False, index=True)

    #逻辑日期开始时间
    day_open=Column(DateTime, nullable=False, index=True)

    #逻辑日期结束时间
    day_close=Column(DateTime, nullable=False, index=True)

    #联合唯一
    __table_args__=( UniqueConstraint('site','day'), )

class DimDateHour(models.Base, star.DimDateHourMixin):
    __tablename__ = 'dim_datehour'

class Station(models.Base, star.FactMixin) :
    __tablename__ = 'station'

    #名称
    name = Column(String(255), nullable=False, unique=True, index=True)
    #描述
    description = Column(String(64), nullable=False, index=True)
    #油站所在省份地址编号
    #等于local表中的id
    locid = Column(Integer, default=0)
    #加油枪数量
    nb_guns = Column(Integer, default=0)

    #加油机/加油枪分布方式
    #a json dict
    #{'machines':[{name:1号加油机,value:[1,2,3,4]}],
    #'passages':[{name:1号通道,value:[1,2,3,4]}],
    #'level':[{name:1号油位,value:[1,2,3,4]}],
    #'column':[{name:1号列道,value:[1,2,3,4]}],
    #}
    machine_passage = Column(TEXT, nullable=True)
    #电话
    phone = Column(String(64), nullable=True)
    #加油站地址
    address = Column(String(2048), nullable=True)
    #在用加油机品牌
    brand = Column(String(64), nullable=True)
    #加油机与油站入口距离
    distance = Column(Integer, default=0)
    #油站数据最早的时间
    earliest_date = Column(DateTime, nullable=True)
    #油站数据最新的时间
    latest_date = Column(DateTime, nullable=True)
    #所有油枪号
    id_guns = Column(String(2048), nullable=True)
    #第三级行政区划代码
    district=Column(Integer,nullable=False,index=True,default=0)
    #第二级行政区划代码
    city=Column(Integer,nullable=False,index=True,default=0)
    #第一级行政区划代码
    province=Column(Integer,nullable=False,index=True,default=0)
