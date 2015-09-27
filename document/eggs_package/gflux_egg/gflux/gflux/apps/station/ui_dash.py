# -*- coding: utf-8 -*-

from dash.core import ui
from django.utils.translation import ugettext_lazy
from ui_dashlet import *
import pdb,inspect

#当日油品销售额趋势图
class OilSalesDailyTrendDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"当日油品销售额趋势图")
    list_dashlet=[OilSalesDailyTrendDashlet]

#当日油品加油量趋势图
class PumpDailyTrendDash(ui.Dash):
    label = ugettext_lazy(u"当日加油量趋势图")
    list_dashlet = [PumpDailyTrendDashlet]

#当日油品交易笔数趋势图
class TransDailyTrendDash(ui.Dash):
    label=ugettext_lazy(u"当日油品交易笔数趋势图")
    list_dashlet=[TransDailyTrendDashlet]


#当日每车加油量趋势图
class PumpCarDailyTrendDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"当日平均每车加油量趋势图")
    list_dashlet=[PumpCarDailyTrendDashlet]

#每车加油量趋势图
class PumpCarTrendDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"每车加油量趋势图")
    list_dashlet=[PumpCarTrendDashlet]

#油站瓶颈与重复客户画像图
class MultiStationProfile1Dash(ui.Dash):
    enable_on_try_user=True
    label = ugettext_lazy(u"竞争力坐标体系")
    list_dashlet=[MultiStationProfile1Dashlet]

#多站加油量趋势
class MultiOilTrendDash(ui.Dash):
    enable_on_try_user=True
    label = ugettext_lazy(u"区域总体加油量趋势图")
    list_dashlet = [MultiOilTrendDashlet]

#多站加油量趋势排行
class MultiOilTrendSortDash(ui.Dash):
    enable_on_try_user=True
    label = ugettext_lazy(u"区域总体加油量趋势排行")
    renderer = "table"
    list_dashlet = [MultiOilTrendSortDashlet]

#多站销售额
class MultiOilMoneyTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域总体销售额趋势图")
    list_dashlet = [MultiOilMoneyTrendDashlet]

#多站销售额趋势排行
class MultiOilMoneySortTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域总体销售额趋势排行")
    renderer = "table"
    list_dashlet = [MultiOilMoneySortTrendDashlet]

#多站出油时间趋势
class MultiOilTimeTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域总体出油时间趋势图")
    list_dashlet = [MultiOilTimeTrendDashlet]

#多站出油时间趋势排行
class MultiOilTimeTrendSortDash(ui.Dash):
    label = ugettext_lazy(u"区域总体出油时间趋势图")
    renderer = "table"
    list_dashlet = [MultiOilTimeTrendSortDashlet]

#多站非油品销量
class MultiNoneOilSalesTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域非油品销量趋势图")
    list_dashlet = [MultiNoneOilSalesTrendDashlet]

#多站非油品销量排行
class MultiNoneOilSalesTrendSortDash(ui.Dash):
    label = ugettext_lazy(u"区域非油品销售排行图")
    renderer = "table"
    list_dashlet = [MultiNoneOilSalesTrendSortDashlet]

#多站高峰期平均出油量
class MultiOilPeakFuelAvgGunTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域高峰期平均出油量趋势图")
    list_dashlet = [MultiOilPeakFuelAvgGunTrendDashlet]

#多站高峰期平均出油量排行
class MultiOilPeakFuelAvgGunTrendSortDash(ui.Dash):
    label = ugettext_lazy(u"区域高峰期平均出油量趋势排行")
    renderer = "table"
    list_dashlet = [MultiOilPeakFuelAvgGunTrendSortDashlet]

#多站油品环比
class MultiOilMoMTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域油品环比趋势图")
    list_dashlet = [MultiOilMoMTrendDashlet]

#多站油品环比排行
class MultiOilMoMTrendSortDash(ui.Dash):
    label = ugettext_lazy(u"区域油品环比趋势排行")
    renderer = "table"
    list_dashlet = [MultiOilMoMTrendSortDashlet]

#多站非油品环比
class MultiNoneOilMoMTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域非油品环比趋势图")
    list_dashlet = [MultiNoneOilMoMTrendDashlet]

#多站非油品环比排行
class MultiNoneOilMoMTrendSortDash(ui.Dash):
    label = ugettext_lazy(u"区域非油品环比趋势排行")
    renderer = "table"
    list_dashlet = [MultiNoneOilMoMTrendSortDashlet]

