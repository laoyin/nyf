#coding=utf-8
from sqlalchemy.sql import insert,select
from gcustomer import models
from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
import sys,pdb,json,datetime

#客户管理数据
customer_profile=[]
big_customer_profile=[]
customer_relation=[]

#初始化用户画像
customer_profile+=[
    dict(
        cardnum=9030230000007810,
        user_source=1,
        user_name='王大川',
        curr_balance=1200.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['93号汽油',],
        favourite_nonfuel_products=['啤酒',],
        recommended_nonfuel_products=['康师傅泡面','香烟'],
    ),
    dict(
        cardnum=9130230000090763,
        user_source=1,
        user_name='李望月',
        curr_balance=1754.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['93号汽油','97号汽油'],
        favourite_nonfuel_products=['雪花啤酒','香烟'],
        recommended_nonfuel_products=['雪花啤酒','香烟'],
    ),
    dict(
        cardnum=9030230000623356,
        user_source=1,
        user_name='陈诚',
        curr_balance=1154.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['93号 车用乙醇汽油',],
        favourite_nonfuel_products=['青岛啤酒','茉莉蜜茶'],
        recommended_nonfuel_products=['青岛啤酒','茉莉蜜茶'],
    ),
    dict(
        cardnum=9030230001726102,
        user_source=1,
        user_name='张中华',
        curr_balance=954.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['90号 车用乙醇汽油',],
        favourite_nonfuel_products=['雪花啤酒','中南海香烟'],
        recommended_nonfuel_products=['雪花啤酒','中南海香烟'],
    ),
    dict(
        cardnum=9030230001731507,
        user_source=1,
        user_name='洪队',
        curr_balance=2754.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['95号油',],
        favourite_nonfuel_products=['白沙(绿盒)','黄金叶香烟'],
        recommended_nonfuel_products=['白沙(绿盒)','黄金叶香烟'],
    ),
    dict(
        cardnum=9030230000583089,
        user_source=1,
        user_name='王刚',
        curr_balance=1230.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['93号汽油',],
        favourite_nonfuel_products=['啤酒',],
        recommended_nonfuel_products=['康师傅泡面','香烟'],
    ),
    dict(
        cardnum=9130230000130769,
        user_source=1,
        user_name='夏明',
        curr_balance=1754.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['93号汽油','97号汽油'],
        favourite_nonfuel_products=['雪花啤酒','香烟'],
        recommended_nonfuel_products=['雪花啤酒','香烟'],
    ),
    dict(
        cardnum=9130230000003889,
        user_source=1,
        user_name='吴春雨',
        curr_balance=1154.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['93号 车用乙醇汽油',],
        favourite_nonfuel_products=['青岛啤酒','茉莉蜜茶'],
        recommended_nonfuel_products=['青岛啤酒','茉莉蜜茶'],
    ),
    dict(
        cardnum=9030230000167369,
        user_source=1,
        user_name='刘艳青',
        curr_balance=9154.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['90号 车用乙醇汽油',],
        favourite_nonfuel_products=['雪花啤酒','中南海香烟'],
        recommended_nonfuel_products=['雪花啤酒','中南海香烟'],
    ),
    dict(
        cardnum=9030230000293051,
        user_source=1,
        user_name='蔡林',
        curr_balance=2654.00,
        prefer_time=1,
        prefer_pump_type=1,
        fuel_products=['95号油',],
        favourite_nonfuel_products=['白沙(绿盒)','黄金叶香烟'],
        recommended_nonfuel_products=['白沙(绿盒)','黄金叶香烟'],
    ),
]

