# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.station.reports import get_fuel_type_name,get_nb_guns_of_station,\
    get_nb_stations_of_location,get_location_id,get_user_stations_by_id,get_station_id,\
    update_station_info
from datetime import datetime
from optparse import make_option
import sys,pdb,re

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--code',help="set barcode like 300585",type="string"),
    )

    def handle(self,  *args, **options):

	# 添加一个油站并获取其编号
	get_station_id("JZTF", 0)
	get_station_id("JZTF", 0)

	# 更新油站的信息
	update_station_info("JZTF", "demo station", 7, 5, None,
	                    "No.9 Jingzhou", None, 100)

	# 获取一个用户的所有油站信息
	get_user_stations_by_id(0)

	# 获取站点油枪数
        nb_guns=get_nb_guns_of_station('BJ-DJ')

	# 获取一个地点的油站数
        nb_sites=get_nb_stations_of_location(6)

	# 获取一个已添加地点的ID
        loc_id=get_location_id(u'SC-CN',"四川")

	# 获取一个新地点的ID
        loc_id=get_location_id(u'HB-CN',"湖北")

	# 获取一种汽油类型编号对应的名称
	get_fuel_type_name(options['code'])