#多站加油卡比例
class MultiVIPPayPercentTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域加油卡消费趋势图")
    list_dashlet = [MultiVIPPayPercentTrendDashlet]

#多站加油卡比例排行
class MultiVIPPayPercentTrendSortDash(ui.Dash):
    label = ugettext_lazy(u"区域加油卡消费趋势排行")
    renderer = "table"
    list_dashlet = [MultiVIPPayPercentTrendSortDashlet]

#多站加满率
class MultiFillOutPercentTrendDash(ui.Dash):
    enable_on_try_user=True
    label = ugettext_lazy(u"区域加满率趋势图")
    list_dashlet = [MultiFillOutPercentTrendDashlet]

#多站加满率排行
class MultiFillOutPercentTrendSortDash(ui.Dash):
    enable_on_try_user=True
    label = ugettext_lazy(u"区域加满率趋势排行")
    renderer = "table"
    list_dashlet = [MultiFillOutPercentTrendSortDashlet]

#区域客单值
class MultiSingleCustomerPayTrendDash(ui.Dash):
    label = ugettext_lazy(u"区域客单值趋势图")
    list_dashlet = [MultiSingleCustomerPayTrendDashlet]

#区域客单值排行
class MultiSingleCustomerPayTrendSortDash(ui.Dash):
    label = ugettext_lazy(u"区域客单值趋势排行")
    renderer = "table"
    list_dashlet = [MultiSingleCustomerPayTrendSortDashlet]

#当月加油量趋势图
class OilTrendDash(ui.Dash):
    label = ugettext_lazy(u"阶段加油量趋势图")
    list_dashlet = [OilTrendDashlet]

#当月加油量环比趋势图
class OilMoMTrendDash(ui.Dash):
    label=ugettext_lazy(u"阶段加油量环比趋势图")
    list_dashlet=[OilMoMTrendDashlet]

#一季度油品销售额趋势图
class OilQuarterTrendDash(ui.Dash):
    label=ugettext_lazy(u"近一季度销售额趋势图")
    list_dashlet=[OilQuarterTrendDashlet]

#当月加油量同比趋势图
class OilYoYTrendDash(ui.Dash):
    label=ugettext_lazy(u"阶段加油量同比趋势图")
    list_dashlet=[OilYoYTrendDashlet]

#加油量趋势对比分析
class OilTrendBetweenTwoDaysDash(ui.Dash):
    label=ugettext_lazy(u"对比分析两天的加油量趋势")
    list_dashlet=[OilTrendBetweenTwoDaysDashlet]

#油品销售额占总销售额比例
class OilToTotalSalesTrendDash(ui.Dash):
    label = ugettext_lazy(u"油品销售额占总销售额比例")
    list_dashlet = [OilToTotalSalesTrendDashlet]

#油非比
class OilAndStorePercentTrendDash(ui.Dash):
    label = ugettext_lazy(u"油非比")
    list_dashlet = [OilAndStorePercentTrendDashlet]

#当日油枪效率
class GunPumpTimeDailyTrendDash(ui.Dash):
    label=ugettext_lazy(u"当日油枪效率")
    list_dashlet=[GunPumpTimeDailyTrendDashlet]

    def __init__(self,*args,**kwargs):
        #使用反射获得调用者信息

        #如果调用者是高峰期page，需要重新指定dash的label
        import inspect
        stack = inspect.stack()
        caller_class=stack[1][0].f_locals["self"].__class__
        if str(caller_class).find('StationPeakPeriodPage')!=-1:
            self.label=ugettext_lazy(u"当日高峰期油枪效率")
        else:
            self.enable_on_try_user=True
        super(GunPumpTimeDailyTrendDash,self).__init__()

#当月油枪效率
class GunPumpTimeMonthTrendDash(ui.Dash):
    label=ugettext_lazy(u"当月油枪效率")
    list_dashlet=[GunPumpTimeMonthTrendDashlet]

#油枪效率鸟瞰图
class GunPumpTimeAerialViewTrendDash(ui.Dash):
    label = ugettext_lazy(u'油枪效率鸟瞰图')
    list_dashlet = [GunPumpTimeAerialViewTrendDashlet]

#月平均加油量
class OilMonthAvgTrendDash(ui.Dash):
    label=ugettext_lazy(u"当月24小时平均加油量")
    list_dashlet=[OilMonthAvgTrendDashlet]

