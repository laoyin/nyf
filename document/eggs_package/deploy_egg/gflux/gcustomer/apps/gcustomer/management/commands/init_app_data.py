#coding=utf-8
from sqlalchemy.sql import insert,select
from gcustomer import models
from gcustomer.app_models import * 
from django.core.management.base import BaseCommand
import sys,pdb,json,datetime

#goods
goods = [
	 {
                        "goods_name": "百岁山天然矿泉水570ml*24",
                        "price": 50,
                        "score": 3,
                        "exchange_score" : 50,
                        "discount": 0.9,
                        "discount_info": "9折",
                        "discount_end_time": "2015-04-08",
                        "available_source": "中森美兴工街加油站便利店",
                        "history": 2,
                        "pick": 0,
                        "img": ""
                    },
                    {
                        "goods_name": "脉动芒果口味600ml/瓶",
                        "price": 3.7,
                        "score": 4,
                        "exchange_score" : 50,
                        "discount": "300积分兑换,限量50瓶",
                        "discount_end_time": "2015-04-10",
                        "available_source": "京东商城",
                        "history": 8,
                        "pick": 1,
                        "img": ""
                      }
]

#services
services = [
	    {

    			"item_type": 0,
    			"dictance":"东北方300米",
    			"title":"洗车人家",
    			"item_img": "0032f190ee0a8b54983bc707d5c57a0a9d009596.jpg",
    			"score":"3",
    			"comment_count":"173",
    			"discount_info": "折扣信息"
                    },

                    {
    			"item_type": 1,
    			"dictance":"向南870mi",
    			"discount_info": "",
    			"title":"丽车房汽车美容装饰(旗舰店)",
    			"item_img": "0032f190ee0a8b54983bc707d5c57a0a9d009596.jpg",
    			"score":"0",
    			"comment_count":"0"
                    }
]
sale_item_usage = [
      {
            "item_sha1": "9f8df847542d36947b1be0b2c411760385020af8",
            "user_sha1": "d86fac45316224179f577439ff3e6905d72fe2ab",
            "nb_purchases":"1",
            "purchased_amount": "100"
      },
      {
            "item_sha1": "f4fbb12da9ddc147011d34d27448c627bdd52590",
            "user_sha1": "d86fac45316224179f577439ff3e6905d72fe2ab",
            "nb_purchases":"1",
            "purchased_amount": "100"
      },
      {
            "item_sha1":"2bb94ac4c625c6fd5191b743b363b6ea3432c322",
            "user_sha1": "d86fac45316224179f577439ff3e6905d72fe2ab",
            "nb_purchases":"1",
            "purchased_amount": "100"
      },
      {
            "item_sha1":"a47a37b3999b206c854a9842e7875756dbad2671",
            "user_sha1": "d86fac45316224179f577439ff3e6905d72fe2ab",
            "nb_purchases":"1",
            "purchased_amount": "100"
      },
]

sellers = [
        {
            "name":"中森美兴工街加油站便利店",
            "address":"南京龙盘路45号",
            "geo_x" : 123.2,
            "geo_y" : 41.1,
            "phone" : "13853224567",
            "image" :""

        },
        {
            "name":"京东商城",
            "address":"南京光华路55号",
            "geo_x" : 123.3,
            "geo_y" : 41.5,
            "phone" : "13843125567",
            "image" :"1.jpg"

        },
        {
            "name":"丽车房汽车美容装饰(旗舰店)",
            "address":"南京中山路45号",
            "geo_x" : 123.21,
            "geo_y" : 41.15,
            "phone" : "13853234567",
            "image" :""

        },
        {
            "name":"洗车人家",
            "address":"南京夫子庙45号",
            "geo_x" : 123.24,
            "geo_y" : 41.15,
            "phone" : "13853214567",
            "image" :""

        }
]

class Command(BaseCommand):
    help="Initialize app data"

    def handle(self, *args, **options):
        
        # init_data()
        for seller in sellers :
            obj = WheelSeller(
                    name = seller["name"],
                    address = seller["address"],
                    geo_x = seller['geo_x'],
                    geo_y = seller['geo_y'],
                    phone = seller['phone']
                )
            try:
                obj.save()
            except Exception ,e:
                print e 

    def init_data(self):

        for  good in goods :
            import hashlib
            sha1=hashlib.sha1()
            sha1.update(str(good['goods_name']))
            sha1.update(str(datetime.datetime.now()))
            img_sha1=sha1.hexdigest()
            obj = WheelSaleItem(
                name = good['goods_name'],
                price = good['price'],
                score =  good['score'],
                exchange_score = good['exchange_score'],
                discount = good['discount'],
                discount_info = good['discount_info'],
                discount_end_time = good['discount_end_time'],
                available_source = good['available_source'],
                img_sha1 = img_sha1
            )
            try :
                obj.save()
            except Exception , e :
                print e 

        objects = WheelSaleItem.objects.all()
        for good in objects :
            if good.sha1 :
                obj = StoreItemUsage(
                     item_sha1 = good.sha1,
                     item_type = 0,
                     user_sha1 = ''
                  )
                try:
                  obj.save()
                except Exception,e :
                  print e 

        # WheelTransaction
        objects = WheelSaleItem.objects.all()
        for good in objects :
            if good.sha1 :
                obj = WheelTransaction(
                     user_sha1 = "d86fac45316224179f577439ff3e6905d72fe2ab",
                     item_sha1 = good.sha1,
                     item_type = 0,
                     item_total = good.price,
                     time = datetime.date(2015,9,1)
                     )
                try :
                    obj.save()
                except Exception,e :
                    print e 

        for service in services :
            obj = WheelSaleService(
                seller_name = "" ,
                service_name = service['title'],
                average_score = service['score'],
                # discount_score = service['discount_info'],
                discount_end_time = datetime.date(2015,9,1),
                nb_comments  = service['comment_count'],
                geo_x = 123,
                geo_y = 41
                )
            try :
                obj.save()
            except Exception,e :
                print e 

        objects = WheelSaleService.objects.all()
        for service in objects :
            if service.sha1 :
               obj = StoreItemUsage(
                     item_sha1 = service.sha1,
                     item_type = 1,
                     user_sha1 = ''
                  )
               try:
                  obj.save()
               except Exception,e :
                  print e 

        # WheelTransaction
        objects = WheelSaleService.objects.all()
        for service in objects :
            if service.sha1 :
                obj = WheelTransaction(
                     user_sha1 = "d86fac45316224179f577439ff3e6905d72fe2ab",
                     item_sha1 = service.sha1,
                     item_type = 1,
                     item_total = service.price,
                     time = datetime.date(2015,9,1)
                     )
                try :
                    obj.save()
                except Exception,e :
                    print e  

        #alter wheelsaleitemusage
        for item in sale_item_usage :
            obj = StoreItemUsage.objects.filter(item_sha1=item['item_sha1']).first()
            # obj.user_sha1 = item["user_sha1"]
            obj.nb_purchases = item["nb_purchases"]
            obj.purchased_amount = item["purchased_amount"]
            try:
                obj.save()
            except Exception,e:
                print e 

    