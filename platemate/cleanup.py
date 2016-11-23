import os, sys
from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.db import connection
from management.models import *
from logger import *


operation = sys.argv[1]
use_sandbox = (sys.argv[-1] != 'real')

APPS = ['management','food']
DB = settings.DATABASES['default']
TURK = settings.TURK_SANDBOX if use_sandbox else settings.TURK_REAL
PYTHONVAR = getattr(settings,'PYTHONVAR','python')

def cmd(c):
    print c
    os.system(c)
    
def drop_db():
    
    try:
        cmd("rm food/fixtures/initial_data.json")
        cmd(PYTHONVAR + " manage.py dumpdata food.Food food.FoodSearchResults food.FoodSearchResult food.Serving auth.User  --indent 4 --format=json --natural > food/fixtures/initial_data.json")
        if DB['ENGINE'] == 'sqlite3':
            print "Deleting %s" % os.path.abspath(DB['NAME'])
            connection.close()
            os.remove(DB['NAME'])
        else:
            print 'Dropping tables %s from DB' % APPS
            #os.environ['PGPASSWORD'] = DB['PASSWORD']
            cmd(PYTHONVAR + ' manage.py sqlclear %s | python manage.py dbshell' % ' '.join(APPS))
    except OSError as e:
        print e
            
            
if operation == 'hitpurge':
    TURK.cleanup()
    drop_db()
    cmd(PYTHONVAR + ' manage.py syncdb --noinput')
    
elif operation == 'sync':
    cmd(PYTHONVAR + ' manage.py syncdb --noinput')
    
elif operation == 'drop':
    # Clear out HITS
    hits = Hit.objects.filter(turk_mode='sandbox' if use_sandbox else 'real')
    for hit in hits:
        log('Deleted hit %s' % hit.turk_id,TURK_CONTROL)
        TURK.delete_hit(hit.turk_id)
        
    # Drop tables
    drop_db()
        
    # Then run syncdb
    cmd(PYTHONVAR + ' manage.py syncdb --noinput')
    
elif operation == 'flush':
    # Clear out HITs
    hits = Hit.objects.all()
    for hit in hits:
        log('Deleted hit %s' % hit.turk_id,TURK_CONTROL)
        TURK.delete_hit(hit.turk_id)
    
    # Flush
    cmd(PYTHONVAR + ' manage.py flush --noinput')
else:
    def all_hits(manager):
        hits = list(Hit.objects.filter(turk_mode='sandbox' if use_sandbox else 'real',manager=manager))
        for employee in manager.employees.all():
            hits += all_hits(employee)
        return hits
            
    chief = Manager.objects.get(name='chief',operation=operation,sandbox=use_sandbox)
    for hit in all_hits(chief):
        log('Deleted hit %s' % hit.turk_id,TURK_CONTROL)
        TURK.delete_hit(hit.turk_id)
    chief.delete()
