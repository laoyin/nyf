# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

from django.conf import settings
from datetime import datetime, timedelta
from dash.core import helper
from dash.core import fields
from dash.core import reports
from dash.core.types import enum
from dash.core.types import overrides
from dash.core.backends.sql.models import get_dash_session_maker
from models import Trans, TransType, PaymentType, CardType, DayPeriod,HealthStatus,\
    FuelType, Location, UserStation, User,StationFuelType,StationNoneFuelTop
from dash.core.utils import uid
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from gflux.apps.common.models import *
from . import cubes
from django.core.cache import cache
from sqlalchemy.sql import select, and_, or_, func
from sqlalchemy import select as select_directly
from sqlalchemy import update
import math,json,copy
import pdb,traceback,logging,re
from gflux.apps.station.models import all_type_args
from gflux.apps.common.models import Station
from gflux.apps.station.sql_utils import *
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.core.management import call_command

#默认时间
DEFAULT_DATE = datetime(2014, 07, 30)

#set logger
ajax_logger=logging.getLogger('ajax')

"""
报表接口 report
"""

# 基于交易记录的分析报告
class TransReport(helper.CubePlanarReport):
    __abstract__ = True
    cube = cubes.TransCube()

    @overrides(helper.CubePlanarReport)
    def init_conditions(self,**context):
        conditions = []
        form = context['form'].cleaned_data
        try:
            self.site = form['site']
            if self.site:
                conditions.append(self.cube.d.site == self.site)
        except:
            pass

        try:
            self.payment_type = int(form['payment_type'])
            if self.payment_type > 0:
                conditions.append(self.cube.d.payment_type == self.payment_type)
        except:
            pass

        try:
            self.date = form['date']

            if context.get('on_between_two_days',False):
                self.other_date=form['other_date']
                conditions.append(or_(and_(
                    self.cube.d.datehour >= self.date,
                    self.cube.d.datehour < self.date + timedelta(days=1)
                ),and_(
                    self.cube.d.datehour >= self.other_date,
                    self.cube.d.datehour < self.other_date + timedelta(days=1)
                )))
            else:
                conditions.append(self.cube.d.datehour >= self.date)
                conditions.append(self.cube.d.datehour < self.date + timedelta(days=1))
        except:
            pass

        try:
            self.start_date = form['start_date']
            self.end_date = form['end_date']

            if context.get('on_MoM_or_YoY',False):
                distance=rrule.rrule(rrule.DAILY,dtstart=self.start_date,
                    until=self.end_date).count()-1
                #环比
                if self.MoM_or_YoY=='MoM':
                    self.tmp_end_date=self.start_date-timedelta(days=1)
                    self.tmp_start_date=self.tmp_end_date-timedelta(days=distance)
                #同比
                else:
                    self.tmp_end_date=self.start_date-relativedelta(years=1)
                    self.tmp_start_date=self.tmp_end_date-timedelta(days=distance)

                conditions.append(or_(and_(
                    self.cube.d.datehour >= self.start_date,
                    self.cube.d.datehour < self.end_date+timedelta(days=1)
                ),and_(
                    self.cube.d.datehour >= self.tmp_start_date,
                    self.cube.d.datehour < self.tmp_end_date+timedelta(days=1)
                )))
            else:
                conditions.append(self.cube.d.datehour >= self.start_date)
                conditions.append(self.cube.d.datehour < self.end_date+timedelta(days=1))
        except:
            pass

        try:
            self.start_hour = form['start_hour']
            self.end_hour = form['end_hour']
            conditions.append(self.cube.d.hour >= self.start_hour)
            conditions.append(self.cube.d.hour <= self.end_hour)
        except:
            pass

        try:
            self.fuel_type=int(form['fuel_type'])
            if self.fuel_type>0:
                conditions.append(self.cube.d.barcode==self.fuel_type)
        except:
            pass

        try:
            system_fuel_type=int(form['system_fuel_type'])
            if system_fuel_type>0:
                conditions.append(self.cube.d.fuel_type==system_fuel_type)
        except:
            pass

        return conditions

# 指数报告

class IndexReport(reports.Report):
    __abstract__ = True
    cube = cubes.TransCube()

    def build_conditions(self,**context):
        #取得查询条件
        conditions = []
        form = context['form'].cleaned_data
        try:
            #取得区域
            self.site = form['site']
            if self.site:
                conditions.append(self.cube.d.site == self.site)

            #非所有区域
            #if self.location:
                #self.site_count = get_nb_stations_of_location(self.location)
                #conditions.append(self.cube.d.location == self.location)
            #所有区域
            #else:
                #self.site_count = get_nb_stations_of_location(self.location)

        except:
            pass

        try:
            self.fuel_type = int(form['fuel_type'])

            #直接查询对应的油品，不再总结
            conditions.append(self.cube.d.barcode == self.fuel_type)

        except:
            pass

        try:
            self.start_date = form['start_date']
            self.end_date = form['end_date']
            conditions.append(self.cube.d.datehour >= self.start_date)
            conditions.append(self.cube.d.datehour <= self.end_date)
        except:
            pass
        return conditions

# 基于交易记录汇总数据的报告
class TransReportWithSummary(TransReport):
    __abstract__ = True

    @overrides(TransReport)
    def build_extra(self, data):
        data['extra'] = []
        summary = {
            "data": [], "name": _(u"比例"), "type": "pie", "showInLegend": False, "center": [50, 0], "size": 100,
            "dataLabels": {
                "enabled": True,
                "distance": 5,
                "style": {
                    "fontWeight": 'bold',
                    "color": 'black',
                },
                "format": '{point.y:.1f}%'
            }
        }
        total = 0.0
        for opt in data["dataset"]:
            data_sum = sum(opt["data"])
            total += data_sum
            summary["data"].append({'name': opt["name"], 'y': data_sum})
        for opt in summary["data"]:
	        if total==0.0:
		        opt['y']=0
	        else:
           	    opt['y'] = round(opt['y'] * 100 / total, 2)
        #data["extra"].append(summary)

# example
class ExampleReport(TransReportWithSummary):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['quantity'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)

#当日油品销售额趋势图
class OilSalesDailyTrendReport(TransReportWithSummary):
    #filters
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    #where
    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    #select
    vertical = ['pay']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['pay'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)

#当日油品加油量趋势图
class PumpDailyTrendReport(TransReportWithSummary):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    fuel_type=fields.ChoiceField(label=ugettext_lazy("油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['quantity'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)

#当日进站车辆趋势图
class TransDailyTrendReport(TransReportWithSummary):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['trans_count']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = result['trans_count']

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)

#当日每车加油量趋势图
class PumpCarDailyTrendReport(TransReportWithSummary):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity','trans_count']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        if result['trans_count']==0:
            stat[cat]=0
        else:
            stat[cat] = round(float(result['quantity'])/result['trans_count'],2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)

    def report(self, request, *args, **kwargs):
        data=super(PumpCarDailyTrendReport,self).report(request, *args, **kwargs)
        for  info in data['dataset'] :
            info['flag'] = {}
	    if info['name']!=None:
                if info['name'].find('92') != -1 or info['name'].find('93') != -1 :
                    for idx in xrange(len(data['categories'])):
                        value = data['categories'][idx]
                        if info['data'][idx]<20:
                            info['flag'][value]="差"
                        elif info['data'][idx]>=20 and info['data'][idx]<40:
                            info['flag'][value]="好"
                        else:
                            info['flag'][value]="优"
                elif info['name'].find('95') != -1 or info['name'].find('97') != -1 :
                    for idx in xrange(len(data['categories'])):
                        value = data['categories'][idx]
                        if info['data'][idx] < 35:
                            info['flag'][value]="差"
                        elif info['data'][idx]>=35 and info['data'][idx]<60:
                            info['flag'][value]="好"
                        else:
                            info['flag'][value]="优"
        return data

#每车加油量趋势图
class PumpCarTrendReport(TransReportWithSummary):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL,TransReport.cube.d.quantity>0]
    vertical = ['quantity','trans_count']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        if result['trans_count']==0:
            stat[cat]=0
        else:
            stat[cat] = round(float(result['quantity'])/result['trans_count'],2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)


#当日每车消费额趋势图
class ConsumeCarDailyTrendReport(TransReportWithSummary):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['pay','trans_count']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        if result['trans_count']==0:
            stat[cat]=0
        else:
            stat[cat] = round(float(result['pay'])/result['trans_count'],2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)

#区域多站图表 抽象
class MultiStationReport(TransReport):
    __abstract__ = True

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def series_name(self, series=None):
        try:
            #曲线是区域代码
            id=int(series)
            return get_china_location_name_by_id(id)
        except:
            #曲线是站点
            return get_station_desc_by_name(series)

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        #确定地区过滤器
        s=request.get_session()
        location_barcode=int(kwargs['form'].cleaned_data['china_location'])

        if location_barcode==0:
            return {
                "categories": [],
                "dataset": []
            }

        location=s.query(DimChinaProvinceCityDistrict).filter_by(id=location_barcode).one()
        conditions = self.init_conditions(**kwargs) + self.conditions

        drilldown = []+self.horizonal

        #取得当前地区过滤选项,以及分组选项
        series_options={"type": "column", "stacking": "normal"}
        if location.level==1:
            conditions.append(Station.province==location.id)
            drilldown.append('city')
            self.series='city'

        elif location.level==2:
            conditions.append(Station.city==location.id)
            drilldown.append('district')
            self.series='district'

        else:
            conditions.append(Station.district==location.id)
            drilldown.append('name')
            self.series='name'
            series_options={"type": "line", "stacking": None}

        #必须是用户拥有的油站
        stations=get_user_stations_by_name(request.session['username'])
        all_sites=[x[0] for x in stations]
        conditions.append(self.cube.d.site.in_(all_sites))

        self.post_init_conditions(**kwargs)
        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details,
            session=request.get_session())
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options

        data['go_to_simple']=False
        for series, stat in items:
            try:
                #地区
                location_id=int(series)

                if location_id==0:
                    continue

                opt = {"data": [], "name": self.series_name(series),"location_id":series}
            except:
                #站点
                opt = {"data": [], "site_name":series,"name": self.series_name(series)}
                data['go_to_simple']=True

            opt.update(series_options)

            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)
            data["dataset"].append(opt)
        self.build_extra(data)
        return data


#区域多站图表排名 抽象
class MultiStationSortReport(TransReport):
    __abstract__ = True

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def series_name(self, series=None):
        try:
            #曲线是区域代码
            id=int(series)
            return get_china_location_name_by_id(id)
        except:
            #曲线是站点
            return get_station_desc_by_name(series)

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        #确定地区过滤器
        s = request.get_session()

        #取得查询对象
        cube = cubes.StationMonthStatCube()

        #获得区县信息和时间
        location_barcode = int(kwargs['form'].cleaned_data['china_location'])
        year_date = int(kwargs['form'].cleaned_data['date'][:4])
        month_date = int(kwargs['form'].cleaned_data['date'][5:7])

        #筛选条件类型
        #choose_type = int(kwargs['form'].cleaned_data['choose_type'])

        #标签
        #tag_id = int(kwargs['form'].cleaned_data['tag'])

        #if(tag_id!=-1 and choose_type==1):
        #    pass

        if location_barcode == 0:
            return {
                "categories": [],
                "dataset": []
            }

        #通过区县信息查询完整的信息
        location = s.query(DimChinaProvinceCityDistrict).filter_by(id=location_barcode).one()

        drilldown = [] + self.horizonal

        #下面的三个判断根据区县等级来确定查询的条件
        if location.level == 1:
            drilldown.append('city')
            self.series = 'city'

        elif location.level == 2:
            drilldown.append('district')
            self.series = 'district'

        else:
            drilldown.append('name')
            self.series = 'name'
            series_options = {"type":"line", "stacking":None}

        #必须是用户拥有的油站
        stations = get_user_stations_by_name(request.session['username'])

        #遍历出所有的油站,并添加在查询条件中
        all_sites = [x[0] for x in stations]
        results=[]
        for site in all_sites:

            #添加查询条件
            conditions = self.init_conditions(**kwargs) + self.conditions
            conditions.append(self.cube.d.year == year_date)
            conditions.append(self.cube.d.month == month_date)
            conditions.append(self.cube.d.site==site)
            self.post_init_conditions(**kwargs)
            if location.level == 1:
                conditions.append(Station.province == location.id)
            elif location.level == 2:
                conditions.append(Station.city == location.id)

            else:
                conditions.append(Station.district == location.id)
            result = self.cube.aggregate(
                session_factory = request.get_session,
                measures = self.vertical,
                drilldown = drilldown,
                conditions = conditions,
                details = self.details,
                order = self.vertical[0] + ' desc',
                session = request.get_session()
            )
            #判断如果查询结果为0就将通过添加条件到一个方法中使其产生数据保存在表中

            if len(result) == 0:
                args = {
                    'site':site,
                    'year_date':year_date,
                    'month_date':month_date,
                    'log_file':settings.BASE_DIR+'/file/tao'+'/process.log'
                }
                call_command('gearman_submit_job', 'compute_station_monthbatch',
                    json.dumps(args), foreground=False)

                #执行添加之后再查询结果
                result = self.cube.aggregate(
                    session_factory = request.get_session,
                    measures = self.vertical,
                    drilldown = drilldown,
                    conditions = conditions,
                    details = self.details,
                    order = self.vertical[0] + ' desc',
                    session = request.get_session()
                )
            if len(result)!=0:
                results.append(result[0])

        self.post_init_conditions(**kwargs)
        categories = []
        fuel_opt = {"data":[], "name":self.fuel_opt_name}
        site_opt = {"data":[], "name":self.site_opt_name}


        #排名
        count = 1
        sort_vertical=self.vertical[0]
        results=sorted(results, key=lambda result: result[sort_vertical],reverse=True)

        #将结果遍历出来并保存到字典中,通过返回data来将数据传递给前端
        for result in results:
            fuel_opt['data'].append(round(result[self.vertical[0]], 2))
            site_name = s.query(Station).filter_by(name=result['site']).one()
            result['site'] = site_name.description
            site_opt['data'].append(result['site'])
            categories.append(count)
            count+=1
        data = {
            "categories": categories,
            "dataset": [fuel_opt, site_opt],
            "opts": {
                'chart': {
                    'type': 'bar',
                },
            }
        }
        self.build_extra(data)
        return data

