from django.conf.urls import patterns, include, url

from django.contrib import admin
from demosite import urls as demosite_urls
import gdesign
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'nyf.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
     url(r'^admin/', include(admin.site.urls)),
     url(r'', include('demosite.urls')),
     url(r'', include('gdesign.urls')),

)

# urlpatterns = patterns('demosite.views',
#      url(r'^demosite/index/$','indexload'),
# )
