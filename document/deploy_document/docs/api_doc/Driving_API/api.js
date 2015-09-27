var api_data = [

    //获取版本号
    {
        "name": "获取版本号(app启动时需要第一个发送该请求)",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
	    	"action": "get_service_version",
		"data":{
		    "app_name":"jiachebao"
		}
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data": {
		"version":1.1
	    },
         },
        "note": {
            "请求参数":"-------------",
	    "app_name":"app的名字，这个值固定",
            "返回参数":"-------------",
            "version": "服务器的版本号",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识"
        }
    },

    //获取附近油站
    {
        "name": "获取附近油站",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
            "action": "get_near_by_station_sha1s",
            "data": {
                "cardnum":"9030270000434268",
                    "longitude": 123.384,
    	        "latitude": 41.8,
    	        "start": 0,
    	        "end": 2
            }
        },

        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "has_next": "true",
                "sha1s":[
                "0fd21fdc35a001d3708f43765021f24e28078b34",
                "2112978c7ada9865f798631731e9ab7fae302433"
            ]
        }

        },
        "note": {
            "请求参数":"-------------",
            "cardnum":"用户卡号",
            "longitude": "经度（float）",
            "latitude": "纬度（float）",
            "start": "请求的开始标识",
            "end": "请求结束的标示符",
            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             "has_next": "是否还有更多油站",
	       "sha1s": "油站的sha1列表"
        }
    },

    // 获取油站的详情
    {
        "name": "获取油站详情",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
            "action": "get_near_by_station",
	    "data": {
            "cardnum":"91302700000235804",
            "longitude": 123.428,
                "latitude": 41.9,
		"sha1s":[
                "0fd21fdc35a001d3708f43765021f24e28078b34",
                                            "1d015577a0849b9e155423f1aa69baffaf804881",
                                            "65f0ed8400d12120cda4961a75ff516333af8d78",
                                            "565680f7bb3d0a8dd8d716d1a9c1d4d753e3f9a4",
                                            "2112978c7ada9865f798631731e9ab7fae302433"]
         }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
	    "data": {
            "detail_list":[
        		{
        		    "site_name": "中石化森美(顺昌城区)",
        		    "site_sha1": "b42d0ea5b1c9f0e21376d065ebdba3aba041c1d9",
                                "src" : "",
                    	    "img_sha1": "",
        		    "assist_type": 3,
        		    "comment_score": 3,
			    "count":203,
        	 	    "fuel_type": [
             			    {
        				"name": "97#",
        			        "info": ""
        			    },
        			    {
        				"name": "93#",
        			        "info": "9折优惠"
        		            }
        		    ],
        		    "is_busy": 1,
			    "all_fuel_type":[{"barcode":"600356","fuel_name":"93#汽油","price":6.5},{"barcode":"600357","fuel_name":"97#汽油","price":7.5}],
                               "busy_info": "繁忙信息(时段)",
        		    "longitude": 123.39,
        	    	"latitude": 41.87,
        		    "address": "顺昌城区中石化森美(具体地址)",
        		    "phone": "13465876878",
                    "promotions": [ {
                        "name":"绑定加油卡，优惠多多",
                        "discount_information":"绑定卡赠送50元信息",
                        "start_time":"2015-04-01",
                        "end_time":"2015-05011",
                        "activity_img":""
                        },]
        	        },

        		{
        		    "site_name": "中石化森美(鼓楼区)",
        		    "site_sha1": "5289fea8f59896f6eb4022a94e1f870d074deb9f",
                    	       "src" : "",
                            "img_sha1": "",
        		    "assist_type": 2,
        		    "comment_score": 4,
			    "count":203,
        	 	    "fuel_type": [
             			    {
        				"name": "97#",
        			        "info": "95折优惠"
        			    },
        			    {
        				"name": "93#",
        			        "info": ""
        		            }
        		    ],
        		    "is_busy": 0,
			    "all_fuel_type":[{"barcode":"600356","fuel_name":"93#汽油"},{"barcode":"600357","fuel_name":"97#汽油"}],
                    "busy_info": "",
        		    "distance": "前方847米",
        		    "longitude": 123.396,
        	            "latitude": 41.88,
        		    "address": "顺昌城区中石化森美(具体地址)",
        		    "phone": "13465876878",
                    "promotions": [{
                        "name":"绑定加油卡，优惠多多",
                        "discount_information":"绑定卡赠送50元信息",
                        "start_time":"2015-04-01",
                        "end_time":"2015-05011",
                        "activity_img":""
                        } ],

        		},
            ],
	    },
        },
        "note": {

            "请求参数":"-------------",
            "sha1s":"油站的sha1",
            "cardnum":"用户卡号",
            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
    	    "detail_list": "所有油站的详细信息",
    	    "site_name": "油站的名字",
    	    "site_sha1": "油站的sha1",
            "src":"油站logo路径",
            "img_sha1": "油站logo",
    	    "assist_type": "是否有自助和刷卡,1:刷卡,2:自助,3:两者都有",
    	    "comment_score": "油站的综合评分,范围是0--5",
    	    "fuel_type": "所有的油品类型",
    	    "name": "油品的名称",
    	    "info": "油品的优惠信息.如果没有优惠则为空",
    	    "is_busy": "当前油站是否繁忙,0:顺畅,1:繁忙",
            "busy_info": "繁忙时段信息",
    	    "distance": "我距离该油站的距离",
    	    "longitude": "油站的经度",
    	    "latitude": "油站的纬度",

    	    "address": "油站详细地址",
    	    "phone": "油站电话",

            "promotion":"优惠活动",
             "name":"优惠活动名称",
            "discount_information":"打折信息",
            "start_time":"活动的开始时间",
            "end_time":"活动的结束时间",
            "activity_img":"优惠活动的图片信息",
	    "count":"评价人数（int）",
	    "all_fuel_type":"该油站的所有油品",
	    "price":"油品单价"

        }
    },
    //获取商品优惠
    {
        "name": "获取商品优惠",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
            "action": "get_goods_list_sha1s",
            //name:根据用户名查询对应卡号,获得指定给其推送的商品
            "data": {
    	        "longitude": 123.384,
    	        "latitude": 41.8,
                    "cardnum" : "9130230000090763",
    	        "start": 0,
    	        "end": 100
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "has_next": "true",
                "sha1s":[
               "9f8df847542d36947b1be0b2c411760385020af8",
                    "f4fbb12da9ddc147011d34d27448c627bdd52590"
                ],
                "promotion_ids":["1","2"]

            }

        },
        "note": {
            "请求参数":"-------------",
            "cardnum":'移动端用户对应的卡号',
            "longitude": "经度（float）",
            "latitude": "纬度（float）",
            "start": "请求的开始标识 （float）",
            "end": "请求结束的 标识（float）",
            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             "has_next": "是否还有更多优惠商品",
	        "sha1s": "商品的sha1列表",
        }
    },

    // 批量商品优惠
    {
        "name": "获取商品优惠详情",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
            "action": "get_goods_list",
    	    "data": {
                "longitude": 123.384,
                "latitude": 41.8,
    		"sha1s":["3b94dd7ec18973fff4fa006ec89f68bb9a2d8bbf",
                 "3fea96a31da8dc7813b99be41e37326c874a3172",
                 "301f89857e9dfb5b5b9a5ea26698cfa18c01381c"]
            }

        },
        "response": {
            "info": "OK",
            "ret": "0001",

    	    "data": {
              "has_next": "true",
              "goods_list":[
                    {
                        "good_pos_id":"4324244",
                        "goods_name": "百岁山天然矿泉水570ml*24",
                        "goods_sha1": "9f8df847542d36947b1be0b2c411760385020af8",
                        "seller_sha1":"58bac0923de5d3570ec22930275721f4684e62ad",
                        "price": 50,
                        "discount" :0.9,
                        "discount_info": "9折",
                        "discount_end_time": "2015-04-08",
                        "available_source": "中森美兴工街加油站便利店",
                        "history": 2,
                        "pick": 0,
                        "img_info": "",
                        "src":"/gcustomer/ajax/render_image/",
                        "img_sha1":""
                    },
                    {
                        "goods_name": "脉动芒果口味600ml/瓶",
                        "goods_sha1": "f4fbb12da9ddc147011d34d27448c627bdd52590",
                        "seller_sha1":"882348fd3762a3804962d23d190041aae5d26ec6",
                        "price": 3.7,
                        "discount" : 0.9,
                        "discount_info": "300积分兑换,限量50瓶",
                        "discount_end_time": "2015-04-10",
                        "available_source": "京东商城",
                        "history": 8,
                        "pick": 1,
                       "src":"/gcustomer/ajax/render_image/",
                        "img_sha1":""
                      },
                ],
            },
        },
        "note": {
            "请求参数":"-------------",
            "sha1s":"需要请求的sha1列表",

            "返回参数":"--------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
    	    "goods_list": "所有商品的列表",
    	    "goods_name": "商品的名字",
    	    "goods_sha1": "商品的sha1",
    	    "price": "商品的价格",
    	    "discount": "商品的打折信息",
    	    "discount_end_time": "优惠截止日期",
    	    "available_source": "商品来源",
    	    "history": "购买历史",
    	    "pick": "取货方式,0:预定自取,1:商城送货",
    	    "distance": "我距离该商品所在店的距离",
    	    "img": "商品图片"
        }
    },

    //获取可积分兑换商品
    {
    "name": "获取可积分兑换商品",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
        "action": "get_score_list_sha1",
        "data": {
            "user_sha1": "32d60201562870f97d4e106596d05eeceaf25851",
            "longitude": 123.384,
            "latitude": 41.8,
            "start":0,
            "end":10
        }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
           "has_next": "true",
                "sha1s":[
               "0636a8541e7fede0cda85dd98a7cb0410fb009fe",
                    "136e18d86a4d66a91427d3274c575384d8a97919"
            ]
    },
        "note": {
            "请求参数":"-------------",

             "user_sha1": "用户的sha1",
            "start":"请求的开始标识",
            "end":"请求结束的标示符",

            "返回参数":"-----",
            "integral_list":"积分列表",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",

            "img":"商品的图片信息",
            "goods_name": "商品名称",
            "sha1": "商品sha1",
            "score":"积分",
            "history":"用户历史购买次数",
            "store_sha1":"商家sha1"
        }
    },
    //获取车后服务
    {
        "name": "获取车后服务",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
            "action": "get_service_list_sha1s",
            "data": {
        	        "longitude": 123.384,
        	        "latitude": 41.8,
        	        "start": 0,
        	        "end": 2
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                  "has_next": "true",
            "sha1s":[
                    "2bb94ac4c625c6fd5191b743b363b6ea3432c322",
                    "a47a37b3999b206c854a9842e7875756dbad2671"
                 ]
            }
        },
        "note": {

            "请求参数":"-----",
             "longitude": "经度（float）",
            "latitude": "纬度（float）",
            "start": "请求的开始标识",
            "end": "请求结束的标示符",

             "返回参数":"-----",

            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
	        "sha1s":"获取车后服务sha1列表",
            "has_next": "是否还有更多服务",
        }
    },

    // 车后服务详情
    {
        "name": "车后服务详情 -- 字段不全 需要添加字段",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
            "action":"get_service_list",
            "data":{
                "longitude": 123.384,
                "latitude": 41.8,
                "sha1s":[
    	       "16cb6d96c4cc1086570efbd190f71aba9134020c"
                 ]

            }
        },

        "response": {
            "ret": "0001",
            "info": "OK",

            "data": {
                "service_list": [
                    {
                        "item_type": 0,
                        "sha1": "16cb6d96c4cc1086570efbd190f71aba9134020c",
                        "title": "洗车人家",
                        "item_img": "0032f190ee0a8b54983bc707d5c57a0a9d009596.jpg",
                        "seller_sha1": "9a129c439aa68199d806a391708234213e9d4bf7",
                        "score": 3,
                        "comment_count": "173",
                        "discount_info": "折扣信息",
                        "latitude": 41.2,
                        "longitude": 123.1,
                        "src": "/gcustomer/ajax/render_image/",
                        "img_sha1": ""
                    },
                    {
                        "item_type": 1,
                        "sha1": "ef052473d5ed6e4893985386be65cd3d962659ad",
                        "discount_info": "",
                        "title": "丽车房汽车美容装饰(旗舰店)",
                        "item_img": "0032f190ee0a8b54983bc707d5c57a0a9d009596.jpg",
                        "seller_sha1": "fe3d9da04ec4c8b26a2f707baec3794cfff8de10",
                        "score": 0,
                        "comment_count": "0",
                        "latitude": 41.2,
                        "longitude": 123.1
                    }
                ]
            }

        },

        "note": {

            "请求参数":"----",
            "sha1s":"请求车后服务的sha1s",
            "返回参数":"------",

            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
    	    "service_list": "所有服务的列表",

    	    "sha1": "商家的sha1",
    	    "item_type": "商品类型：0是商品，1是服务",
    	    "title": "商家名称",
    	    "score": "评分",
    	    "item_img": "商家图片",
    	    "comment_count": "评分人数",
	    "latitude": "经度",
	    "longitude": "纬度"
        }
    },

    // 商品评论
    {
        "name": "商品评论",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
	    "action": "comment_item",
	    "data": {
    		"user_sha1": "32d60201562870f97d4e106596d05eeceaf25851",
    		"item_sha1": "9f8df847542d36947b1be0b2c411760385020af8",
    		"score": 3
    	    }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{},
        },
        "note": {
            "请求参数":"-----",

            "user_sha1": "用户的sha1",
            "item_sha1": "商品sha1",
            "score":"对该商品的评分",

            "返回参数":"------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识"
        }
    },

    // 商家详情
    {
        "name": "获取商家详情（新）",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
	    "action": "get_merchants_info",
	    "data": {
    		"sha1": "fe3d9da04ec4c8b26a2f707baec3794cfff8de10"
    	    }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
		"name":"商家名字",
		"address":"商家地址",
	        "tel":"商家电话",
		"longitude": "经度（float）",
            	"latitude": "纬度（float）",
		"logo":"商家图片",
		"score":3,
		"introduction":"商家简介",
        "src":"/gcustomer/ajax/render_image/",
        "img_sha1":""

	    },
        },
        "note": {
            "请求参数":"-----",

            "user_sha1": "用户的sha1",
            "item_sha1": "商品sha1",
            "score":"对该商品的评分",

            "返回参数":"------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
	    "name":"商家名字",
	    "address":"商家地址",
	    "tel":"商家电话",
	    "longitude": "经度（float）",
            "latitude": "纬度（float）",
	    "score":"商家的综合评分（int 范围0到5）",
	    "introduction":"商家简介"
        }
    },

    // 用户行为
    {
        "name": "用户行为(2015-08-12)",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
            "action": "user_action",
            "data": {
                "action_type" : 0,
                "username":"15996458299",
                "obj_type":0,
                "sha1":"300585",
                "promotion_id":93
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{}
        },
        "note": {
            "请求参数":"-----",
        
            "ret": "代表请求的信息一些标识",
        }
    },

    // 加油宝登录
    {
        "name": "加油宝登录",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
            "action":"staff_login",
            "data":{
                "username": "15996458299",
                "password": "user123"
            }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data": {
            	"user_sha1": "32d60201562870f97d4e106596d05eeceaf25851",
            	"user_name": "15996458299",
                "career":"司机",
    	    	"session_id": "sdfsdfsdfgdgsdfsdaff038b16d84c9a4ae17wsede"
    	     },
         },
        "note": {
            "请求参数":"-------------",
            "username": "用户名",
            "password": "用户密码",
             "返回的参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "返回的状态信息",
	        "user_sha1": "用户的sha1",
            "user_name": "用户名",
            "avarta_sha1":"头像图片sha1",
            "nick":"昵称",
            "score":"用户的积分",
            "career":"职业",
            "session_id": "用户session——id",
            "cardnum": "加油卡信息"
        }
    },

    // 查询用户积分
    {
        "name": "查询用户积分(2015-7-17)",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
	    "action": "get_user_score",
	    "data": {
    		"vcard_id": "15996458299"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
		"total_integrals":100,
		"current_integrals":20,
		"level":1
             }
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号(手机号)",
            "返回参数":"------",
	    "total_integrals":"累计积分",
	    "current_integrals":"可用积分",
	    "level":"用户等级（1-5）"
        }
    },

    // 获取广告位信息
    {
        "name": "获取广告位信息",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
	    "action": "get_advertis",
	    "data": {
    		"name": "15996458299"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
		"list":[
		    {
			"src":"/gcustomer/ajax/render_image/",
                                        "img_sha1" : "",
			"title":"倍耐力轮胎",
			"sha1":"67857698oe64f65o09a89b",
			"play_time":3
		    },
		    {
			"src":"/gcustomer/ajax/render_image/",
                                        "img_sha1" : "",
			"title":"倍耐力轮胎",
			"sha1":"67857698oe64f65o09a89b",
			"play_time":3
		    },
		]

             }
        },
        "note": {
            "请求参数":"-----",
            "user_sha1":"用户的sha1",
            "返回参数":"------",
	    "src":"广告的图片",
	    "title":"广告的标题",
	    "sha1":"广告的sha1",
	    "play_time":"广告的播放时长"
        }
    },

    // 获取广告详情
    {
        "name": "获取广告详情(2015-7-22)",
        "url": "http://wheel.zcdata.com.cn:9988/wheel/api/",
        "method": "POST",
        "params": {
	    "action": "get_advertis_detail",
	    "data": {
    		"sha1": "32d60201562870f97d4e106596d05eeceaf25851"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
		"title":"倍耐力轮胎",
		"content":"广告的内容",
             }
        },
        "note": {
            "请求参数":"-----",
            "sha1":"广告的sha1",
            "返回参数":"------",
	    "title":"广告的标题",
	    "content":"广告的内容",
        }
    },

    // 点击广告
    {
        "name": "点击广告(作为web的广告点击统计的依据)",
        "url": "http://wheel.marketcloud.com.cn/wheel/api",
        "method": "POST",
        "params": {
	    "action": "read_advertis",
	    "data": {
    		"sha1": "1f669c8e46d8b288193004d0dee47e2230767a2a",
		"user_sha1":"4c00c49d9f86daecd199abb1f2803efaf542cd82"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{

             }
        },
        "note": {
            "请求参数":"-----",
            "sha1":"广告的sha1",
	    "user_sha1":"用户的sha1",
            "返回参数":"------",
        }
    },

    //行车轨迹
    {
        "name": "行车轨迹(2015-7-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "trajectory",
	    "data": {
    		"name": "15996458299",
		"longitude": 123.384,
                        "latitude": 41.8
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{}
        },
        "note": {
            "请求参数":"-----",
            "name":"用户名(电话号码)",
            "longitude": "经度",
            "latitude": "纬度",
            "返回参数":"------",
        }
    },


//================  新版驾车宝新增接口 ==============================
{
        "name": "=======================以下为新版驾车宝接口"+
                       "======================",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {},
        "response": {},
        "note": {}
    },
{"name": "********************************用户与加油卡模块"+"****************************",},
//用户与加油卡模块
 // 注册
    {
        "name": "注册(2015-7-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "register",
            "data": {
           "name": "15996458299",
                "password": "920816",
                "career": "其他"
            }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data": {},
         },
        "note": {
            "请求参数":"-------------",

            "name": "手机号",
            "password": "密码",
            "career": "职业",
            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识"
        }
    },
    // 登录
    {
        "name": "登录(2015-7-18)",
        "url": "http://wheel.marketcloud.com.cn/wheel/api",
        "method": "POST",
        "params": {
            "action":"login",
            "data":{
                "name": "15996458299",
                "password": "920816"
            }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data": {
            "vcard_id":"15996458299",
            "avarta_sha1":"0a0f8c22a861231aff038b16d84c9a4ae175083e",
            "nick":"lilei",
            "score":323,
            "career":"司机",
            "id_card":"",
            "is_pay_in_advance":0,
            "session_id": "sdfsdfsdfgdgsdfsdaff038b16d84c9a4ae17wsede",
            "time":"注册时间"
     },
         },
        "note": {
            "请求参数":"-------------",
            "username":"用户虚拟卡号(手机号)",
            "password": "用户密码",
             "返回的参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "返回的状态信息",
            "vcard_id": "用虚拟卡号",
            "avarta_sha1":"头像图片sha1",
            "nick":"昵称",
            "score":"用户的积分",
            "career":"职业",
            "id_card":"用户虚拟卡激活之后,返回其身份证号",
            "is_pay_in_advance":"是否可以预支付:0不可以预支付 1:可以预支付",
            "session_id": "用户session——id",
            "time":"注册时间"
        }
    },