#区域销售额趋势
class MultiOilMoneyTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyFuelSalesCube()

    system_fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['pay']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)

#油站瓶颈与重复客户画像
class MultiStationProfile1Report(TransReport):
    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    health_status_x = fields.ChoiceField(label=ugettext_lazy(u"x指标"), choices=HealthStatus.tuples())
    health_status_y = fields.ChoiceField(label=ugettext_lazy(u"y指标"), choices=HealthStatus.tuples())

    def report(self, request, *args, **kwargs):
        date = kwargs['form'].cleaned_data['date']
        location_barcode=int(kwargs['form'].cleaned_data['china_location'])
        x = int(kwargs['form'].cleaned_data['health_status_x'])
        y = int(kwargs['form'].cleaned_data['health_status_y'])
        session = request.get_session()
        data = {
                "categories": [],
                "dataset": {},
                "opts": {
                    'chart': {
                        'type': 'profile_dash',
                        'x':x,
                        'y':y
                    },
                },
        }
        if x == y:
            return data
        health_status_value = [0,40,20,20,35,5,50,60,70,8,5,5,5]
        data["dataset"]["series"] = []
        data["dataset"]["series"].append(dict(
                            name = "基准点" ,
                            data = [[health_status_value[x],health_status_value[y],0.01]]
                        ))
        #通过区县信息查询完整的信息
        #必须是用户拥有的油站
        site_list = []
        try :
            user = session.query(User).filter_by(name=request.session['username']).one()
            stations = session.query(UserStation).filter_by(user_id=user.id).all()
            for station in stations :
                station_code = station.station
                try:
                    site = session.query(Station).filter_by(name = station_code).one()
                except:
                    continue
                if site.province == location_barcode :
                    site_list.append(station_code)
                else :
                    continue
        except Exception,e:
            data['dataset'] = {}
            return data

        for station_code in site_list :
            date = datetime(date.year,date.month,date.day)
            try:
                station_health_status = session.query(StationHealthStatus).filter(StationHealthStatus.date==date,StationHealthStatus.site==station_code,or_(StationHealthStatus.type==x,StationHealthStatus.type==y)).all()
            except:
                continue
            if not len(station_health_status) == 0 :
                    for obj in station_health_status :
                            station_name = obj.desc
                            #x指标
                            value1 = 0
                            #y指标
                            value2 = 0
                            #健康指标类型，0：瓶颈 1 重复客户
                            if obj.type == x :
                                value1 = obj.value
                            else :
                                value2 = obj.value
                    data["dataset"]["series"].append(dict(
                            name = station_name ,
                            data = [[value1,value2,1]]
                        ))
        if len(data["dataset"]["series"]) == 1 :
            data['dataset'] = {}
            return data
        data["dataset"]["dash_title"] = u"油站健康指数坐标图"
        return data

#区域加油量趋势
class MultiOilTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyFuelSalesCube()
    system_fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    #choose_type=fields.ChoiceField(label=ugettext_lazy(u"类型"),choices=[(0,'区域'),(1,'标签')])
    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    #tag=fields.ChoiceField(label=ugettext_lazy(u"标签"),choices=[])


    conditions = []
    vertical = ['quantity']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['quantity'], 2)

#区域加油量趋势排行
class MultiOilTrendSortReport(MultiStationSortReport):
    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    #choose_type=fields.ChoiceField(label=ugettext_lazy(u"类型"),choices=[(0,'区域'),(1,'标签')])
    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))
    #tag=fields.ChoiceField(label=ugettext_lazy(u"标签"),choices=[])

    conditions = []
    vertical = ['quantity']
    horizonal = ['year', 'month','site']
    series_options = {"type": "chart", "stacking": "normal"}
    fuel_opt_name = _(u"加油量(单位:升)")
    site_opt_name = _(u"站点")

#多站出油时间趋势图
class MultiOilTimeTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyFuelSalesCube()

    system_fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())
    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['quantity']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['quantity']/settings.PUMP_TRANS_TIME,0)

#区域非油品销量趋势图
class MultiNoneOilSalesTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyStatCube()

    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['quantity_nonefuel']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['quantity_nonefuel'],2)

#区域高峰期平均出油量趋势图
class MultiOilPeakFuelAvgGunTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyStatCube()

    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['peak_fuel_count','peak_hour_num','nb_guns']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        if result['nb_guns']==0 or result['peak_hour_num']==0:
            stat[cat]=0
        else:
            stat[cat] = round(result['peak_fuel_count']/result['peak_hour_num']/result['nb_guns'],2)


#区域油品环比百分数
class MultiOilMoMTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyStatCube()

    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['quantity_fuel','pre_mon_quantity_fuel']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "spline", "stacking": None}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        if result['pre_mon_quantity_fuel']==0:
            stat[cat]=0
        else:
            stat[cat] = round(result['quantity_fuel']/result['pre_mon_quantity_fuel']*100,2)

#区域非油品环比百分数
class MultiNoneOilMoMTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyStatCube()

    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['pre_mon_quantity_nonefuel','quantity_nonefuel']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "spline", "stacking": None}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        if result['pre_mon_quantity_nonefuel']==0:
            stat[cat] = 0
        else:
            stat[cat] = round(result['quantity_nonefuel']/result['pre_mon_quantity_nonefuel']*100,2)

#区域加油卡比例
class MultiVIPPayPercentTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyStatCube()

    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['vip_pay_amout','pay_amout']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        if result['pay_amout']==0:
            stat[cat]=0
        else:
            stat[cat] = round(result['vip_pay_amout']/result['pay_amout']*100,2)

#区域加满率
class MultiFillOutPercentTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyStatCube()

    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['fuel_trans_count','fuel_fillout_count']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        if result['fuel_trans_count']==0:
            stat[cat]=0
        else:
            stat[cat] = round(result['fuel_fillout_count']/result['fuel_trans_count']*100,2)

#客单值
class MultiSingleCustomerPayTrendReport(MultiStationReport):
    #使用StationDailyFuelSalesCube
    cube = cubes.StationDailyStatCube()

    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    conditions = []
    vertical = ['single_customer_pay']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['single_customer_pay'],2)

#当月加油量趋势图
class OilTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "area", "stacking": None}


    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['quantity'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'加油量')

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)

        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                count+=value
                opt["data"].append(value)
            data["dataset"].append(opt)
            data["avrg"]= round(count/len(categories),2)
        self.build_extra(data)
        return data

#油品当月销售额趋势
class SaleTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    #where
    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.FUEL]
    vertical = ['pay']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'销售额')

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                count+=value
                opt["data"].append(value)
            data["dataset"].append(opt)
            data["avrg"]= round(count/len(categories),2)
        self.build_extra(data)
        return data

#环比同比趋势    抽象
class MoMYoYTrendReport(object):

    #基线时间
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,*args,**kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        counter=0
        if self.MoM_or_YoY=='MoM':
            trend_type=_(u'环比')
        else:
            trend_type=_(u'同比')
        while curr_date <= end_date:
            counter+=1
            categories.append(_(u"{trend_type}第{counter}天").format(trend_type=trend_type,counter=counter))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['quantity'], 2)

    @overrides(TransReport)
    def series_name(self, be_old, request):
        from django.utils import translation
        label=unicode(self.value_label)
        with translation.override(request.session['django_language']):
            label=unicode(self.value_label)
        if be_old:
            if self.MoM_or_YoY=='MoM':
                return _(u'上月')+label
            else:
                return _(u'去年同期')+label
        else:
            return _(u'当月')+label

    def report(self, request, *args, **kwargs):
        #表明正在进行同比环比数据查询
        kwargs['on_MoM_or_YoY']=True
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions()
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)

        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None])

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        if self.chart_options:
            data['opts'] = self.chart_options

        for series, stat in items:
            #取旧的
            #取值
            opt = {"data": [], "name": self.series_name(True,request)}
            opt.update(self.series_options)
            curr_date = self.tmp_start_date
            while curr_date <= self.tmp_end_date:
                cat=curr_date.strftime("%Y-%m-%d")
                curr_date += timedelta(days=1)

                try:
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)

            data["dataset"].append(opt)

            #新值
            opt = {"data": [], "name": self.series_name(False,request)}
            opt.update(self.series_options)

            start_date=kwargs['form'].cleaned_data['start_date']
            end_date=kwargs['form'].cleaned_data['end_date']
            curr_date = start_date
            while curr_date <= end_date:
                cat=curr_date.strftime("%Y-%m-%d")
                curr_date += timedelta(days=1)

                try:
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)

            data["dataset"].append(opt)

        self.build_extra(data)
        return data

#当月油品销售额环比趋势
class SaleMoMTrendReport(MoMYoYTrendReport,TransReport):
    #基线时间
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.FUEL]
    vertical = ['pay']
    series_options = {"type": "spline", "stacking": None}

    def __init__(self):
        self.MoM_or_YoY='MoM'
        self.value_label=ugettext_lazy(u'销售额')

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)

#当月油品销售额同比趋势
class SaleYoYTrendReport(MoMYoYTrendReport,TransReport):

    #基线时间
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.FUEL]
    vertical = ['pay']
    series_options = {"type": "spline", "stacking": None}

    def __init__(self,*args,**kwargs):
        self.MoM_or_YoY='YoY'
        self.value_label=ugettext_lazy(u'销售额')

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)


#当月加油量环比趋势图
class OilMoMTrendReport(MoMYoYTrendReport,TransReport):

    #基线时间
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    series_options = {"type": "spline", "stacking": None}

    def __init__(self):
        self.MoM_or_YoY='MoM'
        self.value_label=ugettext_lazy(u'加油量')

# 近一季度油品销售额趋势图
class OilQuarterTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=90))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    #where
    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.FUEL]
    vertical = ['pay']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "area", "stacking": None}


    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'销售额')

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                count+=value
                opt["data"].append(value)
            data["dataset"].append(opt)
            data["avrg"]= round(count/len(categories),2)
        self.build_extra(data)
        return data


#当月加油量同比趋势图
class OilYoYTrendReport(MoMYoYTrendReport,TransReport):
    #基线时间
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    series_options = {"type": "spline", "stacking": None}

    def __init__(self,*args,**kwargs):
        self.MoM_or_YoY='YoY'
        self.value_label=ugettext_lazy(u'加油量')

#趋势对比分析    抽象
class TrendBetweenTwoDaysReport(object):
    date = fields.DateField(label=ugettext_lazy(u"日期A"), initial=DEFAULT_DATE)
    other_date = fields.DateField(label=ugettext_lazy(u"日期B"), initial=DEFAULT_DATE- timedelta(days=1))
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    series = ['year', 'month', 'day']
    series_options = {"type": "spline", "stacking": None}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['quantity'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return series

    def report(self, request, *args, **kwargs):
        #表明正在进行对比数据查询
        kwargs['on_between_two_days']=True
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions()
        if self.series:
            if isinstance(self.series,type([])):
                drilldown = self.series + self.horizonal
            else:
                drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)
        stats = {}
        if self.series:
            context=kwargs
            start_cat=context['form'].cleaned_data['date'].strftime('%Y-%m-%d')
            stats.setdefault(start_cat,{})
            end_cat=context['form'].cleaned_data['other_date'].strftime('%Y-%m-%d')
            stats.setdefault(end_cat,{})
            for result in results:
                cat='%d-%02d-%02d' % (result['year'], result['month'], result['day'])
                self.build_result(result, stats[cat])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None])

        items = stats.items()
        categories = self.build_categories(items)
        data = {
            "categories": categories,
            "dataset": []
        }
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)
            data["dataset"].append(opt)
        self.build_extra(data)
        return data

#加油量趋势对比分析
class OilTrendBetweenTwoDaysReport(TrendBetweenTwoDaysReport,TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期A"), initial=DEFAULT_DATE)
    other_date = fields.DateField(label=ugettext_lazy(u"日期B"), initial=DEFAULT_DATE- timedelta(days=1))
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

#油品销售额趋势对比
class OilSaleTrendBetweenTwoDaysReport(TrendBetweenTwoDaysReport,TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期A"), initial=DEFAULT_DATE)
    other_date = fields.DateField(label=ugettext_lazy(u"日期B"), initial=DEFAULT_DATE- timedelta(days=1))
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])


    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.FUEL]
    vertical = ['pay']
    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['pay'], 2)