#油品加满率
class OilFullRateDash(ui.Dash):
    label=ugettext_lazy(u"油品加满率")
    list_dashlet=[OilFullRateDashlet]

#高峰期出油效率
class CrestDailyTrendDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"总体出油效率")
    list_dashlet=[CrestDailyTrendDashlet]

#当日油机效率
class GunMachineTimeDailyTrendDash(ui.Dash):
    label=ugettext_lazy(u"当日油机效率")
    list_dashlet=[GunMachineTimeDailyTrendDashlet]

    def __init__(self,*args,**kwargs):
        #使用反射获得调用者信息

        #如果调用者是高峰期page，需要重新指定dash的label
        import inspect
        stack = inspect.stack()
        caller_class=stack[1][0].f_locals["self"].__class__
        if str(caller_class).find('StationPeakPeriodPage')!=-1:
            self.label=ugettext_lazy(u"当日高峰期油机效率")

        super(GunMachineTimeDailyTrendDash,self).__init__()

#当日通道效率
class PassageTimeDailyTrendDash(ui.Dash):
    label=ugettext_lazy(u"当日通道效率")
    list_dashlet=[PassageTimeDailyTrendDashlet]

    def __init__(self,*args,**kwargs):
        #使用反射获得调用者信息

        #如果调用者是高峰期page，需要重新指定dash的label
        import inspect
        stack = inspect.stack()
        caller_class=stack[1][0].f_locals["self"].__class__
        if str(caller_class).find('StationPeakPeriodPage')!=-1:
            self.label=ugettext_lazy(u"当日高峰期通道效率")

        super(PassageTimeDailyTrendDash,self).__init__()

#高峰期时段定义
class StationPeakPeriodTimeDefinedDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"高峰期时段定义")
    renderer = "table"
    list_dashlet=[StationPeakPeriodTimeDefinedDashlet]

#sku总数
class GoodsSKUCountDash(ui.Dash):
    label=ugettext_lazy(u"SKU指标")
    renderer = "table"
    list_dashlet=[GoodsSKUCountDashlet]

#当日非油品销售额趋势图
class GoodsSalesDailyTrendDash(ui.Dash):
    label=ugettext_lazy(u"当日非油品销售额趋势图")
    list_dashlet=[GoodsSalesDailyTrendDashlet]

#当日销售额客单值
class GoodsSalesPerPeopleDailyTrendDash(ui.Dash):
    label=ugettext_lazy(u"当日销售额客单值")
    list_dashlet=[GoodsSalesPerPeopleDailyTrendDashlet]

#当月非油品销售排行
class GoodsRankMonthTrendDash(ui.Dash):
    label= ugettext_lazy(u"上月非油品销售排行TOP10")
    renderer = "table"
    list_dashlet=[GoodsRankMonthTrendDashlet]

#油非转化率
class OilAndNonOilConversionDash(ui.Dash):
    label = ugettext_lazy(u'油非转化率')
    list_dashlet = [OilAndNonOilConversionDashlet]

#当月销售额趋势图
class GoodsTrendDash(ui.Dash):
    label = ugettext_lazy(u"阶段销售额趋势")
    list_dashlet = [GoodsTrendDashlet]

#近一季度非油品销售额趋势图
class GoodsQuarterTrendDash(ui.Dash):
    label = ugettext_lazy(u"近一季度销售额趋势图")
    list_dashlet = [GoodsQuarterTrendDashlet]

#当月销售额环比趋势图
class GoodsMoMTrendDash(ui.Dash):
    label=ugettext_lazy(u"阶段销售额环比趋势图")
    list_dashlet=[GoodsMoMTrendDashlet]

#当月销售额同比趋势图
class GoodsYoYTrendDash(ui.Dash):
    label=ugettext_lazy(u"阶段销售额同比趋势图")
    list_dashlet=[GoodsYoYTrendDashlet]

#销售额趋势对比分析
class GoodsTrendBetweenTwoDaysDash(ui.Dash):
    label=ugettext_lazy(u"对比分析两天的销售额趋势")
    list_dashlet=[GoodsTrendBetweenTwoDaysDashlet]

#油品与非油品交易比例
class OilGoodsProportionDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"阶段非油品占油品交易比例")
    list_dashlet=[OilGoodsProportionDashlet]

#油品与非油品相关性
class OilGoodsAssocDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"油品与非油品相关性")
    renderer = "table"
    list_dashlet=[OilGoodsAssocDashlet]

