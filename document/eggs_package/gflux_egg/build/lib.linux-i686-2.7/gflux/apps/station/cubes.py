# -*- coding: utf-8 -*-

from sqlalchemy.sql import distinct
from dash.core.backends.sql.cubes import Cube, Aggregation
from gflux.apps.common.models import DimDateHour,Station
from . import models

class CardCube(Cube):
    fact_table = models.Card

    measures = {
        'count': Aggregation.count(fact_table.id),
    }

    dims = {
        'cardtype': fact_table.cardtype,
        'loyalty': fact_table.loyalty,
        'site': fact_table.site,
    }

class StationDailyStatCube(Cube):
    #宿主表格
    fact_table=models.StationDailyStat

    #join查询时依靠的字段
    joins={
        #join DimDateHour表时依赖关系
        DimDateHour: DimDateHour.id == fact_table.date,

        #join Station表时依赖关系
        Station:Station.name==fact_table.site,
    }

    #统计量计算表达式
    measures={
        'quantity_fuel':Aggregation.sum(fact_table.quantity_fuel),
        'quantity_nonefuel':Aggregation.sum(fact_table.quantity_nonefuel),
        'peak_fuel_avg_gun':Aggregation.sum(fact_table.peak_fuel_avg_gun),
        'peak_fuel_biggest':Aggregation.sum(fact_table.peak_fuel_biggest),
        'fuel_mom_percent':Aggregation.sum(fact_table.fuel_mom_percent),
        'nonefuel_mom_percent':Aggregation.sum(fact_table.nonefuel_mom_percent),
        'vip_pay_percent':Aggregation.sum(fact_table.vip_pay_percent),
        'fuel_fillout_percent':Aggregation.sum(fact_table.fuel_fillout_percent),
        'nonefuel_percent':Aggregation.sum(fact_table.nonefuel_percent),
        'single_customer_pay':Aggregation.sum(fact_table.single_customer_pay),
        'peak_fuel_count':Aggregation.sum(fact_table.peak_fuel_count),
        'peak_hour_num':Aggregation.sum(fact_table.peak_hour_num),
        'nb_guns':Aggregation.sum(Station.nb_guns),
        'fuel_fillout_count':Aggregation.sum(fact_table.fuel_fillout_count),
        'fuel_trans_count':Aggregation.sum(fact_table.fuel_trans_count),
        'vip_pay_amout':Aggregation.sum(fact_table.vip_pay_amout),
        'pay_amout':Aggregation.sum(fact_table.pay_amout),
        'pre_mon_quantity_fuel':Aggregation.sum(fact_table.pre_mon_quantity_fuel),
        'pre_mon_quantity_nonefuel':Aggregation.sum(fact_table.pre_mon_quantity_nonefuel),
    }

    #过滤表达式
    dims={
        'year': DimDateHour.year,
        'month': DimDateHour.month,
        'day': DimDateHour.day,
        'city':Station.city,
        'province':Station.province,
        'district':Station.district,
        'name':Station.name,
        'site': fact_table.site,
    }

    #select表达式
    details={

    }

class StationMonthStatCube(Cube):
    #宿主表格
    fact_table=models.StationMonthStat

    #join查询时依靠的字段
    joins={
        #join DimDateHour表时依赖关系
        DimDateHour: DimDateHour.month == fact_table.month,
        DimDateHour: DimDateHour.year==fact_table.year,

        #join Station表时依赖关系
        Station:Station.name==fact_table.site,
    }

    #统计量计算表达式
    measures={
        #加油量统计
        'quantity': Aggregation.sum(fact_table.total_quantity),
        'quantity_fuel':Aggregation.sum(fact_table.quantity_fuel),
        'quantity_nonefuel':Aggregation.sum(fact_table.quantity_nonefuel),
        'peak_fuel_avg_gun':Aggregation.sum(fact_table.peak_fuel_avg_gun),
        'peak_fuel_biggest':Aggregation.sum(fact_table.peak_fuel_biggest),
        'fuel_mom_percent':Aggregation.sum(fact_table.fuel_mom_percent),
        'nonefuel_mom_percent':Aggregation.sum(fact_table.nonefuel_mom_percent),
        'vip_pay_percent':Aggregation.sum(fact_table.vip_pay_percent),
        'fuel_fillout_percent':Aggregation.sum(fact_table.fuel_fillout_percent),
        'nonefuel_percent':Aggregation.sum(fact_table.nonefuel_percent),
        'single_customer_pay':Aggregation.sum(fact_table.single_customer_pay),
        'peak_fuel_count':Aggregation.sum(fact_table.peak_fuel_count),
        'peak_hour_num':Aggregation.sum(fact_table.peak_hour_num),
        'nb_guns':Aggregation.sum(Station.nb_guns),
        'fuel_fillout_count':Aggregation.sum(fact_table.fuel_fillout_count),
        'fuel_trans_count':Aggregation.sum(fact_table.fuel_trans_count),
        'vip_pay_amout':Aggregation.sum(fact_table.vip_pay_amout),
        'pay_amout':Aggregation.sum(fact_table.pay_amout),
        'pre_mon_quantity_fuel':Aggregation.sum(fact_table.pre_mon_quantity_fuel),
        'pre_mon_quantity_nonefuel':Aggregation.sum(fact_table.pre_mon_quantity_nonefuel),
        'pay':Aggregation.sum(fact_table.total_pay),
    }

    #过滤表达式
    dims={
        'year': fact_table.year,
        'month': fact_table.month,
        'city':Station.city,
        'province':Station.province,
        'district':Station.district,
        'name':Station.name,
        'site': fact_table.site,
    }

    #select表达式
    details={

    }

