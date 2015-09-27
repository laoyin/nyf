# -*- coding: utf-8 -*-

from dash.core import ui
from django.utils.translation import ugettext_lazy
from ui_page import *

#多站分析
class MultiStationPortal(ui.Portal):
    label=ugettext_lazy(u"多站分析")

    #pages
    list_page=[
        (ugettext_lazy(u"概况"),[
            #多站画像
            MultiStationProfilePage,
            #多站性能诊断
            MultiStationHealthPage,
        ]),
        (ugettext_lazy(u"油品"),[
            #趋势
            MultiStationOilPeriod,
            #销售额
            MultiStationOilMoneyPeriod,
            #出油时间
            MultiStationOilTimePeriod,
            #高峰期平均出油量
            MultiStationOilPeakFuelAvgGun,
            #油品环比
            MultiStationOilMoM,
            #加油卡消费比例
            MultiStationVIPPayPercent,
            #加满率
            MultiStationFillOutPercent,
        ]),
        (ugettext_lazy(u"非油品"),[
            #销量
            MultiStationNoneOilSales,
            #非油品环比
            MultiStationNoneOilMoM,
        ]),
        (ugettext_lazy(u"客户"),[
            #客单值
            MultiStationSingleCustomerPayTrend,
        ]),
    ]

    try_user_page=[
        (ugettext_lazy(u"油品"),[
            #趋势
            MultiStationOilPeriod,
            #加满率
            MultiStationFillOutPercent,
        ]),

    ]

#加油站栏目
class StationPortal(ui.Portal):
    label = ugettext_lazy(u"单站分析")

    #page容器
    list_page = [
        (ugettext_lazy(u"油品"),[
            #概况
            StationOilSummaryPage,
            #趋势
            StationOilPeriodAnalysisPage,
            #效率
            StationEfficientAnalysisPage,
            #高峰期
            StationPeakPeriodPage,
        ]),
        (ugettext_lazy(u"非油品"),[
            #概况
            StationGoodsSummaryPage,
            #趋势
            StationGoodsPeriodAnalysisPage,
            #相关性
            StationAssocAnalysisPage,
        ]),
        #客户分析
        (ugettext_lazy(u"客户"),StationCustomerAnalysisPage),
        #高级报表
        (ugettext_lazy(u"高级报表"),[StationProfessionalAnalysisPage,HealthPage]),
    ]

    try_user_page=[
        (ugettext_lazy(u"油品"),[
            #概况
            StationOilSummaryPage,
            #效率
            StationEfficientAnalysisPage,
            #高峰期
            StationPeakPeriodPage,
        ]),
        (ugettext_lazy(u"非油品"),[
            #相关性
            StationAssocAnalysisPage,
        ]),
        #客户分析
        (ugettext_lazy(u"客户"),StationCustomerAnalysisPage),
        #高级报表
        (ugettext_lazy(u"高级报表"),StationProfessionalAnalysisPage),
    ]

# example 栏目
# power by smite
class ExamplePortal(ui.Portal):
    label="示例栏目"
    list_page=[
        ExamplePage1,
        ExamplePage2
    ]

#upload 栏目
class UploadPortal(ui.Portal):
    label=ugettext_lazy(u"上传文件")
    list_page=[
        ImportDataPage,
        UploadedPage
    ]

#admin 栏目
class AdminPortal(ui.Portal):
    label=ugettext_lazy(u"用户管理")
    list_page=[
        AllUsersPage,
        FreeUsersPage,
        BasicUsersPage,
        SpecialUsersPage,
        CheckUsersPage,
        UserStationManagePage,
        FuelTypeManagePage,
    ]

#我的账户
class SettingProtal(ui.Portal):
   label=ugettext_lazy(u"我的账户")
   list_page=[WelcomePage,SettingPage,ManagementPage,SiteManagement,TagPage]
   try_user_page=[WelcomePage]

#指数栏目
class IndexPortal(ui.Portal):
    label = ugettext_lazy(u"网感油站指数")
    list_page = [PumpIndexPage, TrafficIndexPage, GunIndexPage, NonFuelIndexPage, CustomerIndexPage, AssocIndexPage]
