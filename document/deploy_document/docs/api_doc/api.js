var api_data = [

    // 注册
    {
        "name": "注册",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    	"action": "register",
    	    "data": {
    		    "name": "15804604064",
    	        "password": "user123",
    	        "nick": "user1",
    	        "career": "其他",
    	        "avarta_sha1": ""
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
            "nick": "昵称",
            "career": "职业",
            "avarta_sha1": "用户头像 没有则传空",
            "返回参数":"-------------",

            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识"
        }
    },

    // 登录
    {
        "name": "登录",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action":"login",
            "data":{
                "username": "15804604064",
                "password": "user123"
            }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data": {
    	    	"user_sha1": "0a0f8c22a861231aff038b16d84c9a4ae175083e",
    	    	"user_name": "15804604064",
                            "avarta_sha1":"0a0f8c22a861231aff038b16d84c9a4ae175083e",
                            "nick":"lilei",
                            "score":323,
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
            "session_id": "用户session——id"
        }
    },

    // 匿名登录
    {
        "name": "匿名登录",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action":"anonymous_login",
            "data":{
                "imei_code": "15804604064",
                "mac_address": "aaa:bbb",
        	 	"sim_number": "16768279",
        		"device_type": "iphone4"
            }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data": {
                "session_id": "sdfsdfsdfgdgsdfsdaff038b16d84c9a4ae17wsede"
             },
         },
        "note": {
            "请求参数":"-------------",

            "imei_code": "序列号 ",
            "mac_address": "Mac地址",
            "sim_number": "手机号",
            "device_type": "设备名称",
            "说明":"如果手机端获取不到这些信息 就传空值 ",
            "返回参数":"-------------",
            
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            "session_id": "用户session——id",
        }
    },

    // 登出
    {
        "name": "登出",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "logout",
            "data":{
               "session_id": "sdfsdfsdfgdgsdfsdaff038b16d84c9a4ae17wsede"
            },
            
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data": {
             },
         },
        "note": {
            "请求参数":"-------------",
            "session_id": "用户session——id",
            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
        }
    },

    //获取附近油站
    {
        "name": "获取附近油站",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "get_near_by_station_sha1s",
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
                "0fd21fdc35a001d3708f43765021f24e28078b34",
                "2112978c7ada9865f798631731e9ab7fae302433"
            ]
        }
	    
        },
        "note": {
            "请求参数":"-------------",
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
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "get_near_by_station",
	    "data": {
            "longitude": 123.384,
                "latitude": 41.8,
		"sha1s":[
			     "0fd21fdc35a001d3708f43765021f24e28078b34",
                  "2112978c7ada9865f798631731e9ab7fae302433", 
                  "565680f7bb3d0a8dd8d716d1a9c1d4d753e3f9a4", 
                  "71ae9117340af6634dd944cf63f5f09d26a3bd94", 
                  "7eaab8bac180a2a9af70868600f98e46568b0019", 
                  "ac407a93905aeb5e47e4fbb5e3fd55d87437ad6e", 
                  "af45eac0a8dd5540227056ff392f0c3f922feebd", 
                  "b23b0df43074dc420d0cb5085d57fdbd37c1e99b", 
                  "cb04edfbe0573136b3e8a8de7ed77a1ef62bf91e",
                   "e08ed03d8f17acaf3f5b82401fecdb8181358700"
		 ]
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
                    	    "site_img": "",
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
                    	    "site_img": "",
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

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
    	    "detail_list": "所有油站的详细信息",
    	    "site_name": "油站的名字",
    	    "site_sha1": "油站的sha1",
            "site_img": "油站logo",
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
	    "count":"评价人数（int）"
            
        }
    },
    //获取商品优惠
    {
        "name": "获取商品优惠",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "get_goods_list_sha1s",
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
               "9f8df847542d36947b1be0b2c411760385020af8",
                    "f4fbb12da9ddc147011d34d27448c627bdd52590"
            ]

            }
    	 
        },
        "note": {
            "请求参数":"-------------",

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
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "get_goods_list",
    	    "data": {
                "longitude": 123.384,
                "latitude": 41.8,
    		"sha1s":[
    			    "9f8df847542d36947b1be0b2c411760385020af8",
    			    "f4fbb12da9ddc147011d34d27448c627bdd52590"
    		 ]
            }   

        },
        "response": {
            "info": "OK",
            "ret": "0001",
    	    
    	    "data": {
              "has_next": "true",  
              "goods_list":[
                    {
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
                        "img": ""
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
                        "img": ""
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


   //喊一嗓子模块
    {
        "name": "喊一嗓子模块--待完善",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "",
            "data": {
              
            }
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
            
          
            }
         
        },
        "note": {
            "请求参数":"-------------",

           

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            
        }
    },
    // 我接收到的消息
    {
        "name": "我接收到的消息",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "my_received_messages",
	    "data": {
	        "user_sha1": "45838696b0720a6cd56ab854d2724e413b77b4ca",
	        "start": 0,
	        "end": 2
	    }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
    	    "data":  {
                "has_next": "true",
                "receive_message_list":[
        		{
        		    "title": "附近哪有4s店和好吃的餐馆",
        		    "sha1": "91db1f9bb11a751708a349b535998c65f3fd3554",
        		    "career": "其他",
        		    "author_sha1": "f08cc249a377bf89153366e252a7b84d66702d2a",
        	 	    "message_type": "求鉴服务",
        		    "time": "11:22:20",
        		    "parent_sha1": "",
        		    "root_sha1": "",
        		    "address": "北京市海淀区清河南镇",
        		    "body": "附近哪有4s店和好吃的餐馆",
        		    "attachment_info": {}
        	        },
        		{
        		    "title": "运货发布",
        		    "sha1": "8fd4992f19bbcb22a73429145296c84633c38258",
        		    "career": "司机",
        		    "author_sha1": "f08cc249a377bf89153366e252a7b84d66702d2a",
        	 	    "message_type": "发货运货",
        		    "time": "08:12:23",
        		    "parent_sha1": "",
        		    "root_sha1": "",
        		    "address": "南平市清城县",
        		    "body": "本人运送果蔬,从北京到青岛,还能运送3吨,电话:18622345678",
        		    "attachment_info": {}
        	        }

        	    ],
            },
        },
        "note": {
            "请求参数":"------",
             "user_sha1": "用户的sha1",
            "start": "请求的开始标识",
            "end": "请求结束的标示符",

            "返回参数":"------",

            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            "has_next": "是否还有更多消息",
    	    "receive_message_list": "我所有接收消息的列表",

    	    "title": "消息的标题",
    	    "sha1": "消息的sha1",
    	    "career": "作者的职业",
    	    "author_sha1": "作者的sha1",
    	    "message_type": "消息类型",
    	    "time": "发布时间",
    	    "parent_sha1": "父亲消息的SHA1",
    	    "root_sha1": "主贴sha1",
    	    "address": "发布消息的地址",
    	    "body": "消息的详细内容",
    	    "attachment_info": "图片或语音消息",
    	    
        }
    },

    // 我发布的消息
    {
        "name": "我发布的消息",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "my_released_messages",
	    "data": {
	        "user_sha1": "45838696b0720a6cd56ab854d2724e413b77b4ca",
	        "start": 0,
	        "end": 2
	    }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
	    
	    "data":  {
            "has_next": "true",
            "post_message_list":[
    		{
    		    "title": "哪里有免费停车场",
    		    "sha1": "f4df897e7d282aa259bf1fdbb6ea43d7d3be7fb8",
    	 	    "message_type": "求鉴服务",
    		    "time": "11:22:20",
    		    "parent_sha1": "",
    		    "root_sha1": "",
    		    "address": "北京市海淀区清河南镇",
    		    "body": "附近哪有免费停车场",
    		    "attachment_info": {}
    	       },
    		{
    		    "title": "运货发布",
    		    "sha1": "8fd4992f19bbcb22a73429145296c84633c38258",
    	 	    "message_type": "发货运货",
    		    "time": "08:12:23",
    		    "parent_sha1": "",
    		    "root_sha1": "",
    		    "address": "南平市清城县",
    		    "body": "本人运送果蔬,从北京到青岛,还能运送3吨,电话:18622345678",
    		    "attachment_info": {}
    	        }

    	    ],
        },
        },
        "note": {
            "请求参数":"------",
             "user_sha1": "用户的sha1",
            "start": "请求的开始标识",
            "end": "请求结束的标示符",

            "返回参数":"------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
    	    "data": "所有发布消息的列表",
            "has_next": "是否还有更多消息",

    	    "title": "消息的标题",
    	    "sha1": "消息的sha1",
    	    "message_type": "消息类型",
    	    "time": "发布时间",
    	    "parent_sha1": "父亲消息的SHA1",
    	    "root_sha1": "主贴sha1",
    	    "address": "发布消息的地址",
    	    "body": "消息的详细内容",
    	    "attachment_info": "图片或语音消息",
    	    
        }
    },
  //获取可积分兑换商品
    {
    "name": "获取可积分兑换商品",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        "action": "get_integral_list_sha1",
        "data": {
            "user_sha1": "2772e37782fbd396fa7b98ea5a3c182bca35e8bc",
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
               "9f8df847542d36947b1be0b2c411760385020af8",
                    "f4fbb12da9ddc147011d34d27448c627bdd52590"
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
      //获取积分商城商品详情
    {
        "name": "获取积分商城商品详情 --待完善",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action": "get_integral_list",
            "data": {
                "longitude": 123.384,
                "latitude": 41.8,
                "sha1s":[
                    "9f8df847542d36947b1be0b2c411760385020af8",
                    "f4fbb12da9ddc147011d34d27448c627bdd52590"
                 ]
                }
            }
        ,
        "response": {
            "info": "OK",
            "ret": "0001",
          "data":{
                "integral_list":[
                    {
                        "img":"图片信息1",
                        "goods_name": "商品名称1",
                        "sha1": "商品sha1",
                        "score":"积分1",
                        "history":"2",  
                        "store_sha1":"商家sha1"
                     },
                    {
                        "img":"图片信息2",
                        "goods_name": "商品名称2",
                        "sha1": "商品sha1",
                        "score":"积分2",
                        "history":"2",
                        "store_sha1":"商家sha1"
                    }
                ]
          
        }
    },
        "note": {

            "请求参数":"-----",
            
             "返回参数":"-----",

            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            
        }
    },
    //获取车后服务
    {
        "name": "获取车后服务",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
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
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
            "action":"get_service_list",
            "data":{
                "longitude": 123.384,
                "latitude": 41.8,
                "sha1s":[
    			  "16cb6d96c4cc1086570efbd190f71aba9134020c",
                    "ef052473d5ed6e4893985386be65cd3d962659ad"
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
    			"title":"洗车人家",
    			"item_img": "0032f190ee0a8b54983bc707d5c57a0a9d009596.jpg",
    			"score":3,
    			"comment_count":"173",
    			"discount_info": "折扣信息",
			"latitude": 41.2,
			"longitude": 123.1
                    },

                    {
    			"item_type": 1,
    			"sha1": "ef052473d5ed6e4893985386be65cd3d962659ad",
    			"discount_info": "",
    			"title":"丽车房汽车美容装饰(旗舰店)",
    			"item_img": "0032f190ee0a8b54983bc707d5c57a0a9d009596.jpg",
    			"score":0,
    			"comment_count":"0",
			"latitude": 41.2,
			"longitude": 123.1
                    },

                ],

            },

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
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
	    "action": "comment_item",
	    "data": {
    		"user_sha1": "d86fac45316224179f577439ff3e6905d72fe2ab",
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
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
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

  
  
        
    {
        "name": "状态码（需要服务器端人员添加）",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/api",
        "method": "POST",
        "params": {
        
       },
        "response": {
               SUCCESS: "0001",
               USER_EXCPTION: {
                  USERNOTEXIST: "0002",
                  PASSWORD_ERROR: "0003",
                  NAMEEXISTED: "0006"
               },
            },
        "note": {
            '0001' : '成功',
            '0002' : '用户不存在',
            '0003' : '密码错误',
            '0004':'评论失败，没有权限',
            '0005':'已评论',
            '0006':'用户已存在',
            '0007' : '暂无数据',
            '0008' : '没有更多数据',
            '1111' : 'An error has occurred.'

        }
    },


]
