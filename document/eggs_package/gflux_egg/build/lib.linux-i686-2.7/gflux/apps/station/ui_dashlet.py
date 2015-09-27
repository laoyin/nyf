# -*- coding: utf-8 -*-

from dash.core import ui
from . import reports
from django.utils.translation import ugettext_lazy

#当日油品销售额趋势图
class OilSalesDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.OilSalesDailyTrendReport

#当日油品加油量趋势图
class PumpDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.PumpDailyTrendReport

#当日进站车辆趋势图
class TransDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"交易笔数(单位：笔)")
    report_interface = reports.TransDailyTrendReport

#当日每车加油量趋势图
class PumpCarDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.PumpCarDailyTrendReport

#每车加油量趋势图
class PumpCarTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.PumpCarTrendReport

#当月加油量趋势图
class OilTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.OilTrendReport

#油站瓶颈与重复客户画像图
class MultiStationProfile1Dashlet(ui.Dashlet):
    label = ugettext_lazy(u"")
    report_interface = reports.MultiStationProfile1Report

#区域加油量趋势
class MultiOilTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.MultiOilTrendReport

#区域加油量趋势排行
class MultiOilTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiOilTrendSortReport

#区域销售额趋势
class MultiOilMoneyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.MultiOilMoneyTrendReport

#区域销售额趋势排行
class MultiOilMoneySortTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiOilMoneyTrendSortReport

#区域出油时间趋势
class MultiOilTimeTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"时间(单位：分钟)")
    report_interface = reports.MultiOilTimeTrendReport

#区域出油时间趋势排行
class MultiOilTimeTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiOilTimeTrendSortReport

#区域非油品销量趋势
class MultiNoneOilSalesTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销量(单位:个)")
    report_interface = reports.MultiNoneOilSalesTrendReport

#区域非油品销量趋势排行
class MultiNoneOilSalesTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    reder_as = "table"
    report_interface = reports.MultiNoneOilSalesTrendSortReport

#区域高峰期平均出油量趋势
class MultiOilPeakFuelAvgGunTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"出油量(单位:升)")
    report_interface = reports.MultiOilPeakFuelAvgGunTrendReport

#区域高峰期平均出油量趋势排行
class MultiOilPeakFuelAvgGunTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiOilPeakFuelAvgGunTrendSortReport

#区域油品环比
class MultiOilMoMTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比(单位：%)")
    report_interface = reports.MultiOilMoMTrendReport

#区域油品环比排行
class MultiOilMoMTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiOilMoMTrendSortReport

#区域非油品环比
class MultiNoneOilMoMTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比(单位：%)")
    report_interface = reports.MultiNoneOilMoMTrendReport

#区域非油品环比排名
class MultiNoneOilMoMTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiNoneOilMoMTrendSortReport

#区域加油卡比例
class MultiVIPPayPercentTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比(单位：%)")
    report_interface = reports.MultiVIPPayPercentTrendReport

#区域加油卡比例排行
class MultiVIPPayPercentTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiVIPPayPercentTrendSortReport

#区域客单值
class MultiSingleCustomerPayTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.MultiSingleCustomerPayTrendReport

#区域客单值排行
class MultiSingleCustomerPayTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiSingleCustomerPayTrendSortReport

#区域加满率
class MultiFillOutPercentTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比(单位：%)")
    report_interface = reports.MultiFillOutPercentTrendReport

#区域加满率排行
class MultiFillOutPercentTrendSortDashlet(ui.Dashlet):
    label = ugettext_lazy(u"排名")
    render_as = "table"
    report_interface = reports.MultiFillOutPercentTrendSortReport

#当月加油量环比趋势图
class OilMoMTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.OilMoMTrendReport

#一个季度油品销售额趋势图
class OilQuarterTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.OilQuarterTrendReport

#当月加油量同比趋势图
class OilYoYTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.OilYoYTrendReport

#加油量趋势对比分析
class OilTrendBetweenTwoDaysDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.OilTrendBetweenTwoDaysReport