#当日油枪效率
class GunPumpTimeDailyTrendReport(TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    series = 'pump_id'
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['quantity']/settings.PUMP_TRANS_TIME,0)

    @overrides(TransReport)
    def series_name(self, series=None):
        return u"%s号枪" % series

    def report(self, request, *args, **kwargs):
        data=super(GunPumpTimeDailyTrendReport,self).report(request, *args, **kwargs)
        #如果是显示高峰期需要丢弃非高峰期的数据
        if request.META.get('HTTP_REFERER','').find('station_peak_period_page')!=-1:
            #算高峰期时段
            #cache result
            cache_key='%s_%s_%s'%(request.GET['site'],request.GET['fuel_type'],
                request.GET['date'])
            values=[]
            try:
                values=json.loads(cache.get(cache_key))
            except:
                pass

            #删数据
            delete_container=[]
            idx=0
            for cat in data['categories']:
                #遍历高峰期区间
                need_delete_count=0
                for value in values:
                    re_cat=re.findall(r'(\d+)[ -]+(\d+)',cat)
                    if int(re_cat[0][0])<value[0]:
                        need_delete_count+=1
                    elif int(re_cat[0][1])>value[1]:
                        need_delete_count+=1

                #不再任何区间内
                if need_delete_count==len(values):
                    delete_container.append(idx)


                idx+=1

            tmp_cat=copy.copy(data['categories'])
            data['categories']=[]
            for idx in xrange(len(tmp_cat)):
                if idx in delete_container:
                    continue
                data['categories'].append(tmp_cat[idx])
            for se in data['dataset']:
                tmp_data=copy.copy(se['data'])
                se['data']=[]
                for idx in xrange(len(tmp_data)):
                    if idx in delete_container:
                        continue
                    se['data'].append(tmp_data[idx])
        else:
            for info in data['dataset']:
                info['flag']={}
                #小于5分钟瘦弱，五分钟到8分钟正常，大于8分钟优
                for idx in xrange(len(data['categories'])):
                    value = data['categories'][idx]
                    if info['data'][idx]<5:
                        info['flag'][value]="瘦弱"
                    elif info['data'][idx]>=5 and info['data'][idx]<8:
                        info['flag'][value]="正常"
                    else:
                        info['flag'][value]="优"
        return data

#当月油枪效率
class GunPumpTimeMonthTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    series = 'pump_id'
    series_options = {"type": "column", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['quantity']/((self.end_date-self.start_date).days+1)/settings.PUMP_TRANS_TIME,0)

    @overrides(TransReport)
    def series_name(self, series=None):
        return u"%s号枪" % series

    def report(self, request, *args, **kwargs):
        data=super(GunPumpTimeMonthTrendReport,self).report(request, *args, **kwargs)
        for info in data['dataset']:
            info['flag']={}
            #小于5分钟瘦弱，五分钟到8分钟正常，大于8分钟优
            for idx in xrange(len(data['categories'])):
                value = data['categories'][idx]
                if info['data'][idx]<5:
                    info['flag'][value]="瘦弱"
                elif info['data'][idx]>=5 and info['data'][idx]<8:
                    info['flag'][value]="正常"
                else:
                    info['flag'][value]="优"
        return data

#月24小时平均效率图表
class OilMonthAvgTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['quantity']/((self.end_date-self.start_date).days+1),0)

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)

    def report(self, request, *args, **kwargs):
        data=super(OilMonthAvgTrendReport,self).report(request, *args, **kwargs)
        return data
#油品加满率
class OilFullRateDashletReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['count','fix_pump_count']
    horizonal = ['hour']
    series = 'barcode'
    series_options = {"type": "spline", "stacking": None}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        data=(float(result['count'] - result['fix_pump_count'])/float(result['count']))*100
        stat[cat] = round(data, 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return get_fuel_type_name(series)

    def report(self, request, *args, **kwargs):
        data=super(OilFullRateDashletReport,self).report(request, *args, **kwargs)
        for  info in data['dataset'] :
            info['flag'] = {}
	    if info['name']!=None:
                if info['name'].find('92') != -1 or info['name'].find('93') != -1 :
                    for idx in xrange(len(data['categories'])):
                        value = data['categories'][idx]
                        if info['data'][idx]<50:
                            info['flag'][value]="瘦弱"
                        elif info['data'][idx]>=50 and info['data'][idx]<60:
                            info['flag'][value]="好"
                        else:
                            info['flag'][value]="优"
                elif info['name'].find('95') != -1 or info['name'].find('97') != -1 :
                    for idx in xrange(len(data['categories'])):
                        value = data['categories'][idx]
                        if info['data'][idx]<60:
                            info['flag'][value]="瘦弱"
                        elif info['data'][idx]>=60 and info['data'][idx]<70:
                            info['flag'][value]="好"
                        else:
                            info['flag'][value]="优"
                elif info['name'].find('柴油') != -1 :
                    for idx in xrange(len(data['categories'])):
                        value = data['categories'][idx]
                        if info['data'][idx]<70:
                            info['flag'][value]="瘦弱"
                        elif info['data'][idx]>=70 and info['data'][idx]<90:
                            info['flag'][value]="好"
                        else:
                            info['flag'][value]="优"
        return data


#高峰期出油效率
class CrestDailyTrendReport(TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    # series = 'pump_id'
    series_options = {"type": "areaspline", "stacking": None}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['quantity']/settings.PUMP_TRANS_TIME,0)

    @overrides(TransReport)
    def series_name(self, series=None):
        return u"加油量(红色为高峰期,绿色为低谷期,紫色为平稳上升期,蓝色为平稳下降期)"

    def report(self, request, *args, **kwargs):
        data=super(CrestDailyTrendReport,self).report(request, *args, **kwargs)

        period_key='%s_%s_%s_period'%(request.GET['site'],request.GET['fuel_type'],
            request.GET['date'])
        period_value=None
        try:
            period_value=json.loads(cache.get(period_key))
        except:
            pass
        data['dataset'][0]['render_period_color']=True
        data['period_key']=period_key
        data['period_value']=period_value
        return data

#油机，油枪类对油枪分组效率    抽象
class GunGroupTimeDailyTrendReport(object):
    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    series = 'pump_id'
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = result['quantity']

    def report_it(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions()
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None])

        items = stats.items()
        categories = self.build_categories(items)
        data = {
            "categories": categories,
            "dataset": []
        }
        if self.chart_options:
            data['opts'] = self.chart_options

        for machine in kwargs['pump_groups']:
            machine_name=machine['name']
            pump_ids=machine['value']

            opt = {"data": [], "name": machine_name}
            opt.update(self.series_options)

            #取值
            for cat in categories:
                all_value=0
                #所有油枪
                for pump_id in pump_ids:
                    try:
                        stat=stats[int(pump_id)]
                    except:
                        continue

                    try:
                        value = stat[cat]
                    except:
                        value = 0

                    all_value+=value

                opt["data"].append(round(all_value/settings.PUMP_TRANS_TIME,0))

            data["dataset"].append(opt)
        self.build_extra(data)
        return data

#当日油机效率
class GunMachineTimeDailyTrendReport(GunGroupTimeDailyTrendReport,TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    def report(self, request, *args, **kwargs):
        kwargs['pump_groups']=get_user_station_description_by_name(
            kwargs['form'].cleaned_data['site'])['machines']
        data=self.report_it(request, *args, **kwargs)

        #如果是显示高峰期需要丢弃非高峰期的数据
        if request.META.get('HTTP_REFERER','').find('station_peak_period_page')!=-1:
            #算高峰期时段
            #cache result
            cache_key='%s_%s_%s'%(request.GET['site'],request.GET['fuel_type'],
                request.GET['date'])
            values=[]
            try:
                values=json.loads(cache.get(cache_key))
            except:
                pass

            #删数据
            delete_container=[]
            idx=0
            for cat in data['categories']:
                #遍历高峰期区间
                need_delete_count=0
                for value in values:
                    if int(cat[:2])<value[0]:
                        need_delete_count+=1
                    elif int(cat[-2:])>value[1]:
                        need_delete_count+=1

                #不再任何区间内
                if need_delete_count==len(values):
                    delete_container.append(idx)


                idx+=1

            tmp_cat=copy.copy(data['categories'])
            data['categories']=[]
            for idx in xrange(len(tmp_cat)):
                if idx in delete_container:
                    continue
                data['categories'].append(tmp_cat[idx])
            for se in data['dataset']:
                tmp_data=copy.copy(se['data'])
                se['data']=[]
                for idx in xrange(len(tmp_data)):
                    if idx in delete_container:
                        continue
                    se['data'].append(tmp_data[idx])
        return data

#当日通道效率
class PassageTimeDailyTrendReport(GunGroupTimeDailyTrendReport,TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    def report(self, request, *args, **kwargs):
        kwargs['pump_groups']=get_user_station_description_by_name(
            kwargs['form'].cleaned_data['site'])['passages']
        data=self.report_it(request, *args, **kwargs)

        #如果是显示高峰期需要丢弃非高峰期的数据
        if request.META.get('HTTP_REFERER','').find('station_peak_period_page')!=-1:
            #算高峰期时段
            #cache result
            cache_key='%s_%s_%s'%(request.GET['site'],request.GET['fuel_type'],
                request.GET['date'])
            values=[]
            try:
                values=json.loads(cache.get(cache_key))
            except:
                pass

            #删数据
            delete_container=[]
            idx=0
            for cat in data['categories']:
                #遍历高峰期区间
                need_delete_count=0
                for value in values:
                    re_cat=re.findall(r'(\d+)[ -]+(\d+)',cat)
                    if int(re_cat[0][0])<value[0]:
                        need_delete_count+=1
                    elif int(re_cat[0][1])>value[1]:
                        need_delete_count+=1

                #不再任何区间内
                if need_delete_count==len(values):
                    delete_container.append(idx)


                idx+=1

            tmp_cat=copy.copy(data['categories'])
            data['categories']=[]
            for idx in xrange(len(tmp_cat)):
                if idx in delete_container:
                    continue
                data['categories'].append(tmp_cat[idx])
            for se in data['dataset']:
                tmp_data=copy.copy(se['data'])
                se['data']=[]
                for idx in xrange(len(tmp_data)):
                    if idx in delete_container:
                        continue
                    se['data'].append(tmp_data[idx])
        return data

#高峰期时段定义
class StationPeakPeriodTimeDefinedReport(TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])

    conditions = [TransReport.cube.d.trans_type==TransType.FUEL]
    vertical = ['trans_count']
    horizonal = ['hour']
    series = None

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = result['trans_count']

    @overrides(TransReport)
    def series_name(self, series=None):
        return '交易笔数'

    def report(self, request, *args, **kwargs):
        data=super(StationPeakPeriodTimeDefinedReport,self).report(request, *args, **kwargs)
        #依照一定算法计算出高峰期时段
        datas=get_peak_period(data)
        values=datas['crest_list']
        diff=datas['diff_value']
        period_key='%s_%s_%s_period'%(request.GET['site'],request.GET['fuel_type'],
            request.GET['date'])
        cache.set(period_key,json.dumps(datas['period']),settings.MEMCACHED_TIMEOUT)

        if diff==0:
            diff='不存在负荷峰谷差异'

        data = {
            "dataset": [],
            "opts": {
                'chart': {
                    'type': 'column',
                }
            }
        }

        #cache result
        cache_key='%s_%s_%s'%(request.GET['site'],request.GET['fuel_type'],
            request.GET['date'])
        cache.set(cache_key,json.dumps(values),settings.MEMCACHED_TIMEOUT)
        #没有高峰期
        if len(values)==0:
            opt = {"data": ['在指定日期内没有发现高峰期'], "name": _(u'值')}
            data['categories']=[_(u'高峰期时段')]
        else:
            opt = {"data": [
                _(u'{start}时-{end}时').format(start=value[0],end=value[1])
                for value in values], "name": _(u'值')}
            data['categories']=[_(u'高峰期时段') for x in values]

        data['categories'].append(_(u'油站负荷峰谷差异'))
        opt['data'].append(diff)
        data['dataset'].append(opt)
        data['period_key']=period_key
        data['period_value']=datas['period']
        return data

#sku总数
class GoodsSKUCountReport(reports.Report):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    def report(self, request, *args, **kwargs):
        site = kwargs['form'].cleaned_data['site']
        cube = cubes.TransCube()
        conditions = [cube.d.quantity > 0,
                      cube.d.trans_type == TransType.NON_FUEL]
        if site:
            conditions.append(cube.d.site == site)
        results = cube.aggregate(
            session_factory=request.get_session,
            measures=['category_count', 'pay', 'trans_count'],
            conditions=conditions)
        stats = {}
        for result in results:
            stats[_(u'总SKU数')] = _(u"{count} 种").format(count=result['category_count'])
            stats[_(u'总销售额')]=_(u'{pay} 元').format(pay=result['pay'])
            stats[_(u'总客户数')]=_(u'{count} 位').format(count=result['trans_count'])
            if result['trans_count']==0:
                stats[_(u'总客单值')] = _(u"{count} 元").format(count=0)
            else:
                stats[_(u'总客单值')] = _(u"{count} 元").format(count=round(result['pay'] / result['trans_count'], 2))

        items = stats.items()
        data = {
            "categories": [],
            "dataset": [],
            "opts": {
                'chart': {
                    'type': 'column',
                }
            }
        }
        opt = {"data": [], "name": _(u'值')}
        for k, v in items:
            data['categories'].append(k)
            opt['data'].append(v)
        data['dataset'].append(opt)
        return data

#当日非油品销售额趋势图
class GoodsSalesDailyTrendReport(TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())

    #where
    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.NON_FUEL]
    #select
    vertical = ['pay']
    horizonal = ['hour']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['pay'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'销售额')

#当日销售额客单值
class GoodsSalesPerPeopleDailyTrendReport(TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())

    #where
    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.NON_FUEL]
    #select
    vertical = ['pay','trans_count']
    horizonal = ['hour']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['pay']/result['trans_count'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'客单值')

    @overrides(reports.Report)
    #整理plot 数据
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal
        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series),"flag":{}}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)
                #客单值指标，20以下不健康，20到100正常，大于100好，flag作为标识
                if value < 20:
                    opt["flag"][cat]="差"
                elif value >=20 and value<100:
                    opt["flag"][cat]="好"
                else:
                    opt["flag"][cat]="优"
            data["dataset"].append(opt)

        self.build_extra(data)
        return data

