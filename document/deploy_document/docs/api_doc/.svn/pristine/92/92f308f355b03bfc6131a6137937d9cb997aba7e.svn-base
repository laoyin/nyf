var api_data = [

    // 注册
    {
        "name": "注册",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
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
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action":"login",
            "data":{
                "username": "15804604064",
                "password": "user122"
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
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
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
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
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

   //喊一嗓子模块
    {
        "name": "喊一嗓子模块--",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "Shouted_other",
            "data": {

              "content":"附近的的4s店在哪里",
              "longitude":114.12313,
              "latitude":34.328,
              "author_sha1":"发布者的sha1", 
          },
        },
        "response": {
            "info": "OK",
            "ret": "0001",
            "data":{
            
          
            }
         
        },
        "note": {
            "请求参数":"-------------",
            "content":"消息的内容信息",
           "longitude":"double 类型 经度",
           "latitude":"double 类型  纬度",
           "author_sha1":"发布者的sha1",

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             
        }
    },
    //道路信息
    {
        "name": "--道路信息--",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "Shouted_roadMessage",
            "data": {

                "RoadMessage":"此处现在 比较拥堵，看到的朋友 绕行",
                "author_sha1":"发布者的sha1",
                "longitude":114.12313,
                "latitude":34.328,

                 "pic_list":[
                 {
                "type":1,
                "content":"图片的二进制内容",
                "file_size":3212,
                "name":"图片名称",
                },
                { "type":1,
                "content":"图片的二进制内容",
                "file_size":3212,
                "name":"图片名称",
                }
                 ]
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
            "RoadMessage":"道路信息的内容",
            "author_sha1":"发布者的sha1",
            "longitude":"double 类型 经度",
            "latitude":"double  类型 纬度",
            "pic_list":"图片的列表",
            "type":"int 类型 0 为File, 1为Image",
            "content":"图片的二进制内容",
            "file_size":"int  大小",
            "name":"图片名称",

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             
        }
    },
    //故障求助
      {
        "name": "--故障求助--",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "Shouted_ForHelp",
            "data": {
                "phoneNo":"15804604064",
                "RoadMessage":"车轮胎坏了，求帮助",
                "author_sha1":"发布者的sha1",
                "longitude":114.12313,
                "latitude":34.328,

                 "pic_list":[
                 {
                "type":1,
                "content":"图片的二进制内容",
                "file_size":3212,
                "name":"图片名称",
                },
                { "type":1,
                "content":"图片的二进制内容",
                "file_size":3212,
                "name":"图片名称",
                }
                 ]
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
            "phoneNo":"电话号码",
             "RoadMessage":"道路信息的内容",
            "author_sha1":"发布者的sha1",
            "longitude":"double 类型 经度",
            "latitude":"double  类型 纬度",
            "pic_list":"图片的列表",
            "type":"int 类型 0 为File, 1为Image",
            "content":"图片的二进制内容",
            "file_size":"int  大小",
            "name":"图片名称",

           

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             
        }
    },
     //发货运货
      {
        "name": "--发货运货--",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "Shouted_sendORacceptGoods",
            "data": {
                "content":"想发3吨的大米",
                "start_address":"北京海淀区",
                "end_address":"山东青岛",
                "time":"20150503",
                "phoneNo":"15804604064",
                "author_sha1":"用户的sha1",
            
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
            "content":"发货的内容",
            "start_address":"出发的地点",
            "end_address":"货物要到达的终点",
            "time":"时间",
            "phoneNo":"电话号码",
            "author_sha1":"用户的sha1",


            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             
        }
    },
     //拼车搭伙
      {
        "name": "--拼车搭伙--",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "Shouted_carPooling",
            "data": {
              "start_address":"北京海淀区",
                "end_address":"山东青岛",
                "time":"20150503",
                "phoneNo":"15804604064",
                "author_sha1":"用户的sha1",
                "longitude":"124.33",
                "latitude":"42.22",
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
              "content":"发货的内容",
            "start_address":"出发的地点",
            "end_address":"货物要到达的终点",
            "time":"时间",
            "author_sha1":"用户的sha1",
           

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             
        }
    },
      //消费点评
      {
        "name": "--消费点评 --待完善",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "Shouted_other",
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
      //消费点评 发送页面
      {
        "name": "--消费点评 发送页面--",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "Shouted_reviews",

            "data": {
                "content":"这家店挺不错的",
                "longitude":"126.333",
                "latitude":"46.22",
                  "pic_list":[
                 {
                "type":1,
                "content":"图片的二进制内容",
                "file_size":3212,
                "name":"图片名称",
                },
                { "type":1,
                "content":"图片的二进制内容",
                "file_size":3212,
                "name":"图片名称",
                }
                 ]
            
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
            
                "content":"发布的内容",
                "pic_list":"放照片的 数组",
                "type":"int 照片类型",
                "content":"图片的二进制内容",
                "file_size":"int 照片的大小",
                "name":"图片名称",
             

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             
        }
    },
        //求荐服务
      {
        "name": "--求荐服务 --",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "Shouted_oRecommended",
            "data": {
            "longitude":114.328,
            "latitude":34.87,
            "content":"附近有什么好的餐馆",
            "author_sha1":"用户的sha1",
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
            "longitude":"double 经度",
            "latitude":"double 纬度 ",
            "content":"发送的内容",
             "author_sha1":"用户的sha1",

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             
        }
    },
          //语音上传
      {
        "name": "--语音上传 --",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "send_voiceFile",
            "data": {
                "name":"语音名字",
                "content":"语音的二进制文件",
                "author_sha1":"发布者的 sha1",
                "file_size":3223,
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
                 "name":"语音名字",
                "content":"语音的二进制文件",
                "author_sha1":"发布者的 sha1",
                "file_size":"(int) 文件大小 ",
           

            "返回参数":"-------------",
            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
             
        }
    },
    // 消息盒子 模块
    {
        "name": "消息盒子 模块",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
        "method": "POST",
        "params": {
            "action": "myMessagesBox",
	    "data": {
	        "user_sha1": "45838696b0720a6cd56ab854d2724e413b77b4ca",
            "Messagetype":"1",
	        "start": 0,
	        "end": 2
	    }

        },
        "response": {
            "info": "OK",
            "ret": "0001",
    	    "data":  {
                "has_next": "true",
                "message_list":[
        		{
        		    
        		    "sha1": "91db1f9bb11a751708a349b535998c65f3fd3554",
        		    "career": "其他",
        		    "author_sha1": "f08cc249a377bf89153366e252a7b84d66702d2a",
        	 	    "message_type": "求鉴服务",
        		    "time": "11:22:20",
        		    "parent_sha1": "",
        		    "root_sha1": "",
        		    "address": "北京市海淀区清河南镇",
        		    "body": "附近哪有4s店和好吃的餐馆",
        		    "attachment_info": {
                        "type":0,
                        "content":"语音的二进制文件",
                        "file_size": 3223,

                    }
        	    },
        		{
        		    "sha1": "8fd4992f19bbcb22a73429145296c84633c38258",
        		    "career": "司机",
        		    "author_sha1": "f08cc249a377bf89153366e252a7b84d66702d2a",
        	 	    "message_type": "发货运货",
        		    "time": "08:12:23",
        		    "parent_sha1": "",
        		    "root_sha1": "",
        		    "address": "南平市清城县",
        		    "body": "本人运送果蔬,从北京到青岛,还能运送3吨,电话:18622345678",
        		    "attachment_info": {
                          "type":1,
                          "img_sha1":"img_sha1",
                         "file_size": 3223,
                    }
        	    }

        	    ],
            },
        },
        "note": {
            "请求参数":"------",
             "user_sha1": "用户的sha1",
             "Messagetype":"发送请求获取消息的 类型 1:是我发布的消息 2:我接收到的消息",
            "start": "请求的开始标识",
            "end": "请求结束的标示符",

            "返回参数":"------",

            "info": "请求成功或者失败的信息",
            "ret": "代表请求的信息一些标识",
            "has_next": "是否还有更多消息",
    	    "receive_message_list": "我所有接收消息的列表",

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
            "type":"int 类型    0 ：为语音，1：为 图片",
            "content":"语音的二进制文件",
            "img_sha1":"img_sha1 通过 该sha1 可以获取图片新消息",
            "file_size": "文件的大小",
    	    
        }
    },

 
 
  
  
//状态码  
    {
        "name": "状态码（需要服务器端人员添加）",
        "url": "http://wheel.marketcloud.com.cn/gcustomer/shout_api",
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

