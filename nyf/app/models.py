#-*- coding: utf-8 -*-

from django.db import models

###################################################################
#  以下表格为APP使用,注意需要与models.py分开存在不同的数据库中，在settings中设置
#  第二个数据库用于专门存储这个数据，除此之外，使用Django的模型
###################################################################

# APP注册用户基本信息

class WheelUser(models.Model):

    __table__ = 'app_wheel_user'

    #用户名
    name=models.CharField(max_length=255,null=False,unique=True)
    sha1=models.CharField(max_length=40)

    #密码
    password=models.CharField(max_length=255,null=False)

    #注册时间
    time=models.DateTimeField(auto_now_add=True)

    #类型：0为普通用户，1为管理员账户
    user_type=models.IntegerField(default=0)

    #用户职业: 司机、学生、白领、其它
    career=models.CharField(max_length=128)

    #头像字段: 指向FileImage的sha1字段
    avarta_sha1=models.CharField(max_length=40)

    #昵称
    nick=models.CharField(max_length=128)

    #积分
    score=models.IntegerField(default=0)

    #支付信息: json格式，存储用户的支付手段
    payment_info=models.TextField(default='{}')
        
    class Meta:
        index_together = (
            ("name",),
        )

# APP匿名用户（设备）的基本信息
class WheelDevice(models.Model):

    __tablename__ = 'app_wheel_device'
    
    #设备id
    imei_code=models.CharField(max_length=128,unique=True)

    #mac 地址
    mac_address=models.CharField(max_length=255,default='')

    #sim 卡号码
    sim_number=models.CharField(max_length=32,default='')

    #型号: iphone5, HTC mate，etc
    device_type=models.CharField(max_length=128,unique=True)
        
    #创建时间
    time=models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (("imei_code",),)

# APP注册用户与设备之间的关系
class WheelUserDevice(models.Model):

    __tablename__ = 'app_wheel_user_device'
    
    #用户sha1
    user_sha1=models.CharField(max_length=40)
        
    #设备imei_code
    imei_code=models.CharField(max_length=128)

    #建立关联时间
    time=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together=('user_sha1', 'imei_code')
        index_together = (("user_sha1",),("imei_code",),)

# APP用户实时地理位置
class WheelUserLocation(models.Model):

    __tablename__ = 'app_wheel_user_location'
    
    # 类型，0为匿名用户，1为已注册登陆用户
    user_type=models.IntegerField(default=0)
    
    # 用户ID: SHA1或imei_code    
    user_id=models.CharField(max_length=128)
    
    # 位置采集时间
    time=models.DateTimeField(auto_now_add=True)
    
    # 地图中的x,y坐标
    geo_x=models.FloatField(default=0)
    geo_y=models.FloatField(default=0)
            
# APP中的用户消息
class WheelMessage(models.Model):

    __tablename__ = 'app_wheel_message'

    # sha1: 根据作者、时间和标题算出
    sha1=models.CharField(max_length=40,unique=True)

    # 消息标题
    title=models.CharField(max_length=128)
    
    # 消息正文
    body=models.CharField(max_length=512)

    # 作者账号
    author_sha1=models.CharField(max_length=40)
    
    # 消息类型：0通用类型，1道路信息，2故障求助，3发货运货
    #         4拼车搭伙  5消费点评 6求荐服务
    message_type=models.IntegerField(default=0)
    
    # 发表时间
    time=models.DateTimeField(auto_now_add=True)
    
    # 发表地点的坐标
    geo_x=models.FloatField(default=0)
    geo_y=models.FloatField(default=0)
    
    # 消息的文件与图片(json格式)
    attachment_info=models.CharField(max_length=512)
    
    # 所回复父亲消息的SHA1，若是主贴则为空
    parent_sha1=models.CharField(max_length=40,default='')

    # 主贴(所涉主题第一个消息)的SHA1，若是主贴则与sha1相同
    root_sha1=models.CharField(max_length=40,default='')
    
# APP中的文件与图片
class WheelFileImage(models.Model):

    __tablename__ = 'app_wheel_file_image'
    
    # sha1: 根据文件名、作者和时间计算得到
    sha1=models.CharField(max_length=40,unique=True)
        
    # 类型:0 为File, 1为Image
    file_type=models.IntegerField(default=0)
    
    # 文件名
    file_name=models.CharField(max_length=256)

    # 文件类型：默认为文件后缀，比如mp3, png, jpg
    file_suffix=models.CharField(max_length=32)

    # 二进制内容（base64解码之后）的sha1值，用于验证是否正确
    content_digest=models.CharField(max_length=40)
    
    # 文件的大小
    file_size=models.IntegerField(default=0)
    
    # 二进制内容
    base64_content=models.TextField(default='')
    
    # 上传时间
    time=models.DateTimeField(auto_now_add=True)
    
    # 作者
    author_sha1=models.CharField(max_length=40)
    
# APP用户与消息的关联属性
class WheelMessageMembership(models.Model):

    __tablename__ = 'app_wheel_message_membership'
    
    # 消息sha1
    message_sha1=models.CharField(max_length=40)
    
    # 用户sha1
    user_sha1=models.CharField(max_length=40)

    # 消息到达类型(0表示测试目的和全部推送，1表示同一家公司/主卡推送, 2表示就近推送, 3表示根据用户订阅和关注推送)
    delivery_type=models.IntegerField(default=0)

    # 消息到达时间
    time=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('message_sha1', 'user_sha1')
    