#非油品之间的相关性
class BetweenGoodsAssocDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"非油品之间的相关性")
    renderer = "table"
    list_dashlet=[BetweenGoodsAssocDashlet]

#当前持卡客户总数
class CustomerVIPCounterDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"当前持卡客户总数")
    renderer = "table"
    list_dashlet=[CustomerVIPCounterDashlet]

#阶段性活跃持卡数量
class CustomerVIPCounterByDateDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"阶段性活跃持卡数量")
    renderer = "table"
    list_dashlet=[CustomerVIPCounterByDateDashlet]

#当月忠诚客户比例
class CustomerVIPLoyaltyProportionDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"近一月忠诚客户比例")
    renderer = "table"
    list_dashlet=[CustomerVIPLoyaltyProportionDashlet]

#持卡客户消费趋势
class CustomerVIPCostTrendProportionDash(ui.Dash):
    enable_on_try_user=True
    label=ugettext_lazy(u"前两月持卡客户消费趋势")
    renderer = "table"
    list_dashlet=[CustomerVIPCostTrendProportionDashlet]

#近一年忠诚客户比例趋势
class CustomerVIPMonthlyLoyaltyDash(ui.Dash):
    label=ugettext_lazy(u"近一年忠诚客户比例趋势")
    list_dashlet=[CustomerVIPMonthlyLoyaltyDashlet]

#客户消费趋势
class CustomerCostTrendDash(ui.Dash):
    label=ugettext_lazy(u"阶段客户消费趋势")
    list_dashlet=[CustomerCostTrendDashlet]

#指数
class PumpDailyAvgDash(ui.Dash):
    label = ugettext_lazy(u"日均加油量")
    list_dashlet = [PumpDailyAvgDashlet]

class PumpHourlyAvgDash(ui.Dash):
    label = ugettext_lazy(u"每小时平均加油量")
    list_dashlet = [PumpHourlyAvgDashlet]

class PumpMonthlyAvgDash(ui.Dash):
    label = ugettext_lazy(u"月均加油量")
    list_dashlet = [PumpMonthlyAvgDashlet]

class TransCountAvgDash(ui.Dash):
    label = ugettext_lazy(u"进站车辆")
    list_dashlet = [TransCountAvgDashlet]

class GunPumpAvgDash(ui.Dash):
    label = ugettext_lazy(u"油枪效率")
    list_dashlet = [GunPumpAvgDashlet]

class NonFuelSalesAvgDash(ui.Dash):
    label = ugettext_lazy(u"非油品销售额")
    list_dashlet = [NonFuelSalesAvgDashlet]

class GoodsMonthAvgTrendDash(ui.Dash):
    label = ugettext_lazy(u"当月24小时非油品平均销售额")
    list_dashlet = [GoodsMonthAvgTrendDashlet]

class NonFuelSalesScaleDash(ui.Dash):
    label = ugettext_lazy(u"非油品交易比例")
    list_dashlet = [NonFuelSalesScaleDashlet]

class Top10NonFuelSalesAvgDash(ui.Dash):
    label = ugettext_lazy(u"Top10非油品销售规律")
    list_dashlet = [Top10NonFuelSalesAvgDashlet]

class CustomerMonthlyLoyaltyDash(ui.Dash):
    label = ugettext_lazy(u"忠实客户比例")
    list_dashlet = [CustomerMonthlyLoyaltyDashlet]

class CustomerMonthlyLeaveDash(ui.Dash):
    label = ugettext_lazy(u"忠实客户流失率")
    list_dashlet = [CustomerMonthlyLeaveDashlet]

class CustomerMonthlySalesScaleDash(ui.Dash):
    label = ugettext_lazy(u"忠实客户销售额占比变化")
    list_dashlet = [CustomerMonthlySalesScaleDashlet]

class FuelAssocDash(ui.Dash):
    label = ugettext_lazy(u"油品与非油品相关性")
    renderer = "table"
    list_dashlet = [FuelAssocDashlet]

#健康诊断
class HealthDash(ui.Dash):
    label=ugettext_lazy(u"健康指标")
    renderer = "table"
    list_dashlet=[HealthDashlet]

#测试瓶颈
class BottleneckDash(ui.Dash):
    label=ugettext_lazy(u"性能瓶颈")
    list_dashlet=[BottleneckDashlet]

#多站健康诊断结果
class MultiStationHealthDash(ui.Dash):
    label = ugettext_lazy(u"多站健康指标")
    renderer = 'table'
    list_dashlet = [MultiStationHealthDashlet]
