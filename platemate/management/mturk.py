# Modules
# -------
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.question import ExternalQuestion
from boto.mturk import qualification
from boto.mturk.price import Price
from logger import *
from helpers import *
import sys, traceback

def catcherror(f):
    def new_f(*args,**kwargs):
        try:
            f(*args,**kwargs)
        except MTurkRequestError, e:
            type,value,tb = sys.exc_info()
            
            message =  '----------------\n'
            message += '    WARNING\n'
            message += '----------------\n'
            message += str(value)
            message += '\n----------------\n'
            log(message,TURK_WARNING)
            
            #print 'Type: %s' % type
            #print 'Value: %s' % value
            #print 'Traceback:'
            #traceback.print_tb(tb)
            
    return new_f


class MTurkClient:

    # SETUP
    # ===========
           
    def __init__(self,aws_access_key,aws_secret_key,aws_mode):
        self.mode = aws_mode
        if aws_mode == 'sandbox':
            self.host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            self.host = 'mechanicalturk.amazonaws.com'

        self.c = MTurkConnection(
            aws_access_key,
            aws_secret_key,
            host=self.host)
            
    default_settings = {
        'lifetime': DAY,
        'duration': 10 * MINUTE,
        'approval_delay': DAY,

        'title': "[title]",
        'description': "[description]",
        'keywords': [],

        'reward': 0.01,
        'max_assignments': 1,
        
        'height': 700,
        
        'qualifications': [],
    }
            
    # HITS
    # ===========
    def create_hit(self,url,extra_settings):
        "Eventually, this should take a TEMPLATE and a dictionary of INPUT data that's put into that template. This function would then create an HTML file locally (assuming we're running on a web server) by replacing template {tags} with input values, and then send the URL to the newly created page to MTurk."
       
        settings = self.default_settings.copy()
        settings.update(extra_settings)

        settings['reward'] = Price(settings['reward'])
        settings['qualifications'] = qualification.Qualifications(settings['qualifications'])
        settings['keywords'] = ','.join(settings['keywords'])
        height = settings.pop('height')

        hit = self.c.create_hit(question=ExternalQuestion(url,height),**settings)[0]
        #print 'Created hit %s' % hit.HITId
        return hit.HITId,hit.HITTypeId
        
        #hit_type=None, # Let Amazon do this automatically
        #annotation=None, # Optional annotation for our system to use
        #questions=None, # If you want to create multiple HITs at a time? Probably irrelevant for External
        #response_groups=None, # Unclear what this does 
        
    def get_hit(self,hit_id):
        return self.c.get_hit(hit_id)[0]
        
    def hit_results(self,hit_id,type=None): # type in ['Submitted','Approved','Rejected',None]
        results = {}
    
        assignments = self.c.get_assignments(hit_id, status=None, page_size=100)
        for asst in assignments:
            results.setdefault(asst.AssignmentId,{})
            answers = asst.answers[0]
            for qfa in answers:
                field, response = qfa.qid, qfa.fields[0]
                results[asst.AssignmentId][field] = response
                
            results[asst.AssignmentId]['worker_id'] = asst.WorkerId
                       
            results[asst.AssignmentId]['accept_time'] = datetime.strptime(asst.AcceptTime,"%Y-%m-%dT%H:%M:%SZ")
            results[asst.AssignmentId]['submit_time'] = datetime.strptime(asst.SubmitTime,"%Y-%m-%dT%H:%M:%SZ")
                
        return results
        
    # URL of a HIT on MTurk
    def hit_url_turk(self,hit_id):
        pass
        
    def hit_url_external(self,hit_id):
        pass
        
    def extend_hit(self,hit_id,extras):
        return self.c.extend_hit(hit_id, extras)
        
    @catcherror
    def delete_hit(self,hit_id):
        self.c.disable_hit(hit_id)
        
    # Deletes all the HITS on the server. Risky!
    def cleanup(self):
        for hit in self.c.get_all_hits():
            self.delete_hit(hit.HITId)
            
    # ASSIGNMENTS
    # ===========
    @catcherror
    def approve(self, asst_id, feedback=None):
        return self.c.approve_assignment(asst_id, feedback)
        
    @catcherror
    def reject(self, asst_id, feedback=None):
        return self.c.reject_assignment(asst_id, feedback)

    def block(self,worker_id,feedback=None):
        return self.c.block_worker(worker_id, feedback)
        
    def unblock(self,worker_id,feedback=None):
        return self.c.unblock_worker(worker_id, feedback)
        
    def bonus(self,asst,amount,feedback):
        return self.c.grant_bonus(asst.worker, asst.asst_id, Price(amount), feedback)
        
    # STATUS / DIAGNOSTICS
    # --------------------
    def balance(self):
        return self.c.get_account_balance()[0]
        