#当月非油品24小时平均销售额
class GoodsMonthAvgTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    payment_type = fields.ChoiceField(label=ugettext_lazy(u"支付方式"), choices=PaymentType.tuples())

    conditions = [TransReport.cube.d.trans_type==TransType.NON_FUEL]
    vertical = ['quantity']
    horizonal = ['hour']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['quantity']/((self.end_date-self.start_date).days+1),0)

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'销售额')

    def report(self, request, *args, **kwargs):
        data=super(GoodsMonthAvgTrendReport,self).report(request, *args, **kwargs)
        return data

#当月非油品销售排行TOP10
class GoodsRankMonthTrendReport(reports.Report):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        site = kwargs['form'].cleaned_data['site']
        date=kwargs['form'].cleaned_data['date']

        cube = cubes.TransCube()
        pre_month_first_day,pre_month_end_day=prev_bounds(date)
        conditions = [cube.d.datehour >= pre_month_first_day,
                      cube.d.datehour < pre_month_end_day+timedelta(days=1),
                      cube.d.quantity > 0,
                      cube.d.trans_type == TransType.NON_FUEL]
        if site:
            conditions.append(cube.d.site == site)

        results = cube.aggregate(
            session_factory=request.get_session,
            measures=['pay'],
            drilldown=['barcode'],
            details=['desc'],
            conditions=conditions,
            order='pay desc',
            limit=10)
        stats = {}
        for result in results:
            product_name = "%s" % (result['desc'].replace(u'昆仑',''))
            stats[product_name] = round(result['pay'], 2)

        items = stats.items()
        items.sort(key=lambda x: x[1], reverse=True)

        data = {
            "categories": [],
            "dataset": [],
            "opts": {
                'chart': {
                    'type': 'column',
                    'height': '500',
                }
            }
        }
        opt = {"data": [], "name": _(u'销售额({first},{last})').format(first=str(pre_month_first_day),last=str(pre_month_end_day))}
        for k, v in items:
            data['categories'].append(k)
            opt['data'].append(v)
        data['dataset'].append(opt)
        return data

#油非转化率
class OilAndNonOilConversionDashletReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = []
    vertical = ['count','non_oil_trans_count']
    horizonal = ['hour']
    series_options = {"type": "spline", "stacking": None}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
         return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        #print result
        if (float(result['count']) - float(result['non_oil_trans_count']) )!= 0 :
            data = ( float(result['non_oil_trans_count'])/ ( float(result['count']) - float(result['non_oil_trans_count']) )  )*100
            stat[cat] = round(data, 2)
        else :
            stat[cat] = 0

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'转化比例')

    def report(self, request, *args, **kwargs):
        data=super(OilAndNonOilConversionDashletReport,self).report(request, *args, **kwargs)
        #依照一定算法计算出高峰期时段
        datas=get_peak_period(data)
        values=datas['crest_list']
        temp=[]
        for value in values :
            i=value[0]
            while  i <= value[1] :
                temp.append(i)
                i = i+1
        for  info in data['dataset'] :
            info['flag'] = {}
            for idx in xrange(len(data['categories'])):
                value = data['categories'][idx]
                if idx in temp :
                    if info['data'][idx]<5:
                        info['flag'][value]="差"
                    elif info['data'][idx]>=5 and info['data'][idx]<10:
                        info['flag'][value]="好"
                    else:
                        info['flag'][value]="优"
                else :
                    if info['data'][idx]<8:
                        info['flag'][value]="差"
                    elif info['data'][idx]>=8 and info['data'][idx]<12:
                        info['flag'][value]="好"
                    else:
                        info['flag'][value]="优"
        return data
#非油品当月销售额趋势图
class GoodsTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    #where
    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.NON_FUEL]
    vertical = ['pay']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'销售额')

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                count+=value
                opt["data"].append(value)
            data["dataset"].append(opt)
            data["avrg"]= round(count/len(categories),2)
        self.build_extra(data)
        return data

#近一季度非油品销售额趋势图
class GoodsQuarterTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=90))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    #where
    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.NON_FUEL]
    vertical = ['pay']
    horizonal = ['year', 'month', 'day']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'销售额')

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)

        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                count+=value
                opt["data"].append(value)
            data["dataset"].append(opt)
            data["avrg"]= round(count/len(categories),2)
        self.build_extra(data)
        return data

#非油品当月销售额环比
class GoodsMoMTrendReport(MoMYoYTrendReport,TransReport):

    #基线时间
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.NON_FUEL]
    vertical = ['pay']
    series_options = {"type": "spline", "stacking": None}

    def __init__(self):
        self.MoM_or_YoY='MoM'
        self.value_label=ugettext_lazy(u'销售额')

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)

#非油品当月销售额同比
class GoodsYoYTrendReport(MoMYoYTrendReport,TransReport):

    #基线时间
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.NON_FUEL]
    vertical = ['pay']
    series_options = {"type": "spline", "stacking": None}

    def __init__(self,*args,**kwargs):
        self.MoM_or_YoY='YoY'
        self.value_label=ugettext_lazy(u'销售额')

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        stat[cat] = round(result['pay'], 2)

#非油品销售额趋势对比
class GoodsTrendBetweenTwoDaysReport(TrendBetweenTwoDaysReport,TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期A"), initial=DEFAULT_DATE)
    other_date = fields.DateField(label=ugettext_lazy(u"日期B"), initial=DEFAULT_DATE- timedelta(days=1))
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])


    conditions = [TransReport.cube.d.quantity > 0,TransReport.cube.d.trans_type == TransType.NON_FUEL]
    vertical = ['pay']
    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        stat[cat] = round(result['pay'], 2)

#指定时间，获取前一年的时间
def get_pre_year_date(end_date,month=None,day=None):
    from datetime import date, datetime, timedelta
    start_date= end_date-relativedelta(years=1)
    month=start_date.month if month==None else month
    day=start_date.day if day==None else day
    start_date=date(start_date.year,month,day)
    return start_date

#近一年忠诚客户百分比趋势
class CustomerVIPMonthlyLoyaltyReport(reports.Report):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=get_pre_year_date(DEFAULT_DATE,day=1))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    def build_categories(self, start_date,end_date):
        categories = []
        curr_date = start_date
        while curr_date < end_date:
            categories.append(curr_date.strftime("%Y-%m"))
            curr_date += relativedelta(months=1)
        return categories

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        from datetime import date, datetime, timedelta
        site = kwargs['form'].cleaned_data['site']
        end_date = kwargs['form'].cleaned_data['end_date']
        end_date=date(end_date.year,end_date.month,1)
        start_date = kwargs['form'].cleaned_data['start_date']

        cube = cubes.TransCube()
        conditions = [
            cube.d.payment_type==PaymentType.VIP,
            and_(
                cube.d.datehour>=start_date,
                cube.d.datehour<end_date+timedelta(days=1)
            ),
        ]
        if site:
            conditions.append(cube.d.site == site)

        results = cube.aggregate(
            session_factory=request.get_session,
            measures=['trans_count'],
            drilldown=['year','month','cardnum'],
            conditions=conditions)

        #统计忠诚客户数和总的持卡客户数
        all_cus={}
        loyalty_cus={}
        all_cats=self.build_categories(start_date,end_date)

        #init
        for cat in all_cats:
            all_cus[cat]=0
            loyalty_cus[cat]=0

        for result in results:
            cat='%d-%02d' % (result['year'], result['month'])

            if cat not in all_cats:
                continue

            if result['trans_count']>1:
                loyalty_cus[cat]+=1

            all_cus[cat]+=1

        data = {
            "categories": self.build_categories(start_date,end_date),
            "dataset": [{'data':[],'name':_(u'忠诚客户百分比'),'flag':{}}],
            "opts": {
                'chart': {
                    'type': 'column',
                    'height': '500',
                }
            }
        }

        for cat in all_cats:
            percent_value = 0
            if all_cus[cat]==0:
                percent_value = 0
                data['dataset'][0]['data'].append(0)
            else:
                percent_value = round(float(loyalty_cus[cat]*100)/all_cus[cat],2)
                data['dataset'][0]['data'].append(
                    round(float(loyalty_cus[cat]*100)/all_cus[cat],2)
                )

            #小于40差，40到60之间好，大于60健壮
            if percent_value<40:
                data['dataset'][0]['flag'][cat] = '差'
            elif percent_value>=40 and percent_value<60:
                data['dataset'][0]['flag'][cat] = '好'
            else:
                data['dataset'][0]['flag'][cat] = '优'
        return data

#油品与非油品交易比例
class OilGoodsProportionReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = []
    vertical = ['trans_count']
    horizonal = ['hour']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        return ['%d - %d' % (i, i + 1) for i in xrange(0, 24)]

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        hour = result['hour']
        cat = '%d - %d' % (hour, hour + 1)
        if stat.has_key(cat):
            stat[cat][str(result['trans_type'])]=result['trans_count']
        else:
            stat[cat]={}
            stat[cat].setdefault('0',0)
            stat[cat].setdefault('1',0)
            stat[cat]={str(result['trans_type']):result['trans_count']}

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'非油品所占油品交易比例')

    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions()
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown+['trans_type'],
            conditions=conditions,
            details=self.details)

        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None])

        items = stats.items()
        categories = self.build_categories(items)
        data = {
            "categories": categories,
            "dataset": []
        }
        if self.chart_options:
            data['opts'] = self.chart_options

        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = round(float(stat[cat]['1'])/stat[cat]['0']*100,2)
                except:
                    value = 0
                opt["data"].append(value)
            data["dataset"].append(opt)
        self.build_extra(data)
        return data

#非油品占油品交易笔数趋势
class OilGoodsProportionMonthReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    #where
    conditions = []
    vertical = ['trans_count']

    #将通过是否是油品或者非油品来进行归类
    horizonal = ['year', 'month', 'day', 'trans_type']
    series_options = {"type": "spline", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date = kwargs['form'].cleaned_data['start_date']
        end_date = kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        if stat.has_key(cat) == False:

            #判断如果是非油品,并将交易额保存,如果不是就将油品交易额保存
            if result['trans_type'] == 1:
                stat[cat] = {'NON_FUEL':result['trans_count'],'FUEL':0}
            else:
                stat[cat] = {'FUEL':result['trans_count'],'NON_FUEL':0}
        else:

            #判断交易类型,并将剩下的补齐
            if result['trans_type'] == 0:
                stat[cat]['FUEL'] = result['trans_count']
            else:
                stat[cat]['NON_FUEL'] = result['trans_count']

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'非油品交易占油品交易比例')

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory = request.get_session,
            measures = self.vertical,
            drilldown = drilldown,
            conditions = conditions,
            details = self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()
        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    stat[cat] = round((float(stat[cat]['NON_FUEL'])/float(stat[cat]['FUEL']))*100,2)
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)
            data["dataset"].append(opt)
        self.build_extra(data)
        return data

#油品与非油品相关性
class OilGoodsAssocReport(reports.Report):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    fuel_type=fields.ChoiceField(label=ugettext_lazy(u"油品"),choices=[])
    period = fields.ChoiceField(label=ugettext_lazy(u"时段"), choices=DayPeriod.tuples())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        barcode = int(kwargs['form'].cleaned_data['fuel_type'])
        period = int(kwargs['form'].cleaned_data['period'])
        site=kwargs['form'].cleaned_data['site']

        # s = request.get_session(site)
        s = request.get_session()

        price_opt = {"data": [], "name": _(u"价格")}
        assoc_opt = {"data": [], "name": _(u"相关性(TOP10)")}
        fuel_opt={"data":[],"name":_(u"油品")}
        data = {
            "categories": [],
            "dataset": [price_opt, assoc_opt,fuel_opt],
            "opts": {
                'chart': {
                    'type': 'bar',
                },
            }
        }

        #当前用户所有的油品barcode
        all_user_fuel_type=get_user_fuel_type_by_name(request.session['username'])
        fuel_barcode_dict={}
        for item in all_user_fuel_type:
            fuel_barcode_dict[item[0]]=item[1]
        all_user_fuel_str=str(tuple(fuel_barcode_dict.keys())).replace('L','')

        #查看所有的
        if barcode==0:
            sql="SELECT station_item_assoc.item_from,item.barcode, item.desc, item.price, station_item_assoc.weight FROM station_item_assoc "\
                "JOIN item ON station_item_assoc.item_to = item.barcode "\
                "WHERE site=\'%s\' and period = %d and item_from in %s and item_to not in %s"\
                "ORDER BY weight DESC LIMIT 10" % (site,period,all_user_fuel_str,all_user_fuel_str)
        else:
            sql = "SELECT station_item_assoc.item_from,item.barcode, item.desc, item.price, station_item_assoc.weight FROM station_item_assoc "\
                  "JOIN item ON station_item_assoc.item_to = item.barcode "\
                  "WHERE site=\'%s\' and item_from = %d and period = %d and item_to not in %s"\
                  "ORDER BY weight DESC LIMIT 10" % (site,barcode, period,all_user_fuel_str)

        rows = s.execute(sql)
        for row in rows:
            data['categories'].append(row['desc'])
            price_opt['data'].append(row['price'])
            assoc_opt['data'].append(
                round(row['weight'],6)
            )
            fuel_opt['data'].append(fuel_barcode_dict.get(row['item_from']))
        return data