//忘记登录密码
{
        "name": "修改登录密码(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "forget_login_password",
        "data": {
            "name":"15996458299",
            "new_password":"920816",
            "re_new_password":"920816"
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "name":"用户名（手机号）",
            "new_password":"新的密码",
            "re_new_password":"重复新的密码",
            "返回参数":"------",
        }
    },

//激活虚拟卡
{
        "name": "激活虚拟卡(2015-7-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action":"activate_vcard",
            "data":{
                "vcard_id": "15996458299",
                "id_card":"320123199208164019",
                "pay_password": "920816",
                "re_pay_password":"920816"
            }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
         },
        "note": {
            "请求参数":"-------------",
            "vcard_id":"用户虚拟卡号(手机号)",
            "id_card":"身份证号",
            "pay_password": "用户密码",
            "re_pay_password":"重复用户密码",
             "返回的参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "返回的状态信息",
        }
    },

//上传或修改头像
 {
        "name": "上传头像(2015-7-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "upload_avarta_image",
        "data": {
                        "name": "15996458299",
                        "avarta_image_data" : ""
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "name": "用户名(手机号，不可修改)",
            "avarta_image_data": "图片二进制数据",
            "返回参数":"------",
        }
    },

//修改用户昵称
    {
        "name": "修改个人信息(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "modify_user_info",
	    "data": {
		"name": "15996458299",
        	            "nick": "user1"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
	    "name": "用户名(手机号，不可修改)",
            "nick": "昵称",
            "返回参数":"------",
        }
    },

    //修改登录密码
    {
        "name": "修改登录密码(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "modify_login_password",
	    "data": {
        	"name":"15996458299",
        	"old_pasword":"123456",
        	"new_password":"234567",
        	"re_new_password":"234567"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "name":"用户名（手机号）",
            "old_pasword":"老的密码",
            "new_password":"新的密码",
            "re_new_password":"重复新的密码",
            "返回参数":"------",
        }
    },

    //获取石油公司信息
    {
        "name": "获取石油公司信息(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "get_oil_company_info",
        "data": {
                        "name":"15996458299"
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":[
                {
                    "comp_id" : 1,
                    "comp_name":"北京壳牌石油公司"
                },
                {
                    "comp_id" : 2,
                    "comp_name":"北京中石油"
                }
            ]
        },
        "note": {
            "请求参数":"-----",
            "name": "用户名，即手机号码",
            "返回参数":"------",

        }
    },


    //和石油公司关联
    {
        "name": "关联石油公司(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "associated_oil_company",
	    "data": {
                        "vcard_id":"15996458299",
                        "id_card":"320123199208164019",
                        "comp_id":9
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "vcard_id": "虚拟卡号，即手机号码",
            "id_card":"身份证号",
            "comp_id":"石油公司id",
            "返回参数":"------",
        }
    },

    //绑定加油实体卡(待定)
    {
        "name": "绑定加油卡(2015-07-31)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "band_oil_card",
	    "data": {
                        "vcard_id":"15996458299",
                        "id_card" : "320123199208164019",
                        "comp_id":9,
                        "card_num": "9130270000530844",
                        "card_type":0
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "card_num": "加油卡号",
            "user_name":"用户名（手机号）",
            "id_card":"用户身份证号",
            "comp_id":"公司id",
            "返回参数":"------",
        }
    },
    //取消绑定加油卡(待定)
    {
        "name": "取消绑定加油卡(2015-07-31)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "delete_oil_card_bind",
        "data":{
                        "vcard_id":"15996458299",
                        "id_card" : "320123199208164019",
                        "comp_id":9,
                        "card_num": "9130270000530844",
                        "pay_password":"920816"
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001"
        },
        "note": {
            "请求参数":"-----",
           "card_num": "加油卡号",
            "vcard_id":"虚拟卡号（手机号）",
            "id_card":"用户身份证号",
            "comp_id":"公司id",
            "pay_password":"支付密码",
            "返回参数":"------",
        }
    },
    //查看我的账户
    {
        "name": "查看我的虚拟卡(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "get_pump_card",
	    "data": {
        	       "vcard_id":"15996458299"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":[
            	{
                "comp_id":1,
        	    "card_desc":"中石油A公司",
                 "current_balance":20.0,
        	},
        	{
                "comp_id":2,
        	    "card_desc":"中石油B公司",
                 "current_balance":80.0,
        	},
            ]
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号（手机号）",
            "返回参数":"------",
            "comp_id": "关联的公司",
            "card_desc":"公司名称",
            "current_balance":"当前余额",
        }
    },

