from django.core.management import setup_environ
import settings
setup_environ(settings)
from logger import *
from time import sleep
from django.db import transaction
from helpers import *

CHECK_FREQ   = 15.0
REFRESH_FREQ = 300.0

def run(chief_module,operation,args={}):  

    # Recursively setup all the managers
    def setup(manager):
        log('Preparing %s' % manager,LOOP_CONTROL)
        manager.setup()
        manager.save()
        for employee in manager.employees.all():
            employee.sandbox = manager.sandbox
            setup(employee)
            
            
    # Recursively work all the managers
    def work(manager):
        log('Working %s' % manager,LOOP_CONTROL)
        
        # Get responses
        manager.check_hits()
        
        # Manager-specific routing
        manager.work()
        
        # Make new hits
        manager.assemble_jobs()
        manager.save()
        
        # Add and delete dummy hits to bring us back to the top
        if manager.active_hits and with_probability(CHECK_FREQ / REFRESH_FREQ):
            manager.refresh_hits()
        
        # Now have employees do the same thing
        for employee in manager.employees.all():
            work(employee)
            
    def get_chief(chief_class,operation):
        return chief_class.objects.get(operation=operation,name='chief',**args)
            
    @transaction.commit_on_success
    def new_chief(chief_class,operation):
        chief = chief_class.factory(operation=operation,name='chief',**args)
        setup(chief)       
        chief.save()
        return chief
            
            
    chief_class = chief_module.Manager
    
    # Try to resume an existing operation
    try:
        chief = get_chief(chief_class,operation)
        log('Resuming', LOOP_SETUP)
        
    # If it's not there, start from scratch
    except chief_class.DoesNotExist:
        log('Starting from scratch', LOOP_SETUP)
        chief = new_chief(chief_class,operation)
                
    # Main loop
    while True:
        log('--- LOOP ---', LOOP_CONTROL)
        work(chief)
        sleep(CHECK_FREQ)
