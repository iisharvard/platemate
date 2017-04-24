from django.conf import settings
from django.http import HttpResponse
from decimal import Decimal
from boto.mturk.price import Price
from django.template.loader import get_template
import subprocess

def turk_balance(request):
    minimum_balance = Price(100.00)
    try:
        turk = settings.TURK_REAL
        balance = turk.balance()
        if balance.amount < minimum_balance.amount:
            return HttpResponse("Low: %s" % balance, status=402)
        else:
            return HttpResponse("OK: %s" % balance, status=200)
    except:
        return HttpResponse("Balance check failed.", status=503)

def ping(request):
    template = get_template('util/ping.html')
    platemate_processor_running = False
    try:
        platemate_processor_status_output = subprocess.check_output('systemctl status platemate-processor.service', shell=True)
        platemate_processor_running = "Active: active (running)" in platemate_processor_status_output
    except:
        platemate_processor_running = False
    everything_ok = platemate_processor_running #other things can be added later
    context = {
        'platemate_processor_running' : platemate_processor_running,
        'everything_ok' : everything_ok
    }
    return HttpResponse(template.render(context, request))