#非油品之间的相关性
class BetweenGoodsAssocReport(reports.Report):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    none_fuel_type=fields.ChoiceField(label=ugettext_lazy(u"非油品"),choices=[])
    period = fields.ChoiceField(label=ugettext_lazy(u"时段"), choices=DayPeriod.tuples())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        barcode = int(kwargs['form'].cleaned_data['none_fuel_type'])
        period = int(kwargs['form'].cleaned_data['period'])
        site=kwargs['form'].cleaned_data['site']

        # s = request.get_session(site)
        s = request.get_session()
        price_opt = {"data": [], "name": _(u"价格")}
        assoc_opt = {"data": [], "name": _(u"相关性(TOP10)")}
        fuel_opt={"data":[],"name":_(u"非油品")}
        data = {
            "categories": [],
            "dataset": [price_opt, assoc_opt,fuel_opt],
            "opts": {
                'chart': {
                    'type': 'bar',
                },
            }
        }
        #当前用户所有的油品barcode
        all_user_fuel_type=get_user_fuel_type_by_name(request.session['username'])
        fuel_barcode_dict={}
        for item in all_user_fuel_type:
            fuel_barcode_dict[item[0]]=item[1]
        all_user_fuel_str=str(tuple(fuel_barcode_dict.keys())).replace('L','')

        #当前用户所有的非油品barcode
        all_user_none_fuel_type=get_user_none_fuel_type_by_name(request.session['username'])
        none_fuel_barcode_dict={}
        for item in all_user_none_fuel_type:
            none_fuel_barcode_dict[item[0]]=item[1]
        all_user_none_fuel_str=str(tuple(none_fuel_barcode_dict.keys())).replace('L','')

        #查看所有的
        if barcode==0:
            sql="SELECT station_item_assoc.item_from,item.barcode, item.desc, item.price, station_item_assoc.weight FROM station_item_assoc "\
                "JOIN item ON station_item_assoc.item_to = item.barcode "\
                "WHERE site=\'%s\' and period = %d and item_from in %s and item_to not in %s "\
                "ORDER BY weight DESC LIMIT 10" % (site,period,all_user_none_fuel_str,all_user_fuel_str)
        else:
            sql = "SELECT station_item_assoc.item_from,item.barcode, item.desc, item.price, station_item_assoc.weight FROM station_item_assoc "\
                  "JOIN item ON station_item_assoc.item_to = item.barcode "\
                  "WHERE site=\'%s\' and item_from = %d and period = %d and item_to not in %s "\
                  "ORDER BY weight DESC LIMIT 10" % (site,barcode, period,all_user_fuel_str)

        rows = s.execute(sql)
        for row in rows:
            data['categories'].append(row['desc'])
            price_opt['data'].append(row['price'])
            assoc_opt['data'].append(
                round(row['weight'],6)
            )
            fuel_opt['data'].append(none_fuel_barcode_dict.get(row['item_from']))
        return data

#阶段性活跃卡数量
class CustomerVIPCounterByDateReport(reports.Report):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    def report(self, request, *args, **kwargs):
        site = kwargs['form'].cleaned_data['site']
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        cube = cubes.TransCube()
        conditions = [cube.d.payment_type==PaymentType.VIP]
        if site:
            conditions.append(cube.d.site == site)

            conditions.append(and_(
                cube.d.datehour>=start_date,
                cube.d.datehour<end_date+timedelta(days=1)
            ))

        results = cube.aggregate(
            session_factory=request.get_session,
            measures=['card_count'],
            conditions=conditions)

        data = {
            "categories": [_(u'阶段性活跃卡数量')],
            "dataset": [],
            "opts": {
                'chart': {
                    'type': 'column',
                    'height': '500',
                }
            }
        }
        opt = {"data": [results[0]['card_count']], "name": _(u'数量（单位：张）')}
        data['dataset'].append(opt)
        return data

#当前持卡客户总数
class CustomerVIPCounterReport(reports.Report):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    def report(self, request, *args, **kwargs):
        site = kwargs['form'].cleaned_data['site']

        cube = cubes.TransCube()
        conditions = [cube.d.payment_type==PaymentType.VIP]
        if site:
            conditions.append(cube.d.site == site)

        results = cube.aggregate(
            session_factory=request.get_session,
            measures=['card_count'],
            conditions=conditions)

        data = {
            "categories": [_(u'阶段性总和数据')],
            "dataset": [],
            "opts": {
                'chart': {
                    'type': 'column',
                    'height': '500',
                }
            }
        }
        opt = {"data": [results[0]['card_count']], "name": _(u'数量（单位：张）')}
        data['dataset'].append(opt)
        return data

#忠诚客户百分比
class CustomerVIPLoyaltyProportionReport(reports.Report):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)

    def report(self, request, *args, **kwargs):
        site = kwargs['form'].cleaned_data['site']
        end_date = kwargs['form'].cleaned_data['date']
        start_date= end_date-timedelta(days=30)

        cube = cubes.TransCube()
        conditions = [
            cube.d.payment_type==PaymentType.VIP,
            and_(
                cube.d.datehour>=start_date,
                cube.d.datehour<end_date+timedelta(days=1)
            ),
        ]
        if site:
            conditions.append(cube.d.site == site)

        results = cube.aggregate(
            session_factory=request.get_session,
            measures=['trans_count'],
            drilldown=['cardnum'],
            conditions=conditions)

        #统计忠诚客户数和总的持卡客户数
        all_cus=len(results)
        loyalty_cus=0
        for result in results:
            if result['trans_count']>1:
                loyalty_cus+=1

        data = {
            "categories": [_(u'忠诚客户百分比')],
            "dataset": [],
            "opts": {
                'chart': {
                    'type': 'column',
                    'height': '500',
                }
            }
        }

        if all_cus==0:
            opt={"data":[0],"name": _(u'百分比（单位：%）')+_(u'(从{start}到{end}统计)').format(start=str(start_date),end=str(end_date))}
        else:
            opt = {"data": [
            round(float(loyalty_cus*100)/all_cus,2)
            ], "name": _(u'百分比（单位：%）')+_('(从{start}到{end}统计)').format(start=str(start_date),end=str(end_date))}
        data['dataset'].append(opt)
        return data

#持卡客户消费趋势
class CustomerVIPCostTrendProportionReport(TransReport):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)

    def build_categories(self,items, **kwargs):
         return ['10%','30%','50%','100%']

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        site = kwargs['form'].cleaned_data['site']
        date=kwargs['form'].cleaned_data['date']

        cube = cubes.TransCube()

        #取得上个自然月时间区间
        pre_month_first_day,pre_month_end_day=prev_bounds(date)
        pre_str='%s-%s'%(pre_month_first_day.year,pre_month_first_day.month)
        ppre_month_first_day,ppre_month_end_day=prev_bounds(pre_month_first_day)
        ppre_str='%s-%s'%(ppre_month_first_day.year,ppre_month_first_day.month)

        conditions = [
            or_(
                and_(
                    cube.d.datehour >= pre_month_first_day,
                    cube.d.datehour < pre_month_end_day+timedelta(days=1)
                ),and_(
                    cube.d.datehour >= ppre_month_first_day,
                    cube.d.datehour < ppre_month_end_day+timedelta(days=1)
                )
            ),
            cube.d.payment_type==PaymentType.VIP
        ]
        if site:
            conditions.append(cube.d.site == site)

        results = cube.aggregate(
            session_factory=request.get_session,
            measures=['pay'],
            drilldown=['year','month','cardnum'],
            conditions=conditions,
            order='pay desc')

        #整理每个客户两个月的消费额
        customer_pay_dict={}
        for result in results:
            customer_pay_dict.setdefault(str(result['cardnum']),{
                pre_str:0,
                ppre_str:0
            })
            customer_pay_dict[str(result['cardnum'])]['%s-%s'%(
                result['year'],result['month']
            )]=result['pay']

        #整理曲线
        go_up_count={}
        go_down_count={}

        #init
        report_cats=self.build_categories(None,**kwargs)
        for cat in report_cats:
            go_up_count.setdefault(cat,0)
            go_down_count.setdefault(cat,0)

        for cus in customer_pay_dict:
            value_of=customer_pay_dict[cus]
            if value_of[ppre_str]==0 and value_of[pre_str]!=0:
                go_up_count['10%']+=1
                continue

            if value_of[pre_str]>value_of[ppre_str]:
                offset=value_of[pre_str]-value_of[ppre_str]
                percent=float(offset*100)/value_of[ppre_str]
                if percent>=100:
                    go_up_count['100%']+=1
                elif percent>=50:
                    go_up_count['50%']+=1
                elif percent>=30:
                    go_up_count['30%']+=1
                elif percent>=10:
                    go_up_count['10%']+=1
            elif value_of[pre_str]==value_of[ppre_str]:
                pass
            else:
                offset=value_of[ppre_str]-value_of[pre_str]
                percent=float(offset*100)/value_of[ppre_str]
                if percent>=100:
                    go_down_count['100%']+=1
                elif percent>=50:
                    go_down_count['50%']+=1
                elif percent>=30:
                    go_down_count['30%']+=1
                elif percent>=10:
                    go_down_count['10%']+=1

        data = {
            "categories":report_cats,
            "dataset": [
                {'data':[],'name':_(u'上升（单位：个）({ppre}对比{pre})').format(ppre=ppre_str,pre=pre_str)},
                {'data':[],'name':_(u'下降（单位：个）({ppre}对比{pre})').format(ppre=ppre_str,pre=pre_str)}
            ],
            "opts": {
                'chart': {
                    'type': 'column',
                    'height': '500',
                }
            }
        }
        for cat in report_cats:
            data['dataset'][0]['data'].append(go_up_count[cat])
            data['dataset'][1]['data'].append(go_down_count[cat])

        return data

#客户消费趋势
class CustomerCostTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    conditions = []
    vertical = ['pay','trans_count']
    horizonal = ['year', 'month', 'day','cardnum','payment_type']
    series_options = {"type": "area", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions()
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)

        #曲线
        loyalty_ser={}
        vip_ser={}
        all_ser={}

        #init
        report_cats=self.build_categories(None,**kwargs)
        for cat in report_cats:
            loyalty_ser.setdefault(cat,0)
            vip_ser.setdefault(cat,0)
            all_ser.setdefault(cat,0)

        already_loyalty_vip={}
        for result in results:
            cat='%d-%02d-%02d' % (result['year'], result['month'], result['day'])
            all_ser[cat]+=result['pay']

            if result['payment_type']==PaymentType.VIP:
                vip_ser[cat]+=result['pay']

                #如果已经被认定为忠诚
                if already_loyalty_vip.has_key(result['cardnum']):
                    #取出第一次的消费额
                    if already_loyalty_vip[result['cardnum']]>0:
                        loyalty_ser[cat]+=already_loyalty_vip[result['cardnum']]
                        already_loyalty_vip[result['cardnum']]=0

                    loyalty_ser[cat]+=result['pay']

                #开始认定
                else:

                    #当天的消费次数已经表明是忠诚
                    if result['trans_count']>1:
                        loyalty_ser[cat]+=result['pay']
                        already_loyalty_vip[result['cardnum']]=0
                    else:
                        already_loyalty_vip[result['cardnum']]=result['pay']

        data = {
            "categories": report_cats,
            "dataset": [
                {"data": [], "name": _(u"忠诚客户消费额")},
                {"data": [], "name": _(u"持卡客户消费额")},
                {"data": [], "name": _(u"所有客户消费额")}
            ]
        }
        if self.chart_options:
            data['opts'] = self.chart_options

        for cat in report_cats:
            data['dataset'][0]['data'].append(round(loyalty_ser[cat],2))
            data['dataset'][1]['data'].append(round(vip_ser[cat],2))
            data['dataset'][2]['data'].append(round(all_ser[cat],2))

        return data

"""
指数
"""

class PumpDailyAvgReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        form = kwargs['form'].cleaned_data
        cache_type=uid('PumpDailyAvgReport')
        cache_key='%s_%s'%(cache_type,'-'.join(all_type_args[cache_type]))
        for arg in all_type_args[cache_type]:
            cache_key+='_'+str(form[arg])

        data=cache.get(cache_key)
        if data is None:
            return {'cache_ret':0}

        else:
            data=json.loads(data)
            data['cache_ret']=1
            return data

class PumpHourlyAvgReport(IndexReport):
    location = fields.ChoiceField(label=u"区域", choices=get_all_locations())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        form = kwargs['form'].cleaned_data
        cache_type=uid('PumpHourlyAvgReport')
        cache_key='%s_%s'%(cache_type,'-'.join(all_type_args[cache_type]))
        for arg in all_type_args[cache_type]:
            cache_key+='_'+str(form[arg])

        data=cache.get(cache_key)
        if data is None:
            return {'cache_ret':0}

        else:
            data=json.loads(data)
            data['cache_ret']=1
            return data

class PumpMonthlyAvgReport(IndexReport):
    location = fields.ChoiceField(label=u"区域", choices=get_all_locations())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        form = kwargs['form'].cleaned_data
        cache_type=uid('PumpMonthlyAvgReport')
        cache_key='%s_%s'%(cache_type,'-'.join(all_type_args[cache_type]))
        for arg in all_type_args[cache_type]:
            cache_key+='_'+str(form[arg])

        data=cache.get(cache_key)
        if data is None:
            return {'cache_ret':0}

        else:
            data=json.loads(data)
            data['cache_ret']=1
            return data

class TransCountAvgReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())
    barcode = fields.ChoiceField(label=ugettext_lazy(u"油品"), choices=get_all_fuel_types(True))

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        form = kwargs['form'].cleaned_data
        cache_type=uid('TransCountAvgReport')
        cache_key='%s_%s'%(cache_type,'-'.join(all_type_args[cache_type]))
        for arg in all_type_args[cache_type]:
            cache_key+='_'+str(form[arg])

        data=cache.get(cache_key)
        if data is None:
            return {'cache_ret':0}

        else:
            data=json.loads(data)
            data['cache_ret']=1
            return data

class GunPumpAvgReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())
    barcode = fields.ChoiceField(label=ugettext_lazy(u"油品"), choices=get_all_fuel_types(True))

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        form = kwargs['form'].cleaned_data
        cache_type=uid('GunPumpAvgReport')
        cache_key='%s_%s'%(cache_type,'-'.join(all_type_args[cache_type]))
        for arg in all_type_args[cache_type]:
            cache_key+='_'+str(form[arg])

        data=cache.get(cache_key)
        if data is None:
            return {'cache_ret':0}

        else:
            data=json.loads(data)
            data['cache_ret']=1
            return data

class NonFuelSalesAvgReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):

        form = kwargs['form'].cleaned_data
        cache_type=uid('NonFuelSalesAvgReport')
        cache_key='%s_%s'%(cache_type,'-'.join(all_type_args[cache_type]))
        for arg in all_type_args[cache_type]:
            cache_key+='_'+str(form[arg])

        data=cache.get(cache_key)
        if data is None:
            return {'cache_ret':0}

        else:
            data=json.loads(data)
            data['cache_ret']=1
            return data

class NonFuelSalesScaleReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        form = kwargs['form'].cleaned_data
        cache_type=uid('NonFuelSalesScaleReport')
        cache_key='%s_%s'%(cache_type,'-'.join(all_type_args[cache_type]))
        for arg in all_type_args[cache_type]:
            cache_key+='_'+str(form[arg])

        data=cache.get(cache_key)
        if data is None:
            return {'cache_ret':0}

        else:
            data=json.loads(data)
            data['cache_ret']=1
            return data

class Top10NonFuelSalesAvgReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        form = kwargs['form'].cleaned_data
        cache_type=uid('Top10NonFuelSalesAvgReport')
        cache_key='%s_%s'%(cache_type,'-'.join(all_type_args[cache_type]))
        for arg in all_type_args[cache_type]:
            cache_key+='_'+str(form[arg])

        data=cache.get(cache_key)
        if data is None:
            return {'cache_ret':0}

        else:
            data=json.loads(data)
            data['cache_ret']=1
            return data

class CustomerMonthlyLoyaltyReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())

    R = {
        0: [16.15, 16.96, 18.04, 19.08, 20.11, 21.07, 22.08, 23.01, 24.2, 25.05, 26.04, 26.98],
        1: [21.26, 22.3, 23.32, 24.4, 25.89, 26.96, 28.44, 29.55, 31.01, 32.42, 33.79, 35.01],
        2: [11.05, 12.46, 13.51, 14.86, 15.93, 17.03, 18.46, 19.81, 20.81, 22.3, 23.41, 24.72],
    }

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        location = int(kwargs['form'].cleaned_data['location'])
        data = {
            "categories": [i for i in range(1, 13)],
            "dataset": [],
        }
        opt = {"data": [], "name": _(u"忠实客户比例"), "type": "column"}
        for cat in data['categories']:
            opt["data"] = self.R[location]
        data["dataset"].append(opt)
        return data

class CustomerMonthlyLeaveReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())

    R = {
        0: [1.82, 1.51, 1.78, 2.14, 2.21, 2.34, 2.25, 2.14, 2.27, 2.27, 2.04, 2.26],
        1: [1.71, 2.73, 1.55, 1.73, 2.44, 1.66, 2.44, 1.58, 2.55, 2.4, 2.67, 1.62],
        2: [1.71, 2.73, 1.55, 1.73, 2.44, 1.66, 2.44, 1.58, 2.55, 2.4, 2.67, 1.62],
    }

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        location = int(kwargs['form'].cleaned_data['location'])
        data = {
            "categories": [i for i in range(1, 13)],
            "dataset": [],
        }
        opt = {"data": [], "name": _(u"忠实客户流失率"), "type": "column"}
        for cat in data['categories']:
            opt["data"] = self.R[location]
        data["dataset"].append(opt)
        return data

class CustomerMonthlySalesScaleReport(IndexReport):
    location = fields.ChoiceField(label=ugettext_lazy(u"区域"), choices=get_all_locations())

    R = {
        0: [45.94, 46.84, 47.78, 48.74, 49.93, 51.0, 52.18, 53.33, 54.41, 55.52, 56.37, 57.36],
        1: [50.87, 51.71, 52.8, 53.66, 54.7, 55.66, 56.63, 57.72, 58.59, 59.43, 60.39, 61.22],
        2: [41.09, 42.11, 43.1, 44.26, 45.46, 46.56, 47.51, 48.33, 49.47, 50.34, 51.36, 52.5],
    }

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        location = int(kwargs['form'].cleaned_data['location'])
        data = {
            "categories": [i for i in range(1, 13)],
            "dataset": [],
        }
        opt = {"data": [], "name": _(u"忠实客户销售额占比"), "type": "column"}
        for cat in data['categories']:
            opt["data"] = self.R[location]
        data["dataset"].append(opt)
        return data

class FuelAssocReport(reports.Report):

    barcode = fields.ChoiceField(label=ugettext_lazy(u"油品"), choices=get_all_fuel_types())
    period = fields.ChoiceField(label=ugettext_lazy(u"时段"), choices=DayPeriod.tuples())

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        barcode = int(kwargs['form'].cleaned_data['barcode'])
        period = int(kwargs['form'].cleaned_data['period'])
        s = request.get_session()
        price_opt = {"data": [], "name": _(u"价格")}
        assoc_opt = {"data": [], "name": _(u"相关性")}
        data = {
            "categories": [],
            "dataset": [price_opt, assoc_opt],
            "opts": {
                'chart': {
                    'type': 'bar',
                },
            }
        }

        sql = "SELECT item.barcode, item.desc, item.price, item_assoc.weight FROM item_assoc "\
              "JOIN item ON item_assoc.item_to = item.barcode "\
              "WHERE item_from = %d and period = %d and item.barcode > 400000 ORDER BY weight DESC LIMIT 25" % (barcode, period)
        rows = s.execute(sql)
        for row in rows:
            data['categories'].append(row['desc'])
            price_opt['data'].append(row['price'])
            assoc_opt['data'].append(row['weight'])
        return data

#油品销售额占总销售额比例
class OilToTotalSalesTrendDashlet(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    #where
    conditions = []
    vertical = ['pay']

    #将通过是否是油品或者非油品来进行归类
    horizonal = ['year', 'month', 'day', 'trans_type']
    series_options = {"type": "spline", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date = kwargs['form'].cleaned_data['start_date']
        end_date = kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        if stat.has_key(cat) == False:

            #判断如果是非油品,并将交易额保存,如果不是就将油品交易额保存
            if result['trans_type'] == 1:
                stat[cat] = {'NON_FUEL':result['pay'],'FUEL':0}
            else:
                stat[cat] = {'FUEL':result['pay'],'NON_FUEL':0}
        else:

            #判断交易类型,并将剩下的补齐
            if result['trans_type'] == 0:
                stat[cat]['FUEL'] = result['pay']
            else:
                stat[cat]['NON_FUEL'] = result['pay']

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'油品占总额比例')

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory = request.get_session,
            measures = self.vertical,
            drilldown = drilldown,
            conditions = conditions,
            details = self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:

                    #计算这天的油品销售额占总额的比例
                    total = stat[cat]['FUEL']+stat[cat]['NON_FUEL']
                    stat[cat] = round((stat[cat]['FUEL']/total)*100,2)
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)
            data["dataset"].append(opt)
        self.build_extra(data)
        return data

#油非比,计算公式：油非比=非油销售额（元）/油品销售升数（升）
class OilAndStorePercentTrendReport(TransReport):
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])

    #where
    conditions = []
    vertical = ['pay','quantity']

    #将通过是否是油品或者非油品来进行归类
    horizonal = ['year', 'month', 'day', 'trans_type']
    series_options = {"type": "spline", "stacking": "normal"}

    @overrides(TransReport)
    def build_categories(self,items, **kwargs):
        start_date = kwargs['form'].cleaned_data['start_date']
        end_date = kwargs['form'].cleaned_data['end_date']

        categories = []
        curr_date = start_date
        while curr_date <= end_date:
            categories.append(curr_date.strftime("%Y-%m-%d"))
            curr_date += timedelta(days=1)
        return categories

    @overrides(TransReport)
    def build_result(self, result, stat,**kwargs):
        cat = '%d-%02d-%02d' % (result['year'], result['month'], result['day'])
        if stat.has_key(cat) == False:

            #判断如果是非油品,并将交易额保存,如果不是就将油品交易量保存
            if result['trans_type'] == 1:
                stat[cat] = {'NON_FUEL':result['pay'],'FUEL':0}
            else:
                stat[cat] = {'FUEL':result['quantity'],'NON_FUEL':0}
        else:

            #判断交易类型,并将剩下的补齐
            if result['trans_type'] == 0:
                stat[cat]['FUEL'] = result['quantity']
            else:
                stat[cat]['NON_FUEL'] = result['pay']

    @overrides(TransReport)
    def series_name(self, series=None):
        return _(u'油非比')

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory = request.get_session,
            measures = self.vertical,
            drilldown = drilldown,
            conditions = conditions,
            details = self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        count=0
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:

                    #计算这天的油非比
                    stat[cat] = round((stat[cat]['NON_FUEL']/stat[cat]['FUEL'])*100,2)
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)
            data["dataset"].append(opt)
        self.build_extra(data)
        return data

#区域销售额趋势排名
class MultiOilMoneyTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['pay']
    horizonal = ['year', 'month', 'site']
    series_options = {"type":"chart", "stacking":"normal"}
    fuel_opt_name = _(u"销售额(单位:元)")
    site_opt_name = _(u"站点")


#多站出油时间趋势图
class MultiOilTimeTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location=fields.ChoiceField(label=ugettext_lazy(u"区域范围"),choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['quantity']
    horizonal = ['year', 'month','site']
    series_options = {"type": "chart", "stacking": "normal"}
    fuel_opt_name = _(u"时间(单位:分钟)")
    site_opt_name = _(u"站点")


#区域非油品销量趋势排行图
class MultiNoneOilSalesTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['quantity_nonefuel']
    horizonal = ['year', 'month', 'site']
    series_options = {"type":"chart", "stacking":"normal"}
    fuel_opt_name = _(u"销量(单位:个)")
    site_opt_name = _(u"站点")

#区域加满率排行
class MultiFillOutPercentTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['fuel_fillout_percent']
    horizonal = ['year', 'month', 'site']
    series_options = {"type":"chart", "stacking":"normal"}
    fuel_opt_name = _(u"百分比(单位:%)")
    site_opt_name = _(u"站点")


#区域高峰期平均出油量趋势排行
class MultiOilPeakFuelAvgGunTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['peak_fuel_count']
    horizonal = ['year', 'month', 'site']
    series_options = {"type":"chart", "stacking":"normal"}
    fuel_opt_name = _(u"出油量(单位:升)")
    site_opt_name = _(u"站点")


#区域加油卡比例排行
class MultiVIPPayPercentTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['vip_pay_percent']
    horizonal = ['year', 'month', 'site']
    series_options = {"type":"chart", "stacking":"normal"}
    fuel_opt_name = _(u"百分比(单位：%)")
    site_opt_name = _(u"站点")


#区域油品环比百分比排行
class MultiOilMoMTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['quantity_fuel','pre_mon_quantity_fuel']
    horizonal = ['year', 'month', 'site']
    series_options = {"type":"chart", "stacking":"normal"}
    fuel_opt_name = _(u"百分比(单位：%)")
    site_opt_name = _(u"站点")

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):

        #确定地区过滤器
        s = request.get_session()

        #取得查询对象
        cube = cubes.StationMonthStatCube()

        #获得区县信息和时间
        location_barcode = int(kwargs['form'].cleaned_data['china_location'])
        year_date = int(kwargs['form'].cleaned_data['date'][:4])
        month_date = int(kwargs['form'].cleaned_data['date'][5:])

        if location_barcode == 0:
            return {
                "categories": [],
                "dataset": []
            }

        #通过区县信息查询完整的信息
        location = s.query(DimChinaProvinceCityDistrict).filter_by(id=location_barcode).one()

        #添加查询条件
        conditions = self.init_conditions(**kwargs) + self.conditions
        conditions.append(self.cube.d.year == year_date)
        conditions.append(self.cube.d.month == month_date)

        drilldown = [] + self.horizonal

        #下面的三个判断根据区县等级来确定查询的条件
        if location.level == 1:
            conditions.append(Station.province == location.id)
            drilldown.append('city')
            self.series = 'city'

        elif location.level == 2:
            conditions.append(Station.city == location.id)
            drilldown.append('district')
            self.series = 'district'

        else:
            conditions.append(Station.district == location.id)
            drilldown.append('name')
            self.series = 'name'
            series_options = {"type":"line", "stacking":None}

        #必须是用户拥有的油站
        stations = get_user_stations_by_name(request.session['username'])

        #遍历出所有的油站,并添加在查询条件中
        all_sites = [x[0] for x in stations]
        conditions.append(self.cube.d.site.in_(all_sites))

        self.post_init_conditions(**kwargs)
        results = self.cube.aggregate(
            session_factory = request.get_session,
            measures = self.vertical,
            drilldown = drilldown,
            conditions = conditions,
            details = self.details,
            order = self.vertical[0] + ' desc',
            session = request.get_session()
        )
        categories = []
        fuel_opt = {"data":[], "name":self.fuel_opt_name}
        site_opt = {"data":[], "name":self.site_opt_name}

        #判断如果查询结果为0就将通过添加条件到一个方法中使其产生数据保存在表中
        if len(results) == 0:
            for site in all_sites:
                compute_station_monthbatch(site, year_date, month_date)

            #执行添加之后再查询结果
            results = self.cube.aggregate(
                session_factory = request.get_session,
                measures = self.vertical,
                drilldown = drilldown,
                conditions = conditions,
                details = self.details,
                order = self.vertical[0] + ' desc',
                session = request.get_session()
            )
        #排名
        count = 1

        #将结果遍历出来并保存到字典中,通过返回data来将数据传递给前端
        for result in results:
            if result['pre_mon_quantity_fuel'] == 0:
                fuel_opt['data'].append(0)
            else:
                fuel_opt['data'].append(round(result['quantity_fuel']/result['pre_mon_quantity_fuel']*100,2))
            site_name = s.query(Station).filter_by(name=result['site']).one()
            result['site'] = site_name.description
            site_opt['data'].append(result['site'])
            categories.append(count)
            count+=1
        data = {
            "categories": categories,
            "dataset": [fuel_opt, site_opt],
            "opts": {
                'chart': {
                    'type': 'bar',
                },
            }
        }
        self.build_extra(data)
        return data