//查看我的石油公司账户的实体卡信息
 {
        "name": "查看我的石油公司账户的实体卡信息(2015-07-31)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "get_my_oil_card",
        "data": {
                    "vcard_id":"15996458299",
                    "comp_id":1
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "card_list":[
                    {
                        "cardnum":"9656840593845",
                        "card_type":1
                    },
                    {
                        "cardnum":"9656840593845",
                        "card_type":0
                    },
                 ]
            }
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号（手机号）",
            "comp_id":"石油公司id",
            "返回参数":"------",
            "card_type":"实体卡类型1:主卡0:副卡",
            "cardnum":"石油公司实体卡",
            "card_list":"实体卡列表,key表示卡号,value为1表示主卡,0表示副卡",
        }
    },


    //忘记支付密码
    {
        "name": "忘记支付密码(2015-08-17)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "forget_pay_password",
	    "data": {
                	"vcard_id":"15996458299",
                            "password":"920816",
                            "re_password":"920816"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号（手机号）",
            "password":"新密码",
            "re_password": "重复新密码",
            "返回参数":"------",
        }
    },

    //检查支付密码是否正确
    {
        "name": "检查支付密码是否正确(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "check_pay_password",
	    "data": {
                    	"vcard_id":"15996458299",
                          "id_card" : "320123199208164019",
                    	"pay_password":"920816"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号（手机号）",
            "id_card" : "身份证号",
            "pay_password":"旧的支付密码",
            "返回参数":"------",
        }
    },

    //修改支付密码
    {
        "name": "修改支付密码(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "modify_pay_password",
	    "data": {
                    	"vcard_id":"15996458299",
                         "id_card" : "320123199208164019",
                    	"old_pay_password":"920816",
                    	"new_pay_password":"920816",
                    	"re_new_pay_password":"920816"
    	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号（手机号）",
            "id_card":"身份证号",
            "old_pay_password":"旧的支付密码",
            "new_pay_password":"新的支付密码",
            "re_new_pay_password":"重复新的支付密码",
            "返回参数":"------",
        }
    },

