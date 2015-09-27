#coding=utf-8

#积分管理setting文件,据此计算用户等级,用户积分变化
#通用积分规则
class DEFAULT :
	#用户等级配置
	USER_INTEGRAL_LEVEL = [
		{"level_type":0,"level_rule":[0,0]},
		{"level_type":1,"level_rule":[1,1000]},
		{"level_type":2,"level_rule":[1001,2000]},
		{"level_type":3,"level_rule":[2001,3000]},
		{"level_type":4,"level_rule":[3001,4000]},
		{"level_type":5,"level_rule":[4001,1000000]},
	]
	#积分变化规则设置
	#消费1元得1积分
	INTEGRAL_CHANGE = {
		"user_score_change" : {
				USER_INTEGRAL_LEVEL[0]['level_type']:0,
				USER_INTEGRAL_LEVEL[1]['level_type']:1,
				USER_INTEGRAL_LEVEL[2]['level_type']:2,
				USER_INTEGRAL_LEVEL[3]['level_type']:3,
				USER_INTEGRAL_LEVEL[4]['level_type']:4,
				USER_INTEGRAL_LEVEL[5]['level_type']:5,
				},
		'good_score_change' : {
				"default" : 1
		}
	}
		
#会员积分规则
class RULE1 :
	#会员等级配置
	NON_MEMBER = 0
	ORDINARY_MEMBER = 1
	GOLD_MEMBER = 2
	#积分变化规则设置
	INTEGRAL_CHANGE = {
		"user_type" : {ORDINARY_MEMBER:"普通会员",GOLD_MEMBER:"金卡会员"},
		"score_change" : {NON_MEMBER:0,ORDINARY_MEMBER:1,GOLD_MEMBER:2}
	}
	#油品类型
	GASOLINE = 0
	DIESEL = 1
	#用户等级规则设置
	USER_INTEGRAL_LEVEL = {
		"fuel_type" : {GASOLINE:"汽油",DIESEL:"柴油"},
		"rule":{GASOLINE:500,DIESEL:3000}

	}

#积分方案
INTEGRAL_OPTION = {
	"0000" : DEFAULT,
	"0001": RULE1
}

#配置积分方案
USE_OPTION = "0000"

