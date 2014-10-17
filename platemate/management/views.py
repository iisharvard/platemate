from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from models import *
from urllib2 import urlopen
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
        all_times.setdefault(r.step,[])
        all_times[r.step] += [r.work_time]
        
    for step, times in all_times.items():
        work_times[step] = "Median: %.2f, Mean: %.2f" % (median(times),mean(times))
        
    return render_to_response('dictionary.html', {"dict": work_times})
    


    
    
def show_hit(request, hit_id):
    h = get_object_or_404(Hit, pk=hit_id)
    #template_name = h.jobs.all()[0].__class__.__name__ + ".html"

    template_name = '%s.html' % h.template
    print 'template_name:', template_name
    useragent = httpagentparser.detect(request.META["HTTP_USER_AGENT"])
    
    try:
        ip = request.META["HTTP_X_FORWARDED_FOR"]
    except KeyError:
        ip = '0.0.0.0'
    country = urlopen("http://api.hostip.info/country.php?ip=%s" % ip).read()
    
    worker_id = request.GET.get("workerId", 'unknown')
    
    
    examples_search = os.path.join(settings.STATIC_DOC_ROOT,'examples',h.template,'*.png')
    examples = []
    for example_path in glob.glob(examples_search):
        filename = os.path.basename(example_path)
        examples.append('%s/static/examples/%s/%s' % (settings.URL_PATH,h.template,filename))
   
    
    return render_to_response(template_name, {
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
    responses = Response.objects.filter(job__manager__operation=operation).order_by('job__manager__pk')
    return render_to_response('responses.html', {
        "responses": responses,
        "path": settings.URL_PATH,
    })

   
def hit_list(request,operation=None):
    if not operation:
        hits = Hit.objects.all()
    else:
        hits = Hit.objects.filter(manager__operation=operation)
    urls = [hit.turk_url for hit in hits]
    return HttpResponse('\n'.join(urls))