#区域非油品环比排行
class MultiNoneOilMoMTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['quantity_nonefuel', 'pre_mon_quantity_nonefuel']
    horizonal = ['year', 'month', 'site']
    series_options = {"type":"chart", "stacking":"normal"}
    fuel_opt_name = _(u"百分比(单位：%)")
    site_opt_name = _(u"站点")

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):

        #确定地区过滤器
        s = request.get_session()

        #取得查询对象
        cube = cubes.StationMonthStatCube()

        #获得区县信息和时间
        location_barcode = int(kwargs['form'].cleaned_data['china_location'])
        year_date = int(kwargs['form'].cleaned_data['date'][:4])
        month_date = int(kwargs['form'].cleaned_data['date'][5:])

        if location_barcode == 0:
            return {
                "categories": [],
                "dataset": []
            }

        #通过区县信息查询完整的信息
        location = s.query(DimChinaProvinceCityDistrict).filter_by(id=location_barcode).one()

        #添加查询条件
        conditions = self.init_conditions(**kwargs) + self.conditions
        conditions.append(self.cube.d.year == year_date)
        conditions.append(self.cube.d.month == month_date)

        drilldown = [] + self.horizonal

        #下面的三个判断根据区县等级来确定查询的条件
        if location.level == 1:
            conditions.append(Station.province == location.id)
            drilldown.append('city')
            self.series = 'city'

        elif location.level == 2:
            conditions.append(Station.city == location.id)
            drilldown.append('district')
            self.series = 'district'

        else:
            conditions.append(Station.district == location.id)
            drilldown.append('name')
            self.series = 'name'
            series_options = {"type":"line", "stacking":None}

        #必须是用户拥有的油站
        stations = get_user_stations_by_name(request.session['username'])

        #遍历出所有的油站,并添加在查询条件中
        all_sites = [x[0] for x in stations]
        conditions.append(self.cube.d.site.in_(all_sites))

        self.post_init_conditions(**kwargs)
        results = self.cube.aggregate(
            session_factory = request.get_session,
            measures = self.vertical,
            drilldown = drilldown,
            conditions = conditions,
            details = self.details,
            order = self.vertical[0] + ' desc',
            session = request.get_session()
        )
        categories = []
        fuel_opt = {"data":[], "name":self.fuel_opt_name}
        site_opt = {"data":[], "name":self.site_opt_name}

        #判断如果查询结果为0就将通过添加条件到一个方法中使其产生数据保存在表中
        if len(results) == 0:
            for site in all_sites:
                compute_station_monthbatch(site, year_date, month_date)

            #执行添加之后再查询结果
            results = self.cube.aggregate(
                session_factory = request.get_session,
                measures = self.vertical,
                drilldown = drilldown,
                conditions = conditions,
                details = self.details,
                order = self.vertical[0] + ' desc',
                session = request.get_session()
            )
        #排名
        count = 1

        #将结果遍历出来并保存到字典中,通过返回data来将数据传递给前端
        for result in results:
            if result['pre_mon_quantity_nonefuel'] == 0:
                fuel_opt['data'].append(0)
            else:
                fuel_opt['data'].append(round(result['quantity_nonefuel']/result['pre_mon_quantity_nonefuel']*100,2))
            site_name = s.query(Station).filter_by(name=result['site']).one()
            result['site'] = site_name.description
            site_opt['data'].append(result['site'])
            categories.append(count)
            count+=1
        data = {
            "categories": categories,
            "dataset": [fuel_opt, site_opt],
            "opts": {
                'chart': {
                    'type': 'bar',
                },
            }
        }
        self.build_extra(data)
        return data


#客单值排行
class MultiSingleCustomerPayTrendSortReport(MultiStationSortReport):

    #使用StationMonthStatCube
    cube = cubes.StationMonthStatCube()
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.MonthDateField(label=ugettext_lazy(u"月份"))

    conditions = []
    vertical = ['single_customer_pay']
    horizonal = ['year', 'month', 'site']
    series_options = {"type":"chart", "stacking":"normal"}
    fuel_opt_name = _(u"销售额(单位：元)")
    site_opt_name = _(u"站点")

#诊断结果
class HealthReport(reports.Report):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)

    @overrides(reports.Report)
    def report(self, request, *args, **kwargs):
        site=kwargs['form'].cleaned_data['site']
        # s = request.get_session(site)
        s = request.get_session()
        src_session=get_dash_session_maker()()
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        result_opt = {"data": [], "name": _(u"诊断结果")}
        data = {
            "categories": [],
            "dataset": [result_opt],
            "opts": {
                'chart': {
                    'type': 'bar',
                },
            }
        }
        s = request.get_session()

        #算高峰期时段
        values={}
        #cache result
        for i in xrange(0, (end_date-start_date).days):
            cache_key='%s_%s_%s'%(site,0,start_date+timedelta(days=i))
            key=(start_date+timedelta(days=i)).strftime("%Y-%m-%d")
            try:
                values[key]=json.loads(cache.get(cache_key))
            except:
                pass


        #指标查询
        sql="SELECT sum(fact_trans.pay) AS pay, count(DISTINCT fact_trans.trans_id) AS trans_count, "\
            "fact_trans.payment_type As payment_type ,fact_trans.cardnum As cardnum ,sum(fact_trans.pump_type) As pump,sum(fact_trans.quantity) As quantity, "\
            "fact_trans.desc As desc,fact_trans.trans_type As trans_type,fact_trans.datehour As datehour FROM fact_trans WHERE fact_trans.site = '%s' AND fact_trans.datehour >= '%s' "\
            " AND fact_trans.datehour < '%s' AND fact_trans.quantity > 0"\
            " GROUP BY fact_trans.payment_type, fact_trans.cardnum,fact_trans.desc,fact_trans.trans_type,fact_trans.datehour"%(site,start_date.strftime('%Y-%m-%d'),end_date.strftime('%Y-%m-%d'))
        rows = s.execute(sql)

        #当前用户所有的油品barcode
        all_user_fuel_type=get_user_fuel_type_by_name(request.session['username'])
        fuel_barcode_dict={}
        for item in all_user_fuel_type:
            fuel_barcode_dict[item[0]]=item[1]
        all_user_fuel_str=str(tuple(fuel_barcode_dict.keys())).replace('L','')

        #当前用户所有的非油品barcode
        all_user_none_fuel_type=get_user_none_fuel_type_by_name(request.session['username'])
        none_fuel_barcode_dict={}
        for item in all_user_none_fuel_type:
            none_fuel_barcode_dict[item[0]]=item[1]
        all_user_none_fuel_str=str(tuple(none_fuel_barcode_dict.keys())).replace('L','')

        #非油品之间的相关性
        sql2="SELECT station_item_assoc.item_from,item.barcode FROM station_item_assoc "\
        "JOIN item ON station_item_assoc.item_to = item.barcode "\
        "WHERE site=\'%s\' and period = 0 and item_from in %s and item_to not in %s "% (site,all_user_none_fuel_str,all_user_fuel_str)

        rows2 = src_session.execute(sql2)

        #油品与非油品之间的相关性
        sql3="SELECT station_item_assoc.item_from FROM station_item_assoc "\
            "JOIN item ON station_item_assoc.item_to = item.barcode "\
            "WHERE site=\'%s\' and period = 0 and item_from in %s and item_to not in %s"\
            % (site,all_user_fuel_str,all_user_fuel_str)

        rows3 = src_session.execute(sql3)

        #油枪出油效率
        sql4="SELECT sum(fact_trans.quantity) AS quantity,fact_trans.datehour As datehour FROM fact_trans "\
             "WHERE fact_trans.site = '%s' AND fact_trans.datehour >= '%s' AND fact_trans.datehour < '%s' "\
             "AND fact_trans.trans_type = 0 GROUP BY fact_trans.datehour"%(site,start_date,end_date)

        rows4 = s.execute(sql4)

        #客单值的初始值
        value = 0.0

        #忠诚度初始值
        percent_value = 0.0

        #92/93加满率初始值
        pump_92_value=0.0
        pump_92_count=0

        #95/97加满率初始值
        pump_95_value=0.0
        pump_95_count=0

        #柴油加满率初始值
        pump_0_value=0.0
        pump_0_count=0

        #92/93平均单车加油量初始值
        single_92_quantity_value=0

        #95/97平均单车加油量初始值
        single_95_quantity_value=0

        #忠诚客户初始值
        loyalty_cus=0

        #总客户初始值
        all_cus=0

        #油品交易笔数初始值
        fuel_count=0

        #非油品交易笔数初始值
        none_fuel_count=0

        #高峰期油品交易笔数初始值
        crest_fuel_count=0

        #高峰期非油品交易笔数初始值
        crest_none_fuel_count=0

        #高峰期油非转化率初始值
        crest_none_and_fuel_percent=0

        #日常油非转化率初始值
        none_and_fuel_percent=0

        #高峰期油枪初始值
        crest_pump_time=0

        #高峰期油枪效率初始值
        crest_pump_time_percent=0


        for row in rows:
            #客单值
            if row['pay']!=None:
                if row['trans_type']==1:
                    value+=round(row['pay']/row['trans_count'], 2)
            else:
                value=-1

            #忠诚客户
            if row['payment_type']==2:
                all_cus += 1
                if row['trans_count']>1:
                    loyalty_cus+=1

            #92/93加满率
            if ('92' in row['desc'] or '93' in row['desc']) and row['trans_type']==0:
                pump_92_value+=row['pump']
                pump_92_count+=1

            #95/97加满率
            elif ('95' in row['desc'] or '97' in row['desc']) and row['trans_type']==0:
                pump_95_value+=row['pump']
                pump_95_count+=1

            #柴油加满率
            elif '柴油' in row['desc'] and row['trans_type']==0:
                pump_0_value+=row['pump']
                pump_0_count+=1

            #92/93平均加油量
            if row['trans_type']==0 and ('92' in row['desc'] or '93' in row['desc']):
                single_92_quantity_value+=row['quantity']

            #95/97平均加油量
            if row['trans_type']==0 and ('95' in row['desc'] or '97' in row['desc']):
                single_95_quantity_value+=row['quantity']

            #油非转化率（分高峰期和日常）
            if row['trans_type']==0:
                fuel_count+=row['trans_count']
            else:
                none_fuel_count+=row['trans_count']

            row_time = row['datehour'].strftime("%Y-%m-%d")
            try:
                for time in values[row_time]:
                    if row['datehour'].hour>=time[0] and row['datehour'].hour<time[1]:
                        if row['trans_type']==0:
                            crest_fuel_count+=row['trans_count']
                        else:
                            crest_none_fuel_count+=row['trans_count']
                        break
            except:
                pass

        #高峰期油枪效率
        for row in rows4:
            row_time = row['datehour'].strftime("%Y-%m-%d")
            try:
                for time in values[row_time]:
                    if row['datehour'].hour>=time[0] and row['datehour'].hour<time[1]:
                        crest_pump_time+=row['quantity']
                        break
            except:
                pass
        crest_pump_time=round(crest_pump_time/settings.PUMP_TRANS_TIME,0)
        crest_pump_time_percent=crest_pump_time/(end_date-start_date).days/24

        assoc_count = rows2.rowcount
        none_and_fuel_assoc_count = rows3.rowcount

        #客单值
        if value>=0:
            value = abs(value/(end_date-start_date).days/24)

        #持卡客户
        if all_cus>0:
            percent_value = round(100*loyalty_cus/all_cus,2)

        #92/93加满率
        if pump_92_count>0:
            pump_92_value = round(100*(pump_92_count-pump_92_value)/pump_92_count,2)

        #95/97加满率
        if pump_95_count>0:
            pump_95_value = round(100*(pump_95_count-pump_95_value)/pump_95_count,2)

        #柴油加满率
        if pump_0_count>0:
            pump_0_value = round(100*(pump_0_count-pump_0_value)/pump_0_count,2)

        single_92_quantity_value = round(single_92_quantity_value/(end_date-start_date).days/24,2)
        single_95_quantity_value = round(single_95_quantity_value/(end_date-start_date).days/24,2)
        if crest_fuel_count>0:
            crest_none_and_fuel_percent = round(100*crest_none_fuel_count/crest_fuel_count/(end_date-start_date).days/24,2)
        if (none_fuel_count-crest_none_fuel_count)>0:
            none_and_fuel_percent = round(100*(none_fuel_count-crest_none_fuel_count)/(none_fuel_count-crest_none_fuel_count)/(end_date-start_date).days/24,2)
        #没有查到数据为无，小于20为差，20到100为正常，100以上为好
        if rows.rowcount==0 or value<0:
            result_opt['data'].append('无')
        elif value < 20:
            result_opt['data'].append('差')
        elif value >=20 and value<100:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        if rows.rowcount==0 or percent_value<0:
            result_opt['data'].append('无')
        #小于40差，40到60之间好，大于60健壮
        elif percent_value<40:
            result_opt['data'].append('差')
        elif percent_value>=40 and percent_value<60:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')


        #92/93平均单车加油量
        if rows.rowcount==0 or single_92_quantity_value<0:
            result_opt['data'].append('无')
        elif single_92_quantity_value<20:
            result_opt['data'].append('差')
        elif single_92_quantity_value>=20 and single_92_quantity_value<40:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #95/97平均单车加油量
        if rows.rowcount==0 or single_95_quantity_value<0:
            result_opt['data'].append('无')
        elif single_95_quantity_value<20:
            result_opt['data'].append('差')
        elif single_95_quantity_value>=20 and single_95_quantity_value<40:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #日常油枪效率
        if rows.rowcount==0 or crest_pump_time_percent<0:
            result_opt['data'].append('无')
        elif crest_pump_time_percent<5:
            result_opt['data'].append('差')
        elif crest_pump_time_percent>=5 and crest_pump_time_percent<8:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #92/93加满率
        if rows.rowcount==0 or pump_92_value<0:
            result_opt['data'].append('无')
        elif pump_92_value<50:
            result_opt['data'].append('差')
        elif pump_92_value>=50 and pump_92_value<60:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #95/97加满率
        if rows.rowcount==0 or pump_95_value<0:
            result_opt['data'].append('无')
        elif pump_95_value<60:
            result_opt['data'].append('差')
        elif pump_95_value>=60 and pump_95_value<70:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #柴油加满率
        if rows.rowcount==0 or pump_0_value<0:
            result_opt['data'].append('无')
        elif pump_0_value<70:
            result_opt['data'].append('差')
        elif pump_0_value>=70 and pump_0_value<90:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #日常时期油非转化率
        if rows.rowcount==0 or none_and_fuel_percent<0:
            result_opt['data'].append('无')
        elif none_and_fuel_percent<8:
            result_opt['data'].append('差')
        elif none_and_fuel_percent>=8 and none_and_fuel_percent<12:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #高峰期油非转化率
        if rows.rowcount==0 or crest_none_and_fuel_percent<0:
            result_opt['data'].append('无')
        elif crest_none_and_fuel_percent<5:
            result_opt['data'].append('差')
        elif crest_none_and_fuel_percent>=5 and crest_none_and_fuel_percent<10:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #非油品之间的相关性
        if assoc_count<=0:
            result_opt['data'].append('差')
        elif assoc_count>=5 and assoc_count<8:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        #油品与非油品之间的相关性
        if none_and_fuel_assoc_count<=0:
            result_opt['data'].append('差')
        elif none_and_fuel_assoc_count>=5 and none_and_fuel_assoc_count<8:
            result_opt['data'].append('好')
        else:
            result_opt['data'].append('优')

        data['categories']=['客单值','忠诚客户','92/93#平均单车加油量','95/97#平均单车加油量','高峰期油枪效率','92/93#加满率','95/97#加满率','柴油加满率','日常油非转化率','高峰期油非转化率','非油品相关性','油品与非油品的相关性']
        return data

