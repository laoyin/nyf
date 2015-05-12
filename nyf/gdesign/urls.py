#coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
import pdb,os,sys
import os
static_dir = os.path.join(os.path.dirname(__file__),'static')
GDESIGN = 'gdesign/'

#初始化page_view
urlpatterns = patterns('gdesign.page_views',
    url(r'^test$','test_page'),
    url(r'^temp$','temp_page'),
    #首页
    url(r'^$','gdesign_index_page'),
    # url(r'^index$','gdesign_index_page'),
    #站点画像
    url(r'^station/$','index_page'),
    url(r'^station/accident_list/$','index_page'),
    url(r'^station/stationIntroduct/$','stationIntroduct_page'),
    url(r'^station/simulationIntroduct/$','simulationIntroduct_page'),
    url(r'^station/settings/','settings_page'),
    #事故统计分析
    url(r'^accidentStatistics/$','accidentStatistics_page'),
    url(r'^accidentStatistics/locationStatistics/$','locationStatistics_page'),
    url(r'^accidentStatistics/typeStatistics/$','typeStatistics_page'),
    url(r'^accidentStatistics/lossStatistics/$','lossStatistics_page'),
    #模拟分析
    url(r'^simulationAnalysis/$','simulationAnalysis_page'),
    url(r'^definedSimulation/$','definedSimulation_page'),
    url(r'^simulationAnalysis/fireAndExplosionSimulation/','fireAndExplosionSimulation_page'),

    #站点管理
    url(r'^add_station/$','add_station_page'),
    #三维动态模拟
    url(r'^three_dim_simulation/$','three_dim_simulation_page'),
)

#初始化ajax_view
urlpatterns +=patterns('gdesign.ajax_views',
    url(r'^test_ajax$','test_ajax'),
    url(r'^request_simulaton_data/$','request_simulation_data'),
)

#数据库增删改查的接口路由
urlpatterns +=patterns('gdesign.ajax_views',
    url(r'^gdesign/station_list/$','station_list'),
    url(r'^gdesign/station_delete/$','station_delete'),
    url(r'^gdesign/station_create/$','station_create'),
    url(r'^gdesign/station_update/$','station_update'),
)

