from django.conf.urls import *

urlpatterns = patterns(
    'management.views',
    (r'^$', 'index'),
    (r'^(?P<hit_id>\d+)/$', 'show_hit'),

    # Stubbed HIT result handling
    (r'^save_stubbed/$', 'save_stubbed_hit'),
)
