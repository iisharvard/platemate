# Modules
# -------

from boto.mturk.question import ExternalQuestion
import boto3
from botocore.exceptions import ClientError
from logger import *
from helpers import *
import sys
from datetime import datetime
import xmltodict

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
        settings['LifetimeInSeconds'] = extra_settings.get('lifetime', DAY)
        settings['AssignmentDurationInSeconds'] = extra_settings.get('duration', 10 * MINUTE)
        settings['AutoApprovalDelayInSeconds'] = extra_settings.get('approval_delay', DAY)
        settings['Title'] = extra_settings.get('title', 'Unknown')
        settings['Description'] = extra_settings.get('description', 'Unknown')
        settings['Keywords'] = ','.join(extra_settings.get('keywords', []))
        settings['Reward'] = str(extra_settings.get('reward', '0.01'))
        settings['QualificationRequirements'] = extra_settings.get('qualifications', [])
        settings['MaxAssignments'] = extra_settings.get('max_assignments', 1)
        settings["Question"] = ExternalQuestion(url, extra_settings.get('height', 700)).get_as_xml()

        hit = self.c.create_hit(**settings)["HIT"]
        return hit["HITId"], hit["HITGroupId"]

    def get_hit(self, hit_id):
        return self.c.get_hit(HITId=hit_id)["HIT"]

    def hit_results(self, hit_id, type=None): # type in ['Submitted','Approved','Rejected',None]
        results = []

        try:
            response = self.c.list_assignments_for_hit(
                HITId=hit_id,
                MaxResults=100,
            )
            for assignment in response["Assignments"]:
                asst = {
                    'worker_id': assignment['WorkerId'],
                    'assignment_id': assignment['AssignmentId'],
                    'auto_approval_time': assignment['AutoApprovalTime'],
                    'accept_time': assignment['AcceptTime'],
                    'submit_time': assignment['SubmitTime'],
                    'assignment_status': assignment['AssignmentStatus'],
                    'answer': {},
                }
                xml_doc = xmltodict.parse(assignment['Answer'])
                for answer_field in xml_doc['QuestionFormAnswers']['Answer']:
                    field = answer_field['QuestionIdentifier']
                    # Some responses are coming as empty XML elements, resulting in the value of response for this key
                    # to be None. DB has a NOT NULL constraint on this field. As a temp fix assign empty string to make
                    # the response save successfully.
                    response = answer_field['FreeText'] or ''
                    asst['answer'][field] = response
                results.append(asst)
            return results
        except:
            log(u'Error getting assignments for HIT %s. Does this hit exist on Amazon?' % (hit_id), MANAGER_CONTROL)
            return []

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
    def approve(self, asst_id, feedback=None):
        try:
            return self.c.approve_assignment(
                AssignmentId=asst_id,
                RequesterFeedback=feedback,
            )
        except ClientError as e:
            if "This operation can be called with a status of" in str(e):
                log("Tried to approve assignment but it is already approved or rejected; skipping", MANAGER_CONTROL)
            else:
                raise e

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
