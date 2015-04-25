#coding=utf-8
from django.db import models

#事故分析表
class accidentStatistics(models.Model):
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
    time=models.CharField(max_length=5)
    local=models.IntegerField()
    type=models.IntegerField()
    loss=models.IntegerField()

#模拟数据表
class SimulationData(models.Model):
        #除系统选取的控制变量外的其它变量整体看成常量,默认为0
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

