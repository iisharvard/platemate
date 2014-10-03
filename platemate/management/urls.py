from django.conf.urls.defaults import *

urlpatterns = patterns('management.views',
    (r'^$', 'index'),
    (r'^(?P<hit_id>\d+)/$', 'show_hit'),
)