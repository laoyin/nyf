#coding=utf-8
from django.core.management.base import BaseCommand
from django.conf import settings
from gcustomer.models import *
from gcustomer.apps.jiachebao import *
from dash.core.backends.sql.models import *
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm import sessionmaker
from datetime import *
import sys, pdb

class Command(BaseCommand):
    help = 'Init  server data env'

    def handle(self, *args, **options):
    	old_session = get_app_session_maker()()
    	session = get_dash_session_maker()()
    	#初始化商品优惠
    	init_store_good_data(old_session,session)
    	#初始化油站数据
    	#init_station_data(old_session,session)

#初始化便利店商品
def init_store_good_data(old_session,session):
	print "开始初始化便利店商品数据!"
	count = 0
	sql = 'select * from gcustomer_store_goods'
	store_item_list = old_session.execute(sql)
	for store_item in store_item_list :
		pos_id = store_item.pos_id
		name = store_item.name
		price = store_item.price
		count = store_item.count
		score = store_item.score
		exchange_score = store_item.exchange_score
		member_option = store_item.member_option
		discount = store_item.discount
		discount_info = store_item.discount_info
		discount_end_time = store_item.discount_end_time
		img_sha1 = store_item.img_sha1
		seller_sha1 = store_item.seller_sha1
		information = store_item.information
		comp_id = 10
		import hashlib
		sha1 = hashlib.sha1()
		sha1.update(str(pos_id)+str(comp_id))
		sha1 = sha1.hexdigest()
		item = StoreItem(
				comp_id = 2,
				sha1 = sha1,
				source_id = 1,
				pos_id = pos_id,
				name = name ,
				price = price,
				count = count,
				score = score,
				exchange_score = exchange_score,
				member_option = member_option,
				discount = discount,
				discount_info = discount_info,
				discount_end_time = discount_end_time,
				img_sha1 = img_sha1,
				seller_sha1 = seller_sha1,
				information = information
			)
		score_item = ItemScoreRule(
				comp_id = 2,
			)
		session.add(item)
		session.add(score_item)
		count = count + 1
	try:
		session.commit()
	except Exception,e:
		session.rollback()
		print e
		count  = 0
	print "便利店商品数据初始化完毕..."
	print "共导入数据"+ str(count) + "条."

#初始化油站信息
def init_station_data(old_session,session):
	print "开始初始化油站数据"
	sql = 'select * from gcustomer_site_profile'
	old_station_list = old_session.execute(sql)
	count = 0
	for old_station in old_station_list :
		site = old_station.site
		site_code = old_station.site_code
		start_time = old_station.start_time
		end_time = old_station.end_time
		nb_total_customers = old_station.nb_total_customers
		total_fuel_amount = old_station.total_fuel_amount
		total_sales_amount = old_station.total_sales_amount
		total_nonfuel_sales_amount = old_station.total_nonfuel_sales_amount
		fuel_sales = old_station.fuel_sales
		peak_range = old_station.peak_range
		top_100_customers = old_station.top_100_customers
		rank = old_station.rank
		top_100_goods = old_station.top_100_goods
		bottom_100_goods = old_station.bottom_100_goods
		percent_dist = old_station.percent_dist
		geo_x = old_station.geo_x
		geo_y = old_station.geo_y
		comment_score = old_station.comment_score
		comment_count = old_station.comment_count
		fuel_type = old_station.fuel_type
		assist_type = old_station.assist_type
		site_sha1 = old_station.site_sha1
		img_sha1 = old_station.img_sha1
		site_tel = old_station.site_tel
		address = old_station.address

		station = Station(
				comp_id = 10,
				name = site,
				geo_x = geo_x,
				geo_y = geo_y,
				comment_score = comment_score,
				comment_count = comment_count,
				fuel_type = fuel_type,
				assist_type = assist_type,
				sha1 = site_sha1,
				img_sha1 = img_sha1,
				site_tel = site_tel,
				address = address
			)
		try :
			session.add(station)
			session.commit()
		except Exception,e:
			print "初始化油站数据失败"
			count = 0
			print "初始化" + str(count) + "条油站数据"
			return 
		station = session.query(Station).filter_by(comp_id = 10,sha1 = site_sha1).one()
		station_profile = StationProfile(
				station_id = station.id,
				start_time = start_time,
				end_time = end_time,
				nb_total_customers = nb_total_customers,
				total_fuel_amount = total_fuel_amount,
				total_sales_amount = total_sales_amount,
				total_nonfuel_sales_amount = total_nonfuel_sales_amount,
				fuel_sales = fuel_sales,
				peak_range = peak_range,
				top_100_customers = top_100_customers,
				rank = rank ,
				top_100_goods = top_100_goods ,
				bottom_100_goods = bottom_100_goods ,
				percent_dist = percent_dist 
			)
		session.add(station_profile)
		try : 
			session.commit()
			count = count + 1
		except Exception,e:
			session.rollback()
			session.delete(station)
			session.commit()
			print "初始化油站画像失败"
			break	
	print "初始化" + str(count) + "条油站数据"

	
		
