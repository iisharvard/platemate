from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
import subprocess

def turk_balance(request):
    minimum_balance = 100.00
    try:
        turk = settings.TURK_REAL # Use REAL turk mode, sandbox always returns 10000.00
        balance = turk.balance()
        if balance < minimum_balance:
            return HttpResponse("Low: %.2f" % balance, status=402)
        else:
            return HttpResponse("OK: %.2f" % balance, status=200)
    except Exception as err:
        return HttpResponse("Balance check failed. " + err.message, status=503)

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
