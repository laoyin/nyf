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
    url(r'^$','gdesign_frame_page'),
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
    url(r'^simulationAnalysis/fireAndExplosionSimulation/','fireAndExplosionSimulation_page'),
    #三维动态模拟
    url(r'^three_dim_simulation/$','three_dim_simulation_page'),
)

#初始化ajax_view
urlpatterns +=patterns('gdesign.ajax_views',
    url(r'^test_ajax$','test_ajax'),
    url(r'^request_simulaton_data$','request_simulation_data'),
)

