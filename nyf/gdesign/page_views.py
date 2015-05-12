#coding=utf-8
from django.shortcuts import render_to_response,render
from django.conf import settings
from django.http import *
from django.template import Context
import pdb

#test page
def test_page(request):
    return render_to_response('gdesign_frame.html')
#temp_page
def temp_page(request):
    return render_to_response('temp1.html')

#首页
def gdesign_index_page(request):
    return render_to_response('gdesign_index_page.html')

#站点画像
#数故列表   
def index_page(request):
    return render_to_response('accident_list.html')
#气站数据
def stationIntroduct_page(request):
    return render_to_response('stationIntroduct.html')
#模拟分析案例
def simulationIntroduct_page(request):
    return render_to_response('simulationIntroduct.html')

#设置
def settings_page(request):
    return render_to_response('settings.html')

#事故统计分析
def accidentStatistics_page(request):
    return render_to_response('accidentStatistics.html')
#事故发生位置分析
def locationStatistics_page(request):
    return render_to_response('locationStatistics.html')
#事故类型分析
def typeStatistics_page(request):
    return render_to_response('typeStatistics.html')
#事故只要损失构成
def lossStatistics_page(request):
    return render_to_response('lossStatistics.html')

#模拟分析
def simulationAnalysis_page(request):
    return render_to_response('simulationAnalysis.html')

def definedSimulation_page(request):
    return render_to_response("definedSimulation.html")
#火灾爆炸模拟
def fireAndExplosionSimulation_page(request):
    return render_to_response('FireAndExplosionSimulation.html')

#三维动态模拟
def three_dim_simulation_page(request):
    return render_to_response('three_dim_simulation.html')

def add_station_page(request):
    return render_to_response('add_station.html')

