from management import qualifications
from management.helpers import *
from management.models.turk import *
from django.db.models import Min
from logger import *
from turk import Hit
from django.conf import settings
from django.db import transaction
from datetime import datetime
from time import sleep
from urllib import unquote
from random import randrange
import json

class Supervisor(object):

    @property
    def turk(self):
        return settings.TURK_SANDBOX if self.sandbox else settings.TURK_REAL

    ####################
    # DEFAULT SETTINGS #
    ####################

    # Batching
    batch_size = 1
    max_wait = 5 * MINUTE

    # HIT Interface
    height = 700

    # Payment
    reward = .01
    duplication = 1

    # Timing
    duration = 20 * MINUTE
    approval_delay = 3 * DAY
    lifetime = 3 * DAY

    # Advertising
    qualifications = []
    keywords = ['PlateMate', 'plate', 'food']
    title = 'Untitled HIT'
    description = ''

    ################
    # HIT CREATION #
    ################

    def new_job(self, **kwargs):
        j = self.Job.factory(**kwargs)
        j.manager = self
        j.save()
        return j

    @property
    def waiting_jobs(self):
        return self.jobs.filter(hit__isnull=True)

    @property
    def active_hits(self):
        return self.hits.filter(completed=False)

    def create_job(self, job):
        print "Created job %s" % job
        self.jobs.add(job)

    @transaction.atomic
    def assemble_jobs(self):
        # Pop out batches of HITs
        while len(self.waiting_jobs) >= self.batch_size:
            self.create_hit(self.waiting_jobs[:self.batch_size])

        # If at least one job has been waiting too long, create a HIT out of all remaining jobs
        if self.waiting_jobs:
            earliest_job = self.waiting_jobs.aggregate(Min('creation_time'))['creation_time__min']
            time_elapsed = datetime.now() - earliest_job
            max_wait = 2 if settings.DEBUG else self.max_wait
            if time_elapsed.seconds >= max_wait:
                self.create_hit(self.waiting_jobs)

    def delete_hit(self, hit):
        self.turk.delete_hit(hit.turk_id)
        hit.manager = None
        for job in hit.jobs.all():
            job.delete()
        hit.delete()

    @transaction.atomic
    def refresh_hits(self):
        pass
        # This logic does not work anymore. Deleting HIT raises an error:
        # An error occurred (RequestError) when calling the DeleteHIT operation: This HIT is currently in the state 'Unassignable'.
        # This operation can be called with a status of: Reviewing, Reviewable (1620320956873)
        #
        # Need to rethink how to "bubble up" HITs to the top of the workers queue

        # log(u"Refreshing HITs for %s" % (self.__class__.__name__), TURK_CONTROL)
        # for jobcount in range(self.batch_size):
        #     dummy = Job()
        #     jobs = [dummy] * (jobcount + 1)
        #     h = self.create_hit(jobs, announce=False)
        #     sleep(5)
        #     self.delete_hit(h)

    def create_hit(self, jobs, announce=True):
        # Set up HIT settings
        settings = {}
        for attr in ['lifetime', 'duration', 'approval_delay', 'title', 'description', 'keywords', 'reward', 'qualifications', 'height']:
            settings[attr] = getattr(self, attr)

        # Turn off qualifications on sandbox so we can play with the HITs
        if self.sandbox:
            settings['qualifications'] = []

        settings['max_assignments'] = self.duplication
        settings['reward'] *= len(jobs)
        settings['duration'] *= len(jobs)

        # Build HIT object, associate jobs with it
        hit = Hit(manager=self)
        hit.save()
        for job in jobs:
            job.hit = hit
            job.save()

        # Create HIT on Turk, store Turk identifier
        url = hit.external_url
        turk_id, turk_group = self.turk.create_hit(url, settings)
        hit.turk_id = turk_id
        hit.turk_group = turk_group
        hit.turk_mode = self.turk.mode
        hit.save()

        if announce:
            log(u"""Created HIT %d with %d jobs and %d assignments
                External URL: %s
                Turk ID: %s
                Turk URL: %s
                Type: %s""" % (hit.id, len(jobs), self.duplication, hit.external_url, hit.turk_id, hit.turk_url, self.__class__.__name__), MANAGER_CONTROL)
            if os.getenv("STUB_TURK"):
                for i in range(0, self.duplication):
                    log("Stubbed HIT URL %s: %s?assignmentId=%s" % (str(i + 1), hit.external_url, str(randrange(sys.maxint))), MANAGER_CONTROL)

        # TODO(jon): error handling
        return hit

    ################
    # HIT CHECKING #
    ################
    def get_responses(self, hit):
        results = self.turk.hit_results(hit.turk_id)

        # Break HIT answers into job-specific responses
        for assignment in results:

            # Ignore assignments we've already parsed
            if hit.assignments.filter(turk_id=assignment['assignment_id']):
                continue

            worker, created = Worker.objects.get_or_create(turk_id=assignment.get('worker_id'))
            worker.country = assignment['answer'].pop('country')
            worker.os = assignment['answer'].pop('os')
            worker.browser = assignment['answer'].pop('browser')
            worker.ip = assignment['answer'].pop('ip')
            worker.save()

            asst = hit.assignments.create(turk_id=assignment.get('assignment_id'))
            # comments are disabled since we use turk feedback instead
            # comment = assignment['answer'].pop('comment')
            # asst.comment = '' if comment is None else comment
            asst.accept_time = assignment.get('accept_time')
            asst.submit_time = assignment.get('submit_time')
            asst.worker = worker
            asst.save()

            log(u'Recording assignment %s on HIT %s from worker %s...' % (asst.turk_id, hit.turk_id, worker.turk_id), MANAGER_CONTROL)

            responses = {}
            # TODO: how to parse the results?
            for key, value in assignment.get('answer').items():
                if '_' not in key:
                    continue
                job_id, field = key.split('_', 1)
                job = hit.jobs.get(pk=job_id)
                responses[job_id] = responses.get(job_id, self.Response(assignment=asst, job=job))

                # TODO: use mashemallow to unmarshal responses.
                if field == "has_food":
                    # Python trick to convert empty strings to False
                    value = bool(value)

                if field == "box_group_json" or field == "selections":
                    try:
                        value = json.loads(unquote(value))
                    except ValueError:
                        value = {}

                setattr(responses[job_id], field, value)
                log(u"  %s_%s =" % (job_id, field), MANAGER_CONTROL, value)

            for response in responses.values():
                self.validate_response(response)

    def validate_response(self, response):
        # Validate each response
        v = response.validate()
        if v is True:
            response.valid = True
        else:
            response.valid = False
            response.feedback = v
        response.save()

    def review_assignment(self, asst):
        if asst.valid:
            self.turk.approve(asst.turk_id, asst.feedback)
            asst.approved = True
            log(u'Approved assignment %s ' % asst.turk_id, MANAGER_CONTROL)
        else:
            self.turk.reject(asst.turk_id, asst.feedback)
            # TODO reenable after filter is working.
            self.turk.extend_hit(asst.hit.turk_id, 1) #Commented out because generally hits are rejected because of bad photo data, don't want hit to advance.
            asst.approved = False
            log(u'Rejected assignment %s because %s' % (asst.turk_id, asst.feedback), MANAGER_CONTROL)
        asst.save()

    @transaction.atomic
    def check_hits(self):
        for hit in self.active_hits:
            self.get_responses(hit)
            for asst in hit.reviewable_assignments:
                self.review_assignment(asst)

    @property
    def completed_hits(self):
        for hit in self.active_hits:
            if len(hit.approved_assignments) == self.duplication:
                hit.completed = True
                hit.save()
                yield hit

    @property
    def completed_jobs(self):
        for hit in self.completed_hits:
            for job in hit.jobs.all():
                yield job