//生成充值订单
 {
        "name": "生成充值订单(2015-08-07)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "create_recharge_order",
        "data":{
            "vcard_id":"15996458299",
            "comp_id":0,
            "money":100
        }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "order_sha1": "66f3e0e39ea401f968b8e4f2bb0d33d159222b4f",
            }
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号（手机号）",
            "money":"充值金额（float）",
            "comp_id": "选择充值的公司 0表示网感至察",
            "返回参数":"------",
            "order_sha1":"订单sha1",
        }
    },

  //充值
    {
        "name": "充值(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "recharge",
        "data":{
            "vcard_id":"15996458299",
            "id_card" : "320123199208164019",
            "comp_id":0,
            "money":100
        }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                        "current_balance":10034.50,
                        "money":23.0
            }
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号（手机号）",
            "id_card":"身份证号",
            "money":"充值金额（float）",
            "comp_id": "选择充值的公司 0表示网感至察",
            "返回参数":"------",
            "current_balance":"当前余额",
        }
    },
{"name": "********************************油品购买模块"+"****************************",},
//油品购买模块
// 用户扫码查看油品订单
    {
        "name": "确认订单状态(待定2015-7-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "confirm_order_by_user",
            "data": {
                "vcard_id":"15996458299",
                "order_sha1": "9fa5a3cf6eb9071f30d2c765995ae104d946a31d"
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "order_info":{
                    "order_sha1":"9fa5a3cf6eb9071f30d2c765995ae104d946a31d",
                    "trans_type":0,
                    "order_total":20.0,
                    "item_count":1.2,
                    "time":"",
                    "status":1,
                    "vcard_id":"",
                    "fuel_info":{
                        "fuel_name": "脉动芒果口味600ml/瓶",
                        "barcode": "f4fbb12da9ddc147011d34d27448c627bdd52590",
                        "price": 3.7,
                        "src":"/gcustomer/ajax/render_image/",
                        "img_sha1":""
                    },
                    "site_info":{
                        "name" : "",
                        "sha1" : "sdcasdca",
                        "address" : "北京市",
                        "phone" : "1523828282",
                    }
              }
            }
        },
        "note": {
            "vcard_id":"虚拟卡号(电话号码)",
            "order_sha1":"订单号",
            "order_type":" 整型 0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城 ",
            "fuel_info":"油品信息",
            "fuel_name" : "油品名字",
            "site_sha1": "油站sha1",
            "price":"该油站该油品的价格",
            "barcode":"油品的条形码",
            "order_total":"订单总价",
            "pump_count":"油品升数",
            "time":"订单生成时间",
            "site_info":"商家信息",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识"
        }
    },

