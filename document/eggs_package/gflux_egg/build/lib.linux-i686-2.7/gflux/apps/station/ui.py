# -*- coding: utf-8 -*-
#当前文件仅用作dash 库的自动发现服务
from ui_portal import *
from dash.core import site

#setting 栏目
site.register(SettingProtal)

#加油站栏目
site.register(StationPortal)

#多站
site.register(MultiStationPortal)

#指数栏目
site.register(IndexPortal)

#example 栏目
#site.register(ExamplePortal)

#upload 栏目
site.register(UploadPortal)

#admin 栏目
site.register(AdminPortal)



#ui层级关系
"""
整个page_view由：
    ui_portal（加油站，Gilbarco指数）构成由：
        ui_page(油品概况，油品趋势分析)构成由：
            ui_dash(油品当日加油量，油品当日销售额)构成由：
                ui_dashlet(油品当日加油量，油品当日销售额)
"""