class StationDailyFuelSalesCube(Cube):
    #宿主表格
    fact_table=models.StationDailyFuelSales

    #join查询时依靠的字段
    joins={
        #join DimDateHour表时依赖关系
        DimDateHour: DimDateHour.id == fact_table.date,

        #join Station表时依赖关系
        Station:Station.name==fact_table.site,
    }

    #统计量计算表达式
    measures={
        #销售额统计
        'pay':Aggregation.sum(fact_table.total_pay),
        #加油量统计
        'quantity': Aggregation.sum(fact_table.total_quantity),
    }

    #过滤表达式
    dims={
        'year': DimDateHour.year,
        'month': DimDateHour.month,
        'day': DimDateHour.day,
        'fuel_type':fact_table.fuel_type,
        'payment_type': fact_table.payment_type,
        'city':Station.city,
        'province':Station.province,
        'district':Station.district,
        'name':Station.name,
        'site': fact_table.site,
    }

    #select表达式
    details={

    }


class TransCube(Cube):
    fact_table = models.Trans

    joins = {
        DimDateHour: DimDateHour.id == fact_table.datehour,
        models.Card: models.Card.cardnum == fact_table.cardnum,
    }

    measures = {
        #所有交易数，1笔交易可以包含多次交易
        'count': Aggregation.count(fact_table.id),
        #所有交易笔数
        #等同与所有进站车数（1车1笔） 交易类型为油品交易
        #等同客户数 交易类型为非油品
        'trans_count': Aggregation.count(distinct(fact_table.trans_id)),
        #定额加油的笔数
        'fix_pump_count' : Aggregation.sum(fact_table.pump_type),
        #油非转化率
        'non_oil_trans_count' : Aggregation.sum(fact_table.trans_type),
        #所有销售额
        'pay': Aggregation.sum(fact_table.pay),
        #所有交易量
        'quantity': Aggregation.sum(fact_table.quantity),
        #交易种类
        'category_count': Aggregation.count(distinct(fact_table.barcode)),
        #卡号种类
        'card_count': Aggregation.count(distinct(fact_table.cardnum)),
        #时段种类
        'hours': Aggregation.count(distinct(fact_table.datehour)),
        'pump_count':Aggregation.count(distinct(fact_table.pump_id)),
    }

    dims = {
        'trans_type': fact_table.trans_type,
        'site': fact_table.site,
        'pump_id': fact_table.pump_id,
        'barcode': fact_table.barcode,
        'location': fact_table.location,
        'datehour': fact_table.datehour,
        'quantity': fact_table.quantity,
        'payment_type': fact_table.payment_type,
        'year': DimDateHour.year,
        'month': DimDateHour.month,
        'day': DimDateHour.day,
        'week': DimDateHour.week,
        'day_of_week': DimDateHour.day_of_week,
        'hour': DimDateHour.hour,
        'loyalty': models.Card.loyalty,
        'cardnum':fact_table.cardnum,
        'trans_id':fact_table.trans_id,
        'pump_type':fact_table.pump_type,
    }

    details = {
        'unitname': fact_table.unitname,
        'desc': fact_table.desc,
        'id':fact_table.id,
    }