//选择支付帐号
{
        "name": "选择支付方式(2015-07-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "get_pay_account",
        "data":{
            "vcard_id":"15996458299",
            "id_card" : "320123199208164019",
            "order_sha1":"9fa5a3cf6eb9071f30d2c765995ae104d946a31d"
        }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":[
                {
                    "comp_id":0,
                    "comp_desc":"网感至察",
                    "current_balance":4540.50
                },
                {
                    "comp_id":1,
                    "comp_desc":"中石油",
                    "current_balance":4540.50
                },
            ]
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号(电话号码)",
            "id_card":"身份证号",
            "order_sha1":"交易sha1,其中的comp_id用于查询匹配的支付帐号",
            "返回参数":"------",
            "comp_id":"帐号",
            "comp_desc":"帐号名",
            "current_balance":"余额"

        }
    },

//加油卡支付
    {
        "name": "加油卡支付(2015-08-06)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "pay_by_oil_card",
        "data":{
            "vcard_id":"15996458299",
            "order_sha1":"1c3f3b9818303760373fa6dc0d46bb7b1f36e97c",
            "id_card" : "320123199208164019",
            "comp_id":9,
            "pay_password":"920816",
            "pay":100
        }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号(电话号码)",
            "order_sha1":"订单号",
            "id_card":"身份证号",
            "pay_password":"支付密码",
            "pay":"付款金额（float）",
             "comp_id":"公司",
            "返回参数":"------",

        }
    },

//存储out_trade_no 与订单的关联
{
        "name": "存储out_trade_no 与订单的关联(2015-08-06)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "download_trade_no_with_order",
        "data": {
            "order_sha1": "1c3f3b9818303760373fa6dc0d46bb7b1f36e97c",
            "vcard_id": "15996458299",
            "out_trade_no":"4324242424"
            }
        },
        "response": {
           "ret":"0001",
           "info":"OK"
        },
        "note": {
            "请求参数":"-----",
            "order_sha1":"订单号",
            "vcard_id":"虚拟卡号(电话号码)",
            "返回参数":"------",
            "message":"success",
        }
    },

 // 支付完成修改订单状态 支付已完成(消息服务器通知:用户和收银员 待定)
    {
        "name": "商品确认已交易",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "purchase_complete_by_user",
        "data": {
            "order_sha1": "1c3f3b9818303760373fa6dc0d46bb7b1f36e97c",
            "vcard_id": "15996458299"
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "order_sha1":"订单号",
            "vcard_id":"虚拟卡号(电话号码)",
            "返回参数":"------"
        }
    },

