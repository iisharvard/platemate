from django.conf.urls.defaults import *

urlpatterns = patterns('food.views',
    # Hits
    (r'^search/(?P<query>[\w\S\s]+)/$', 'food_search'),
    
    # Frontend
    (r'^autocomplete/$', 'food_autocomplete'),
    (r'^edit_ingredient/$', 'edit_ingredient'),
    (r'^add_ingredient/$', 'add_ingredient'),
    (r'^delete_ingredient/$', 'delete_ingredient'),
    (r'^delete_submission/$', 'delete_submission'),
)