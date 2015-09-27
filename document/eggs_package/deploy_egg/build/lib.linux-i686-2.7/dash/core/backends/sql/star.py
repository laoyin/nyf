# -*- coding: utf-8 -*-

from sqlalchemy import Column, BigInteger, SmallInteger, Date, DateTime
#from sqlalchemy.ext.declarative import declared_attr

class DimMixin(object):
    pass

class DimDateMixin(DimMixin):
    """
    将每一天的datetime数据抽取出来存入数据库
    """
    id = Column(Date, primary_key=True)
    year = Column(SmallInteger, index=True, nullable=False)
    month = Column(SmallInteger, index=True, nullable=False)
    day = Column(SmallInteger, index=True, nullable=False)
    week = Column(SmallInteger, index=True, nullable=False)
    day_of_week = Column(SmallInteger, index=True, nullable=False)
    quater = Column(SmallInteger, index=True, nullable=False)

class DimDateHourMixin(DimMixin):
    """
    将每一小时的datetime数据抽取出来存入数据库
    """
    id = Column(DateTime, primary_key=True)
    year = Column(SmallInteger, index=True, nullable=False)
    month = Column(SmallInteger, index=True, nullable=False)
    day = Column(SmallInteger, index=True, nullable=False)
    hour = Column(SmallInteger, index=True, nullable=False)
    week = Column(SmallInteger, index=True, nullable=False)
    day_of_week = Column(SmallInteger, index=True, nullable=False)
    quater = Column(SmallInteger, index=True, nullable=False)

class FactMixin(object):
    id = Column(BigInteger, primary_key=True)
