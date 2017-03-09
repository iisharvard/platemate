from django.conf import settings
from django.http import HttpResponse
from decimal import Decimal
from boto.mturk.price import Price

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