#初始化大客户数据
big_customer_profile+=[
    dict(
         user_source=1,
         source_id=10000,
         master_cardnum=4367420011310479058,
         name='福州汽车公司',
         prepaid_amount=360000,
         current_balance=151320,
         nb_slave_cards=15,
         contribution=1000000,
         score=150
    ),
    dict(
         user_source=1,
         source_id=10000,
         master_cardnum=4392260001410420,
         name='福州客运公司',
         prepaid_amount=460000,
         current_balance=251320,
         nb_slave_cards=25,
         contribution=1005000,
         score=250
    ),
    dict(
         user_source=1,
         source_id=10000,
         master_cardnum=4270205902834225,
         name='福州市公交第一公司',
         prepaid_amount=360000,
         current_balance=151320,
         nb_slave_cards=15,
         contribution=120.0,
         score=150
    ),
    dict(
         user_source=1,
         source_id=10000,
         master_cardnum=4637580000573018,
         name='福州市市政府',
         prepaid_amount=460000,
         current_balance=251320,
         nb_slave_cards=25,
         contribution=98.0,
         score=250
    ),
    dict(
         user_source=1,
         source_id=10000,
         master_cardnum=4062522839289782,
         name='福州市长途运输公司',
         prepaid_amount=460000,
         current_balance=251320,
         nb_slave_cards=25,
         contribution=65.0,
         score=250
    ),
]
#初始化主卡与副卡数据
customer_relation+=[
    #主卡为4367420011310479058
    dict(
         user_source=1,
         master_cardnum=4367420011310479058,
         slave_cardnum=9030230000007810,
    ),
    dict(
         user_source=1,
         master_cardnum=4367420011310479058,
         slave_cardnum=9130230000090763,
    ),
    dict(
         user_source=1,
         master_cardnum=4367420011310479058,
         slave_cardnum=9030230000623356,
    ),
    dict(
         user_source=1,
         master_cardnum=4367420011310479058,
         slave_cardnum=9030230001726102,
    ),
    dict(
         user_source=1,
         master_cardnum=4367420011310479058,
         slave_cardnum=9030230001731507,
    ),
    #主卡为4392260001410420
    dict(
         user_source=1,
         master_cardnum=4392260001410420,
         slave_cardnum=9030230000583089,
    ),
    dict(
         user_source=1,
         master_cardnum=4392260001410420,
         slave_cardnum=9130230000130769,
    ),
    dict(
         user_source=1,
         master_cardnum=4392260001410420,
         slave_cardnum=9130230000003889,
    ),
    dict(
         user_source=1,
         master_cardnum=4392260001410420,
         slave_cardnum=9030230000167369,
    ),
    dict(
         user_source=1,
         master_cardnum=4392260001410420,
         slave_cardnum=9030230000293051,
    ),
]

#营销活动数据
promotion=[]
promotion_response=[]

promotion+=[
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,8),
        name='百岁山天然矿泉水570ml*24',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=1,
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
        sha1 = '03f361b38d55b975e10c486ae7cb9aaf91053e5c',
        discount_information = '9折',
    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,10),
        name='脉动芒果口味600ml/瓶',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=1,
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
        sha1 = '1f96543b6510811230e3d8cb5b86b83a7c495b4c',
        discount_information = '300积分兑换,限量50瓶',

    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,19),
        name='长城红酒优惠',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=1,
        discount_information='加油98折 限时段',
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,2,25),
        end_time=datetime.date(2015,4,25),
        name='晚十一点到五点优惠',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=1,
        discount_information='加油98折 限时段',
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,19),
        name='加400元送20积分',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=1,
        discount_information='加油98折 限时段',
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,19),
        name='充值3万元95折优惠',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=1,
        discount_information='加油98折 限时段',
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,19),
        name='福州柴油4月99折',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=1,
        discount_information='加油98折 限时段',
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,19),
        name='长乐93# 3月28日95折',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=1,
        discount_information='加油98折 限时段',
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,19),
        name='红河香烟积分兑换',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=0,
        discount_information='加油98折 限时段',
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
    ),
    dict(
        user_source=1,
        source_id=10000,
        start_time=datetime.date(2015,3,19),
        end_time=datetime.date(2015,4,19),
        name='厦门定额400元送10积分',
        area='消费金额100000元以上的客户',
        area_type=1,
        trigger_type=0,
        target_audience='厦门重型卡车群',
        contact_approach=0,
        discount_type=0,
        status=0,
        discount_information='加油98折 限时段',
        description='2月25日至4月25日，对晚上十一点到第二天早上五点间加油活动实现98折优惠',
        subject='定额加油500元送矿泉水一瓶',
        sender='中森美福州市公司',
        template_style=0,
    ),
]
promotion_response+=[
    dict(
        promotion_id=9,
        nb_participates=280,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=10,
        total_fuel_purchase=28,
        total_fuel_amount=100,
        total_nonfuel_purcahse=5,
        total_service_purcahse=2,
    ),
    dict(
        promotion_id=10,
        nb_participates=240,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=15,
        total_fuel_purchase=36,
        total_fuel_amount=120,
        total_nonfuel_purcahse=4,
        total_service_purcahse=1,
    ),
    dict(
        promotion_id=7,
        nb_participates=280,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=10,
        total_fuel_purchase=28,
        total_fuel_amount=100,
        total_nonfuel_purcahse=5,
        total_service_purcahse=2,
    ),
    dict(
        promotion_id=8,
        nb_participates=240,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=15,
        total_fuel_purchase=36,
        total_fuel_amount=120,
        total_nonfuel_purcahse=4,
        total_service_purcahse=1,
    ),
    dict(
        promotion_id=1,
        nb_participates=102,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=10,
        total_fuel_purchase=28,
        total_fuel_amount=100,
        total_nonfuel_purcahse=5,
        total_service_purcahse=2,
    ),
    dict(
        promotion_id=2,
        nb_participates=802,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=15,
        total_fuel_purchase=36,
        total_fuel_amount=120,
        total_nonfuel_purcahse=4,
        total_service_purcahse=1,
    ),
    dict(
        promotion_id=3,
        nb_participates=1102,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=10,
        total_fuel_purchase=28,
        total_fuel_amount=100,
        total_nonfuel_purcahse=5,
        total_service_purcahse=2,
    ),
    dict(
        promotion_id=4,
        nb_participates=12,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=15,
        total_fuel_purchase=36,
        total_fuel_amount=120,
        total_nonfuel_purcahse=4,
        total_service_purcahse=1,
    ),
    dict(
        promotion_id=5,
        nb_participates=12,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=10,
        total_fuel_purchase=28,
        total_fuel_amount=100,
        total_nonfuel_purcahse=5,
        total_service_purcahse=2,
    ),
    dict(
        promotion_id=6,
        nb_participates=12,
        user_participates=['9030230000007810','9130230000090763',],
        nb_notified=300,
        cost=15,
        total_fuel_purchase=36,
        total_fuel_amount=120,
        total_nonfuel_purcahse=4,
        total_service_purcahse=1,
    ),
]