# APP中消息的统计属性
class WheelMessageStat(models.Model):

    __tablename__ = 'app_wheel_message_stat'
    
    # 消息的sha1
    message_sha1=models.CharField(max_length=40,unique=True)

    # 投送给多少人
    nb_deliveries=models.IntegerField(default=0)
    
    # 多少点击阅读
    nb_reads=models.IntegerField(default=0)
    
    # 多少回复
    nb_replies=models.IntegerField(default=0)

    # 多少次再传播
    nb_spreads=models.IntegerField(default=0)

    # 多少次忽略
    nb_ignores=models.IntegerField(default=0)

    #########################################
    # 以下为根据下面的WheelAppUsage计算生成
    #########################################
    
    # 最近24小时的点击量趋势,json格式
    recent_click_trend=models.TextField(default='')
    
    # 最近24小时的传播趋势,json格式
    recent_spread_trend=models.TextField(default='')

    # 最近24小时的回复量趋势,json格式
    recent_reply_trend=models.TextField(default='')

# APP上所售非油品货物商品
class WheelSaleItem(models.Model):

    __tablename__ = 'app_wheel_sale_item'
    
    # sha1 (由产品名称和出售、订购渠道生成)
    sha1=models.CharField(max_length=40,unique=True)
        
    # 产品名称
    name=models.CharField(max_length=256)

    # 价格
    price=models.FloatField(default=1)
    
    # 折扣信息
    discount=models.CharField(max_length=256,default=0.99)

    # 价格有效时间
    discount_end_time=models.DateTimeField(null=False)
    
    # 出售地点或订购渠道(此处仅能显示，内部与加油站和外部卖场的对接没有想好)
    available_source=models.TextField(default='')

# APP上所售服务和商品与用户的关联信息
class WheelSaleItemUsage(models.Model):

    __tablename__ = 'app_wheel_sale_item_usage'
    
    # 商品或服务的sha1
    item_sha1=models.CharField(max_length=40)

    # 商品类型：0是商品，1是服务
    item_type=models.IntegerField(default=0)
    
    # 用户sha1
    user_sha1=models.CharField(max_length=40)

    # 购买次数
    nb_purchases=models.IntegerField(default=0)

    # 累积金额
    purchased_amount=models.FloatField(default=0)

    #是否取货 0：表示预定取货 1：表示商城送货
    pickup_setting=models.IntegerField(default=0)

        
    class Meta:
        unique_together=('user_sha1', 'item_type', 'item_sha1')
    
# APP上所售的车后服务
class WheelSaleService(models.Model):

    __tablename__ = 'app_wheel_sale_service'
    
    # sha1 (由店名／公司名和服务名称生成)
    sha1=models.CharField(max_length=40,unique=True)
    
    # 店名和公司名
    seller_name=models.CharField(max_length=256)
    
    # 服务名称
    service_name=models.CharField(max_length=256)

    # 用户平均评分
    average_score=models.FloatField(default=3)

    # 折扣信息
    discount_score=models.FloatField(default=0.99)

    # 折扣截至时间
    discount_end_time=models.DateTimeField(null=False)
    
    # 价格
    price=models.FloatField(default=100)

    # 用户评论数量
    nb_comments=models.IntegerField(default=0)

    # 服务地址
    geo_x=models.FloatField(default=0)
    geo_y=models.FloatField(default=0)
    
# APP中用户对商品和服务的评论，以及打分
class WheelPurchaseComment(models.Model):

    __tablename__ = 'app_wheel_purchase_comment'
    
    # 商品或服务的sha1
    item_sha1=models.CharField(max_length=40)
    
    # 商品类型：0是商品，1是服务
    item_type=models.IntegerField(default=0)
        
    # 用户sha1
    user_sha1=models.CharField(max_length=40)
    
    # 购买纪录sha1，下面WheelTransaction中的sha1:只有购买过才能有资格去评论
    transaction_sha1=models.CharField(max_length=40)
    
    # 打的分数
    user_score=models.FloatField(default=3)

    # 评论内容
    comment_content=models.TextField(default='')    

    # 评论时间
    time=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('item_sha1', 'item_type', 'user_sha1')
    
# APP用户的支付交易纪录
class WheelTransaction(models.Model):

    __tablename__ = 'app_wheel_transaction'
    
    # 交易的sha1: 由用户sha1、商品服务sha1、商品服务类型、交易时间计算出
    sha1=models.CharField(max_length=40,unique=True)

    # 用户的sha1
    user_sha1=models.CharField(max_length=40)
    
    # 商品或服务的sha1
    item_sha1=models.CharField(max_length=40)

    # 商品类型：0是商品，1是服务
    item_type=models.IntegerField(default=0)
    
    # 到账金额
    item_total=models.FloatField(default=0)
    
    # 交易时间
    time=models.DateTimeField(auto_now_add=True)
    
# APP用户的APP使用纪录：打开、点击、购买、评论、回复、发言、忽略阅读等
class WheelAppUsage(models.Model):

    __tablename__ = 'app_wheel_appusage'
    
    # 类型，0为匿名用户，1为已注册登陆用户
    user_type=models.IntegerField(default=0)
    
    # 用户ID: SHA1或imei_code    
    user_id=models.CharField(max_length=256)
    
    # 数据采集时间
    time=models.DateTimeField(auto_now_add=True)
    
    # 数据使用类型:
    # 0 打开APP
    # 1 点击查看
    # 2 点击购买
    # 3 点击评论
    # 4 发表回复
    # 5 喊一嗓子
    # 6 忽略阅读
    data_type=models.IntegerField(default=0)

    # 数据涉及目标的类型
    # 0 推销商品
    # 1 加油
    # 2 车后服务
    # 3 喊一嗓子
    object_type=models.IntegerField(default=0)

    # 数据涉及目标的主键，商品、服务、油站、帖子的SHA1
    object_sha1=models.CharField(max_length=40)

    class Meta:
        unique_together=('user_type', 'user_id', 'time')

