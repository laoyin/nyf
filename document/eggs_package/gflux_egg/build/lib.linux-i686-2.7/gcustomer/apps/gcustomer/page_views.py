#encoding=utf-8
from django.shortcuts import *
from django.http import *
import pdb
from gcustomer.utils import *
from gcustomer import models
from gflux import settings
from gflux.util import *
from django.views.decorators.cache import cache_page
from django.conf import settings
from gcustomer.status  import * 
#登录
def login_page(request):
    return render(request,'gcustomer/login.html',{'settings':settings})
#注册
def register_page(request):
    return render(request,'gcustomer/register.html',{'settings':settings})

#登录成功
def login_success_page(request):
    return render(request,'gcustomer/gcustomer_frame.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#客户营销与分析首页
def gcustomer_home_view(request):
    return render(request,'gcustomer/gcustomer_frame.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 人群分析
def gcustomer_pupulation__portal_view(request):
    return render(request,'gcustomer/home.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 新建页面
def create_new_activity(request):
    return render(request,'gcustomer/create_activity_page.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 系统首页
def gcustomer_index(request):
    return render(request,'gcustomer/gcustomer_frame.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 广告投放页面
def gcustomer_advert_page(request):
    return render(request,'gcustomer/gcustomer_advert.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#商品管理
# @cache_page(60 * 15)
def gcustomer_goods_page(request):
    return render(request,'gcustomer/gcustomer_goods.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 油站画像页面
# @cache_page(60 * 15)
def gcustomer_station_page(request):
    return render(request,'gcustomer/gcustomer_station.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#非油品销售情况
def nonfuel_sale_page(request):
    return render(request,'gcustomer/nonfuel_sale.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#主要客户
def main_customer_list_page(request):
        return render(request,'gcustomer/main_customer_list.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 营销活动页面
#@cache_page(60 * 15)
def gcustomer_activity_page(request):
    return render(request,'gcustomer/gcustomer_activity.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#时间转换
#时间字符串转化为时间戳
def stringToTimeStamp(timestr):
    timearray=time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    timestamp=int(time.mktime(timearray))
    return timestamp

#客户管理页面
# @cache_page(60 * 15)
def gcustomer_manage_page(request):
    return render(request,'gcustomer/gcustomer_manage.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':settings.SHOW_OPTION})

#消费习惯
def consumption_habits_page(request):
    return render(request,'gcustomer/consumption_habits.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':settings.SHOW_OPTION})

#消费预测
def consumption_forecase_page(request):
    return render(request,'gcustomer/consumption_forecase.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':settings.SHOW_OPTION})

#贡献价值
def contribution_page(request):
    return render(request,'gcustomer/contribution.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':settings.SHOW_OPTION})

#创建群
def create_group_page(request):
    return render(request,'gcustomer/create_group_page.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':settings.SHOW_OPTION})

#已有群
def group_page(request):
    return render(request,'gcustomer/group_page.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':settings.SHOW_OPTION})

# 创建营销活动页面
def start_activity_page(request):
    return render(request,'gcustomer/start_activity.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#通知客户
def gcustomer_notice_page(request):
    return render(request,'gcustomer/contact_settings.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 显示活动状态页面
def show_activity_page(request):
    return render(request,'gcustomer/show_activity.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 结束活动界面
def stop_activity_page(request):
    return render(request,'gcustomer/stop_activity.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 邮件设置页面
def contact_settings_page(request):
    return render(request,'gcustomer/email_setting.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#短信设置
def short_message_settings_page(request):
    return render(request,'gcustomer/short_message_setting.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

def customer_manager_settings_page(request):
    return render(request,'gcustomer/customer_manage.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 已有广告页面
@cache_page(60 * 15)
def show_advert_page(request):
    return render(request,'gcustomer/show_advert.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 添加商品
def add_store_items(request):
    return render(request,'gcustomer/add_store_items.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 管理商品
def show_store_items(request):
    return render(request,'gcustomer/show_store_items.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#货运
def goods_launch_page(request):
    return render(request,'gcustomer/advert_goods_launch.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#维修
def repair_launch_page(request):
    return render(request,'gcustomer/advert_repair_launch.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#保养
def maintenance_launch_page(request):
    return render(request,'gcustomer/advert_maintenance_launch.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 上传广告页面
def upload_advert_page(request):
    return render(request,'gcustomer/upload_advert.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 广告统计页面
def advert_count_page(request):
    return render(request,'gcustomer/advert_count.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 转化销量
def advert_convert_page(request):
    return render(request,'gcustomer/advert_convert.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 创建大客户
def create_customer_page(request):
    return render(request,'gcustomer/create_customer.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':1})

# 管理大客户
def manage_customer_page(request):
    return render(request,'gcustomer/manage_customer.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':1})

# 客户贡献
def customer_contribution_page(request):
    return render(request,'gcustomer/customer_contribution.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':1})

# 客户积分
def customer_grade_page(request):
    return render(request,'gcustomer/customer_grade.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

# 客户信息主页
def gcustomer_info_page(request):
    return render(request,'gcustomer/gcustomer_info.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#用户管理界面
def gcustomer_admin_page(request):
    return render(request,'gcustomer/gcustomer_admin.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#油站营运效率
def station_operation_efficiency_page(request):
    return render(request,'gcustomer/station_operation_efficiency.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#油品销售
def fuel_sale_page(request):
    return render(request,'gcustomer/fuel_sale.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#创建油站群
def create_station_group_page(request):
    return render(request,'gcustomer/create_station_group.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#油站群页面
def station_group_page(request):
    return render(request,'gcustomer/station_group.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

def my_station_list_page(request):
    return render(request,'gcustomer/my_station_page.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#上传图片
def upload_app_img_page(request):
    return render(request,'gcustomer/upload_app_img.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#广告周期页面
def advert_launch_setting_page(request):
    return render(request,'gcustomer/advert_launch_setting.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#用户统计页面
def customer_statistics_page(request):
    return render(request,'gcustomer/customer_statistics.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':1})

#加油卡消费统计
def customer_consume_statistics_page(request):
    return render(request,'gcustomer/customer_consume_statistics.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':1})

#积分设置
def gcustomer_score(request):
    return render(request,'gcustomer/gcustomer_score.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#积分规则设置
def score_rule_setting(request):
    return render(request,'gcustomer/score_rule_setting.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#积分等级设置
def score_level_setting(request):
    return render(request,'gcustomer/score_level_setting.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#积分查询
def score_query(request):
    return render(request,'gcustomer/score_query.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#积分兑换
def score_exchange(request):
    return render(request,'gcustomer/score_exchange.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#会员积分
def score_member(request):
    return render(request,'gcustomer/score_member.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#行车轨迹
def driving_track(request):
    return render(request,'gcustomer/driving_track.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'show_option':settings.SHOW_OPTION})

#订单管理
def gcustomer_order(request):
    return render(request,'gcustomer/gcustomer_order_page.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#订单流水
def my_order_list(request):
    return render(request,'gcustomer/order_list_page.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#退款处理
def refund_process(request):
    return render(request,'gcustomer/order_refund_page.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request)})

#系统设置
def system_settings(request):
    setting_type = int(request.GET['type'])
    return render(request,'gcustomer/system_settings.html',{'settings':settings,'user_type':get_user_type(request),'role':get_user_role(request),'setting_type':setting_type})