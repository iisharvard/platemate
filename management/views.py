from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from models import *
from food.models import *
#from urllib2 import urlopen
import requests
import httpagentparser
import os, glob

default_assignment_id = 'ASSIGNMENT_ID_NOT_AVAILABLE'

def index(request):
    return HttpResponse("Hello World")

def show_stats(request, operation):

   # Work time
    all_times = {}
    work_times = {}

    for r in Response.objects.filter(job__manager__operation=operation):
        all_times.setdefault(r.step, [])
        all_times[r.step] += [r.work_time]

    for step, times in all_times.items():
        work_times[step] = "Median: %.2f, Mean: %.2f" % (median(times), mean(times))

    return render(request, 'dictionary.html', context={"dict": work_times})

def show_hit(request, hit_id):
    h = get_object_or_404(Hit, pk=hit_id)
    #template_name = h.jobs.all()[0].__class__.__name__ + ".html"

    template_name = '%s.html' % h.template
    print 'template_name:', template_name
    try:
        useragent = httpagentparser.detect(request.META["HTTP_USER_AGENT"])
    except KeyError:
        useragent = {'os': {'name': 'Unknown'}}
    try:
        ip = request.META["HTTP_X_FORWARDED_FOR"]
    except KeyError:
        ip = '0.0.0.0'
    try:
        if False:
            #country_response = requests.get("http://api.hostip.info/country.php?ip=%s" % ip, timeout=3)
            country_response = requests.get("https://freegeoip.net/json/%s" % ip, timeout=4)
            country = (country_response.json())['country_code']
        else:
            country = "GeoLocation Disabled"
    except requests.Timeout:
        print("ERROR: THE GEOLOCATION API TIMED OUT")
        country = "Unknown"

    worker_id = request.GET.get("workerId", 'unknown')
    #print("Worker: %s\t country: %s"%(worker_id,country))

    examples_search = os.path.join(settings.STATIC_DOC_ROOT, 'examples', h.template, '*.png')
    examples = []
    for example_path in glob.glob(examples_search):
        filename = os.path.basename(example_path)
        examples.append('%s/static/examples/%s/%s' % (settings.URL_PATH, h.template, filename))

    return render(request, template_name, context={
        "hit": h,
        "assignment": request.GET.get("assignmentId", default_assignment_id),
        "worker_id": worker_id,
        "forbidden": worker_id in [worker.turk_id for worker in h.forbidden_workers.all()],
        "os": useragent["os"]["name"],
        #"browser": useragent["browser"]["name"] + " " + useragent["browser"]["version"],
        "browser": 'buggy',
        "country": country,
        "ip": ip,
        "path": settings.URL_PATH,
        "example_urls": examples,
    })

def show_responses(request, operation):
    # Limiting the result set here, so the page does not grow unbounded
    page_size = 10
    limit = request.GET.get('limit', str(page_size)) # poor man's pagination
    limit = int(limit)
    responses = Response.objects.filter(job__manager__operation=operation).order_by('-assignment_id')[:limit]
    return render(
        request,
        'fe/responses.html',
        context={
            "responses": responses,
            "path": settings.URL_PATH,
            "next_limit": limit + page_size,
            "operation": operation,
        }
    )

def hit_list(request, operation=None):
    if not operation:
        hits = Hit.objects.all()
    else:
        hits = Hit.objects.filter(manager__operation=operation)
    urls = [hit.turk_url for hit in hits]
    return HttpResponse('\n'.join(urls))
