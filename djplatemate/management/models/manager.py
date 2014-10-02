from smart_model import SmartModel
from django.db.models import *
from platemate.logger import *
from supervisor import Supervisor

class Input(SmartModel):
    creation_time = DateTimeField(auto_now_add=True)
    processed = BooleanField(default=False)
    
    @property
    def manager(self):
        return self.managers.all()[0]
    
class Output(SmartModel):
    creation_time = DateTimeField(auto_now_add=True)
    processed = BooleanField(default=False)
    from_job = ForeignKey('Job',related_name='to_outputs',null=True)
    
    @property
    def manager(self):
        return self.managers.all()[0]
    
class Manager(SmartModel,Supervisor):

    @property
    def level(self):
        if self.name == 'chief':
            return 0
        else:
            return 1 + self.boss.level

    def work(self):
        pass
        
    def setup(self):
        pass

    @property
    def done(self):
        hits_done = self.active_hits.count() == 0
        jobs_done = self.waiting_jobs.count() == 0
        inputs_done = self.inbox.filter(processed=False).count() == 0
        outputs_done = self.outbox.filter(processed=False).count() == 0
    
        done = hits_done and jobs_done and inputs_done and outputs_done
        for employee in self.employees.all():
            done = done and employee.done
        return done

    inbox = ManyToManyField(Input,related_name='managers')
    outbox = ManyToManyField(Output,related_name='managers')
    boss = ForeignKey('self',related_name='employees',null=True)
    operation = CharField(max_length=100)
    name = CharField(max_length=100)
    sandbox = BooleanField(default=True)

    def get_outputs(self,**conditions):
        "Returns an ordered list of outputs from this manager and its employees"
        outputs = []
        for employee in self.employees.order_by('id'):
            outputs += employee.get_outputs(**conditions) # Add all his employees' outputs
        my_output = Output.objects.filter(managers=self,**conditions)
        outputs += my_output # Add this manager's output
        return outputs
    
    
    def __unicode__(self):
        return '<%s>' % self.name
    
    # Return an employee by name
    def employee(self,name):
        e = self.employees.filter(operation = self.operation, name=name)
        return e[0]
    
    def hire(self,other,name=None):
        o = other.Manager()
        o.boss = self
        o.operation = self.operation
        o.name = name or other.__name__
        o.save()
        log("%s hired %s" % (self, o),MANAGER_CONTROL)
        
    # Takes either an Input object, or the arguments to create one
    def assign(self,input=None,**kwargs):
        i = input or self.Input.factory(**kwargs)
        i.save()
        self.inbox.add(i)
        self.save()
        log("%s assigned item %s" % (self, i),MANAGER_CONTROL)
        return i
    
    # Takes either an Output object, or the arguments to create one
    def finish(self,output=None,**kwargs):
        o = output or self.Output.factory(**kwargs)   
        o.save()
        self.outbox.add(o)
        self.save()
        log("%s finished %s" % (self, o),MANAGER_CONTROL)
        return o
        
    @property
    def assigned(self):
        for product in self.inbox.filter(processed=False):
            yield product
            product.processed = True
            product.save()
    
    @property
    def finished(self):
        for product in self.outbox.filter(processed=False):
            yield product
            product.processed = True
            product.save()