{"name": "********************************功能模块"+"****************************",},
//功能模块
//附近
    {
        "name": "附近(2015-07-15)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "get_near_by_infos",
        "data": {
                    "longitude": 116.170,
                    "latitude": 40.340,
                    "info_flag":0
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":[
                {
                  "longitude": 123.384,
                  "latitude": 41.8,
                  "name":"商家名字",
                  "sha1":"商家sha1",
                  "distance":5,
                },
                {
                  "longitude": 123.384,
                  "latitude": 41.8,
                  "name":"商家名字",
                  "sha1":"商家sha1",
                  "distance":5,
                },
            ]
        },
        "note": {
            "请求参数":"-----",
        "longitude": "我的经度",
            "latitude": "我的纬度",
            "info_flag":"请求消息类型，0：油品；1：便利店；2：车后服务",
            "返回参数":"------",
            "longitude": "油站或商家的经度",
            "latitude": "油站或商家的纬度",
            "name":"油站或商家的名字",
            "sha1":"商家的sha1",
            "distance":"距离(单位km)",
        }
    },


    //热销商品
    {
        "name": "热销商品top10(2015-08-08)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "get_hot_goods",
	    "data":{
                    "username":"15996458299",
	        "longitude": 116.300,
        	        "latitude": 40.052,
                    "flag":0
	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":[
                {
              "name":"商品名字",
              "sha1":"油品唯一标识,此处用油品的barcode",
              "img_sha1":"商品图片",
              "src": "/gcustomer/ajax/render_image/",
              "counts":201,
        	  "price":51.8,
        	  "longitude": 123.384,
        	  "latitude": 41.8,
        	  "phone":"13243432424",
        	  "address":"公司名字"
                },
                {
                  "name":"商品名字",
                   "sha1":"便利店商品sha1",
                  "img_sha1":"商品图片",
                  "src": "/gcustomer/ajax/render_image/",
                  "counts":201,
              "price":51.8,
              "longitude": 123.384,
              "latitude": 41.8,
              "phone":"13243432424",
              "address":"公司名字"
                },
                {
                  "name":"商品名字",
                   "sha1":"车后服务sha1",
                  "img_sha1":"商品图片",
                  "src": "/gcustomer/ajax/render_image/",
                  "counts":201,
        	  "price":51.8,
        	  "longitude": 123.384,
        	  "latitude": 41.8,
        	  "phone":"13243432424",
        	  "address":"公司名字"
                },
            ]
        },
        "note": {
            "请求参数":"-----",
            "username" :"用户名",
            "longitude": "我的经度",
            "latitude": "我的纬度",
            "flag":"热销商品类型   0：油品；1：商品；2：车后服务",
            "返回参数":"------",
            "name": "商品名字",
            "sha1":"商品的sha1",
            "img_sha1": "商品图片",
            "counts":"商品销量（整型）",
            "price":"商品价格，float型",
            "longitude": "经度",
            "latitude": "纬度",
            "phone":"油站电话",
            "address":"公司名字"
        }
    },

    //获取道路救援
    {
        "name": "道路救援(2015-07-11)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "get_help",
                "data" : {
                    "name":"15996458299"
                }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":[
                {
                  "name": "名字",
        	  "phone": "2382173190"
                },
                {
                  "name": "名字",
        	  "phone": "2382173190"
                },
            ]
        },
        "note": {
            "请求参数":"-----",
            "name":"虚拟卡号(手机号)",
            "返回参数":"------",
            "name": "救援机构名字",
            "phone": "救援电话",
        }
    },

    //获取我的专享
    {
        "name": "我的专享(2015-08-04)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "get_my_sales_summary",
	    "data":{
	        "vcard_id":"15996458299",
	        "flag":0,
	        "start":0,
                    "end":2
	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":[
		{
                                    "sha1":"354523dfsadfasdfdsaf35423454fsdfasd",
                                    "name":"百岁山矿泉水",
                                    "price":5.0,
                                    "discount":0.9,
                                    "count":100,
                                    "comp_name":"北京壳牌",
                                    "address":"北京壳牌加油站",
                                    "seller_sha1":"fjsdjfsd;lfjsdf;lksdjfsdlkfsdjflsd;kfjsdlf",
                                    "phone":"15996458299",
                                    "promotion_id":1,
                                    "pay_type":1,
                                    "desc":"",
                                    "img_sha1":"",
                                    "src":""
                               
                        },
                        {
                                    "sha1":"354523dfsadfasdfdsaf35423454fsdfasd",
                                    "name":"百岁山矿泉水",
                                    "price":5.0,
                                    "discount":0.9,
                                    "count":100,
                                    "comp_name":"北京壳牌",
                                    "address":"北京壳牌加油站",
                                    "seller_sha1":"fjsdjfsd;lfjsdf;lksdjfsdlkfsdjflsd;kfjsdlf",
                                    "phone":"15996458299",
                                    "promotion_id":1,
                                    "pay_type":1,
                                     "desc":"",
                                    "img_sha1":"",
                                    "src":""
                               
                        },
            ],
            "has_next":"false"
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号（手机号）",
            "flag":"请求标识，0：油品；1：商品；2：车后服务",
            "start":"起始",
            "end":"结束",
            "返回参数":"------",
            "sha1":"商品sha1",
            "name":"商品名",
            "price":"商品价格",
            "discount":"折扣",
            "count":"已购买数量",
            "comp_name":"公司名",
            "address":"商家地址",
            "seller_sha1":"商家sha1",
            "phone":"商家电话",
            "promotion_id":"营销活动id",
            "pay_type":"是否可预付(pay_type 0:不可以预付,只能预订 1:可以预付)",
             "desc":"商品额外信息",
            "img_sha1":"商品图片",
            "src":"图片路由",
            "has_next":"是否还有更多"
        }
    },

    //获取用户信息
    {
        "name": "获取用户信息(2015-7-18)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action":"get_user_info",
            "data":{
                "name": "15996458299",
                "password": "920816"
            }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data": {
            "score":323,
            "current_balance":24390.89,
            "rank":1,
            "avarta_image_sha1":"fdsfdsf",
     },
         },
        "note": {
            "请求参数":"-------------",
            "username":"用户虚拟卡号(手机号)",
            "password": "用户密码",
             "返回的参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "返回的状态信息",
            "score":"用户的积分",
            "current_balance":"当前余额",
            "ranl":"等级",
            "avarta_image_sha1":"头像sha1",
        }
    },
    
    //获取我的订单数量
    {
        "name": "获取我的订单数量(2015-08-07)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "get_order_num",
	    "data":{
                    "vcard_id": "15996458299",
	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "wait_pick_up_num":2,
                "wait_pay_num":2,
                "wait_refund_num":2,
                "wait_fix_num":2

            }
        },
        "note": {
            "请求参数":"-----",
            "vcard_id": "用户卡号",
            "响应参数":"-----",
            "wait_pick_up_num":"等待取货数量",
            "wait_pay_num":"等待付款数量",
            "wait_refund_num":"等待退款数量",
            "wait_fix_num":"预付的数量",

        }
    },

    //获取我的订单详情列表
    {
        "name": "获取我的订单列表(2015-08-04)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "get_order_list",
	    "data":{
                    "vcard_id": "15996458299",
                    "start": 0,
                    "end": 10,
                    "status":1
	    }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "has_next":"true",
                "trans_list":[
		            {
                        "item_name":"商品名字",
                        "item_sha1":"商品sha1",
                        "time":"交易时间",
                        "item_total":"交易金额",
                        "item_count":"购买数量",
                        "status":"交易状态",
                        "address":"交易地点",
                        "station_sha1":"油站的sha1",
                        "seller_sha1":"便利店的sha1",
                        "geo_x":"精度",
                        "geo_y":"维度",
                        "trans_type":"交易类型",
                        "order_sha1":"订单号",
                        "status_flag":"订单状态"
                    },
                ],
            }
        },
        "note": {
            "请求参数":"-----",
            "vcard_id": "用户卡号",
            "start": "起始位置",
            "end": "结束位置",
            "status":"请求交易类型,订单状态  0 代表订单生成  1代表支付完成 2代表交易完成 3代表交易被收银员录入 4商品预订状态  5 申请退款完成状态,等待审核 6 工作人员完成退款 ",
	        "返回参数":"-----",
            "item_name":"商品名字",
            "item_sha1":"商品sha1",
            "time":"交易时间",
            "item_total":"交易金额",
            "item_count":"购买数量",
            "address":"交易地点",
            "station_sha1":"油站的sha1",
            "geo_x":"精度",
            "geo_y":"维度",
            "seller_sha1":"便利店的sha1",
            "has_next": "是否还有更多数据",
            "trans_type":"交易类型，0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城",
            "order_id":"订单号",
            "status_flag":"订单状态,订单状态0未支付，1已支付未取货，2已交易并取货(同为收银员未录入状态)，3收银员已录入状态 4商品预订状态",

        }
    },

