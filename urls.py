from django.conf.urls import *
from django.conf import settings

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns(
    '',
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

    # HITs
    (r'^hits/$', 'management.views.hit_list'),

    # Submissions
    (r'^submissions/(?P<submission_id>\w*)/$', 'food.views.submission_details'),
    (r'^submissions/$', 'food.views.submission_list'),

    # Static Content
    (
        r'^static/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT}
    ),
    #(r'^admin/', include(admin.site.urls)),

    # API
    (r'^api/upload_photo/?$', 'food.views.api_photo_upload'),
    (r'^api/submission_statuses/?$', 'food.views.api_submission_statuses'),

    # Util
    (r'^util/turk_balance/?$', 'util.views.turk_balance'),
    (r'^util/ping/?$', 'util.views.ping'),
)
