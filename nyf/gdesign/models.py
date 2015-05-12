#coding=utf-8
from django.db import models

class GdesignUser(models.Model):
    #用户名
    name=models.CharField(max_length=255,null=False,unique=True)

    #密码
    password=models.CharField(max_length=255,null=False)

    #注册时间
    time=models.DateTimeField(auto_now_add=True)

    #类型：0为普通用户，1为管理员账户
    user_type=models.IntegerField(default=0)
        
    class Meta:
        unique_together = ('name','user_type')



class DimChinaProvinceCityDistrict(models.Model):                                                                                                                                                                                 
    """
    中国三级行政区划
    省市区/县
    """
    #区划代码
    area_id=models.IntegerField()

    #名称
    name=models.CharField(max_length = 256)

    #级别
    level=models.IntegerField()

    #上级代码
    parent=models.IntegerField()

    class Meta:
        unique_together = ("area_id",)


#加气站
class Station(models.Model):

        name = models.CharField(max_length = 255)
        #加气站类型 0:加气母站 1:加气子站
        type = models.IntegerField(default=1)
        #行政区划
        location = models.CharField(max_length = 10,default=320100)
        #地址
        address = models.CharField(max_length = 1024)

        #投产时间
        time = models.DateTimeField(auto_now_add = True)

        class Meta:
            unique_together = ("name","location","address")

#模拟分析基础参数表
#需要在添加站点时设置,并实时自动更新,每一条记录表示一个加气站的基础参数
class SimulationBaseParam(models.Model):

        #站点的id
        station_id = models.IntegerField()

        #环境压力 pa 随地域,环境的变化而不同
        pressure = models.FloatField(default=1.01*100000)

        #环境温度 K
        T = models.FloatField(default=298.15)

        #风速
        windSpeed = models.FloatField(default=0)

        #气体绝热系数 
        gas_k = models.FloatField(default=1.33)

        #气体泄漏系数,与裂口形状有关  圆形:1.0 三角形:0.95 长方形:0.90
        gas_Cd = models.FloatField(default=1.0)

        #天然气体摩尔质量kg/ kmol 
        molar_mass = models.FloatField(default=16)

        #热力学理想气体常数
        gas_R = models.FloatField(default = 8.314)


#常规分析模拟参数表
class RoutineSimulationParam(models.Model):

        #站点id
        station_id = models.IntegerField()

        #裂口直径
        rip_d = models.FloatField()

        #容器内介质压力
        container_medium_pressure = models.FloatField()

        #泄漏量
        Q = models.FloatField() 


#比较分析模拟表
class SimulationData(models.Model):
        # sha1 = models.CharField(max_length = 40)
        #除系统选取的控制变量外的其它变量整体看成常量
        constant=models.IntegerField()
        #单独考虑泄放速度时,windspeed=-1
        windSpeed=models.CharField(max_length=5)
        #单独考虑风速时,dischargeSpeed=-1
        dischargeSpeed=models.CharField(max_length=5)
        #泄漏扩散距离
        distance=models.CharField(max_length=5)
        #两个控制变量综合影响
        leakage_concentration=models.CharField(max_length=5)
        leakage_speed=models.CharField(max_length=5)
        #单个控制变量影响
        single_leakage_concentration=models.CharField(max_length=5)
        single_leakage_speed=models.CharField(max_length=5)

#事故表
class Accident(models.Model):
        """ 
        local:
                 0: 高压管道
                 1:车用气瓶
                 2:CNG压缩系统
                 3:储气系统
                 4:售气系统
        type:
                 0:高压管线腐蚀报废
                 1:泄漏
                 2:燃烧
                 3:爆炸
                 4:储气井管套冲出
        loss:
                 0:车用气瓶爆炸
                 1:压缩机燃烧
                 3:站用气瓶爆炸
                 4:压缩机震动报废,冰堵
                 5:售气机相关部件损坏报废
                 6:储气井泄漏
                 7:储气井管套冲出,窜动
                 8:高压管线腐蚀报废更换
        """
        sha1 = models.CharField(max_length = 40)
        title = models.CharField(max_length = 1024)
        station_name = models.CharField(max_length = 255)
        time = models.DateTimeField(auto_now_add = True)
        local = models.CharField(max_length = 1024)
        context = models.TextField()
        type=models.IntegerField()
        loss=models.IntegerField()