# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.station import cubes
from gflux.apps.station.models import TransType, PaymentType, CardType, DayPeriod
from datetime import datetime
from optparse import make_option
import sys,pdb,re,json
from django.core.cache import cache
from django.conf import settings
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import all_type_args
from gflux.apps.station.sql_utils import get_nb_stations_of_location,\
get_fuel_type_name,get_nb_guns_of_station,\
get_all_sites_by_location_id

def gen_options():
    exists=[]
    options=set()
    options.add(make_option('--type',help="set compute type",type="string"))
    for type in all_type_args:
        for arg in all_type_args[type]:
            if arg not in exists:
                exists.append(arg)
                options.add(make_option('--%s'%arg,help="set args %s"%arg,type="string"))

    return BaseCommand.option_list + tuple(options)

class CusBaseCommand(type):
    def __new__(cls, name, bases, attrs):
        attrs['option_list']=gen_options()

        return super(CusBaseCommand, cls).__new__(cls, name, bases, attrs)

class Command(BaseCommand):
    __metaclass__ = CusBaseCommand

    def build_conditions(self):
        self.cube=cubes.TransCube()
        #取得查询条件
        conditions = []
        form = self.form#.cleaned_data
        try:
            #取得区域
            self.location = int(form['location'])

            #非所有区域
            if self.location:
                self.site_count = get_nb_stations_of_location(self.location)
                conditions.append(self.cube.d.location == self.location)
            #所有区域
            else:
                self.site_count = get_nb_stations_of_location(self.location)

        except:
            pass

        try:
            self.fuel_type = int(form['barcode'])

            #直接查询对应的油品，不再总结
            conditions.append(self.cube.d.barcode == self.fuel_type)

        except:
            pass
        return conditions

    def handle(self,  *args, **options):
        self.form=options

        #取得location的所有site列表
        self.sites=get_all_sites_by_location_id(int(self.form['location']))

        type=options['type']

        #check type
        if type not in all_type_args.keys():
            print 'ERROR:type not right'
            return

        #check args
        need_args=all_type_args[type]
        for need_arg in need_args:
            if options[need_arg] is None:
                print 'ERROR:'+type+' need arg '+need_arg
                return

        s_list=[]
        already_shard_ids=[]
        for site in self.sites:
            shard_id,sm=get_dash_session_maker(site,with_shard_id=True)
            if shard_id in already_shard_ids:
                continue
            already_shard_ids.append(shard_id)
            s_list.append(sm())

        if type=='pump_daily_avg_report':
            conditions = self.build_conditions()
            conditions.append(self.cube.d.trans_type == TransType.FUEL)

            results=[]
            for s in s_list:
                results += self.cube.aggregate(measures=['quantity'],
                                          drilldown=['barcode', 'month', 'day'],
                                          conditions=conditions,
                                          session=s)

            stats = {}
            categories = set()
            for result in results:
                barcode = result['barcode']
                stats.setdefault(barcode, {})
                cat = '%02d-%02d' % (result['month'], result['day'])
                categories.add(cat)
                stat = stats[barcode]
                stat[cat] = round(result['quantity'] / self.site_count, 2)

            categories = list(categories)
            categories.sort()
            data = {
                "categories": categories,
                "dataset": [],
            }
            for series, stat in stats.items():
                opt = {"data": [], "name": get_fuel_type_name(series), "type": "area", "stacking": "normal"}
                for cat in data['categories']:
                    opt["data"].append(stat.get(cat, 0))
                data["dataset"].append(opt)

            cache_key='%s_%s'%(type,'-'.join(all_type_args[type]))
            for arg in all_type_args[type]:
                cache_key+='_'+str(options[arg])

            cache_value=json.dumps(data)
            cache.set(cache_key,cache_value,settings.MEMCACHED_TIMEOUT)

        elif type=='gun_pump_avg_report':
            conditions = self.build_conditions()
            conditions.append(self.cube.d.trans_type == TransType.FUEL)
            #统计出油量，多少天数
            #group by 每个站，每小时
            results=[]
            for s in s_list:
                results += self.cube.aggregate(measures=['quantity','hours'],
                                          drilldown=['hour', 'site'],
                                          conditions=conditions,
                                          session=s)
            stats = {}
            counter_dic={}
            for result in results:
                hour = result['hour']
                site = result['site']
                cat = '%02d:00 - %02d:00' % (hour, hour + 1)
                stats.setdefault(cat, 0)
                counter_dic.setdefault(cat,0)
                #不同的站
                #加上枪效率，出油量是在多少枪，多少天完成的，需要平均下
                stats[cat]+=result['quantity'] / 40 / get_nb_guns_of_station(site) / result['hours']
                counter_dic[cat]+=1

            #平均到每个站
            for cat in stats:
                stats[cat] = round(stats[cat]/counter_dic[cat], 2)

            data = {
                "categories": ['%02d:00 - %02d:00' % (i, i + 1) for i in range(0, 24)],
                "dataset": [],
            }
            opt = {"data": [], "name": "油枪平均每小时工作时间", "type": "column"}
            for cat in data['categories']:
                opt["data"].append(stats.get(cat, 0))
            data["dataset"].append(opt)
            cache_key='%s_%s'%(type,'-'.join(all_type_args[type]))
            for arg in all_type_args[type]:
                cache_key+='_'+str(options[arg])

            cache_value=json.dumps(data)
            cache.set(cache_key,cache_value,settings.MEMCACHED_TIMEOUT)

        elif type=='non_fuel_sales_avg_report':
            conditions = self.build_conditions()
            conditions.append(self.cube.d.trans_type == TransType.NON_FUEL)
            conditions.append(self.cube.d.quantity > 0)

            results=[]
            for s in s_list:
                results += self.cube.aggregate(measures=['pay', 'hours'],
                                          drilldown=['hour'],
                                          conditions=conditions,
                                          session=s)
            stats = {}
            for result in results:
                hour = result['hour']
                cat = '%02d:00 - %02d:00' % (hour, hour + 1)
                stats[cat] = round(result['pay'] / (self.site_count * result['hours']), 2)

            data = {
                "categories": ['%02d:00 - %02d:00' % (i, i + 1) for i in range(0, 24)],
                "dataset": [],
            }
            opt = {"data": [], "name": "非油品平均每小时销售额", "type": "column"}
            for cat in data['categories']:
                opt["data"].append(stats.get(cat, 0))
            data["dataset"].append(opt)

            cache_key='%s_%s'%(type,'-'.join(all_type_args[type]))
            for arg in all_type_args[type]:
                cache_key+='_'+str(options[arg])

            cache_value=json.dumps(data)
            cache.set(cache_key,cache_value,settings.MEMCACHED_TIMEOUT)

        elif type=='non_fuel_sales_scale_report':
            conditions = self.build_conditions()
            conditions2 = conditions[:]
            conditions2.append(self.cube.d.trans_type == TransType.NON_FUEL)
            conditions2.append(self.cube.d.quantity > 0)

            results=[]
            for s in s_list:
                results += self.cube.aggregate(measures=['trans_count', 'hours'],
                                          drilldown=['hour'],
                                          conditions=conditions2,
                                          session=s)
            stats2 = {}
            for result in results:
                hour = result['hour']
                cat = '%02d:00 - %02d:00' % (hour, hour + 1)
                stats2[cat] = float(result['trans_count']) / result['hours']

            conditions.append(self.cube.d.trans_type == TransType.FUEL)

            results=[]
            for s in s_list:
                results += self.cube.aggregate(measures=['trans_count', 'hours'],
                                          drilldown=['hour'],
                                          conditions=conditions,
                                          session=s)
            stats = {}
            for result in results:
                hour = result['hour']
                cat = '%02d:00 - %02d:00' % (hour, hour + 1)
                stats[cat] = float(result['trans_count']) / result['hours']


            data = {
                "categories": ['%02d:00 - %02d:00' % (i, i + 1) for i in range(0, 24)],
                "dataset": [],
            }

            for cat in data['categories']:
                total = stats.get(cat, 0) + stats2.get(cat, 0)
                if total > 0:
                    stats[cat] = round(stats2.get(cat, 0) * 100 / total, 2)
                else:
                    stats[cat] = 0

            opt = {"data": [], "name": "非油品平均每小时交易比例", "type": "column"}
            for cat in data['categories']:
                opt["data"].append(stats.get(cat, 0))
            data["dataset"].append(opt)

            cache_key='%s_%s'%(type,'-'.join(all_type_args[type]))
            for arg in all_type_args[type]:
                cache_key+='_'+str(options[arg])

            cache_value=json.dumps(data)
            cache.set(cache_key,cache_value,settings.MEMCACHED_TIMEOUT)

        elif type=='top10_non_fuel_sales_avg_report':
            self.build_conditions()
            location = int(options['location'])

            conditions = [self.cube.d.quantity > 0,
                          self.cube.d.trans_type == TransType.NON_FUEL]
            if location > 0:
                conditions.append(self.cube.d.location == location)

            results=[]
            for s in s_list:
                results += self.cube.aggregate(measures=['pay'],
                                          drilldown=['barcode'],
                                          details=['desc'],
                                          conditions=conditions,
                                          order='pay desc',
                                          limit=10,
                                          session=s)
            barcodes = []
            for result in results:
                barcodes.append(result['barcode'])

            conditions = self.build_conditions()
            conditions.append(self.cube.d.trans_type == TransType.NON_FUEL)
            conditions.append(self.cube.d.barcode.in_(barcodes))
            conditions.append(self.cube.d.quantity > 0)

            results=[]
            for s in s_list:
                results += self.cube.aggregate(measures=['pay'],
                                          drilldown=['barcode', 'hour'],
                                          details=['desc'],
                                          conditions=conditions,
                                          session=s)
            stats = {}
            descs = {}
            for result in results:
                barcode = result['barcode']
                descs[barcode] = result['desc']
                stats.setdefault(barcode, {})
                stat = stats[barcode]
                hour = result['hour']
                cat = '%02d:00 - %02d:00' % (hour, hour + 1)
                stat[cat] = round(result['pay'] / (373 * 24 * self.site_count), 2)

            data = {
                "categories": ['%02d:00 - %02d:00' % (i, i + 1) for i in range(0, 24)],
                "dataset": [],
            }
            for series, stat in stats.items():
                opt = {"data": [], "name": descs[series], "type": "line"}
                for cat in data['categories']:
                    opt["data"].append(stat.get(cat, 0))
                data["dataset"].append(opt)

            cache_key='%s_%s'%(type,'-'.join(all_type_args[type]))
            for arg in all_type_args[type]:
                cache_key+='_'+str(options[arg])

            cache_value=json.dumps(data)
            cache.set(cache_key,cache_value,settings.MEMCACHED_TIMEOUT)


        elif type=='pump_hourly_avg_report':
            conditions = self.build_conditions()
            conditions.append(self.cube.d.trans_type == TransType.FUEL)

            results=[]
            for s in s_list:
                results += self.cube.aggregate(measures=['quantity','hours'],
                                          drilldown=['barcode', 'hour'],
                                          conditions=conditions,
                                          session=s)
            stats = {}
            categories = set()
            for result in results:
                barcode = result['barcode']
                stats.setdefault(barcode, {})
                hour = result['hour']
                cat = '%02d:00 - %02d:00' % (hour, hour + 1)
                categories.add(cat)
                stat = stats[barcode]
                stat[cat] = round(result['quantity'] / (result['hours'] * self.site_count), 2)

            data = {
                "categories": ['%02d:00 - %02d:00' % (i, i + 1) for i in range(0, 24)],
                "dataset": [],
            }
            for series, stat in stats.items():
                opt = {"data": [], "name": get_fuel_type_name(series), "type": "area", "stacking": "normal"}
                for cat in data['categories']:
                    opt["data"].append(stat.get(cat, 0))
                data["dataset"].append(opt)

            cache_key='%s_%s'%(type,'-'.join(all_type_args[type]))
            for arg in all_type_args[type]:
                cache_key+='_'+str(options[arg])

            cache_value=json.dumps(data)
            cache.set(cache_key,cache_value,settings.MEMCACHED_TIMEOUT)

        elif type=="pump_monthly_avg_report":
            conditions = self.build_conditions()
            conditions.append(self.cube.d.trans_type == TransType.FUEL)

            results=[]
            for s in s_list:
                s=get_dash_session_maker(site)()
                results += self.cube.aggregate(measures=['quantity'],
                                          drilldown=['barcode', 'month'],
                                          conditions=conditions,
                                          session=s)

            stats = {}
            for result in results:
                barcode = result['barcode']
                stats.setdefault(barcode, {})
                stat = stats[barcode]
                stat[result['month']] = round(result['quantity'] / self.site_count, 2)

            data = {
                "categories": [i for i in range(1, 13)],
                "dataset": [],
            }
            for series, stat in stats.items():
                opt = {"data": [], "name": get_fuel_type_name(series), "type": "area", "stacking": "normal"}
                for cat in data['categories']:
                    opt["data"].append(stat.get(cat, 0))
                data["dataset"].append(opt)

            cache_key='%s_%s'%(type,'-'.join(all_type_args[type]))
            for arg in all_type_args[type]:
                cache_key+='_'+str(options[arg])

            cache_value=json.dumps(data)
            cache.set(cache_key,cache_value,settings.MEMCACHED_TIMEOUT)

        elif type=='trans_count_avg_report':
            conditions = self.build_conditions()
            conditions.append(self.cube.d.trans_type == TransType.FUEL)

            results=[]
            for s in s_list:
                s=get_dash_session_maker(site)()
                results += self.cube.aggregate(measures=['trans_count','hours'],
                                          drilldown=['hour'],
                                          conditions=conditions,
                                          session=s)

            stats = {}
            for result in results:
                hour = result['hour']
                cat = '%02d:00 - %02d:00' % (hour, hour + 1)
                stats[cat] = int(result['trans_count'] / (self.site_count * result['hours']))

            data = {
                "categories": ['%02d:00 - %02d:00' % (i, i + 1) for i in range(0, 24)],
                "dataset": [],
            }
            opt = {"data": [], "name": "进站车辆", "type": "column"}
            for cat in data['categories']:
                opt["data"].append(stats.get(cat, 0))
            data["dataset"].append(opt)

            cache_key='%s_%s'%(type,'-'.join(all_type_args[type]))
            for arg in all_type_args[type]:
                cache_key+='_'+str(options[arg])

            cache_value=json.dumps(data)
            cache.set(cache_key,cache_value,settings.MEMCACHED_TIMEOUT)

        #close session
        for s in s_list:
            s.close()