#油品销售额占总销售额比例
class OilToTotalSalesTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比（单位：%）")
    report_interface = reports.OilToTotalSalesTrendDashlet

#油非比
class OilAndStorePercentTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比（单位：%）")
    report_interface = reports.OilAndStorePercentTrendReport

#当日油枪效率
class GunPumpTimeDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"时间(单位：分钟)")
    report_interface = reports.GunPumpTimeDailyTrendReport

#当月油枪效率
class GunPumpTimeMonthTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"时间(单位：分钟)")
    report_interface = reports.GunPumpTimeMonthTrendReport

#油枪效率鸟瞰图
class GunPumpTimeAerialViewTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u'时间(单位：分钟)')
    report_interface = reports.ThreeDimensionalReport

#月平均加油量
class OilMonthAvgTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"加油量(单位：升)")
    report_interface = reports.OilMonthAvgTrendReport

#油品加满率
class OilFullRateDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比(单位：%)")
    report_interface = reports.OilFullRateDashletReport

#高峰期出油效率
class CrestDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"时间(单位：分钟)")
    report_interface = reports.CrestDailyTrendReport

#当日油机效率
class GunMachineTimeDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"时间(单位：分钟)")
    report_interface = reports.GunMachineTimeDailyTrendReport

#当日通道效率
class PassageTimeDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"时间(单位：分钟)")
    report_interface = reports.PassageTimeDailyTrendReport

#高峰期时段定义
class StationPeakPeriodTimeDefinedDashlet(ui.Dashlet):
    label = ugettext_lazy(u"指标")
    render_as = "table"
    report_interface = reports.StationPeakPeriodTimeDefinedReport

#sku总数
class GoodsSKUCountDashlet(ui.Dashlet):
    label = ugettext_lazy(u"指标")
    render_as = "table"
    report_interface = reports.GoodsSKUCountReport

#当日非油品销售额趋势图
class GoodsSalesDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.GoodsSalesDailyTrendReport

#当日销售额客单值
class GoodsSalesPerPeopleDailyTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.GoodsSalesPerPeopleDailyTrendReport

#当月非油品销售排行
class GoodsRankMonthTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"非油品名")
    render_as = "table"
    report_interface = reports.GoodsRankMonthTrendReport

#油非转化率
class OilAndNonOilConversionDashlet(ui.Dashlet):
    label = ugettext_lazy(u'油非转化率')
    report_interface = reports.OilAndNonOilConversionDashletReport

#当月销售额趋势图
class GoodsTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.GoodsTrendReport

#近一季度非油品销售额趋势图
class GoodsQuarterTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.GoodsQuarterTrendReport

#当月销售额环比趋势图
class GoodsMoMTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.GoodsMoMTrendReport

#当月销售额同比趋势图
class GoodsYoYTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.GoodsYoYTrendReport

#销售额趋势对比分析
class GoodsTrendBetweenTwoDaysDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销售额(单位：元)")
    report_interface = reports.GoodsTrendBetweenTwoDaysReport

#油品与非油品交易比例
class OilGoodsProportionDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比(单位：%)")
    report_interface = reports.OilGoodsProportionReport

#油品与非油品相关性
class OilGoodsAssocDashlet(ui.Dashlet):
    label = ugettext_lazy(u"非油品")
    render_as = "table"
    report_interface = reports.OilGoodsAssocReport

#非油品之间的相关性
class BetweenGoodsAssocDashlet(ui.Dashlet):
    label = ugettext_lazy(u"非油品")
    render_as = "table"
    report_interface = reports.BetweenGoodsAssocReport

#当前持卡客户总数
class CustomerVIPCounterDashlet(ui.Dashlet):
    label = ugettext_lazy(u"指标")
    render_as = "table"
    report_interface = reports.CustomerVIPCounterReport

#阶段性活跃持卡数量
class CustomerVIPCounterByDateDashlet(ui.Dashlet):
    label = ugettext_lazy(u"指标")
    render_as = "table"
    report_interface = reports.CustomerVIPCounterByDateReport

