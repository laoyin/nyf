#-*- coding: utf-8 -*-
from sqlalchemy import (Column, Integer, BigInteger, Numeric, SmallInteger,
                        Float, String, DateTime, ForeignKey,UniqueConstraint,TEXT)
from sqlalchemy.types import LargeBinary
from dash.core.backends.sql import models as dash_models
from django.utils.translation import ugettext_lazy
from dash.core.types import enum
import datetime
from django.db import models

#每个加油站属于下面大集团公司的一种
UserCardType = enum(
    #中石油
    CNPC=(1,ugettext_lazy(u"中石油")),
    #中石化
    SINOPEC=(2,ugettext_lazy(u"中石化")),
    #中海油
    CNOOC=(3,ugettext_lazy(u"中海油")),
    #壳牌
    SHELL=(4,ugettext_lazy(u"壳牌")),
    #中化
    SINOCHEM=(5,ugettext_lazy(u"中化"))
)

PromotionModelType = enum(
    # 以改善油站的 设备运营效率为目的（结合用户的属性让某些用户在效率低的时候来加油）
    IMPROVE_EFFICT=(0,ugettext_lazy(u"改善运营效率")),
    # """
    # 监测到你经常于高峰期时段加油，为了节约你的加油时间，请于（非高峰期时间段）来加油。
    # """

    # 以增加非忠诚 用户回头率为目的（用户的加油时间间隔太长）
    # 以改善加油用 户流失率为目的（用户一段时间后不来了，要发短信给其油品的优惠）
    INCREASE_LOYALTY=(1,ugettext_lazy(u"油品优惠")),
    # """
    # 监测到你加油间隔太长，油品优惠哦，快来。
    # """

    # 以解决用户体 验和增加非油品销售额为目的（短信告知其最可能买的商品热销，在某时段内买多就特价）
    # 以快推热销商 品和增加非油品销售额为目的（发短信告知频繁购买该商品的用户买的更多还有优惠特价）
    # 以清仓滞销非 油品为目的（以较大优惠推广到那些买过的，和有可能买的用户）
    IMPROVE_NONE_FUEL_SALES=(2,ugettext_lazy(u"非油品优惠")),
    # """
    # 监测到你最有可能买的非油品商品符合当前搞活动的商品，请来买一些。
    # """

    # 以提高换枪率 为目的，也即加满率其实不好（短信告知与其经常加油量相关的何种定额将会有优惠）
    IMPROVE_GUN_EFFICIENCY=(3,ugettext_lazy(u"定额优惠")),
    # """
    # 监测到你喜欢加满，来加定额吧，有优惠。
    # """

    # 以表彰忠诚用 户为目的（买的越多加的越多价格越便宜，无论是油品还是非油品）
    COMMEND_LOYALTY=(4,ugettext_lazy(u"忠诚客户优惠")),
    # """
    # 监测到你经常来，是忠诚客户，我们这里有活动仅限忠诚客户
    # """
)

#主键
class GCustomerBaseModel(object):
    id = Column(BigInteger, primary_key=True)

class DimChinaProvinceCityDistrict(dash_models.Base,GCustomerBaseModel):
    """
    中国三级行政区划
    省市区/县
    """
    __tablename__ = 'gcustomer_dim_chinaprovincecitydistrict'

    #名称
    name=Column(String(256), nullable=False, index=True)

    #级别
    level=Column(Integer, nullable=False, index=True)

    #上级代码
    parent=Column(Integer, nullable=False, index=True)