//取消订单的接口,修改订单状态为已过期
{
        "name": "取消订单的接口(2015-08-07)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "delete_order",
        "data":{
                    "vcard_id": "15996458299",
                    "order_sha1":"66f3e0e39ea401f968b8e4f2bb0d33d159222b4f"
        }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "ret":"0001",
                "info":"OK",
            }
        },
        "note": {
            "请求参数":"-----",
            "vcard_id": "用户卡号",
            "order_sha1":"订单sha1",
            "响应参数":"-----",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识"
        }
    },

//我的专享商品预付模块
{"name": "********************************商品预付模块"+"****************************",},
// 点击购买，生成订单
    {
        "name": "点击购买(2015-08-05)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "create_order",
            "data": {
                "vcard_id": "13591995090",
                "good_sha1": "7f968f3911501f782c0d0b85c9772b235915328c",
                "order_type":1,
                "item_count":1.0,
                "promotion_id":34,
                "seller_sha1":"",
                "price":40.7,
                "order_total":20.12,
                "status":4
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "order_sha1": "66f3e0e39ea401f968b8e4f2bb0d33d159222b4f",
            }
        },
        "note": {
            "请求参数":"-----",
            "status":"订单状态0未支付，1已支付未取货，2已交易并取货(同为收银员未录入状态)，3收银员已录入状态 4商品预订状态",
            "price":"商品或车后服务的单价",
            "order_type":" 0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城 ",
            "vcard_id":"虚拟卡号",
            "good_sha1":"商品的sha1",
            "order_sha1":"订单sha1",
            "promotion_id":"营销活动id",
            "seller_sha1":"我的专享商家sha1",
            "order_total":"订单总价",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识"
        }
    },

//查看预订是否可以购买
{
        "name": "收银员查看订单是否已支付(2015-08-03)",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/jiayouyuan_api",
        "method": "POST",
        "params": {
        "action": "check_reservation_by_user",
            "data": {
                    "order_sha1": "5ab7f6baf8b25a73b7a76ff834bceab47d1607d8"
                }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数": "-----",
            "order_id": "订单号",
            "seller_sha1": "取货地点商家信息",
            "返回参数": "------"
        }
    },

{"name": "**********************************积分模块"+"****************************",},
 //获取积分商城商品详情
    {
        "name": "获取积分商城商品摘要信息（2015-7-20）",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "get_score_list",
            "data": {
                "vcard_id": "15996458299",
                "start":0,
                "end":10
                }
            }
        ,
        "response": {
            "info": "OK",
            "ret": "0001",
          "data":{
                "has_next":"true",
                "score_list":[
                    {
                        "img_sha1":"",
                        "src" : "",
                        "goods_name": "商品名称1",
                        "sha1": "商品sha1",
                        "seller_sha1":"58bac0923de5d3570ec22930275721f4684e62ad",
                        "score":"积分1",
                     },
                    {
                        "img_sha1":"",
                        "src" : "",
                        "goods_name": "商品名称2",
                        "sha1": "商品sha1",
                        "seller_sha1":"882348fd3762a3804962d23d190041aae5d26ec6",
                        "score":"积分2",
                    }
                ]

        }
    },
        "note": {

            "请求参数":"-----",
            "vcard_id": "虚拟卡号，如果没登录，发空字符串",
            "start":0,
            "end":10,

             "返回参数":"-----",

            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            "img_sha1":"",
        "src" : "",
        "goods_name": "商品名称2",
        "sha1": "商品sha1",
        "seller_sha1":"商家sha1",
        "score":"积分2",

        }
    },

//获取积分商品详情
{
        "name": "获取积分商品详情（2015-08-04）",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "get_score_good_detials",
            "data": {
                    "sha1":"0d48360b085f18655b2a1fea552e4c5d1e100551"
                }
            }
        ,
        "response": {
            "info": "OK",
            "ret": "0001",
          "data":{
                        "sha1": "商品sha1",
                        "goods_name": "商品名称1",
                        "purchase_count":0,
                        "score":"积分1",
                        "seller_name":"北京壳牌石油公司",
                        "seller_address":"北京西二旗",
                        "seller_phone":"商家电话",
                        "img_sha1":"",
                        "src" : "",
                    },
        }
    ,
        "note": {

            "请求参数":"-----",
            "sha1":"积分商品sha1",
             "返回参数":"-----",

            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            "img_sha1":"",
            "src" : "",
            "goods_name": "商品名称2",
            "sha1": "商品sha1",
            "score":"积分2",
            "purchase_count":"已购买数量",
            "seller_name":"商家名称",
            "seller_address":"商家地址",
            "seller_phone":"商家电话",

        }
    },

//生成积分商品订单
{
        "name": "生成积分商品订单",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "create_score_order",
            "data": {
                "vcard_id": "15996458299",
                "good_sha1": "d61bfc5f8a811ef8ba498dfe9383817eaa8d4ac8",
                "order_type":3,
                "item_count":1,
                "score":40
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
                "order_sha1": "66f3e0e39ea401f968b8e4f2bb0d33d159222b4f"
            }
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号",
            "good_sha1":"商品的sha1",
            "order_type":"订单类型 0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城",
            "item_count":"兑换数量",
            "score":"积分",
            "order_sha1":"此次交易的订单号",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
        }
    },

