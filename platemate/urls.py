from django.conf.urls import *
from django.conf import settings

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Hits
    (r'^hit/', include('management.urls')),
    (r'^food/', include('food.urls')),

    # Frontend
    (r'^$', 'food.views.fe_main'),
    (r'^day/(?P<day>.*)/$', 'food.views.fe_day'),
    (r'^upload/(?P<day>.*)/$', 'food.views.fe_upload'),

    # Authentication
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'fe/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),

    # Pipeline Data
    (r'^responses/(?P<operation>\w*)/$', 'management.views.show_responses'),
    (r'^stats/(?P<operation>\w*)/$', 'management.views.show_stats'),
    (r'^pipeline/(?P<operation>\w*)/((?P<photo>\d+)/)?$', 'food.views.show_pipeline'),
    (r'^hit_list/(?P<operation>\w*)/$', 'management.views.hit_list'),

    # Experiment summary
    (r'^summary/(?P<photo_id>\w*)/$', 'food.views.photo_summary'),
    # Static Content
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT}),
#    (r'^admin/', include(admin.site.urls)),

    #API 
    (r'^api/upload_photo/$', 'food.views.api_photo_upload')
)
