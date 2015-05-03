#fcoding=utf-8
from django.conf.urls import patterns, include, url
from demosite.views import *
from django.conf import settings
from django.conf.urls.static import static
import os
static_dir = os.path.join(os.path.dirname(__file__),'../logindemo/static')
DEMOSITE = 'demosite/'
urlpatterns = patterns('',
        #登录
	url('^%slogin$'%DEMOSITE,loginpage),
	url('^%slogincheck/$'%DEMOSITE,logincheck),
        #注册
	url('^%sregisterpage/$'%DEMOSITE,registerload),
	url('^%sregisterpage/register/$'%DEMOSITE,register),
	#上传
	url('^%suploadFile/$'%DEMOSITE,uploadFilePage),
	url('^%supload_file/$'%DEMOSITE,uploadFile),
	url('^%slinkPage/$'%DEMOSITE,linkPage),
        url('^%slinkPage/addlink/$'%DEMOSITE,add_link),
	#首页
	url('^%sindex/$'%DEMOSITE,indexload),
	url('^%sindex/requestlinkdata/$'%DEMOSITE,request_link_data),
	url('^%sindex/insert_blog_url/$'%DEMOSITE,insert_link_url),
	url('^%sindex/search_blog/$'%DEMOSITE,search_blog),
	#文章
	url('^%s(articles)/$'%DEMOSITE,articlelistload),
	url('^%sarticles/getFilename/$'%DEMOSITE,get_filename),
	url('^%sshowfile/$'%DEMOSITE,show_file),	
	url('^%s(search)/$'%DEMOSITE,search_articles),
	#知识树页面
	url('^%sknowledgeTree/$'%DEMOSITE,knowledge_tree),

        #已解决问题上传
        url('^%supload_question_and_method/$'%DEMOSITE,newques),	
	url('^%squestion_and_method_list/$'%DEMOSITE,queslist),
)

urlpatterns += patterns('',
	(r'^nyf/static/(?P<path>.*)$','django.views.static.serve',        {'document_root':static_dir}),   
)

