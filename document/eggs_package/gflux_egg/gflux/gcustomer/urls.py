#coding=utf-8
from django.conf.urls import patterns, include, url
from django.conf import settings
import pdb,os,sys

#page view
urlpatterns = patterns('gcustomer.apps.gcustomer.page_views',
    url(r'^%s$' % settings.GCUSTOMER_URL_PREFIX,"gcustomer_home_view"),
    
    url(r'^%speople/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_home_view"),
    
    #login
    url(r'^%slogin/$'% settings.GCUSTOMER_URL_PREFIX,"login_page"),
    
    #register
    url(r'^%sregister/$'% settings.GCUSTOMER_URL_PREFIX,"register_page"),
    
    # 客户管理
    url(r'^%sgcustomer_manage/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_manage_page"),
    
    # 消费习惯
    url(r'^%sconsumption_habits/$'%settings.GCUSTOMER_URL_PREFIX,"consumption_habits_page"),
    
    # 消费预测
    url(r'^%sconsumption_forecase/$'%settings.GCUSTOMER_URL_PREFIX,"consumption_forecase_page"),
    
    # 贡献价值
    url(r'^%scontribution/$'%settings.GCUSTOMER_URL_PREFIX,"contribution_page"),
    
    # 创建群
    url(r'^%screate_group/$'%settings.GCUSTOMER_URL_PREFIX,"create_group_page"),
    
    # 已有群
    url(r'^%sgroup_page/$'%settings.GCUSTOMER_URL_PREFIX,"group_page"),
    
    # 广告接入
    url(r'^%sgcustomer_advert/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_advert_page"),
    
    # 油站画像
    url(r'^%sgcustomer_station/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_station_page"),
    
    # 运营效率
    url(r'^%sstation_operation_efficiency/$'% settings.GCUSTOMER_URL_PREFIX,"station_operation_efficiency_page"),
    
    # 油品销售
    url(r'^%sfuel_sale/$'% settings.GCUSTOMER_URL_PREFIX,"fuel_sale_page"),
    
    #创建群
    url(r'^%screate_station_group/$'% settings.GCUSTOMER_URL_PREFIX,"create_station_group_page"),
    
    #已有群
    url(r'^%sstation_group/$'% settings.GCUSTOMER_URL_PREFIX,"station_group_page"),

    #我的油站
    url(r'^%smy_station_list/$'% settings.GCUSTOMER_URL_PREFIX,"my_station_list_page"),
    
    #主要客户
    url(r'^%smain_customer_list/$'% settings.GCUSTOMER_URL_PREFIX,"main_customer_list_page"),
    
    #非油品销售情况
    url(r'^%snonfuel_sale/$'% settings.GCUSTOMER_URL_PREFIX,"nonfuel_sale_page"),
    
    # 营销活动
    url(r'^%sgcustomer_activity/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_activity_page"),
    
    # 开始活动
    url(r'^%sstart_activity/$'% settings.GCUSTOMER_URL_PREFIX,"start_activity_page"),
    
    # 通知客户
    url(r'^%sgcustomer_notice_page/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_notice_page"),
    
    # 显示活动
    url(r'^%sshow_activity/$'% settings.GCUSTOMER_URL_PREFIX,"show_activity_page"),
    
    # 停止活动
    url(r'^%sstop_activity/$'% settings.GCUSTOMER_URL_PREFIX,"stop_activity_page"),
    
    # 沟通设置页面
    url(r'^%scontact_settings/$'% settings.GCUSTOMER_URL_PREFIX,"contact_settings_page"),
    
    #短信设置
    url(r'^%sshort_message_settings/$'% settings.GCUSTOMER_URL_PREFIX,"short_message_settings_page"),
    
    #客户经理
    url(r'^%scustomer_manager_settings/$'% settings.GCUSTOMER_URL_PREFIX,"customer_manager_settings_page"),
    
    # 已有广告页面
    url(r'^%sshow_advert/$'% settings.GCUSTOMER_URL_PREFIX,"show_advert_page"),
    
    # 上传广告页面
    url(r'^%supload_advert/$'% settings.GCUSTOMER_URL_PREFIX,"upload_advert_page"),
    
    # 广告统计
    url(r'^%sadvert_count/$'% settings.GCUSTOMER_URL_PREFIX,"advert_count_page"),
    
    # 广告转化
    url(r'^%sadvert_convert/$'% settings.GCUSTOMER_URL_PREFIX,"advert_convert_page"),
    
    # advert goods launch 
    url(r'^%sgoods_launch/$'% settings.GCUSTOMER_URL_PREFIX,"goods_launch_page"),
    
    # advert repair launch
    url(r'^%srepair_launch/$'% settings.GCUSTOMER_URL_PREFIX,"repair_launch_page"),
    
    # advert maintenance_launch 
    url(r'^%smaintenance_launch/$'% settings.GCUSTOMER_URL_PREFIX,"maintenance_launch_page"),
    
    # 创建新客户
    url(r'^%screate_customer/$'% settings.GCUSTOMER_URL_PREFIX,"create_customer_page"),
    
    # 管理大客户
    url(r'^%smanage_customer/$'% settings.GCUSTOMER_URL_PREFIX,"manage_customer_page"),
    
    # 大客户贡献
    url(r'^%scustomer_contribution/$'% settings.GCUSTOMER_URL_PREFIX,"customer_contribution_page"),
    
    # 用户等级积分
    url(r'^%scustomer_grade/$'% settings.GCUSTOMER_URL_PREFIX,"customer_grade_page"),
    
    # 客户信息主页
    url(r'^%sgcustomer_info/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_info_page"),
    
    # gcustomer admin界面
    url(r'^%sgcustomer_admin/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_admin_page"),
    
    #upload_app_img_page
    url(r'^%supload_app_img_page/$'% settings.GCUSTOMER_URL_PREFIX,"upload_app_img_page"),
    
    #advert_launch_setting
    url(r'^%sadvert_launch_setting/$'% settings.GCUSTOMER_URL_PREFIX,"advert_launch_setting_page"),
    
    #大客户统计
    url(r'^%scustomer_statistics/$'% settings.GCUSTOMER_URL_PREFIX,"customer_statistics_page"),
    
    #加油卡消费统计
    url(r'^%scustomer_consume_statistics/$'% settings.GCUSTOMER_URL_PREFIX,"customer_consume_statistics_page"),
    #添加商品
    url(r'^%sadd_store_items/$'% settings.GCUSTOMER_URL_PREFIX,"add_store_items"),
    #管理商品
    url(r'^%sshow_store_items/$'% settings.GCUSTOMER_URL_PREFIX,"show_store_items"),
    #积分设置
    url(r'^%sgcustomer_score/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_score"),

    #score_rule_settings
    url(r'^%sscore_rule_setting/$'% settings.GCUSTOMER_URL_PREFIX,"score_rule_setting"),

    #score_rule_settings
    url(r'^%sscore_level_setting/$'% settings.GCUSTOMER_URL_PREFIX,"score_level_setting"),

    #score_rule_settings
    url(r'^%sscore_query/$'% settings.GCUSTOMER_URL_PREFIX,"score_query"),
    #score_exchange
    url(r'^%sscore_exchange/$'% settings.GCUSTOMER_URL_PREFIX,"score_exchange"),
    #gcustomer_goods
    url(r'^%sgcustomer_goods/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_goods_page"),
    #score_member
    url(r'^%sscore_member/$'% settings.GCUSTOMER_URL_PREFIX,"score_member"),
    #行车轨迹
    url(r'^%sdriving_track/$'% settings.GCUSTOMER_URL_PREFIX,"driving_track"),

    #订单管理
    url(r'^%sgcustomer_order/$'% settings.GCUSTOMER_URL_PREFIX,"gcustomer_order"),
    #订单流水
    url(r'^%smy_order_list/$'% settings.GCUSTOMER_URL_PREFIX,"my_order_list"),
    #退款处理
    url(r'^%srefund_process/$'% settings.GCUSTOMER_URL_PREFIX,"refund_process"),
    #system_settings
    url(r'^%ssystem_settings/$'% settings.GCUSTOMER_URL_PREFIX,"system_settings"),
)

#初始化ajax view
urlpatterns += patterns('gcustomer.apps.gcustomer.ajax_views',
    url(r'^%sajax/get_user_profile/$' % settings.GCUSTOMER_URL_PREFIX,'get_user_profile'),
    
    #big_customer_manage
    url(r'^%sajax/big_customer_manage/$'% settings.GCUSTOMER_URL_PREFIX,'big_customer_manage'),

    #show activity
    url(r'^%sajax/show_activity/$'% settings.GCUSTOMER_URL_PREFIX,'show_activity'),
    
    #completed_activity
    url(r'^%sajax/completed_activity/$'% settings.GCUSTOMER_URL_PREFIX,'completed_activity'),
    
    #get_station_information
    #url(r'^%sajax/get_station_information/$'% settings.GCUSTOMER_URL_PREFIX,'get_station_information'),
    
    #get_advertisement_list
    url(r'^%sajax/get_advertisement_list/$'% settings.GCUSTOMER_URL_PREFIX,'get_advertisement_list'),
    
    #get_advertisement_information
    url(r'^%sajax/get_advertisement_information/$'% settings.GCUSTOMER_URL_PREFIX,'get_advertisement_information'),

    #delete_advertisement
    url(r'%sajax/delete_advertisement/$' % settings.GCUSTOMER_URL_PREFIX, 'delete_advertisement'),
    
    #get_activity_data
    url(r'^%sajax/get_activity_data/$'% settings.GCUSTOMER_URL_PREFIX,'get_activity_data'),
    
    #get_main_customer_list
    url(r'^%sajax/get_main_customer_list/$'% settings.GCUSTOMER_URL_PREFIX,'get_main_customer_list'),
    
    #create_commodity
    url(r'^%sajax/create_commodity/$' % settings.GCUSTOMER_URL_PREFIX, 'create_commodity'),

    #auto_create_commodity
    url(r'^%sajax/auto_create_commodity/$' % settings.GCUSTOMER_URL_PREFIX, 'auto_create_commodity'),

    #create station
    url(r'^%sajax/create_station/$' % settings.GCUSTOMER_URL_PREFIX,'create_station'),

    #get_station_list
    url(r'%sajax/get_station_list/$' % settings.GCUSTOMER_URL_PREFIX,'get_station_list'),

    #get_station_detail
    url(r'%sajax/get_station_detail/$' % settings.GCUSTOMER_URL_PREFIX,'get_station_detail'),

    #modify_detail_station
    url(r'%sajax/modify_detail_station/$' % settings.GCUSTOMER_URL_PREFIX,'modify_detail_station'),

    #delete_station
    url(r'%sajax/delete_station/$' % settings.GCUSTOMER_URL_PREFIX,'delete_station'),

    #get_goods_list
    url(r'^%sajax/get_goods_list/$' % settings.GCUSTOMER_URL_PREFIX, 'get_goods_list'),

    #delete_goods
    url(r'^%sajax/delete_goods/$' % settings.GCUSTOMER_URL_PREFIX, 'delete_goods'),

    #modify_goods_detail
    url(r'^%sajax/modify_goods_detail/$' % settings.GCUSTOMER_URL_PREFIX, 'modify_goods_detail'),

    #get_goods_detail
    url(r'^%sajax/get_goods_detail/$' % settings.GCUSTOMER_URL_PREFIX, 'get_goods_detail'),

    #create_advertisement
    url(r'^%sajax/create_advertisement/$'% settings.GCUSTOMER_URL_PREFIX,'create_advertisement'),
    
    #render_image
    url(r'^%sajax/render_image/$'% settings.GCUSTOMER_URL_PREFIX,'render_image'),
    
    #create_group
    url(r'^%sajax/create_group/$'% settings.GCUSTOMER_URL_PREFIX,'create_group'),
    
    #create_promotion_activity
    url(r'^%sajax/create_promotion_activity/$'% settings.GCUSTOMER_URL_PREFIX,'create_promotion_activity'),
    
    #upload_app_img
    url(r'^%sajax/upload_app_img/$'% settings.GCUSTOMER_URL_PREFIX,'upload_app_img'),

    #upload_cards_file
    url(r'^%sajax/upload_cards_file/$' % settings.GCUSTOMER_URL_PREFIX, 'upload_cards_file'),

    #create service advertisement
    url(r'%sajax/create_service_advertisement/$' % settings.GCUSTOMER_URL_PREFIX, 'create_service_advertisement'),

    #get_service_advertisement
    url(r'%sajax/get_service_advertisement/$' % settings.GCUSTOMER_URL_PREFIX, 'get_service_advertisement'),

    #get_detail_advertisement
    url(r'%sajax/get_detail_advertisement/$' % settings.GCUSTOMER_URL_PREFIX, 'get_detail_advertisement'),

    #modify_detail_advertisement
    url(r'%sajax/modify_detail_advertisement/$' % settings.GCUSTOMER_URL_PREFIX, 'modify_detail_advertisement'),

    #delete_goods_advertisement
    url(r'%sajax/delete_goods_advertisement/$' % settings.GCUSTOMER_URL_PREFIX, 'delete_goods_advertisement'),
    
    #create big customer
    url(r'^%sajax/create_big_customer/$'% settings.GCUSTOMER_URL_PREFIX,'create_big_customer'),
    
    #get_consume_record
    url(r'^%sajax/get_consume_record/$'% settings.GCUSTOMER_URL_PREFIX,'get_consume_record'),
    
    #get_slave_consume_record
    url(r'^%sajax/get_slave_consume_record/$'% settings.GCUSTOMER_URL_PREFIX,'get_slave_consume_record'),
    
    #get_customer_group_info
    url(r'^%sajax/get_customer_group_info/$'% settings.GCUSTOMER_URL_PREFIX,'get_customer_group_info'),

    #get_customer_group_detail
    url(r'^%sajax/get_customer_group_detail/$' % settings.GCUSTOMER_URL_PREFIX,'get_customer_group_detail'),

    #delete_customer_group
    url(r'^%sajax/delete_customer_group/$'% settings.GCUSTOMER_URL_PREFIX,'delete_customer_group'),
    
    #create_station_group
    url(r'^%sajax/create_station_group/$'% settings.GCUSTOMER_URL_PREFIX,'create_station_group'),
    
    #get_station_group_info
    url(r'^%sajax/get_station_group_info/$'% settings.GCUSTOMER_URL_PREFIX,'get_station_group_info'),

    #get_station_group_detail
    url(r'^%sajax/get_station_group_detail/$' % settings.GCUSTOMER_URL_PREFIX, 'get_station_group_detail'),

    #delete_station_group
    url(r'^%sajax/delete_station_group/$'% settings.GCUSTOMER_URL_PREFIX,'delete_station_group'),
    
    #create activity
    url(r'^%sajax/create_promotion_activity/$'% settings.GCUSTOMER_URL_PREFIX,'create_promotion_activity'),

    #get_target_audience
    url(r'^%sajax/get_target_audience/$' % settings.GCUSTOMER_URL_PREFIX, 'get_target_audience'),
    
    #get_advert_cycle_setting_info
    url(r'^%sajax/get_advert_cycle_setting_info/$'% settings.GCUSTOMER_URL_PREFIX,'get_advert_cycle_setting_info'),

    #modify_advert_cycle_setting_info
    url(r'^%sajax/modify_advert_cycle_setting_info/$' % settings.GCUSTOMER_URL_PREFIX, 'modify_advert_cycle_setting_info'),
    
    #get_promotion_goods_map
    url(r'^%sajax/get_promotion_goods_map/$' % settings.GCUSTOMER_URL_PREFIX, 'get_promotion_goods_map'),

    #get_station_group_list
    url(r'^%sajax/get_station_group_list/$' % settings.GCUSTOMER_URL_PREFIX, 'get_station_group_list'),

    #update_score_rule
    url(r'^%sajax/update_score_rule/$' % settings.GCUSTOMER_URL_PREFIX, 'update_score_rule'),
    #get_good_score_ratio
    url(r'^%sajax/get_good_score_ratio/$' % settings.GCUSTOMER_URL_PREFIX, 'get_good_score_ratio'),
    #alter_good_score_ratio
    url(r'^%sajax/alter_good_score_ratio/$' % settings.GCUSTOMER_URL_PREFIX, 'alter_good_score_ratio'),
    #alter_level_score_ratio
    url(r'^%sajax/alter_level_score_ratio/$' % settings.GCUSTOMER_URL_PREFIX, 'alter_level_score_ratio'),
    #get_score_level_info
    url(r'^%sajax/get_score_level_info/$' % settings.GCUSTOMER_URL_PREFIX, 'get_score_level_info'),
    #get_exchange_good_info
    url(r'^%sajax/get_exchange_good_info/$' % settings.GCUSTOMER_URL_PREFIX, 'get_exchange_good_info'),
    #get_member_good_info
    url(r'^%sajax/get_member_good_info/$' % settings.GCUSTOMER_URL_PREFIX, 'get_member_good_info'),
    #delete_member_good
    url(r'^%sajax/delete_member_good/$' % settings.GCUSTOMER_URL_PREFIX, 'delete_member_good'),
    #get_score_record_details
    url(r'^%sajax/get_score_record_details/$' % settings.GCUSTOMER_URL_PREFIX, 'get_score_record_details'),
    #update_activity_status
    url(r'^%sajax/update_activity_status/$' % settings.GCUSTOMER_URL_PREFIX, 'update_activity_status'),
    #jquery_upload_images
    url(r'^%sajax/jquery_upload_images/$' % settings.GCUSTOMER_URL_PREFIX, 'jquery_upload_images'),
    #add_exchange_score_good
    url(r'^%sajax/add_exchange_score_good/$' % settings.GCUSTOMER_URL_PREFIX, 'add_exchange_score_good'),
    #get_station_fuel
    url(r'^%sajax/get_station_fuel/$' % settings.GCUSTOMER_URL_PREFIX, 'get_station_fuel'),
    #delete_promotion_activity
    url(r'^%sajax/delete_promotion_activity/$' % settings.GCUSTOMER_URL_PREFIX, 'delete_promotion_activity'),
    #add_member_good
    url(r'^%sajax/add_member_good/$' % settings.GCUSTOMER_URL_PREFIX, 'add_member_good'),
    #alter_good_member_discount
    url(r'^%sajax/alter_good_member_discount/$' % settings.GCUSTOMER_URL_PREFIX, 'alter_good_member_discount'),
    #get_user_driving_trace
    url(r'^%sajax/get_user_driving_trace/$' % settings.GCUSTOMER_URL_PREFIX, 'get_user_driving_trace'),
    #promotion_good_list
    url(r'^%sajax/promotion_good_list/$' % settings.GCUSTOMER_URL_PREFIX, 'promotion_good_list'),
    #get_promotion_goods_lanch_info
    url(r'^%sajax/get_promotion_goods_lanch_info/$' % settings.GCUSTOMER_URL_PREFIX, 'get_promotion_goods_lanch_info'),
    #获取公司类型
    url(r'^%sajax/get_comp_type/$' % settings.GCUSTOMER_URL_PREFIX, 'get_comp_type'),
    #获取公司
    url(r'^%sajax/get_comp_list/$' % settings.GCUSTOMER_URL_PREFIX, 'get_comp_list'),
    #get_app_user_setting
    url(r'^%sajax/get_app_user_setting/$' % settings.GCUSTOMER_URL_PREFIX, 'get_app_user_setting'),
    #alter_app_user_settting
    url(r'^%sajax/alter_app_user_settting/$' % settings.GCUSTOMER_URL_PREFIX, 'alter_app_user_settting'),
    #查询退款订单
    url(r'^%sajax/get_refund_order_info/$' % settings.GCUSTOMER_URL_PREFIX, 'get_refund_order_info'),
    #确认退款
    url(r'^%sajax/confirm_order_refund/$' % settings.GCUSTOMER_URL_PREFIX, 'confirm_order_refund'),
    #第三方回调
    url(r'^jcbpay/ajax/purchase_complete_by_the_third/', 'purchase_complete_by_the_third'),
    #获取公司订单列表
    url(r'^%sajax/get_comp_order_list/$' % settings.GCUSTOMER_URL_PREFIX, 'get_comp_order_list'),
    #根据用户虚拟卡号查询订单
    url(r'^%sajax/search_order_by_vcard_id/$' % settings.GCUSTOMER_URL_PREFIX, 'search_order_by_vcard_id'),
    #alter_advert_setting
    url(r'^%sajax/alter_advert_setting/$' % settings.GCUSTOMER_URL_PREFIX, 'alter_advert_setting'),
    #get_app_user_favourite_goods
    url(r'^%sajax/get_app_user_favourite_goods/$' % settings.GCUSTOMER_URL_PREFIX, 'get_app_user_favourite_goods'),
    #language_type_setting
    url(r'^%sajax/language_type_setting/$' % settings.GCUSTOMER_URL_PREFIX, 'language_type_setting'),
    #
    url(r'^%sajax/get_user_feed_back/$' % settings.GCUSTOMER_URL_PREFIX, 'get_user_feed_back'),
)

#初始化user_views
urlpatterns += patterns('gcustomer.apps.gcustomer.user_views',

    url(r'^%sajax/check_login/$' % settings.GCUSTOMER_URL_PREFIX,'check_login'),
    
    url(r'^%sajax/check_register/$' % settings.GCUSTOMER_URL_PREFIX,'check_register'),
    
    url(r'^%sajax/logout/$' % settings.GCUSTOMER_URL_PREFIX,'LogoutRequest'),
    
    url(r'^%sajax/get_china_location/$' % settings.GCUSTOMER_URL_PREFIX,'get_china_location'),

    #获取系统用户
    url(r'^%sajax/get_system_user_list/$'% settings.GCUSTOMER_URL_PREFIX,'get_system_user_list'),

    #获取石油公司管理员用户
    url(r'^%sajax/get_all_comp_user_list/$'% settings.GCUSTOMER_URL_PREFIX,'get_all_comp_user_list'),
    # admin 获取app用户列表hu
    url(r'^%sajax/get_app_user_list/$'% settings.GCUSTOMER_URL_PREFIX,'get_app_user_list'),
    
    url(r'^%sajax/admin_change_user_type/$'% settings.GCUSTOMER_URL_PREFIX,'change_user_type'),

    url(r'^%sajax/change_app_user_type/$'% settings.GCUSTOMER_URL_PREFIX,'change_app_user_type'),
    #alter_user_password
    url(r'^%sajax/alter_user_password/$' % settings.GCUSTOMER_URL_PREFIX, 'alter_user_password'),
)

#jiachebao app url

urlpatterns += patterns('gcustomer.apps.jiachebao.api_views',
    url(r'^%sapi/$' % settings.APP_URL_PREFIX,"jiachebao_api_router"),
)

#jiayouyuan app url
urlpatterns += patterns('gcustomer.apps.jiayouyuan.api_views',
    url(r'^%sjiayouyuan_api/$' % settings.APP_URL_PREFIX,"jiayouyuan_api_router"),
)

#shout app url
urlpatterns += patterns('gcustomer.apps.shout.api_views',
    url(r'^%sshout_api/$'%settings.APP_URL_PREFIX,"shout_api_router"),
)

#初始化 crud view
urlpatterns += patterns('gcustomer.apps.gcustomer.crud_views',
    #副卡信息
    url(r'^%sajax/create_slave_card/$'%settings.GCUSTOMER_URL_PREFIX,'create_slave_card'),
    url(r'^%sajax/get_slave_card/$'%settings.GCUSTOMER_URL_PREFIX,'get_slave_card'),
    url(r'^%sajax/update_slave_card/$'%settings.GCUSTOMER_URL_PREFIX,'update_slave_card'),
    url(r'^%sajax/delete_slave_card/$'%settings.GCUSTOMER_URL_PREFIX,'delete_slave_card'),
)


urlpatterns += patterns('gcustomer.apps.gcustomer.cache_views',
        url(r'^%sajax/cache_customer_group_objs/$'%settings.GCUSTOMER_URL_PREFIX,'download_in_cache'),
    )