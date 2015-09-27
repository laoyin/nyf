#coding=utf-8
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
import pdb,os,sys

#初始化dash库
import dash
dash.core.reportor.autodiscover()
dash.core.site.autodiscover()
urlpatterns = patterns('',
    url(r'', include(dash.core.reportor.urls)),
    url(r'', include(dash.core.site.urls)),
    url(r'', include('gcustomer.urls')),
)

#初始化page view
urlpatterns += patterns('gflux.apps.station.page_views',
    url(r'^%s$' % settings.GFLUX_URL_PREFIX,"gflux_views"),
    url(r'^%slogin.html$' % settings.GFLUX_URL_PREFIX,"login_views"),
    url(r'^%sregister.html$' % settings.GFLUX_URL_PREFIX,"register_views"),
    url(r'^%sregister_success.html$' % settings.GFLUX_URL_PREFIX,"register_success_views"),
    url(r'^%sdemo.html$'% settings.GFLUX_URL_PREFIX,"demo_view"),
)

#初始化ajax view
urlpatterns += patterns('gflux.apps.station.ajax_views',
    url(r'^%sajax/update_password/$'%settings.GFLUX_URL_PREFIX,'UpdatePassword'),
    url(r'^%sajax/get_user_station/$' % settings.GFLUX_URL_PREFIX,'GetUserStation'),
    url(r'^%sajax/remove_user_site/$' % settings.GFLUX_URL_PREFIX,'RemoveUserStation'),
    url(r'^%sajax/add_user_site/$' % settings.GFLUX_URL_PREFIX,'AddUserStation'),
    url(r'^%sajax/get_station_fuel_type/$' % settings.GFLUX_URL_PREFIX,'GetStationFuelType'),
    url(r'^%sajax/professional_analysis/$' % settings.GFLUX_URL_PREFIX,'ProfessionalAnalysis'),
    url(r'^%sajax/check_login/$' % settings.GFLUX_URL_PREFIX,'checkLoginAjaxRequest'),
    url(r'^%sajax/check_register/$' % settings.GFLUX_URL_PREFIX,'checkRegisterAjaxRequest'),
    url(r'^%sajax/check_users/$' % settings.GFLUX_URL_PREFIX,'checkUsersAjaxRequest'),
    url(r'^%sajax/upload_file/$' % settings.GFLUX_URL_PREFIX,'uploadFileAjaxRequest'),
    url(r'^%sajax/check_uploaded_files/$' % settings.GFLUX_URL_PREFIX,'checkFilesAjaxRequest'),
    url(r'^%sajax/check_files/$' % settings.GFLUX_URL_PREFIX,'checkFilesAjaxRequest'),
    url(r'^%sajax/get_station_latest_earliest_date/$' % settings.GFLUX_URL_PREFIX,'GetStationLatestEarliestDate'),
    url(r'^%sajax/update_user_type/$'%settings.GFLUX_URL_PREFIX,'UpdateUserType'),
    url(r'^%sajax/logout/$' % settings.GFLUX_URL_PREFIX,'LogoutRequest'),
    url(r'^%sajax/importData/$' % settings.GFLUX_URL_PREFIX,'ImportData'),
    url(r'^%sajax/deleteFile/$' % settings.GFLUX_URL_PREFIX,'DeleteFile'),
    url(r'^%sajax/show_import_data_process/$' % settings.GFLUX_URL_PREFIX,'ShowImportDataProcess'),
    url(r'^%sajax/check_unique/$' % settings.GFLUX_URL_PREFIX,'checkUnique'),
    url(r'^%sajax/set_language/$' % settings.GFLUX_URL_PREFIX,'setLanguage'),
    url(r'^%sajax/get_guns_id/$' % settings.GFLUX_URL_PREFIX,'getGusIdBySite'),
    url(r'^%sajax/add_channel_machine/$' % settings.GFLUX_URL_PREFIX,'addChannelOrMachineAjax'),
    url(r'^%sajax/get_channel_machine/$' % settings.GFLUX_URL_PREFIX,'getChannelAndMachineAjax'),
    url(r'^%sajax/del_channel/$' % settings.GFLUX_URL_PREFIX,'delChannelAjax'),
    url(r'^%sajax/del_machine/$' % settings.GFLUX_URL_PREFIX,'delMachineAjax'),
    url(r'^%sajax/del_level/$' % settings.GFLUX_URL_PREFIX,'delLevelAjax'),
    url(r'^%sajax/del_column/$' % settings.GFLUX_URL_PREFIX,'delColumnAjax'),
    url(r'^%sajax/check_passage_machine_level_name/$' % settings.GFLUX_URL_PREFIX,'checkPassageMachineLevelName'),
    url(r'^%sajax/get_china_location/$' % settings.GFLUX_URL_PREFIX,'get_china_location'),
    url(r'^%sajax/get_info_by_sitename/$' % settings.GFLUX_URL_PREFIX,'getInfoBySiteName'),
    url(r'^%sajax/save_station_info/$' % settings.GFLUX_URL_PREFIX,'saveStationInfo'),
    url(r'^%sajax/edit_fuel_type_relation/$' % settings.GFLUX_URL_PREFIX,'editFuelTypeRelation'),
    url(r'^%sajax/remove_fuel_type_relation/$' % settings.GFLUX_URL_PREFIX,'removeFuelTypeRelation'),
    url(r'^%sajax/get_user_info/$' % settings.GFLUX_URL_PREFIX,'getUserInfo'),
    url(r'^%sajax/update_user_info/$' % settings.GFLUX_URL_PREFIX,'UpdateUserInfo'),
    url(r'^%sajax/export_table_to_xls/$'%settings.GFLUX_URL_PREFIX,'exportTableToXls'),
    url(r'^%sajax/download_xls_file/$'%settings.GFLUX_URL_PREFIX,'downloadXlsFile'),
    url(r'^%sajax/downloadXlsFile/$'%settings.GFLUX_URL_PREFIX,'download_xls_file'),
    url(r'^%sajax/add_tag/$'%settings.GFLUX_URL_PREFIX,'addTag'),
    url(r'^%sajax/get_user_tags/$'%settings.GFLUX_URL_PREFIX,'getUserTags'),
    url(r'^%sajax/remove_tag/$'%settings.GFLUX_URL_PREFIX,'removeTag'),
    url(r'^%sajax/get_user_tag_sites/$'%settings.GFLUX_URL_PREFIX,'getUserTagSites'),
    url(r'^%sajax/bind_site_for_tag/$'%settings.GFLUX_URL_PREFIX,'bandSiteForTag'),
    url(r'^%sajax/remove_site_for_tag/$'%settings.GFLUX_URL_PREFIX,'removeSiteForTag'),
)

urlpatterns += patterns('',
    url(r'^%s(?P<path>.*)$'%settings.STATIC_URL[1:],
         'django.views.static.serve', {
         'document_root': settings.STATIC_ROOT
    }),
)

js_info_dict = {
    'domain': 'djangojs',
    'packages': (
        'gflux',
    ),
}
urlpatterns += patterns('gflux.apps.station.i18n',
    url(r'^%sjsi18n/$'% settings.GFLUX_URL_PREFIX, 'javascript_catalog', js_info_dict),
)