#当月忠诚客户比例
class CustomerVIPLoyaltyProportionDashlet(ui.Dashlet):
    label = ugettext_lazy(u"指标")
    render_as = "table"
    report_interface = reports.CustomerVIPLoyaltyProportionReport

#持卡客户消费趋势
class CustomerVIPCostTrendProportionDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比（单位：%）")
    render_as = "table"
    report_interface = reports.CustomerVIPCostTrendProportionReport

#近一年忠诚客户比例趋势
class CustomerVIPMonthlyLoyaltyDashlet(ui.Dashlet):
    label = ugettext_lazy(u"百分比（单位：%）")
    report_interface = reports.CustomerVIPMonthlyLoyaltyReport

#客户消费趋势
class CustomerCostTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"销费额(单位：元)")
    report_interface = reports.CustomerCostTrendReport

#指数
class PumpDailyAvgDashlet(ui.Dashlet):
    label = ugettext_lazy(u"日均加油量")
    report_interface = reports.PumpDailyAvgReport

class PumpHourlyAvgDashlet(ui.Dashlet):
    label = ugettext_lazy(u"每小时平均加油量")
    report_interface = reports.PumpHourlyAvgReport

class PumpMonthlyAvgDashlet(ui.Dashlet):
    label = ugettext_lazy(u"月均加油量")
    report_interface = reports.PumpMonthlyAvgReport

class TransCountAvgDashlet(ui.Dashlet):
    label = ugettext_lazy(u"每小时平均进站车辆数")
    report_interface = reports.TransCountAvgReport

class GunPumpAvgDashlet(ui.Dashlet):
    label = ugettext_lazy(u"油枪平均每小时工作时间")
    report_interface = reports.GunPumpAvgReport

class NonFuelSalesAvgDashlet(ui.Dashlet):
    label = ugettext_lazy(u"非油品平均每小时销售额")
    report_interface = reports.NonFuelSalesAvgReport

class GoodsMonthAvgTrendDashlet(ui.Dashlet):
    label = ugettext_lazy(u"当月非油品24小时平均销售额")
    report_interface = reports.GoodsMonthAvgTrendReport

class NonFuelSalesScaleDashlet(ui.Dashlet):
    label = ugettext_lazy(u"非油品平均每小时交易比例")
    report_interface = reports.NonFuelSalesScaleReport

class Top10NonFuelSalesAvgDashlet(ui.Dashlet):
    label = ugettext_lazy(u"Top10非油品平均每小时销售额")
    report_interface = reports.Top10NonFuelSalesAvgReport

class CustomerMonthlyLoyaltyDashlet(ui.Dashlet):
    label = ugettext_lazy(u"忠实客户比例变化")
    report_interface = reports.CustomerMonthlyLoyaltyReport

class CustomerMonthlyLeaveDashlet(ui.Dashlet):
    label = ugettext_lazy(u"忠实客户流失率变化")
    report_interface = reports.CustomerMonthlyLeaveReport

class CustomerMonthlySalesScaleDashlet(ui.Dashlet):
    label = ugettext_lazy(u"忠实客户销售额占比变化")
    report_interface = reports.CustomerMonthlySalesScaleReport

class FuelAssocDashlet(ui.Dashlet):
    label = ugettext_lazy(u"油品")
    report_interface = reports.FuelAssocReport

#健康诊断
class HealthDashlet(ui.Dashlet):
    label = ugettext_lazy(u"健康指标")
    render_as = "table"
    report_interface = reports.HealthReport

#测试瓶颈
class BottleneckDashlet(ui.Dashlet):
    label = ugettext_lazy(u"性能瓶颈")
    report_interface = reports.BottleneckReport

#
class MultiStationHealthDashlet(ui.Dashlet):
    label = ugettext_lazy(u"健康指标")
    render_as = "table"
    report_interface = reports.MultiStationHealthReport
