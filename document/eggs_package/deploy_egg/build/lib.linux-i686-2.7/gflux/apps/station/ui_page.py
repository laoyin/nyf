# -*- coding: utf-8 -*-

from dash.core import ui
from django.utils.translation import ugettext_lazy
from django.forms import Media
from ui_dash import *
from django.template import Context, loader
from django.conf import settings
import json

version = settings.STATIC_VERSION

# example
class ExamplePage1(ui.Page):
    label="示例视图1"

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("test.html")
        self.extend_media=Media(css={
            'all':(
                'css/test.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/test.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'test1.html')

    def render(self, **context):
        context.update({'label':'hello smite! this is example1.html'})
        return super(self.__class__,self).render(**context)

class ExamplePage2(ui.Page):
    label="示例视图2"

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("test.html")
        self.extend_media=Media(css={
            'all':(
                'css/test.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/test.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'test2.html')

    def render(self, **context):
        context.update({'label':'hello smite! this is example2.html'})
        return super(self.__class__,self).render(**context)

#导入数据页面
class ImportDataPage(ui.Page):
    label=ugettext_lazy(u"导入数据")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("import.html")
        self.extend_media=Media(css={
            'all':(
                'css/fileuploader.'+settings.STATIC_VERSION+'.css',
                'css/import.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/fileuploader.'+settings.STATIC_VERSION+'.js',
            'js/import.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'import.html')

    def render(self, **context):
        import json
        from sql_utils import get_all_locations,get_user_stations_by_name
        request=context['request']

        #取得所有的地区信息
        all_locations=get_all_locations(with_dict_info=True)

        #取得用户的站点
        all_stations=get_user_stations_by_name(request.session['username'],with_dict_info=True)

        context.update({'all_locations':json.dumps(all_locations),
            'all_stations':json.dumps(all_stations),
            'version':version})
        return super(self.__class__,self).render(**context)

#已上传
class UploadedPage(ui.Page):
    label=ugettext_lazy(u"已上传")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("uploaded_page.html")
        self.extend_media=Media(css={
            'all':(
                'css/fileuploader.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/uploaded.'+settings.STATIC_VERSION+'.js',
            'js/fileuploader.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'uploaded_page.html')

    def render(self, **context):
        import json
        from sql_utils import get_all_locations,get_user_stations_by_name
        request=context['request']

        #取得所有的地区信息
        all_locations=get_all_locations(with_dict_info=True)

        #取得用户的站点
        all_stations=get_user_stations_by_name(request.session['username'],with_dict_info=True)

        context.update({'all_locations':json.dumps(all_locations),
            'all_stations':json.dumps(all_stations),
            'version':json.dumps(version)})
        return super(self.__class__,self).render(**context)

#所有用户
class AllUsersPage(ui.Page):
    label=ugettext_lazy(u"所有用户")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("admin_page_tbd.html")
        self.extend_media=Media(css={
            'all':(
                'css/fileuploader.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/admin.'+settings.STATIC_VERSION+'.js',
            'js/fileuploader.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'admin_page_all.html')

    def render(self, **context):
        context['filter_user_type']=-1
        return super(self.__class__,self).render(**context)

#试用版用户
class FreeUsersPage(ui.Page):
    label=ugettext_lazy(u"试用版用户")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("admin_page_tbd.html")
        self.extend_media=Media(css={
            'all':(
                'css/fileuploader.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/admin.'+settings.STATIC_VERSION+'.js',
            'js/fileuploader.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'admin_page_free.html')

    def render(self, **context):
        context['filter_user_type']=1
        return super(self.__class__,self).render(**context)

#普通版用户
class BasicUsersPage(ui.Page):
    label=ugettext_lazy(u"普通版用户")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("admin_page_tbd.html")
        self.extend_media=Media(css={
            'all':(
                'css/fileuploader.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/admin.'+settings.STATIC_VERSION+'.js',
            'js/fileuploader.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'admin_page_basic.html')

    def render(self, **context):
        context['filter_user_type']=2
        return super(self.__class__,self).render(**context)

#专业版用户
class SpecialUsersPage(ui.Page):
    label=ugettext_lazy(u"专业版用户")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("admin_page_tbd.html")
        self.extend_media=Media(css={
            'all':(
                'css/fileuploader.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/admin.'+settings.STATIC_VERSION+'.js',
            'js/fileuploader.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'admin_page_enterprise.html')

    def render(self, **context):
        context['filter_user_type']=3
        return super(self.__class__,self).render(**context)

#待审核用户
class CheckUsersPage(ui.Page):
    label=ugettext_lazy(u"待审核用户")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("admin_page_tbd.html")
        self.extend_media=Media(css={
            'all':(
                'css/fileuploader.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/admin.'+settings.STATIC_VERSION+'.js',
            'js/fileuploader.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'admin_page_tbd.html')

    def render(self, **context):
        context['filter_user_type']=0
        return super(self.__class__,self).render(**context)

#用户油站管理
class UserStationManagePage(ui.Page):
    label=ugettext_lazy(u"用户油站管理")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("userstationmanage.html")
        self.extend_media=Media(css={
            'all':(
                'css/userstationmanage.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/userstationmanage.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'userstationmanage.html')

    def render(self, **context):
        request=context['request']
        s=request.get_session()

        #get all user
        from gflux.apps.station.models import *
        all_users=s.query(User).all()
        context['users']=[{'id':user.id,'name':user.name} for user in all_users]

        #get all station
        from gflux.apps.common.models import *
        all_sites=s.query(Station).all()
        all_stations=[{'desc':site.description,'name':site.name} for site in all_sites]
        context['all_stations']=json.dumps(all_stations)
        return super(self.__class__,self).render(**context)

#汽车油牌管理
class FuelTypeManagePage(ui.Page):
    label=ugettext_lazy(u"汽油牌号管理")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("fueltypemanage.html")
        self.extend_media=Media(css={
            'all':(
                'css/fueltypemanage.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/fueltypemanage.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'fueltypemanage.html')

    def render(self, **context):
        request=context['request']
        s=request.get_session()
        from gflux.apps.station.models import *

        #获取所有油品编号与系统定义油品类型关系
        results=[]
        obj=s.query(FuelTypeRelation).all()
        for item in obj:
            result={}
            result['id']=item.id
            result['name']=item.name
            result['barcodes']=json.loads(item.barcodes)
            results.append(result)

        context['all_fuel_type_relation']=json.dumps(results)

        return super(self.__class__,self).render(**context)


#页面设置
class SettingPage(ui.Page):
    label=ugettext_lazy(u"设置")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("language_setting.html")
        self.extend_media=Media(css={
            'all':(

            )
        },js=[
            'js/language.'+settings.STATIC_VERSION+'.js',

        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'language_setting.html')

    def render(self, **context):
        context['language']=settings.LANGUAGES
        return super(self.__class__,self).render(**context)

#欢迎页面
class WelcomePage(ui.Page):
    label=ugettext_lazy(u"欢迎页面")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("welcome.html")
        self.extend_media=Media(css={
            'all':(
                'css/welcome.'+settings.STATIC_VERSION+'.css',
                'bootstrap-datepicker/css/datepicker.css',
            )
        },js=[
            'js/welcome.'+settings.STATIC_VERSION+'.js',
            'bootstrap-datepicker/js/bootstrap-datepicker.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'welcome.html')

    def render(self, **context):
        import json
        from sql_utils import get_all_locations,get_user_stations_by_name
        request=context['request']

        #取得所有的地区信息
        all_locations=get_all_locations(with_dict_info=True)

        #取得用户的站点
        all_stations=get_user_stations_by_name(request.session['username'],with_dict_info=True)

        context.update({'all_locations':json.dumps(all_locations),
            'all_stations':json.dumps(all_stations)})

        #公司名
        try:
            context['user_company']=request.session['company_name']
        except:
            context['user_company'] = ''
        return super(self.__class__,self).render(**context)

#通道和油机管理页面
class ManagementPage(ui.Page):
    label=ugettext_lazy(u"油枪分组")


    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("management.html")
        self.extend_media=Media(css={
            'all':(
                'css/management.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/management.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'management.html')

    def render(self, **context):
        import json
        from sql_utils import get_user_stations_by_name
        request=context['request']

        #取得用户的站点
        all_stations=get_user_stations_by_name(request.session['username'],with_dict_info=True)

        context.update({'all_stations':json.dumps(all_stations)})
        return super(self.__class__,self).render(**context)

#自定义标签页面
class TagPage(ui.Page):
    label=ugettext_lazy(u"自定义标签")


    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("tag.html")
        self.extend_media=Media(css={
            'all':(


            )
        },js=[
            'js/tag.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'tag.html')

    def render(self, **context):
        import json
        from sql_utils import get_user_stations_by_name
        request=context['request']

        #取得用户的站点
        all_stations=get_user_stations_by_name(request.session['username'],with_dict_info=True)

        context.update({'all_stations':json.dumps(all_stations)})
        return super(self.__class__,self).render(**context)


#油品概况视图
class StationOilSummaryPage(ui.Page):
    label = ugettext_lazy(u"概况")
    icon = "glyphicon-eye-open"
    list_module = [
        #当日油品销售额
        #OilSalesDailyTrendDash,
        #当日油品加油量
        PumpDailyTrendDash,
        #当日进站车辆
        TransDailyTrendDash,
        #当日平均每车加油量
        PumpCarDailyTrendDash,
        #平均每车加油量
        PumpCarTrendDash,
        #当月24小时平均加油量
        OilMonthAvgTrendDash,
        #油品加满率
        OilFullRateDash,
    ]

#多站画像
class MultiStationProfilePage(ui.Page):
    label=ugettext_lazy(u"竞争力坐标体系")
    icon="glyphicon-eye-open"
    list_module=[
        #油站瓶颈与重复客户画像
        MultiStationProfile1Dash,
    ]

#多站油品趋势分析
class MultiStationOilPeriod(ui.Page):
    label=ugettext_lazy(u"加油量趋势")
    icon="glyphicon-eye-open"
    list_module=[
        #加油量趋势
        MultiOilTrendDash,
        #加油量趋势排行
        MultiOilTrendSortDash,
    ]

#多站油品销售额趋势
class MultiStationOilMoneyPeriod(ui.Page):
    label=ugettext_lazy(u"销售额趋势")
    icon="glyphicon-eye-open"
    list_module=[
        #销售额趋势
        MultiOilMoneyTrendDash,
        #销售额趋势排行
        MultiOilMoneySortTrendDash,
    ]

#多站出油时间趋势
class MultiStationOilTimePeriod(ui.Page):
    label=ugettext_lazy(u"出油时间趋势")
    icon="glyphicon-eye-open"
    list_module=[
        #出油时间趋势
        MultiOilTimeTrendDash,
        #出油时间趋势排行
        MultiOilTimeTrendSortDash,
    ]

#多站非油品销量趋势
class MultiStationNoneOilSales(ui.Page):
    label=ugettext_lazy(u"销量趋势")
    icon="glyphicon-eye-open"
    list_module=[
        #销量趋势
        MultiNoneOilSalesTrendDash,
        #销量趋势排行
        MultiNoneOilSalesTrendSortDash,
    ]

#多站高峰期平均出油量趋势
class MultiStationOilPeakFuelAvgGun(ui.Page):
    label=ugettext_lazy(u"高峰期平均出油量趋势")
    icon="glyphicon-eye-open"
    list_module=[
        #高峰期平均出油量趋势
        MultiOilPeakFuelAvgGunTrendDash,
        #高峰期平均出油量趋势排行
        MultiOilPeakFuelAvgGunTrendSortDash,
    ]

#多站油品环比趋势
class MultiStationOilMoM(ui.Page):
    label=ugettext_lazy(u"油品环比趋势")
    icon="glyphicon-eye-open"
    list_module=[
        #油品环比趋势
        MultiOilMoMTrendDash,
        #油品环比趋势排行
        MultiOilMoMTrendSortDash,
    ]

#多站非油品环比趋势
class MultiStationNoneOilMoM(ui.Page):
    label=ugettext_lazy(u"非油品环比趋势")
    icon="glyphicon-eye-open"
    list_module=[
        #非油品环比趋势
        MultiNoneOilMoMTrendDash,
        #非油品环比趋势排行
        MultiNoneOilMoMTrendSortDash,
    ]

#多站加油卡比例
class MultiStationVIPPayPercent(ui.Page):
    label=ugettext_lazy(u"加油卡消费比例")
    icon="glyphicon-eye-open"
    list_module=[
        #加油卡消费比例
        MultiVIPPayPercentTrendDash,
        #加油卡消费比例排行
        MultiVIPPayPercentTrendSortDash,
    ]

#多站加满率
class MultiStationFillOutPercent(ui.Page):
    label=ugettext_lazy(u"加满率")
    icon="glyphicon-eye-open"
    list_module=[
        #加满率
        MultiFillOutPercentTrendDash,
        #加满率排行
        MultiFillOutPercentTrendSortDash,
    ]

#多站客单值
class MultiStationSingleCustomerPayTrend(ui.Page):
    label=ugettext_lazy(u"客单值")
    icon="glyphicon-eye-open"
    list_module=[
        #客单值
        MultiSingleCustomerPayTrendDash,
        #客单值排行
        MultiSingleCustomerPayTrendSortDash,
    ]

#油品趋势分析视图
class StationOilPeriodAnalysisPage(ui.Page):
    label=ugettext_lazy(u"趋势")
    icon = "glyphicon-eye-open"
    list_module = [
        #加油量趋势
        OilTrendDash,
        #一季度油品销售额趋势
        #OilQuarterTrendDash,
        #加油量趋势环比
        OilMoMTrendDash,
        #加油量趋势同比
        OilYoYTrendDash,
        #加油量趋势对比分析
        OilTrendBetweenTwoDaysDash,
        #油品销售额占总销售额比例
        #OilToTotalSalesTrendDash,
        #油非比
        OilAndStorePercentTrendDash
    ]

#加油效率分析视图
class StationEfficientAnalysisPage(ui.Page):
    label=ugettext_lazy(u"效率")
    icon = "glyphicon-eye-open"
    list_module=[
        #当日油枪效率
        #GunPumpTimeDailyTrendDash,
        #当日油机效率
        GunMachineTimeDailyTrendDash,
        #当日通道效率
        PassageTimeDailyTrendDash,
        #当月油枪效率
        GunPumpTimeMonthTrendDash,
        #油枪效率鸟瞰图
        GunPumpTimeAerialViewTrendDash,
    ]

#高峰期视图
class StationPeakPeriodPage(ui.Page):
    label=ugettext_lazy(u"高峰期")
    icon = "glyphicon-eye-open"
    list_module=[
        #高峰期时段定义
        StationPeakPeriodTimeDefinedDash,

        #以下同效率，请判断request是否是高峰期视图来的返回对应数据
        #高峰期出油效率
        CrestDailyTrendDash,
        #当日油枪效率
        GunPumpTimeDailyTrendDash,
        #当日油机效率
        GunMachineTimeDailyTrendDash,
        #当日通道效率
        PassageTimeDailyTrendDash,
    ]

#非油品概况视图
class StationGoodsSummaryPage(ui.Page):
    label = ugettext_lazy(u"概况")
    icon = "glyphicon-eye-open"
    list_module = [
        #sku总数
        GoodsSKUCountDash,
        #当日非油品销售额趋势图
        GoodsSalesDailyTrendDash,
        #当月24小时平均加油量
        GoodsMonthAvgTrendDash,
        #当日销售额客单值
        GoodsSalesPerPeopleDailyTrendDash,
        #当月非油品销售排行
        GoodsRankMonthTrendDash,
        #油非转化率
        OilAndNonOilConversionDash,
    ]

#非油品趋势分析视图
class StationGoodsPeriodAnalysisPage(ui.Page):
    label=ugettext_lazy(u"趋势")
    icon = "glyphicon-eye-open"
    list_module=[
        #加油量趋势
        GoodsTrendDash,
        #近一季度非油品销售额趋势图
        #GoodsQuarterTrendDash,
        #加油量趋势环比
        GoodsMoMTrendDash,
        #加油量趋势同比
        GoodsYoYTrendDash,
        #加油量趋势对比分析
        GoodsTrendBetweenTwoDaysDash,
    ]

#非油品相关性分析视图
class StationAssocAnalysisPage(ui.Page):
    label=ugettext_lazy(u"相关性")
    icon = "glyphicon-eye-open"
    list_module=[
        #油品与非油品交易比例
        OilGoodsProportionDash,
        #油品与非油品相关性
        OilGoodsAssocDash,
        #非油品之间的相关性
        BetweenGoodsAssocDash,
    ]

#客户行为分析视图
class StationCustomerAnalysisPage(ui.Page):
    label = ugettext_lazy(u"客户分析")
    icon = "glyphicon-heart"
    list_module = [
        #当前持卡客户总数
        CustomerVIPCounterDash,
        #阶段性活跃持卡数量
        CustomerVIPCounterByDateDash,
        #当月忠诚客户比例
        CustomerVIPLoyaltyProportionDash,
        #持卡客户消费趋势
        CustomerVIPCostTrendProportionDash,
        #近一年忠诚客户比例趋势
        CustomerVIPMonthlyLoyaltyDash,
        #客户消费趋势
        CustomerCostTrendDash,
    ]

#高级报表
class StationProfessionalAnalysisPage(ui.Page):
    label=ugettext_lazy(u"自定义报表")
    icon = "glyphicon-heart"

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("station_professional_analysis.html")
        self.extend_media=Media(css={
            'all':(
                'css/professional.'+settings.STATIC_VERSION+'.css',
                'bootstrap-datepicker/css/datepicker.css',
            )
        },js=[
            'js/professional.'+settings.STATIC_VERSION+'.js',
            'bootstrap-datepicker/js/bootstrap-datepicker.js',
            'highcharts/js/highcharts.js',
            'highcharts/js/highcharts-more.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'professional.html')

    def render(self, **context):
        import json
        from sql_utils import get_user_stations_by_name,get_user_fuel_type_by_name,\
            get_passage_machine_level_by_user_site
        request=context['request']
        #取得用户的站点
        all_stations=get_user_stations_by_name(request.session['username'],with_dict_info=True)
        all_passage_machine_level=get_passage_machine_level_by_user_site(all_stations)
        context['all_stations']=json.dumps(all_stations)
        context['all_passage_machine_level']=json.dumps(all_passage_machine_level)
        user_fuel_types=get_user_fuel_type_by_name(request.session['username'])
        context['user_fuel_types']=user_fuel_types
        return super(self.__class__,self).render(**context)

#指数
class PumpIndexPage(ui.Page):
    label = ugettext_lazy(u"加油量指数")
    icon = "glyphicon-tint"
    list_module = [PumpDailyAvgDash, PumpHourlyAvgDash, PumpMonthlyAvgDash]

class TrafficIndexPage(ui.Page):
    label = ugettext_lazy(u"车流量指数")
    icon = "glyphicon-sort"
    list_module = [TransCountAvgDash]

class GunIndexPage(ui.Page):
    label = ugettext_lazy(u"油枪效率指数")
    icon = "glyphicon-filter"
    list_module = [GunPumpAvgDash]

class NonFuelIndexPage(ui.Page):
    label = ugettext_lazy(u"非油品指数")
    icon = "glyphicon-shopping-cart"
    list_module = [NonFuelSalesAvgDash, NonFuelSalesScaleDash, Top10NonFuelSalesAvgDash]

class CustomerIndexPage(ui.Page):
    label = ugettext_lazy(u"客户忠诚度")
    icon = "glyphicon-user"
    list_module = [CustomerMonthlyLoyaltyDash, CustomerMonthlyLeaveDash, CustomerMonthlySalesScaleDash]

class AssocIndexPage(ui.Page):
    label = ugettext_lazy(u"相关性分析")
    icon = "glyphicon-map-marker"
    list_module = [FuelAssocDash]

#站点管理页面
class SiteManagement(ui.Page):
    label=ugettext_lazy(u"站点管理")

    def __init__(self,*args,**kwargs):
        super(self.__class__,self).__init__(*args,**kwargs)

        self.template=loader.get_template("myselftationmanage.html")
        self.extend_media=Media(css={
            'all':(
                'css/userstationmanage.'+settings.STATIC_VERSION+'.css',
            )
        },js=[
            'js/myselftationmanage.'+settings.STATIC_VERSION+'.js',
        ])

    def path(self):
        return "%s/%s" % (self.portal.path(), 'myselftationmanage.html')

    def render(self, **context):
        request=context['request']

        s=request.get_session()

        #取得登录者的用户信息
        from gflux.apps.station.models import *

        #从session中取得用户名
        username = request.session['username']

        #使用取得的用户名来查询,这样将得到登录者的信息
        user=s.query(User).filter_by(name=username).one()
        context['userid']=user.id

        return super(self.__class__,self).render(**context)

#健康诊断
class HealthPage(ui.Page):
    label=ugettext_lazy(u"性能诊断")
    icon = "glyphicon-eye-open"
    list_module=[
        #健康诊断结果
        HealthDash,
        #测试瓶颈
        BottleneckDash,
    ]

#多站健康诊断
class MultiStationHealthPage(ui.Page):
    label=ugettext_lazy(u"多站性能诊断")
    icon = "glyphicon-eye-open"
    list_module=[
        #多站健康诊断结果
        MultiStationHealthDash,
    ]
