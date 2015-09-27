var api_data = [

    // 多媒体服务器 -> GAdvertise接口: 登录
    {
        "name": "登录",
        "url": "https://www.zcdata.com.cn/gadvertise/api",
        "method": "POST",
        "params": {
	    	"action": "login",
	    	"data": {
			"name": "gilbarco",
	        	"password": "pku123"
	    	}
        },
        "response": {
            "info": "OK",
            "ret": "0",
	    "session_id": "82jsdjs823kjhsdkjDSASDaB"
        },
        "note": {
	    "注释": "必须先登录GAdvertise接口才能执行后续命令",
            "info": "请求成功或者失败的信息",
            "ret": "0表示成功,1表示密码或帐号错误，2表示服务不可用",
	    "session_id": "本次会话后续请求的ID, 超过30分钟未基于此ID发起请求则ID失效，以后需要重新登录"
        }
    },

    // 多媒体服务器 -> GAdvertise接口: 注销
    {
        "name": "注销",
        "url": "https://www.zcdata.com.cn/gadvertise/api",
        "method": "POST",
        "params": {
	    	"action": "logout",
	    	"data": {
	    		"session_id": "82jsdjs823kjhsdkjDSASDaB"
	    	}
        },
        "response": {
            "info": "OK",
            "ret": "0"
        },
        "note": {
	    "注释": "从GAdvertise接口注销，或者草果30分钟没有请求会自动注销",
            "info": "请求成功或者失败的信息",
            "ret": "0表示成功,1表示未登录和非法"
        }
    },


    // 多媒体服务器 -> GAdvertise接口: 清除便利店商品信息
    {
        "name": "清除",
        "url": "https://www.zcdata.com.cn/gadvertise/api",
        "method": "POST",
        "params": {
	    	"action": "clear",
	    	"data": {
	    		"session_id": "82jsdjs823kjhsdkjDSASDaB",
	    		"station_name": "中石油吉林普庆站",
	    		"station_id": "ksjhdjk23i4782893rjkklsdjfk",
	    	}
        },
        "response": {
            "info": "OK",
            "ret": "0"
        },
        "note": {
	    "注释": "清除所有的便利店商品信息，用于便利店商品信息初始化",
            "info": "请求成功或者失败的信息",
            "station_name": "油站的名称",
            "station_id": "油站的ID",
            "ret": "0表示成功,1表示未登录和非法,2表示数据格式错误,3表示不存在站点名称或ID",
        }
    },


    // 多媒体服务器 -> GAdvertise接口: 同步便利店商品信息
    {
        "name": "同步",
        "url": "https://www.zcdata.com.cn/gadvertise/api",
        "method": "POST",
        "params": {
	    	"action": "sync",
	    	"data": {
	    		"session_id": "82jsdjs823kjhsdkjDSASDaB",
	    		"station_name": "中石油吉林普庆站",
	    		"station_id": "ksjhdjk23i4782893rjkklsdjfk",
			"items": [
			   {
	    			"name": "康师傅方便面四桶装",
	    			"id": "hsshds323isdsdieiw923498324joisdjkksA",
				"category":"食品",
				"brand":"康师傅",
				"description":"康师傅方便面卖的最火的一种",
				"info":"此处为附加信息，保留字段"
			   },
			   {	
	    			"name": "统一酸辣面",
	    			"id": "989sdjhsdsdieiw923498324joisdjkksA",
				"category":"食品",
				"brand":"统一",
				"description":"另一种方便面",
				"info":"此处为附加信息，保留字段"
			   },
			   {
	    			"name": "飞利浦五号电池",
	    			"id": "87239482374SDFSDF23498324joisdjkksA",
				"category":"电池",
				"brand":"飞利浦",
				"description":"卖的最好的一款电池",
				"info":"此处为附加信息，保留字段"
			   }
			]
	    	}

        },
        "response": {
            "info": "OK",
            "ret": "0"
        },
        "note": {
	    "注释":"同步便利店的商品信息到GAdvertise，此命令可以反复多次调用，相同名称的商品信息将会被后面的同名信息覆盖",
            "info": "请求成功或者失败的信息",
            "ret": "0表示成功,,1表示未登录和非法,2表示数据格式错误,3表示不存在站点名称或ID",
	    "items": "在售的商品列表",
	    "name": "商品的全名，也就是现在小票上打印的全名",
	    "id": "商品的ID，建议采取name的SHA1值作为ID，亦可采取其它值",
	    "category": "商品的种类",
	    "brand": "商品的品牌",
	    "description": "商品的描述信息文本",
            "station_name": "油站的名称",
            "station_id": "油站的ID",
	    "info": "保留字段，将来扩展使用"
        }
    },

    // 多媒体服务器 -> GAdvertise接口：根据卡号查询相关的广告
    {
        "name": "查询",
        "url": "https://www.zcdata.com.cn/gadvertise/api",
        "method": "POST",
        "params": {
            "action":"query",
            "data":{
	    	"session_id": "82jsdjs823kjhsdkjDSASDaB",
	   	"station_name": "中石油吉林普庆站",
	    	"station_id": "ksjhdjk23i4782893rjkklsdjfk",
		"object_value":"873931819999122",
		"object_type":"0",
		"period":"0"
            }

        },
        "response": {
            "info": "OK",
            "ret": "0",
	    "item_name": "康师傅方便面四桶装",
	    "item_id": "hsshds323isdsdieiw923498324joisdjkksA"
        },
        "note": {
	    "注释": "输入用户的卡号等标记身份信息，返回最适合为其播放的广告的商品ID",
            "info": "请求成功或者失败的信息",
            "ret": "0表示成功,,1表示未登录和非法,2表示数据格式错误,3表示不存在卡号等身份信息",
	    "object_value" : "查询对象的值，比如卡号",
	    "object_type" : "查询对象的类型，0为卡号，1为用户姓名，2为手机号，3为IMEI码",
	    "period": "0表示加油中等待时，1表示加油前准备时, 2表示加油后收款结束时",
	    "item_name": "广告商品的名字（由多媒体服务器同步时提供）",
	    "item_id": "广告商品的ID（由多媒体服务器同步时提供）",
            "station_name": "油站的名称",
            "station_id": "油站的ID",
        }
    },

   // 多媒体服务器 -> GAdvertise接口：写回油枪油机上记录的用户使用信息
    {
        "name": "写回",
        "url": "https://www.zcdata.com.cn/gadvertise/api",
        "method": "POST",
        "params": {
            "action":"notify",
            "data":{
	    	"session_id": "82jsdjs823kjhsdkjDSASDaB",
	   	"station_name": "中石油吉林普庆站",
	    	"station_id": "ksjhdjk23i4782893rjkklsdjfk",
		"actions" : [
		   {
			"object_type":"0",
			"object_value":"87681121132323",
			"action_type":"0",
			"item_amount":"3",
			"item_subtotal":"12.00",
	    		"item_name": "康师傅方便面四桶装",
	    		"item_id": "hsshds323isdsdieiw923498324joisdjkksA",
			"action_time":"2006-04-17 21:22:48"
		   },
		   {
			"object_type":"0",
			"object_value":"87681121132323",
			"action_type":"0",
			"item_amount":"30",
			"item_subtotal":"500.00",
	    		"item_name": "93#汽油",
	    		"item_id": "ansmasassdsdieiw923498324joisdjkksA",
			"action_time":"2006-04-17 21:22:48"
		   },
		   {
			"object_type":"2",
			"object_value":"13520245986",
			"action_type":"1",
	    		"item_name": "康师傅方便面四桶装",
	    		"item_id": "hsshds323isdsdieiw923498324joisdjkksA",
			"action_time":"2008-05-17 21:22:48"
		   }
		]
            }
        },
        "response": {
            "info": "OK",
            "ret": "0"
        },
        "note": {
	    "注释":"将加油机经由多媒体服务器暂存的用户消费和行为数据传回GAdvertise接口",
            "info": "请求成功或者失败的信息",
            "ret": "0表示成功,,1表示未登录和非法,2表示数据格式错误,3表示不存在站点名称或ID",
	    "object_value" : "查询对象的值，比如卡号",
	    "object_type" : "查询对象的类型，0为卡号，1为用户姓名，2为手机号，3为IMEI码",
	    "action_type": "0表示购买，1表示点击查看了广告详情但未购买",
	    "item_name": "相关商品的名字",
	    "item_id": "相关商品的ID",
   	    "item_amount":"购买数量，可选字段",
	    "item_subtotal":"购买金额，可选字段",
            "station_name": "油站的名称",
            "station_id": "油站的ID",
        }
    },

]
