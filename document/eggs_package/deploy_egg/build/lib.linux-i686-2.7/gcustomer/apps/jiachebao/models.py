#-*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy
from dash.core.types import enum
from django.db import models
import datetime,time

###################################################################
#  以下表格为APP使用,注意需要与models.py分开存在不同的数据库中，在settings中设置
#  第二个数据库用于专门存储这个数据，除此之外，使用Django的模型
###################################################################

# APP匿名用户（设备）的基本信息
class WheelDevice(models.Model) :
    
    #设备id
    imei_code=models.CharField(max_length=128,unique=True)

    #mac 地址
    mac_address=models.CharField(max_length=255,default='')

    #sim 卡号码
    sim_number=models.CharField(max_length=32,default='')

    #型号: iphone5, HTC mate，etc
    device_type=models.CharField(max_length=128,unique=True)
        
    #创建时间
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (("imei_code",),)

# APP虚拟卡号与设备之间的关系
class WheelAccountDeviceInfo(models.Model):
    
    # 虚拟卡号id
    vcard_id=models.CharField(max_length=40)
        
    #设备imei_code
    imei_code=models.CharField(max_length=128)

    #建立关联时间
    time=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together=('vcard_id', 'imei_code')
        index_together = (("vcard_id",),("imei_code",),)

# APP虚拟卡实时地理位置(行车轨迹)
class WheelAccountLocation(models.Model):
    
    # 类型，0为匿名用户，1为已注册登陆用户
    user_type=models.IntegerField(default=0)
    
    # 用户ID: vcard_id或imei_code    
    user_id = models.CharField(max_length=128)
    
    # 位置采集时间
    time = models.DateTimeField(auto_now_add=True)
    
    # 地图中的x,y坐标
    geo_x = models.FloatField(default=0)
    geo_y = models.FloatField(default=0)
            
# APP中的用户消息
class WheelMessage(models.Model):

    # sha1: 根据作者、时间和标题算出
    sha1 = models.CharField(max_length=40,unique=True)

    # 消息标题
    title=models.CharField(max_length=128)
    
    # 消息正文
    body=models.CharField(max_length=512)

    # 作者账号
    author_sha1=models.CharField(max_length=40)
    
    # 消息类型：0通用类型，1道路信息，2故障求助，3发货运货
    #         4拼车搭伙  5消费点评 6求荐服务
    message_type=models.IntegerField(default=0)

    #request type "1":我发布的消息; "2":我接受的消息
    request_type = models.CharField(max_length=10,default='1')
    
    # 发表时间
    time=models.DateTimeField(auto_now_add=True)
    
    # 发表地点的坐标
    geo_x=models.FloatField(default=0)
    geo_y=models.FloatField(default=0)
    
    # 消息的文件与图片(json格式)
    attachment_info = models.CharField(max_length=512)
    
    # 所回复父亲消息的SHA1，若是主贴则为空
    parent_sha1=models.CharField(max_length=40,default='')

    # 主贴(所涉主题第一个消息)的SHA1，若是主贴则与sha1相同
    root_sha1=models.CharField(max_length=40,default='')
    
    #主键
    class Meta :
        unique_together = ('sha1',)
    
# APP用户与消息的关联属性
class WheelMessageMembership(models.Model):
    
    # 消息sha1
    message_sha1=models.CharField(max_length=40)
    
    # 用户sha1
    user_sha1=models.CharField(max_length=40)

    # 消息到达类型(0表示测试目的和全部推送，1表示同一家公司/主卡推送, 
    # 2表示就近推送, 3表示根据用户订阅和关注推送)
    delivery_type=models.IntegerField(default=0)

    # 消息到达时间
    time=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('message_sha1', 'user_sha1')
    
# APP中消息的统计属性
class WheelMessageStat(models.Model):
    
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
  
# APP中用户对商品和服务的评论，以及打分
class WheelPurchaseComment(models.Model):
    
    # 商品或服务的sha1
    item_sha1=models.CharField(max_length=40)
    
    # 商品类型：0是加油站油品，1是便利店商品，2是服务
    item_type=models.IntegerField(default=0)
        
    # 用户Id
    vcard_id=models.CharField(max_length=40)
    
    # 购买纪录sha1，下面AccountTransaction中的sha1:只有购买过才能有资格去评论
    transaction_sha1=models.CharField(max_length=40,default="")
    
    # 打的分数
    user_score=models.FloatField(default=3)

    # 评论内容
    comment_content=models.TextField(default='')    

    # 评论时间
    time=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('item_sha1', 'item_type', 'vcard_id')

# APP用户的APP使用纪录：打开、点击、购买、评论、回复、发言、忽略阅读等
class WheelAppUsage(models.Model):
    
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
        unique_together = ('user_type', 'user_id', 'time')

#道路救援电话
class WheelHelpPhone(models.Model):
    #名称
    name = models.CharField(max_length = 255,default = "")

    #行政区划
    location = models.CharField(max_length = 255,null = True)

    #phone
    phone = models.CharField(max_length = 11)

    class Meta:
        unique_together=('phone',)

# APP中的文件与图片
class WheelFileImage(models.Model):
    
    # sha1: 根据文件名、作者和时间计算得到
    sha1=models.CharField(max_length=40,unique=True)
        
    # 类型:0 为File, 1为Image
    file_type=models.IntegerField(default=1)
    
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

    class Meta:
        unique_together=('sha1',)



#实体卡画像临时表格
class UserCardProfilingResult(models.Model) :

    #加油卡号
    cardnum = models.CharField(max_length=255,unique=True)
    
    #用户类型 1:中石油 2:中石化 3:中海油 4:壳牌 5:中化
    comp_id = models.IntegerField(default=0)

    #最喜爱的非油品商品列表 barcode 非油品条形码: 如: '[]'
    favourite_nonfuel_products = models.TextField(default='[]')

    #推荐购买的非油品列表
    recommended_nonfuel_products = models.TextField(default='[]')

    class Meta:
        unique_together=('cardnum',)

#意见反馈
class AppUserFeedBack(models.Model):

    # 虚拟卡号id
    vcard_id = models.CharField(max_length=40)

    #0:用户意见反馈 1:收银员意见反馈
    type = models.IntegerField(default=0)

    #内容
    content = models.CharField(max_length=255)

    #反馈时间
    time = models.DateTimeField(null=False,default=datetime.datetime.now())





