from smart_model import SmartModel
from django.db.models import *
from django.conf import settings

class Hit(SmartModel):
    template = CharField(max_length=100)
    
    turk_id = CharField(max_length=30)
    turk_group = CharField(max_length=30)
    turk_mode = CharField(max_length=10)
    
    manager = ForeignKey('Manager',related_name='hits',null=True)
    creation_time = DateTimeField(auto_now_add=True)
    completed = BooleanField(default=False)
    
    
    @property
    def forbidden_workers(self):
        return Worker.objects.filter(forbidden_jobs__pk__in = self.jobs.all())
    
    @property
    def template(self):
        return self.jobs.all()[0].template
        
    
    @property
    def external_url(self):
        return settings.URL_PATH + '/hit/%d/' % self.id
        
    @property
    def turk_url(self):
        host = 'workersandbox.mturk.com' if self.turk_mode == 'sandbox' else 'worker.mturk.com'
        return "https://%s/mturk/preview?groupId=%s" % (host,self.turk_group)
    
    @property
    def approved_assignments(self):
        return self.assignments.filter(approved=True)
    
    @property
    def rejected_assignments(self):
        return self.assignments.filter(approved=False)
    
    @property
    def reviewable_assignments(self):
        return self.assignments.filter(approved=None)

class Job(SmartModel):
    hit = ForeignKey('Hit',related_name='jobs',null=True,blank=True)
    manager = ForeignKey('Manager',related_name='jobs',null=True)
    forbidden_workers = ManyToManyField('Worker',related_name='forbidden_jobs')
    creation_time = DateTimeField(auto_now_add=True)
    from_input = ForeignKey('Input',related_name='to_jobs',null=True)

    @property
    def valid_responses(self):
        return self.responses.filter(valid=True)
        
    @property
    def valid_response(self):
        return self.valid_responses.all()[0]
    
class Worker(SmartModel):
    turk_id = CharField(max_length=20)
    ip = IPAddressField(null=True)
    browser = CharField(max_length=100)
    os = CharField(max_length=100)
    country = CharField(max_length=100)
    
    def __str__(self):
        return self.turk_id
   
class Assignment(SmartModel):
    turk_id = CharField(max_length=100) 
    worker = ForeignKey(Worker,null=True)
    approved = NullBooleanField()
    hit = ForeignKey('Hit',related_name='assignments')
    comment = TextField()
    accept_time = DateTimeField(null=True)
    submit_time = DateTimeField(null=True)
    
    @property
    def work_time(self):
        return (self.submit_time - self.accept_time).total_seconds()
    
    # Returns None if any responses aren't validated yet
    # Returns False if at least one response is invalid
    # Returns True if all responses are valid
    @property
    def valid(self):
        for r in self.responses.all():
            if not r.valid:
                return r.valid
        return True
        
    @property
    def feedback(self):
        for r in self.responses.all():
            if r.valid is False:
                return r.feedback
        return self.responses.all()[0].feedback
    
class Response(SmartModel):
    assignment = ForeignKey('Assignment',related_name='responses')
    job = ForeignKey(Job,related_name='responses')
    valid = NullBooleanField()
    feedback = CharField(max_length=500,default='Thank you!')
    raw = TextField()
    
    def __str__(self):
        return "%d from %s on %s: %s" % (self.pk, self.assignment, self.job, self.raw)
    
    @property
    def work_time(self):
        return self.assignment.work_time / self.assignment.hit.jobs.count()
    
    @property
    def to_job(self):
        return self.job.downcast()
    
    def validate(self):
        return True