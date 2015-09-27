#coding=utf-8

#django command import
from django.core.management.base import BaseCommand
from django.conf import settings

#all model import
from dash.core.backends.sql.models import *
from gflux.apps.station.models import *
from gflux.apps.common.models import *
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm import sessionmaker

#sys lib import
from datetime import *
import sys, pdb

#车用汽油标准
#id=1101+省行政区划代码前2位+标准代数2位+汽油牌号
china_car_fuel_gb=[]

#第五阶段国标 2018正式供应
china_car_fuel_gb+=[
    dict(id=1101000589,
        #国IV标准中为90号
        name="89号汽油(国V)",
        #油站系统中使用的编号
        barcodes=[

    ]),
    dict(id=1101000592,
        #国IV标准中为93号
        name="92号汽油(国V)",
        #油站系统中使用的编号
        barcodes=[
            300585,60206059,
    ]),
    dict(id=1101000595,
        #国IV标准中为97号
        name="95号汽油(国V)",
        #油站系统中使用的编号
        barcodes=[
            300586,60206060,
    ]),
    dict(id=1101000598,
        #
        name="98号汽油(国V)",
        #油站系统中使用的编号
        barcodes=[
            60209058,
    ]),
    dict(id=1101000505,
        name="5号柴油(国V)",
        #油站系统中使用的编号
        barcodes=[

    ]),
    dict(id=1101000500,
        name="0号柴油(国V)",
        #油站系统中使用的编号
        barcodes=[
            300603,60189274,300566,16714339,4603112,
    ]),
    dict(id=1101000510,
        name="-10号柴油(国V)",
        #油站系统中使用的编号
        barcodes=[
            300602,
    ]),
    dict(id=1101000520,
        name="-20号柴油(国V)",
        #油站系统中使用的编号
        barcodes=[
            300567,300601,
    ]),
    dict(id=1101000535,
        name="-35号柴油(国V)",
        #油站系统中使用的编号
        barcodes=[

    ]),
]

#第四阶段国标 2014正式供应
china_car_fuel_gb+=[
    dict(id=1101000490,
        #国IV标准中为90号
        name="90号汽油(国IV)",
        #油站系统中使用的编号
        barcodes=[
            300003,
    ]),
    dict(id=1101000493,
        #国IV标准中为93号
        name="93号汽油(国IV)",
        #油站系统中使用的编号
        barcodes=[
            300656,93,12827124,989976,300007,300590,6448894,1910560,
    ]),
    dict(id=1101000497,
        #国IV标准中为97号
        name="97号汽油(国IV)",
        #油站系统中使用的编号
        barcodes=[
            300657,97,9661572,5915711,300014,300591,2523955,8899677,
    ]),
    dict(id=1101000498,
        #国IV标准中为98号
        name="98号汽油(国IV)",
        #油站系统中使用的编号
        barcodes=[
            300653,
    ]),
    dict(id=1101000405,
        name="5号柴油(国IV)",
        #油站系统中使用的编号
        barcodes=[

    ]),
    dict(id=1101000400,
        name="0号柴油(国IV)",
        #油站系统中使用的编号
        barcodes=[

    ]),
    dict(id=1101000410,
        name="-10号柴油(国IV)",
        #油站系统中使用的编号
        barcodes=[

    ]),
    dict(id=1101000420,
        name="-20号柴油(国IV)",
        #油站系统中使用的编号
        barcodes=[

    ]),
    dict(id=1101000435,
        name="-35号柴油(国IV)",
        #油站系统中使用的编号
        barcodes=[

    ]),
]

#第三阶段国标 2007.7.1正式供应
china_car_fuel_gb+=[
    dict(id=1101000390,
        #国IV标准中为90号
        name="90号汽油(国III)",
        #油站系统中使用的编号
        barcodes=[

    ]),
    dict(id=1101000393,
        #国IV标准中为93号
        name="93号汽油(国III)",
        #油站系统中使用的编号
        barcodes=[
            60090935,300060,
    ]),
    dict(id=1101000397,
        #国IV标准中为97号
        name="97号汽油(国III)",
        #油站系统中使用的编号
        barcodes=[
            60090936,300061,
    ]),
    dict(id=1101000398,
        #国IV标准中为98号
        name="98号汽油(国III)",
        #油站系统中使用的编号
        barcodes=[
            300314,
    ]),
    dict(id=1101000305,
        name="5号柴油(国III)",
        #油站系统中使用的编号
        barcodes=[

    ]),
    dict(id=1101000300,
        name="0号柴油(国III)",
        #油站系统中使用的编号
        barcodes=[
            300472,
    ]),
    dict(id=1101000310,
        name="-10号柴油(国III)",
        #油站系统中使用的编号
        barcodes=[
            300471,
    ]),
    dict(id=1101000320,
        name="-20号柴油(国III)",
        #油站系统中使用的编号
        barcodes=[
            300470,
    ]),
    dict(id=1101000335,
        name="-35号柴油(国III)",
        #油站系统中使用的编号
        barcodes=[
            300550,
    ]),
    dict(id=1101000350,
        name="-50号柴油(国III)",
        #油站系统中使用的编号
        barcodes=[

    ]),
]

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            sm=get_dash_session_maker()
            s=sm()
            for gb in china_car_fuel_gb:
                gb['barcodes']=json.dumps(gb['barcodes'])
                obj=FuelTypeRelation(**gb)
                s.add(obj)
                try:
                    s.commit()
                except Exception,e:
                    s.rollback()
        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
