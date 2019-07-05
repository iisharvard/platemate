# Modules
# -------
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.question import ExternalQuestion
from boto.mturk import qualification
from boto.mturk.price import Price
import boto3
from logger import *
from helpers import *
import sys, traceback
from collections import defaultdict
from datetime import datetime

def catcherror(f):
    def new_f(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except MTurkRequestError, e:
            type, value, tb = sys.exc_info()

            message = '----------------\n'
            message += '    WARNING\n'
            message += '----------------\n'
            message += str(value)
            message += '\n----------------\n'
            log(message, TURK_WARNING)

            #print 'Type: %s' % type
            #print 'Value: %s' % value
            #print 'Traceback:'
            #traceback.print_tb(tb)

    return new_f

class MTurkClient:

    # SETUP
    # ===========

    def __init__(self, aws_access_key, aws_secret_key, aws_mode):
        self.mode = aws_mode

        self.boto_config = {
            "aws_access_key_id": aws_access_key,
            "aws_secret_access_key": aws_secret_key,
            "region_name": "us-east-1"
        }

        if aws_mode == 'sandbox':
            self.boto_config["endpoint_url"] = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

        self.c = boto3.client(
            "mturk",
            **self.boto_config
        )

    default_settings = {
        'LifetimeInSeconds': DAY,
        'AssignmentDurationInSeconds': 10 * MINUTE,
        'AutoApprovalDelayInSeconds': DAY,

        'Title': "[title]",
        'Description': "[description]",
        'Keywords': "",

        'Reward': '0.01',
        'MaxAssignments': 1,

        'height': 700,

        'QualificationRequirements': [],
    }

    # HITS
    # ===========
    def create_hit(self, url, extra_settings):
        """Eventually, this should take a TEMPLATE and a dictionary of INPUT
        data that's put into that template. This function would then create
        an HTML file locally (assuming we're running on a web server) by
        replacing template {tags} with input values, and then send the URL to
        the newly created page to MTurk."""

        settings = self.default_settings.copy()
        settings.update(extra_settings)

        settings['Reward'] = str(settings['Reward'])
        settings['QualificationRequirements'] = settings['QualificationRequirements']
        settings['Keywords'] = ','.join(settings['Keywords'])
        height = settings.pop('height')
        settings["Question"] = ExternalQuestion(url, height).get_as_xml()

        hit = self.c.create_hit(**settings)["HIT"]
        #print 'Created hit %s' % hit.HITId
        return hit["HITId"], hit["HITTypeId"]

        #hit_type=None, # Let Amazon do this automatically
        #annotation=None, # Optional annotation for our system to use
        #questions=None, # If you want to create multiple HITs at a time? Probably irrelevant for External
        #response_groups=None, # Unclear what this does

    def get_hit(self, hit_id):
        return self.c.get_hit(hit_id)["HIT"]

    def hit_results(self, hit_id, type=None): # type in ['Submitted','Approved','Rejected',None]
        results = defaultdict(lambda: {})

        try:
            assignments = self.c.list_assignments_for_hit(
                HITID=hit_id,
                status=None,
                MaxResults=100,
            )["Assignments"]

            for asst in assignments:
                answers = asst.answers[0] if len(asst.answers) > 0 else []
                for qfa in answers:
                    field, response = qfa.qid, qfa.fields[0]
                    results[asst.AssignmentId][field] = response

                results[asst.AssignmentId]['worker_id'] = asst.WorkerId

                results[asst.AssignmentId]['accept_time'] = datetime.strptime(asst.AcceptTime, "%Y-%m-%dT%H:%M:%SZ")
                results[asst.AssignmentId]['submit_time'] = datetime.strptime(asst.SubmitTime, "%Y-%m-%dT%H:%M:%SZ")
        except:
            log(u'Error getting assignments for HIT %s. Does this hit exist on Amazon?' % (hit_id), MANAGER_CONTROL)
        finally:
            return results

    # URL of a HIT on MTurk
    def hit_url_turk(self, hit_id):
        pass

    def hit_url_external(self, hit_id):
        pass

    def extend_hit(self, hit_id, extras):
        return self.c.create_additional_assignments_for_hit(
            HITId=hit_id,
            NumberOfAdditionalAssignments=extras,
        )

    @catcherror
    def delete_hit(self, hit_id):
        self.c.update_expiration_for_hit(
            HITId=hit_id,
            ExpireAt=datetime.now(),
        )
        self.c.delete_hit(
            HITId=hit_id
        )

    # Deletes all the HITS on the server. Risky!
    def cleanup(self):
        for hit in self.c.list_hits()["HITs"]:
            self.delete_hit(hit["HITId"])

    # ASSIGNMENTS
    # ===========
    @catcherror
    def approve(self, asst_id, feedback=None):
        return self.c.approve_assignment(
            AssignmentId=asst_id,
            RequesterFeedback=feedback,
        )

    @catcherror
    def reject(self, asst_id, feedback=None):
        self.c.reject_assignment(
            AssignmentId=asst_id,
            RequesterFeedback=feedback,
        )

    def block(self, worker_id, feedback=None):
        self.c.create_worker_block(
            WorkerId=worker_id,
            Reason=feedback,
        )

    def unblock(self, worker_id, feedback=None):
        self.c.delete_worker_block(
            WorkerId=worker_id,
            Reason=feedback,
        )

    def bonus(self, asst, amount, feedback):
        self.c.send_bonus(
            WorkerId=asst.worker,
            BonusAmount=amount,
            AssignmentId=asst.asst_id,
            Reason=feedback,
        )

    # STATUS / DIAGNOSTICS
    # --------------------
    def balance(self):
        balance_response = self.c.get_account_balance()
        return float(balance_response["AvailableBalance"])