#
class MultiStationHealthReport(TransReport):
    china_location = fields.ChoiceField(label=ugettext_lazy(u"区域范围"), choices=[])
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)

    @overrides(TransReport)
    def report(self, request, *args, **kwargs):

        date = kwargs['form'].cleaned_data['date']
        location_barcode=int(kwargs['form'].cleaned_data['china_location'])
        session = request.get_session()

        data = {
            "categories": [],
            "dataset": [],
            "opts": {
                'chart': {
                    'type': 'multi_table',
                },
            }
        }

        data['categories']=['瓶颈','重复客户','客单值',
        '92/93#平均单车加油量','95/97#平均单车加油量',
        '高峰期油枪效率','92/93#加满率','95/97#加满率',
        '柴油加满率','日常油非转化率','高峰期油非转化率',
        '非油品相关性','油品与非油品的相关性']

        data['dataset'].append(dict(
                station_name = "油站名",
                data = [{"title":u"健康指标","value":u"诊断结果","status":u"参考区间"}]
            ))

        #通过区县信息查询完整的信息
        #必须是用户拥有的油站
        site_list = []
        try :
            user = session.query(User).filter_by(name=request.session['username']).one()
            stations = session.query(UserStation).filter_by(user_id=user.id).all()
            for station in stations :
                station_code = station.station
                try :
                    site = session.query(Station).filter_by(name = station_code).one()
                except Exception,e:
                    continue
                if site.province == location_barcode :
                    site_list.append(dict(
                            station_name = site.description,
                            station_code = site.name
                        ))
                else :
                    continue
        except Exception,e:
            data['dataset'] = []
            return data
        health_type_map = {

                0:u"瓶颈",
                1:u"重复客户",
                2:u"客单值",
                3:u"92/93#平均单车加油量",
                4:u"95/97#平均单车加油量",
                5:u"高峰期油枪效率",
                6:u"92/93#加满率",
                7:u"95/97#加满率",
                8:u"柴油加满率",
                9:u"日常油非转化率",
                10:u"高峰期油非转化率",
                11:u"非油品相关性",
                12:u"油品与非油品的相关性",

            }
        health_type_length = len(health_type_map.keys())
        for station in site_list :
            date = datetime(date.year,date.month,date.day)
            station_health_status = session.query(StationHealthStatus).filter_by(date=date,site=station['station_code']).all()
            #健康指标类型，0：瓶颈 1 重复客户 2 客单值 3 92/93#平均单车加油量 4 95/97#平均单车加油量
            #5 高峰期油枪效率 6 92/93#加满率 7 95/97#加满率 8 柴油加满率 9 日常油非转化率 10 高峰期油非转化率
            #11 非油品相关性 12 油品与非油品的相关性
            #健康指标数量


            health_type_list = []
            health_status_list = {}
            for station_health in station_health_status :
                health_type_list.append(station_health.type)
                health_status_list[station_health.type] = station_health.info
            temp_data = []
            for i in range(health_type_length) :
                if i in health_type_list :
                    temp_data.append(dict(
                            title = str(health_type_map[i]),
                            value = health_status_list[i],
                            type = i
                        ))
                else :
                    temp_data.append(dict(
                            title = health_type_map[i],
                            value = u"无",
                            type = i
                        ))

            data['dataset'].append(dict(
                    station_name = station['station_name'],
                    data = temp_data
                ))
        return data

#性能瓶颈
class BottleneckReport(TransReport):
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])
    start_date = fields.DateField(label=ugettext_lazy(u"开始"), initial=DEFAULT_DATE - timedelta(days=30))
    end_date = fields.DateField(label=ugettext_lazy(u"结束"), initial=DEFAULT_DATE)


    @overrides(TransReport)
    def report(self, request, *args, **kwargs):
        site=kwargs['form'].cleaned_data['site']
        s = request.get_session(site)
        start_date=kwargs['form'].cleaned_data['start_date']
        end_date=kwargs['form'].cleaned_data['end_date']

        #初始化两条曲线，第三个显示指标
        result_opt1 = {"data": [0 for i in xrange(0, 24)], "name": ""}
        result_opt2 = {"data": [0 for i in xrange(0, 24)], "name": ""}

        #求高峰期临时存储数据
        temp_result_opt1 = []
        temp_result_opt2 = []

        temp_data1={"dataset":[]}
        temp_data2={"dataset":[]}


        data = {
            "categories": ['%d - %d' % (i, i + 1) for i in xrange(0, 24)],
            "dataset": [result_opt1,result_opt2],
            "opts": {
                'chart': {
                    'type': 'spline',
                },
            },
            "tip":"无瓶颈"
        }


        #从一个月中选出2天最大的出油量
        sql="SELECT sum(fact_trans.quantity) AS quantity ,dim_datehour.year, dim_datehour.month,dim_datehour.day FROM fact_trans JOIN dim_datehour ON dim_datehour.id = fact_trans.datehour "\
             "WHERE fact_trans.site = '%s' AND fact_trans.datehour >= '%s' AND fact_trans.datehour < '%s' "\
             "AND fact_trans.trans_type = 0 GROUP BY dim_datehour.year, dim_datehour.month,dim_datehour.day ORDER BY quantity DESC LIMIT 2"%(site,start_date,end_date)

        rows = s.execute(sql)

        #存储时间
        times=[]

        for row in rows:
            time='%s-%s-%s'%(row['year'],row['month'],row['day'])
            time=datetime.strptime(time, "%Y-%m-%d")
            times.append(time)
        if len(times)==2:
            temp_sql="SELECT sum(fact_trans.quantity) AS quantity, dim_datehour.hour AS hour "\
                    "FROM fact_trans JOIN dim_datehour ON dim_datehour.id = fact_trans.datehour "\
                    "WHERE fact_trans.site = '%s' AND fact_trans.datehour >= '%s'"\
                    " AND fact_trans.datehour < '%s' AND fact_trans.trans_type = 0 GROUP BY dim_datehour.hour"%(site,times[0].strftime("%Y-%m-%d"),(times[0]+timedelta(days=1)).strftime("%Y-%m-%d"))

            temp_rows=s.execute(temp_sql)
            for temp_row in temp_rows:
                result_opt1['data'][temp_row['hour']]=temp_row['quantity']
            result_opt1['name']=times[0].strftime("%Y-%m-%d")

            temp_sql2="SELECT sum(fact_trans.quantity) AS quantity, dim_datehour.hour AS hour "\
                    "FROM fact_trans JOIN dim_datehour ON dim_datehour.id = fact_trans.datehour "\
                    "WHERE fact_trans.site = '%s' AND fact_trans.datehour >= '%s'"\
                    " AND fact_trans.datehour < '%s' AND fact_trans.trans_type = 0 GROUP BY dim_datehour.hour"%(site,times[1].strftime("%Y-%m-%d"),(times[1]+timedelta(days=1)).strftime("%Y-%m-%d"))

            temp_rows2=s.execute(temp_sql2)
            for temp_row in temp_rows2:
                result_opt2['data'][temp_row['hour']]=temp_row['quantity']
            result_opt2['name']=times[1].strftime("%Y-%m-%d")

            temp_result_opt1.append(result_opt1)
            temp_result_opt2.append(result_opt2)
            temp_data1['dataset']=temp_result_opt1
            temp_data2['dataset']=temp_result_opt2

            crest1=get_peak_period(temp_data1)
            crest2=get_peak_period(temp_data2)

            #求高峰期交际
            tmp = [val for val in crest1['period']['crest'] if val in crest2['period']['crest']]

            #查询高峰期时两条曲线是否有交点，如果有则存在瓶颈
            for point in tmp:
                if result_opt1['data'][point]<result_opt2['data'][point]:
                    data['tip']="有瓶颈"
                    break

        return data

#整站单枪效能鸟瞰图  需要找渲染插件
class ThreeDimensionalReport(TransReport):
    date = fields.DateField(label=ugettext_lazy(u"日期"), initial=DEFAULT_DATE)
    site = fields.ChoiceField(label=ugettext_lazy(u"站点"), choices=[])


    def report(self, request, *args, **kwargs):
        site=kwargs['form'].cleaned_data['site']
        date = kwargs['form'].cleaned_data['date']
        start_time = str(date) + " " + "00:00:00"
        end_time = str(date) + " " + "23:59:59"
        s = request.get_session(site)

        result=[]
        #临时
        data = {
            "categories": [],
            "dataset": {},
            "opts": {
                'chart': {
                    'type': 'threedimensionaldash',
                },
            },
        }
        sql="SELECT sum(fact_trans.quantity) AS quantity, fact_trans.pump_id AS pump_id "\
        "FROM fact_trans WHERE fact_trans.site = '%s' And fact_trans.trans_type = 0 And fact_trans.timestamp >= '%s' And fact_trans.timestamp <= '%s' " \
        " GROUP BY fact_trans.pump_id"%(site,start_time,end_time)
        rows=s.execute(sql)
        for row in rows:
            tmp=getChannelAndColumnByPump(site,row['pump_id'])
            if tmp.has_key('column') and tmp.has_key('passage'):
                tmp['pump_id']=row['pump_id']
                tmp['quantity']=round(row['quantity'],2)
            result.append(tmp)
        passages = []
        columns = []
        for item in result :
            if item.has_key("passage") and item.has_key("column"):
                if not item['passage'] in passages :
                    passages.append(item['passage'])
                if not item['column'] in columns :
                    columns.append(item['column'])
            else :
                continue
        columns.sort()
        passages.sort()
        data['dataset']['vars']= columns
        data['dataset']['smps'] = passages
        render_data = []
        i = 0
        for column in columns : 
            render_data.append([])
            for passage in passages : 
                render_data[i].append(0.0)
            i = i + 1
        i=0
        for column in columns :
            j = 0
            for passage in passages :
                for item in result :
                    if item.has_key("column") and item.has_key("passage") :
                        if item['column'] == column and item['passage'] == passage :
                            render_data[i][j]=round(float(item['quantity'])/float(settings.PUMP_TRANS_TIME),3)
                    else :
                        continue 
                j = j + 1
            i=i+1
        data['dataset']['data'] = render_data
        return data
