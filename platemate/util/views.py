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
    processor_up = False
    try:
        status_check_output = subprocess.check_output('systemctl status platemate-processor.service', shell=True)
        processor_up = "Active: active (running)" in status_check_output
    except:
        processor_up = False
    everything_ok = processor_up #other things can be added later
    context = {
        'processor_up' : processor_up,
        'everything_ok' : everything_ok
    }
    status = 200 if everything_ok else 503
    return HttpResponse(template.render(context, request), status=status)