#gcustomer公司用户管理
class GCompany(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_company'

    #石油公司类型：中石化，中石油，中海油等，在此大公司下加油卡唯一，对应于上面的CardType
    user_source = Column(Integer,nullable=False,default=1)

    #公司名
    name = Column(String(255),nullable=False)

    #sha1
    sha1 = Column(String(40),nullable=False,default="")

    #支付信息: json格式，存储公司接收付款的支付手段
    payment_info= Column(TEXT,nullable=False,default="{}")

    #联系电话
    phone = Column(String(255),default="")

    #地址
    address = Column(String(255),default="")

    #注册时间
    time = Column(DateTime,nullable=False,default=datetime.datetime.now())

    __table_args__ = ( UniqueConstraint("user_source","name"), )

#公司用户关系
class  GCompanyMembership(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_company_membership'

    #公司id
    comp_id = Column(Integer,nullable=False)

    #公司用户id
    user_id = Column(Integer,nullable=False)

    #用户角色 0:待审核 1:普通 2:管理员 
    role = Column(Integer,nullable=False,default=0)

    __table_args__ = ( UniqueConstraint("comp_id","user_id"),)

#GCustomer网站系统用户
class GCustomerUser(dash_models.Base,GCustomerBaseModel):

    __tablename__='gcustomer_user'

    #公司ID 0 :默认为系统用户的公司id
    comp_id = Column(Integer,nullable=False)

    name = Column(String(140), nullable=False)

    #注册时间
    time = Column(DateTime, nullable=False,default= datetime.datetime.now())

    #用户类型 4:super 3:公司用户 2:大客户  1:备用  0:未审核用户
    type = Column(SmallInteger, nullable=False)

    email = Column(String(140), nullable=False , unique=True)

    password = Column(String(32), nullable=False)

    #0:en 1:zh
    language = Column(SmallInteger,default=0)

    #第三级行政区划代码
    district = Column(Integer,nullable=False,default=110000)

    __table_args__ = ( UniqueConstraint("comp_id","name","email"),)

#营销目标人群，对每个人群都采取对应的查询条件生成，会相应采取不同的营销策略
class TargetAudience(dash_models.Base,GCustomerBaseModel):
    __tablename__='gcustomer_target_audience'

    #sha1
    sha1 = Column(String(40),nullable=False)

    #公司  例如中石化江苏公司与中石化南京公司可能同时使用系统开展营销
    comp_id = Column(Integer,nullable=False)

    #群的名称
    group_name=Column(String(256),nullable=False,index=True)

    #gcustomer操作帐号id，
    source_id=Column(Integer,nullable=False,index=True)

    #地理范围(对应于location中的字段)
    location=Column(String(256),nullable=False)

    #群的描述
    description=Column(TEXT, nullable=False, default='group description')

    #创建的时间
    time=Column(DateTime, nullable=False, index=True,default=datetime.datetime.now())

    #群组用户的职业类别司机、学生、白领、其他
    career = Column(String(256),nullable=True,default='')

    #群组用户的性别:0为男性,1为女性,-1为不限制性别
    gender = Column(SmallInteger)

    #群组用户的年龄段
    from_age=Column(SmallInteger)
    to_age=Column(SmallInteger)

    #群组用户的收入区间
    from_income=Column(SmallInteger)
    to_income=Column(SmallInteger)

    #群组用户的加满习惯 0:"无规律",1:"加满",2:"定额"，-1不限制
    prefer_pump_type = Column(String(255),default="")

    #消费金额倾向
    prefer_cost = Column(String(255),default="")

    ##群组用户的时间习惯 0:"无规律",1:"早上",2:"中午",3:"晚上",4:"午夜"
    prefer_time = Column(String(255),default="")

    #单次加油额
    prefer_fuel_cost = Column(String(255),default="")

    #非油品消费类型
    prefer_nonfuel_cost = Column(String(255),default="")

    #加油间隔
    pump_timeout = Column(String(255),default="")

    #描述
    description = Column(TEXT,nullable=False,default="")

    #喜爱商品列表
    favourite_products = Column(TEXT, nullable=False,default='[]')

    #群组用户的贡献
    from_contribution = Column(Float)
    to_contribution = Column(Float)

    #群组用户的积分
    from_score = Column(BigInteger)
    to_score = Column(BigInteger)

    #用户列表 CustomerAccount中的cardnum列表
    user_list = Column(TEXT, nullable=False,default='[]')

    __table_args__=( UniqueConstraint('comp_id','group_name'), )

# 站点
class Station(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_station'

    #公司ID
    comp_id = Column(Integer,nullable=False)

    #油站编码，此处与gflux系统的站点对应
    site_code = Column(String(255))

    #station的名字
    name=Column(String(255))

    #行政区划
    location = Column(TEXT,nullable=False,default='{"province":110000,"city":110100,"district":110101}')

    # 地图坐标，x经度，y纬度
    geo_x=Column(Float, nullable=False, default=0)
    geo_y=Column(Float, nullable=False, default=0)

    # 油站的平均评分:1,2,3,4,5
    comment_score=Column(Integer,nullable=False,default=3)

    #comment count
    comment_count = Column(Integer,nullable = False,default=0)

    # 油品类型
    fuel_type=Column(Integer,nullable=False,default=1)

    # 自助加油还是人工加油： 1 为人工，2为自助，3为两者皆有
    assist_type=Column(Integer,nullable=False,default=1)

    # 油站sha1: 由comp_id和name计算得到, 见utils中的compute_site_sha1
    sha1=Column(String(40),nullable=False,default='')

    #img_sha1
    img_sha1 = Column(String(40),nullable=False,default='')

    #油站电话
    site_tel=Column(String(20),nullable=False,default='')

    #详细地址
    address=Column(String(255),nullable=False,default='')

    __table_args__=( UniqueConstraint('comp_id','site_code'),)

# 站点画像
class StationProfile(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_station_profile'

    #公司ID
    station_id = Column(Integer,nullable=False,default=1)

    #分析目标Transaction的起始时间
    start_time=Column(DateTime, nullable=False, index=True)

    #分析目标Transaction的结束时间
    end_time=Column(DateTime, nullable=False, index=True)

    #总客户数
    nb_total_customers = Column(BigInteger, nullable=False, default=0)

    #总加油量(按照容积算)
    total_fuel_amount=Column(Float, nullable=False, default=0)

    #总销售金额
    total_sales_amount=Column(Float, nullable=False, default=0)

    #总非油品销售金额
    total_nonfuel_sales_amount=Column(Float, nullable=False, default=0)

    #油品销售额
    fuel_sales=Column(Float, nullable=False, default=0)

    #高峰期时间段，用于营销活动, json格式 : [[7,9],[15,17]]
    peak_range = Column(TEXT, nullable=False,default='')

    #排名前一百的大客户: 客户信息列表的json格式
    top_100_customers=Column(TEXT, nullable=False, default='[]')

    #在公司系统内的站点排名
    rank=Column(Integer,nullable=False,default=0)

    #排名前一百的非油品: 非油品信息列表的json格式 
    #type 0:油品 1:便利店商品 2:车后服务
    #[{"barcode":"600615","type":0},{"sha1":"kc7394lkjfdslfsfs",type:1}]
    top_100_goods=Column(TEXT, nullable=False, default='[]')

    #排名最后一百的非油品: 非油品信息列表的json格式
    bottom_100_goods=Column(TEXT, nullable=False, default='[]')

    #按照贡献值从大到小排序后的百分比对应值，比如缺省值中前20%的客户贡献了40%的销售额
    percent_dist=Column(TEXT, nullable=False, default='[(0.1,0.2),(0.2,0.4),(0.3,0.5)]')

    __table_args__=( UniqueConstraint('station_id',),)

# 管理员自己创建的油站群组
class StationGroup(dash_models.Base,GCustomerBaseModel):
    __tablename__='gcustomer_station_group'

    #公司ID
    comp_id = Column(Integer,nullable=False)

    #群组的名字
    group_name = Column(String(255))

    #管理员id
    admin_id = Column(Integer,nullable = False)

    #油站群组范围
    group_location =  Column(TEXT,nullable=False,default='{"province":110000,"city":110100,"district":110101}')

    #销售额
    total_sales_amount = Column(Float,nullable = Float,default = 0)

    #排名前多少
    rank = Column(Integer,nullable= False)

    #油站群描述
    group_info = Column(TEXT,default="")

    #油站群的油站列表 油站的sha1
    site_sha1_list = Column(TEXT,default="[]")

    #创建时间
    time=Column(DateTime, nullable=False,default=datetime.datetime.now())

    __table_args__=( UniqueConstraint('comp_id','group_name'), )


# 油站群组与油站的所属关系
class StationGroupMembership(dash_models.Base,GCustomerBaseModel):
    __tablename__='gcustomer_station_group_membership'

    #群组ID，指StationGroup中的id
    station_group_id=Column(Integer,nullable=False,index=True)

    #站点ID，指Station中的id
    site_id=Column(Integer,nullable=False)

    __table_args__=( UniqueConstraint('station_group_id','site_id'), )


# 虚拟加油卡账号,每个用户一张虚拟卡，可以和多个实体卡绑定
class CustomerAccount(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_app_account'

    #虚拟卡号,主键,唯一, 系统中的vcard_id都指此字段，而非自增长ID
    cardnum = Column(String(40),nullable=False)

    #用户登录密码  加密形式
    password = Column(String(255),nullable=False)

    #当前总余额
    balance = Column(Float,nullable=False,default=0.0)

    #累计总充值额
    total_charge_num = Column(Float,nullable=False,default=0.0)

    #用户身份证号，如果购买，需要填写，唯一
    id_card = Column(String(40),nullable=False,default="")

    #支付密码 加密形式
    pay_password = Column(String(40))

    #用户名，注册填写，检查唯一
    name=Column(String(40),nullable=False,default="")

    #注册时间
    time=Column(DateTime,nullable=False,default=datetime.datetime.now())

    #注册地址
    location = Column(Integer,default=110000)

    # 车牌号
    plate_no = Column(Numeric(20),nullable=False,index = True,default = 0)

    #用户性别 0:男 1:女
    gender = Column(Integer,nullable=False,default=0)

    #用户职业: 司机、学生、白领、其他
    career = Column(String(128),nullable=False,default="其他")

    #用户年龄
    age = Column(Integer,nullable=False,default=20)

    #头像字段: 指向FileImage的sha1字段
    avarta_sha1 = Column(String(40),nullable=False,default="")

    #累计积分
    all_score = Column(Integer,nullable=False,default=0)

    #当前积分
    score = Column(Integer,nullable=False,default=0)

    #根据用户累计积分计算等级   0:用户没有获得过任何积分  1:1星用户 2:2星用户 3:3星用户 4:4星用户 5:5星用户
    score_rank = Column(Integer,nullable=False,default=0)

    #昵称
    nick = Column(String(128))

    #支付信息: json格式，存储用户的支付手段
    payment_info = Column(TEXT,nullable=False,default="{}")

    #是否代表大客户 0:不是大客户 1:是大客户
    is_big_customer = Column(Integer,nullable=False,default=0)

    #是否是测试用户  0: 不是 1:是
    is_pay_in_advance = Column(Integer,nullable=False,default=0)

    __table_args__ = (UniqueConstraint("cardnum",),)

# 虚拟加油卡与石油公司的对应关系
class CustomerCompInfo(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_account_comp_info'

    #虚拟卡ID
    vcard_id = Column(String(40),nullable=False)

    #公司id，0表示志察数据
    comp_id = Column(Integer,nullable=False)

    #虚拟卡在此公司的充值余额
    balance = Column(Float,nullable=False,default=0.0)

    #虚拟卡在此公司的累计总充值额
    total_charge_num = Column(Float,nullable=False,default=0.0)

    #虚拟卡在此公司绑定的用户卡号,json格式，词典, 值为1表示主卡，为0表示副卡
    #[{"card_type": 0, "cardnum": "9130270000349240"}]
    card_list = Column(TEXT,nullable=False,default='[]')

    __table_args__ = ( UniqueConstraint("vcard_id","comp_id",),)

# 虚拟加油卡交易记录
class CustomerAccountTransaction(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_account_transaction'

    #虚拟卡id
    vcard_id = Column(String(40),nullable=False)

    #公司id: 0表示志察数据账号，否则表示具体公司的id
    comp_id = Column(Integer,nullable=False)

    #交易类型  0:充值  1:购买油品 2:购买非油品 3:购买车后服务 4:积分商城
    trans_type = Column(Integer,nullable=False)

    #油站id: 交易地点，交易类型非0需要指定
    station_sha1 = Column(String(40))

    #如果交易类型为油品则需指定油枪号
    pump_id = Column(Integer)

    #商品sha1
    item_sha1 = Column(String(40))

    #商品名称
    item_name = Column(String(255))

    #商品数量
    item_count = Column(Float)

    #交易时间
    time = Column(DateTime,nullable=False,default=datetime.datetime.now())

    # 交易的sha1 由交易信息和时间生成
    sha1 = Column(String(40),nullable=False)

    #便利店sha1
    seller_sha1 = Column(String(40))

    # 加油员的sha1
    worker_sha1 = Column(String(40))

    # 营销id
    promotion_id = Column(Integer)

    # 到账金额
    item_total = Column(Float,nullable=False,default=0.0)

    #订单状态  0 代表订单生成  1代表支付完成 2代表交易完成 3代表交易被收银员录入 
    #4商品预订状态  5 申请退款完成状态 6 工作人员完成退款  7 订单已过期
    status = Column(Integer,nullable=False)

    #第三方回调id
    sessionid = Column(String(255))

    #申请退款日期
    application_time = Column(DateTime)

    #退款成功时间
    success_time = Column(DateTime)

    class Meta:
        unique_together=('vcard_id','comp_id','time',)

#用户画像
class CustomerProfile(dash_models.Base,GCustomerBaseModel) :
    __tablename__ = 'gcustomer_user_profile'

    #虚拟卡id
    vcard_id = Column(String(40),nullable=False)

    # 0表示profileing_area是某个油站的名字，1表示是某个地域的名字(与location表格对应)
    area_type=Column(SmallInteger, nullable=False,default=1)

    # 用户画像可能分为站级和地域两种，针对某个油站进行分析，或者针对某个地区的所有油站进行分析
    profiling_area=Column(String(255),nullable=False,index=True,default='110000')

    # 价值贡献: 过去两年的消费总额
    contribution=Column(Float, nullable=False, default=0)

    #加油
    # 当前余额时间倾向
    #0  无
    #1  早
    #2  中
    #3  晚
    #4  夜
    prefer_time=Column(SmallInteger, nullable=False, index=True, default=0)

    #加满率
    #0  无
    #1  加满
    #2  定额
    prefer_pump_type=Column(SmallInteger, nullable=False, index=True, default=0)

    #加油额
    #0  无规律
    #1  加很多
    #2  加很少
    #3  一般
    prefer_fuel_cost=Column(SmallInteger, nullable=False, index=True, default=0)

    #非油品销售量
    #0  无规律
    #1  买很多
    #2  买很少
    #3  一般
    prefer_nonfuel_cost=Column(SmallInteger, nullable=False, index=True, default=0)

    #油品消费情况 存储油品的barcode list
    fuel_products=Column(TEXT, nullable=False, default='[]')

    #最喜爱的非油品商品列表
    favourite_nonfuel_products=Column(TEXT, nullable=False, default='')

    #最有可能再次买的非油品商品列表
    recommended_nonfuel_products=Column(TEXT, nullable=False, default='')

    #聚合情况
    grouped=Column(TEXT, nullable=False, default='')

    #平均加油间隔
    #平均间隔的天数
    avg_charge_period=Column(Integer, nullable=False, index=True,default=1)

    # 对油站的影响程度
    #0  无影响 1/3
    #1  一般   1/3-2/3
    #2  严重   2/3
    efficiency=Column(SmallInteger, nullable=False, index=True, default=0)

    #重要程度
    #打分0-100
    prominence=Column(SmallInteger, nullable=False, index=True, default=90)

    #壳牌用户累计会员等级用
    #贡献的汽油加油量
    total_fuel_amount_1 = Column(Float,nullable=False,default=0)
    #贡献的柴油量
    total_fuel_amount_2 = Column(Float,nullable=False,default=0)

    #贡献的加油量
    total_fuel_amount=Column(Float, nullable=False, default=0)

    #贡献的销售额
    total_purchase_amount=Column(Float, nullable=False, default=0)

    #贡献的非油品销售额
    total_nonfuel_purchase_amount=Column(Float, nullable=False, default=0)

    #用户最适合的促销模式
    best_promotion_mode=Column(SmallInteger, nullable=False, index=True, default=0)

    #是否是加油流失客户，'[]':非流失客户  '["station_sha1"]' : 某个站的流失客户
    is_oil_loss_customer = Column(TEXT, default='[]')

    __table_args__=( UniqueConstraint("vcard_id",), )

# 用户创建的优惠活动    __tablename__ = 'gcustomer_promotion'

class Promotion(dash_models.Base,GCustomerBaseModel) :
    __tablename__ = 'gcustomer_promotion'

    #公司
    comp_id = Column(Integer,nullable=False)

    #活动名称
    name=Column(String(255),nullable=False,index=True)

    #sha1
    sha1 = Column(String(40),nullable=False,default='')

    #gcustomer操作帐号id
    source_id=Column(Integer,nullable=False)

    # 优惠活动的开始时间
    start_time=Column(DateTime, nullable=False)

    # 优惠活动的截止时间
    end_time=Column(DateTime, nullable=False)

    #创建类型 0:传统手动创建 1:自动创建
    create_type = Column(Integer,nullable = False,default=0)

    #自动创建的情景
    # 0:表示手动创建，没有情景选择
    # 1:改善油站的设备运营效率
    # 2:增加非忠诚用户回头率
    # 3:改善加油用户流失率
    # 4:提高换枪率
    # 5:表彰忠诚用户
    # 6:清仓滞销非油品
    # 7:快推热销商品和增加非油品销售额
    auto_create_option = Column(Integer,nullable = False,default = 0)

    #活动范围: 地域或者油站群组
    area = Column(String(255))

    #油站群id
    station_group_id = Column(Integer)

    #0表示地域，1表示油站群组
    area_type=Column(SmallInteger, nullable=False, default=0)

    #触发类型: 0表示主动推送，1表示到站推送，2表示分享推送
    trigger_type=Column(SmallInteger, nullable=False, default=0)

    #目标用户群
    target_audience=Column(String(255), nullable=False)

    #沟通类型:0 是email, 1是短信，2是导出，3是直接邮递
    contact_approach = Column(Integer, nullable=False)

    #折扣信息
    discount_information=Column(TEXT)

    #折扣类型: 0是限时，1是限量，2是无折扣, 3是限时限量
    discount_type=Column(SmallInteger, nullable=False, default=0)

    #限时 0~23 表示一天24小时
    start = Column(Integer)
    finish = Column(Integer)

    #status
    #-1 还未开始
    #0  结束
    #1  正在进程中
    status=Column(SmallInteger, nullable=False, default=-1)

    #促销模式: 操作员出于什么目的来进行此次营销,对应于上述的PromotionModelType
    promotion_mode=Column(SmallInteger, nullable=False, default=0)

    #描述信息
    description=Column(TEXT, nullable=False,default='')

    #所发送优惠信息的主题
    subject=Column(TEXT, nullable=True, default='')

    #所发送优惠信息的名义发件人
    sender=Column(String(128), nullable=True, default='')

    #所发送优惠信息的模板: 0是简约，1是炫彩
    template_style=Column(SmallInteger, nullable=False, default=0)

    __table_args__=( UniqueConstraint('comp_id','name'), )

# 营销活动所有油品，非油品，车后服务的打折信息表
class PromotionInfo(dash_models.Base,GCustomerBaseModel) :
    __tablename__ = 'gcustomer_promotion_info'

    #上述Promotion表格的主键
    promotion_id=Column(BigInteger)

    # 活动推出商品的类型 0 油品，1 非油品，2车后服务
    promotion_type=Column(Integer, default=0)

    # 促销商品的id
    obj_id = Column(BigInteger,nullable=False, default=0)

    #油站代码，此处与gflux系统的站点对应
    site_code = Column(String(255))

    #折扣率 0.6～0.9
    discount = Column(Float, nullable=False, default=0)

    #折扣类型: 0是限时，1是限量，2是无折扣, 3是限时限量
    discount_type=Column(SmallInteger, nullable=False, default=0)

    # 促销关系建立的事件
    time = Column(DateTime,nullable = False,default = datetime.datetime.now())

    # 促销关系的状态  0 已过期， 1 正在进行
    status = Column(Integer, default=0)



# 营销活动开展的当前效果(如果营销活动已经结束即最终效果)
class PromotionEffect(dash_models.Base,GCustomerBaseModel) :
    __tablename__ = 'gcustomer_promotion_effect'

    #上述Promotion表格的主键
    promotion_id=Column(BigInteger)

    #当前参与的人数
    nb_participates=Column(Integer, default=0)

    #活动参与用户列表, cardnum数组的json形式
    user_participates=Column(TEXT, nullable=False)

    #营销活动通知到达的人数, 和nb_participates一起来算到达率
    nb_notified=Column(Integer, default=0)

    #投入成本(如何计算现在未知,应该是根据限时限量打折的结果来计算最大成本)
    cost=Column(Float, nullable=False, default=0)

    #用户参与促销活动贡献的加油量
    total_fuel_amount=Column(Float, nullable=False, default=0)

    #用户参与促销活动贡献的销售额
    total_fuel_purchase=Column(Float, nullable=False, default=0)

    #用户参与促销活动贡献的非油品销售额
    total_nonfuel_purcahse=Column(Float, nullable=False, default=0)

    #用户参与促销活动贡献的车后服务销售额
    total_service_purcahse=Column(Float, nullable=False, default=0)

    __table_args__=( UniqueConstraint('promotion_id',), )

# 用户对营销活动和广告投放的详细动作反馈记录，根据对此表格的动态查询可以获知营销活动的人群分布特征和参与趋势
class UserAction(dash_models.Base,GCustomerBaseModel) :
    __tablename__ = 'gcustomer_useraction'

     # APP端的虚拟卡号
    vcard_id = Column(String(40),nullable=False)

    # 营销/广告类型: 0表示是油品，1表示是便利店商品， 2表示是车后服务，3是广告
    obj_type=Column(SmallInteger,nullable=False, index=True)

    # 营销推送 的商品sha1或广告的sha1
    sha1 = Column(String(40),nullable=False, index=True)

    # 用户动作类型: 0表示点击查看，1表示实际购买, 此两类信息需要从不同的渠道获取并计算
    action=Column(SmallInteger, nullable=False)

    #营销营销活动id
    promotion_id = Column(Integer)

    # 用户动作的时间
    action_time=Column(DateTime)



#大客户基本信息表
class BigCustomerProfile(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_big_customer_profile'

    #公司
    comp_id = Column(Integer,nullable=False)

    #管理员的虚拟卡id, 其is_big_customer设置为1
    vcard_id = Column(String(40),nullable=False)

    #副卡数量
    nb_slave_cards=Column(SmallInteger, nullable=False, index=True, default=0)

    #客户贡献: 也就是过去两年的总消费额
    contribution=Column(Float, nullable=False, default=0)

    #等级积分
    score=Column(BigInteger, default=0)

    #积分排名
    score_rank = Column(Integer,default=0)

    #加油范围
    pump_range = Column(String(255),default="")

    #上个月消费额
    last_month_sale = Column(Float,default=0)

    #排名前20的大客户: 客户信息列表的json格式
    top_100_customers=Column(TEXT, nullable=False, default='[]')

    #排名后一百的大客户
    bottom_100_customers=Column(TEXT, nullable=False, default='[]')

    #按照贡献值从大到小排序后的百分比对应值，比如缺省值中前20%的客户贡献了40%的销售额
    percent_dist=Column(TEXT, nullable=False, default='[(0.1,0.2),(0.2,0.4),(0.3,0.5)]')

    __table_args__=( UniqueConstraint('comp_id','vcard_id'),)

# 主卡与副卡的关联，副卡即上面的CustomerProfile也就是普通散客
class CustomerRelation(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_customer_relation'

    #公司
    comp_id = Column(Integer,nullable=False)

    #主虚拟卡号
    master_cardnum = Column(Numeric(20),nullable=False)

    #副虚拟卡号
    slave_cardnum = Column(Numeric(20),nullable=False)

    __table_args__=( UniqueConstraint('comp_id', 'master_cardnum','slave_cardnum'), )

# 操作营销活动的联系沟通设置
class AdminContactInfo(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_admin_contactinfo'

    #公司Id
    comp_id = Column(Integer,nullable=False)

    #Gcustomer的web账号ID
    user_id = Column(Integer,nullable=False)

    #操作员的职位
    title=Column(String(255),nullable=False, default='')

    #操作员的Email
    email=Column(String(255),nullable=False, default='')

    #操作员的电话
    tel = Column(String(20),nullable = False , default = '')

    __table_args__=( UniqueConstraint("comp_id","user_id"), )

#沟通记录
class AdminContactRecord(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_admin_contact_record'

    #公司
    comp_id = Column(Integer,nullable=False)

    #大客户经理的gcustomer操作帐号id
    source_id = Column(Integer,nullable=False)

    #大客户卡号
    cardnum = Column(Numeric(20),nullable=False, index=True)

    #沟通时间
    time = Column(DateTime,nullable = False,default = datetime.datetime.now())

    #沟通内容
    contact_content = Column(TEXT,nullable = False,default = '')

#广告表(对应与上传广告)
class Advertisement(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_advertisement'

    #公司
    comp_id = Column(Integer,nullable=False)

    #sha1
    sha1 = Column(String(40),nullable=False,default='')

    #广告名称标题
    title  = Column(String(255),nullable=False,index=True,default='')

    #广告类型:
    type = Column(Integer,nullable=False,index=True,default=0)

    #操作帐号id
    source_id = Column(Integer,nullable=False)

    #客户名称
    name=Column(String(255),nullable=False,index=True)

    # 介绍信息(用于存储广告内容)
    abstract=Column(TEXT, nullable=False)

    # 联系方式
    contact=Column(TEXT, nullable=False,default='')

    #image sha1
    image_sha1 = Column(String(40),nullable = False,default='')

    #广告投放起止时间
    start_time=Column(DateTime, nullable=False,default=datetime.date(2015,1,1))
    end_time=Column(DateTime, nullable=False,default=datetime.date(2015,12,30))

    #广告投放的间隔，以分钟为单位
    interval=Column(Integer,nullable=False,default=60)

    __table_args__=( UniqueConstraint('comp_id','title'), )

#截至当前的广告效果
class AdvertisementEffect(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_advertisement_effect'

    #公司
    comp_id = Column(Integer,nullable=False)

    #广告id，Advertisement表格中的主键
    advert_id = Column(Integer,nullable=False)

    #广告总点击量
    click_amount=Column(BigInteger,nullable=False,default=0)

    #广告总投放量
    delivery_amount=Column(Float, nullable=False, default=0)

    #转化的销量
    purchase_amount=Column(Float, nullable=False, default=0)

    #转化的购买次数
    nb_purchases=Column(BigInteger,nullable=False,default=0)

    __table_args__ = ( UniqueConstraint('comp_id','advert_id'),)

#广告投放设置
class AdvertisementLaunchSetting(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_advertisement_launch_setting'

    #公司
    comp_id = Column(Integer,nullable=False)

    #广告id，Advertisement表格中的主键
    advert_id = Column(Integer,nullable=False)

    #生命周期 :秒
    life_cycle = Column(BigInteger,nullable = False ,default = 30)

    #播放时间 :秒
    play_time = Column(BigInteger,nullable = False,default = 1*60)

    #播放频率  :秒/次
    play_frequency = Column(Integer,nullable = False,default = 15)

    #是否关闭广告播放 0:关闭 1:开启
    is_close = Column(Integer,default = 1)

    __table_args__ = ( UniqueConstraint('comp_id','advert_id'),)

#便利店商品
class StoreItem(dash_models.Base,GCustomerBaseModel):
    __tablename__ = "gcustomer_store_item"

    #公司
    comp_id = Column(Integer,nullable=False)

    #sha1
    sha1 = Column(String(40),nullable=False)

    #操作帐号id
    source_id = Column(Integer,nullable=False)

    #商品pos系统ID
    pos_id = Column(Integer,nullable=False)

    #商品名称
    name = Column(String(40),nullable=False)

    #商品单价
    price = Column(Float,nullable = False)

    #商品数量(库存)
    count = Column(Integer,nullable = False,default=0)

    # score
    score = Column(Float,nullable = False,default =0)

    #exchange score  -1:no exchange
    exchange_score = Column(Integer,default=-1)

    #会员商品标识 -1:非会员商品 0:会员商品
    member_option = Column(Integer,default=-1)

    #discount
    discount = Column(Float,default = 0.9)

    # 折扣信息
    discount_info=Column(String(255),default="")

    # 价格有效时间
    discount_end_time= Column(DateTime)

    #商品图片
    image = Column(LargeBinary)

    #img sha1
    img_sha1 = Column(String(40))

    #便利店sha1
    seller_sha1 = Column(String(40))

    #商品描述
    information = Column(TEXT,default='')

    __table_args__=( UniqueConstraint('comp_id','pos_id'), )


#车后服务表
class ServiceInformation(dash_models.Base,GCustomerBaseModel):
    __tablename__ = "gcustomer_service_info"

    #公司
    comp_id = Column(Integer,nullable=False)

    #操作帐号id
    source_id = Column(Integer,nullable=False)

    #sha1
    sha1 = Column(String(40),nullable=False)

    #信息类型：0 - 货运，1 - 维修，2 - 保养
    info_type = Column(Integer,nullable=False)

    #货运，维修，保养等信息的标题
    title = Column(String(255),nullable=False,default="")

    #出发城市
    from_city = Column(String(255),nullable=False,default = "")

    #目的城市
    dest_city = Column(String(255),nullable=False,default = "")

    #创建时间
    create_time = Column(DateTime,nullable=False,default=datetime.datetime.now())

    #用户平均评分
    average_score= Column(Float)

    # 折扣信息
    discount_score= Column(Float)

    # 价格
    price= Column(Float)

    # 用户评论数量
    nb_comments= Column(Integer)

    #exchange score  -1:no exchange
    exchange_score = Column(Integer)

    #img_sha1
    img_sha1 = Column(String(40))

    #联系电话
    phone_number = Column(String(255))

    #详细内容描述
    content = Column(String(1024),nullable=False,default = "")

    #店名和公司名
    seller_sha1 = Column(String(40))

    #address
    address = Column(String(255),default='')

    __table_args__=( UniqueConstraint('comp_id','title'), )

 #服务商家
class Seller(dash_models.Base,GCustomerBaseModel):
    __tablename__ = 'gcustomer_seller'

    #公司
    comp_id = Column(Integer,nullable=False)

    #sha1
    sha1 = Column(String(40),nullable = False)

    #商家名
    name = Column(String(255),nullable=False)

    #商家地址
    address = Column(String(255),nullable = False)

    #地理位置信息
    geo_x = Column(Float, nullable=False, default = 123.12)
    geo_y = Column(Float, nullable=False, default=123.12)

    #tel
    phone = Column(String(40),nullable=False)

    #img_sha1
    img_sha1 = Column(String(40))

    #score
    score = Column(Integer)

    #introduction
    introduction = Column(TEXT,nullable=False,default = '')

    __table_args__ = ( UniqueConstraint('comp_id','name',), )

# 针对用户的APP与广告投放：每个用户获取哪个优惠，千人千变
class UserTargetedPromotion(dash_models.Base,GCustomerBaseModel) :
    __tablename__ = 'gcustomer_user_targeted_promotion'

    # 用户或是群组：0是群组，1是用户
    user_type = Column(Integer,nullable=False, index=True)

    # 用户卡号或CustomerGroup ID或所有用户(0)
    user_id = Column(BigInteger,nullable=False, index=True)

    # 营销/广告类型: 0表示是油品，1表示是便利店商品， 2表示是车后服务，3是广告
    obj_type=Column(SmallInteger,nullable=False, default=0)

    # 商品或广告的ID 油品的barcode
    obj_id = Column(BigInteger,nullable=False, default=0)

    # 活动的ID
    promotion_id = Column(BigInteger,nullable=False)

    # 投放方式：直接推送为0，到站推送为1
    delivery_type=Column(SmallInteger,nullable=False, default=0)

    # json格式的描述信息，里面可以包括油品的促销时间/价格/站名等，以及其它种类的具体优惠信息。
    desc=Column(TEXT, nullable=False, default='')

    # 推送时间
    start_time=Column(DateTime, index=True)

    # 显示天数
    duration=Column(SmallInteger,nullable=False, default=0)

#用户积分变化记录表
class UserScoreRecord(dash_models.Base,GCustomerBaseModel):
    __tablename__ = "gcustomer_user_score_record"

    #公司
    comp_id = Column(Integer,nullable=False)

    #用户卡号
    cardnum = Column(Integer,nullable=False,index=True)

    #交易记录sha1
    trans_sha1 = Column(String,nullable=False,index=True)

    #积分变化时间
    time = Column(DateTime,nullable=False,default=datetime.datetime.now())

    #当前交易后积分(剩余积分)
    current_score = Column(Integer,default=0)

    #当前累计积分
    all_score = Column(Integer,default=0)

    #当前交易的积分变化值(增加或减少的积分)
    score_change = Column(Integer)

    __table_args__ = (UniqueConstraint('comp_id','cardnum','trans_sha1'),)

#公司积分规则设置表
class UserScoreRule(dash_models.Base,GCustomerBaseModel):
    __tablename__ = "gcustomer_user_score_rule"

    #公司id
    comp_id = Column(Integer,nullable=False)

    #等级
    level = Column(Integer,nullable=False,default=0)

    #等级的积分范围
    level_range = Column(String(40),default="1001:2000")

    #积分系数 不同等级的用户积分系数不同(>=1)  每一笔app支付的积分= 基本积分值*用户积分系数*商品积分系数
    score_ratio = Column(Float,default=1)

    __table_args__ = (UniqueConstraint('comp_id','level'),)

#商品积分规则设置
class ItemScoreRule(dash_models.Base,GCustomerBaseModel):
    __tablename__ = "gcustomer_item_score_rule"

   #公司id
    comp_id = Column(Integer,nullable=False)

    #商品item_sha1
    item_sha1 = Column(String(40),nullable=False)

    #积分系数 不同商品的积分系数    积分系数 = 商品单价 * 基准返点
    score_ratio = Column(Float,default=1)

    __table_args__ = (UniqueConstraint('comp_id','item_sha1'),)

#会员商品打折信息
class MemberDiscountInfo(dash_models.Base,GCustomerBaseModel):
    __tablename__ = "gcustomer_member_discount_info"

    #公司
    comp_id = Column(Integer,nullable=False)

    #商品sha1
    item_sha1 = Column(String(40),nullable=False)

    #普通会员折扣
    ordinary_discount = Column(Float,default=1)

    #金卡会员折扣
    gold_discount = Column(Float,default=1)

    __table_args__ = (UniqueConstraint("comp_id","item_sha1"),)

#存储web系统图片
class FileImage(dash_models.Base,GCustomerBaseModel):
    __tablename__ = "gcustomer_fileimage"

    #图片sha1
    sha1 = Column(String(40),nullable=False)

    #存储图片数据
    image = Column(LargeBinary)

    #image name
    image_name = Column(String(255),nullable=False,default='')

    #image size
    image_size = Column(Integer)

    #upload author
    author = Column(String(40))

    #上传时间
    time = Column(DateTime,nullable = False)

    __table_args__ = (UniqueConstraint('sha1',),)

#油站工作人员
class GasWorker(dash_models.Base,GCustomerBaseModel):
    __tablename__ = "gcustomer_gas_worker"

    #用户名
    name = Column(String(255),nullable=False)

    #类型：0:未验证用户 1:为加油员，2:为收银员
    user_type = Column(Integer,nullable=False)

    #油站sha1
    station_sha1 = Column(String(40),nullable=False)

    #油站工作人员sha1
    sha1 = Column(String(40),nullable=False)

    #密码
    password = Column(String(255),nullable=False)

    #sim 卡号码
    sim_number = Column(String(40),nullable=False,default="")

    #型号: iphone5, HTC mate，etc
    device_type = Column(String(128),nullable=False,default="")

    #注册时间
    time = Column(DateTime,nullable=False,default=datetime.datetime.now())

    #用户性别 0:男 1:女
    gender = Column(Integer,default=0)

    #头像字段: 指向FileImage的sha1字段
    avarta_sha1= Column(String(40),default="")

    #昵称
    nick = Column(String(128))

    __table_args__ =  ( UniqueConstraint("name","user_type","station_sha1"),)