#油站画像数据
siteprofile=[]

siteprofile+=[
    dict(
        user_source=1,
        site='福州油站',
        start_time=datetime.date(2015,1,1),
        end_time=datetime.date(2015,12,30),
        nb_total_customers=100000,
        total_fuel_amount= 1000,
        total_sales_amount=3125,
        fuel_sales=2313,
        total_nonfuel_sales_amount=812,
        top_100_customers=['4637580000573018','4270205902834225','4062522839289782'],
        rank=9,
        top_100_goods=[('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods=[('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist=   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],

    ),
    dict(
        user_source=1,
        site='上海油站',
        start_time=datetime.date(2015,1,1),
        end_time=datetime.date(2015,12,30),
        nb_total_customers=100000,
        total_fuel_amount= 1000,
        total_sales_amount=3125,
        fuel_sales=2313,
        total_nonfuel_sales_amount=812,
        top_100_customers=['4270205902834225','4637580000573018','4062522839289782'],
        rank=9,
        top_100_goods=[('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods=[('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist=   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],

    ),
    dict(
        user_source=1,
        site='广东油站',
        start_time=datetime.date(2015,1,1),
        end_time=datetime.date(2015,12,30),
        nb_total_customers=100000,
        total_fuel_amount= 1000,
        total_sales_amount=3125,
        fuel_sales=2313,
        total_nonfuel_sales_amount=812,
        top_100_customers=['4637580000573018','4062522839289782','4270205902834225'],
        rank=9,
        top_100_goods=[('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods=[('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist=   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],

    ),
    dict(
        user_source = 1,
        site = '中石化森美(顺昌城区)',
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 3,
        comment_score = 3 ,
        geo_x = 123.396 ,
        fuel_type = 3 ,
        geo_y = 41.88 ,
        address = "顺昌城区中石化森美(具体地址)", 
        site_tel = "13465876878",
        img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "中石化森美(鼓楼区)",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "顺昌城区中石化森美(具体地址)", 
        site_tel = "13465876878" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "卡子门加油站",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "雨花镇丁墙村", 
        site_tel = "025-52412647" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "中石化加油站(油坊桥加油站)",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "凤台南路198号附近", 
        site_tel = "025-86802364" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "清凉山加油站",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "鼓楼区虎踞路84-1号附近", 
        site_tel = "025-83701717" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "中山南路加油站",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "中山南路160号", 
        site_tel = "025-84469172" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "中石油加油站(龙蟠中路店)",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "玄武区龙蟠中路101号山水大酒店对面(山水大酒店西)", 
        site_tel = "025-84518516" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "加油站(龙蟠中路)",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "龙蟠中路321号", 
        site_tel = "025-84518506" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "加油站(灵山北路店)",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "灵山北路", 
        site_tel = "025-84503526" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "中国石化加油站(湖西街站)",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "建邺区所街和湖西街的交叉路口处", 
        site_tel = "025-84503527" ,
         img_sha1 = ''
        ),
    dict(
        user_source = 1,
        site = "中国海油加油站(协和石油加油站天元西路)",
        start_time = datetime.date(2015,1,1),
        end_time = datetime.date(2015,12,30),
        nb_total_customers = 100000,
        total_fuel_amount = 1000,
        total_sales_amount = 3125,
        fuel_sales = 2313,
        total_nonfuel_sales_amount=812,
        top_100_customers = ['4637580000573018','4062522839289782','4270205902834225'],
        rank = 9,
        top_100_goods = [('青岛啤酒',325.0),('苏烟',186),('燃油宝',85)],
        bottom_100_goods = [('达利园蛋黄面包',8.6),('康师傅方便面',9.2),('娃哈哈AD钙奶',12.3)],
        percent_dist =   [(0.1,0.2),(0.2,0.4),(0.3,0.5)],
        assist_type = 2,
        comment_score = 4 ,
        fuel_type = 3,
        geo_x = 123.396 ,
        geo_y = 41.88 ,
        address = "江宁区天元西路111号", 
        site_tel = "025-84503528" ,
         img_sha1 = ''
        ),
]

#广告接入数据
advertisement=[]
advertisement_effect=[]



#活动参与情况数据
#广告效果数据

class Command(BaseCommand):
    help="Initialize gcustomer data"

    def handle(self, *args, **options):
        try:
            # 建立数据会话
            create_session = get_dash_session_maker()
            s = create_session()

            #客户管理数据
            # for row in big_customer_profile:
            #     obj=models.BigCustomerProfile(**row)
            #     s.add(obj)
            #     try:
            #         s.commit()
            #     except Exception,e:
            #         s.rollback()
            # for row in customer_relation:
            #     obj=models.CustomerRelation(**row)
            #     s.add(obj)
            #     try:
            #         s.commit()
            #     except Exception,e:
            #         s.rollback()
            # for row in customer_profile:
            #     row['favourite_nonfuel_products']=json.dumps(row['favourite_nonfuel_products'])
            #     row['fuel_products']=json.dumps(row['fuel_products'])
            #     row['recommended_nonfuel_products']=json.dumps(row['recommended_nonfuel_products'])
            #     obj=models.CustomerProfile(**row)
            #     s.add(obj)
            #     try:
            #         s.commit()
            #     except Exception,e:
            #         s.rollback()

            # #营销活动数据
            # for row in promotion:
            #     obj=models.Promotion(**row)
            #     s.add(obj)
            #     try:
            #         s.commit()
            #     except Exception,e:
            #         s.rollback()
            # for row in promotion_response:
            #     row['user_participates']=json.dumps(row['user_participates'])
            #     obj=models.PromotionEffect(**row)
            #     s.add(obj)
            #     try:
            #         s.commit()
            #     except Exception,e:
            #         s.rollback()

            #油站画像数据
            for row in siteprofile:
                row['top_100_customers']=json.dumps(row['top_100_customers'])
                row['top_100_goods']=json.dumps(row['top_100_goods'])
                row['bottom_100_goods']=json.dumps(row['bottom_100_goods'])
                row['percent_dist']=json.dumps(row['percent_dist'])
                obj=models.StationProfile(**row)
                s.add(obj)
                try:
                    s.commit()
                except Exception,e:
                    s.rollback()

            # #广告接入数据
            # for row in advertisement:
            #     obj=models.Advertisement(**row)
            #     s.add(obj)
            #     try:
            #         s.commit()
            #     except Exception,e:
            #         s.rollback()

        except Exception,e:print >> sys.stderr, "Exception: ", str(e)