//用积分兑换积分商城商品
{
        "name": "积分兑换积分商城商品",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "purchase_score_item",
        "data": {
                "vcard_id":"15996458299",
                "pay_password":"920816",
                "order_sha1": "66f3e0e39ea401f968b8e4f2bb0d33d159222b4f",
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "pay_password": "用户密码",
            "vcard_id":"虚拟卡号(手机号)",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识"
        }
    },
    
    //申请商品退款
{
        "name": "申请商品退款（2015-08-06）",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "apply_refund",
        "data": {
                "order_sha1": "66f3e0e39ea401f968b8e4f2bb0d33d159222b4f",
                "vcard_id":"15996458299",
                "pay_password":"920816"
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "order_sha1": "订单号",
            "vcard_id":"虚拟卡号",
            "pay_password":"支付密码",
            "响应参数":"-----",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            "备注：":"目前只支持用户申请退款后持身证去油站当面确认退款"
        }
    },

//查询微信订单
{
        "name": "查询微信订单-08-11）",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "query_weixin_order_params",
        "data": {
                "order_sha1": "22c551b9eb6ef2ed1bafdba2a494b63a699e9fff",
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "order_sha1": "订单号",
            "vcard_id":"虚拟卡号",
            "pay_password":"支付密码",
            "响应参数":"-----",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            "备注：":"目前只支持用户申请退款后持身证去油站当面确认退款"
        }
    },

//意见反馈
{
        "name": "意见反馈-08-21）",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "app_user_feedback",
        "data": {
                "vcard_id": "15996458299",
                "content":"xxx"
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
        },
        "note": {
            "请求参数":"-----",
            "vcard_id":"虚拟卡号",
            "content":"意见反馈内容",
            "响应参数":"-----",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            "备注：":"意见反馈内容不超过100个字符（包括标点符号）",
        }
    },


//状态码
{
        "name": "状态码（需要服务器端人员添加）",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {

       },
        "response": {
          UNKNOWNERR                        : '1111',
    LOGINSUCCESS                       : '0001',
    OK                                           :'0001',
    USERNOTEXIST                       :'0002',
    PASSWORDERROR                  :'0003',
    WITHOUTPERMISSION            : '0004',
    HAVECOMMENTS                    : '0005',
    USEREXIST                               : '0006',
    NODATA                                  : '0007',
    NOMOREDATA                         : '0008',
    CREATE_ORDER_ERROR             : '0009',
    QUERY_ORDER_ERROR              : '0010',
    GOODS_SCORE_ERROR              : '0011',
    PASSWORDINCONSISTENT        : '0012',
    PUMPCARDNOTEXIST                : '0013',
    NOTLOGGEDIN                         : '0014',
    MODIFYPAYPASSWORDERROR  : '0015',
    CURRENTBALANCEDEFICENTCY : '0016',
    PAYBYOILCARDERRO                 : '0017',
    RECHARGEERROR                      : '0018',
    GET_ORDER_INFO_ERROR         : '0019',
    GasWorkerNOTEXIST                : '0020',
    DELETE_ORDER_ERROR              : '0021',
    ALTER_ORDER_STATUS_ERROR   : '0022',
    UPLOAD_IMAGE_ERROR            : '0023',
    ALTER_USER_ERROR                  : '0024',
    PUMP_CARD_HAS_EXIST            : '0025',
    ID_CARD_FORMAT_ERROR          : '0026',
    QUERY_SITE_ERROR                   : '0027',
    QUERY_SITE_FUEL_ERROR          : '0028',
    QUERY_NEAR_INFO_ERROR        : '0029',
    GET_STORE_HOT_GOODS_ERROR : '0030',
    QUERY_HELP_PHONE_ERROR       : '0031',
    USER_ID_CARD_CHECK_ERROR     : '0032',
    GET_ADVERTISE_SETTING_ERROR  : '0033',
    QUERY_ADVERTISE_ERROR             : '0034',
    QUERY_CUSTOMER_ERROR            : '0035',
    ADVERTISEMENT_RECORD             : '0036',
    DRIN_TRACE_RECORD_ERROR         : '0037',
    REGISTER_ERROR                           : '0038',
    REQMETHODERROR                       : '0039',
    LOGINED_ON_OTHER_SIDE            : '0040',
    SAVE_USER_ID_CARD_ERROR          : '0041',
    BIND_PUMP_CARD_ERROR             : '0042',
    PLEASE_FRIST_CREATE_CARD          : '0043',
    QUERY_BIND_CARD_ERROR            : '0044',
    QUERY_COMPANY_ERROR              : '0045',
    CHECK_USER_AND_CARD_ERROR    : '0046',
    DELETE_BIND_CARD_ERROR           : '0047',
            },
        "note": {
              '1111':'服务器端异常',
    '0000':'用户未登录',
    '0001':'Everything is OK',
    '0002':'用户不存在',
    '0003':'密码错误',
    '0004':'评论失败，没有权限',
    '0005':'已评论',
    '0006':'用户已存在',
    '0007':'暂无数据',
    '0008':'没有更多数据',
    '0009':'创建订单出错，订单创建失败',
    '0010':'订单查询出错，未能找到订单',
    '0011':'创建订单失败，积分不足',
    '0012':'两次密码不一致',
    '0013':'加油卡不存在',
    '0014':'当前未登录',
    '0015':'修改支付密码错误',
    '0016':'加油卡余额不足',
    '0017':'加油卡支付失败',
    '0018':'充值失败',
    '0019':'获取订单详情失败',
    '0020':'收银员不存在',
    '0021':'删除订单失败',
    '0022':'修改订单状态失败',
    '0023':'上传图片失败',
    '0024':'修改用户信息失败',
    '0025':'加油卡已存在',
    '0026':'用户身份证信息格式错误',
    '0027':'查询油站失败',
    '0028':'查询指定油站的油品失败',
    '0029':'获取附近失败',
    '0030':'获取便利店热销商品失败',
    '0031':'获取救援电话失败',
    '0032':'用户身份验证错误',
    '0033':'获取广告周期设置失败',
    '0034':'查询广告失败',
    '0035':'查询Gcustomer用户信息失败',
    '0036':'广告查看记录失败',
    '0037':'记录行车轨迹失败',
    '0038':'注册验证错误',
    '0039':'请求方法错误',
    '0040':'用户在其它地方登录',
    '0041':'存储用户身份证号失败',
    '0042':'绑定加油卡失败',
    '0043':'请先办理虚拟卡业务',
    '0044':'查询绑定卡失败',
    '0045':'查询公司失败',
    '0046':'验证用户和卡关联信息失败',
    '0047':'解除卡绑定失败',
        }
    },

]
