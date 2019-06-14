
from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
from urllib import unquote

class Input(base.Input):
    photo = OneOf(Photo)

class Output(base.Output):
    photo = OneOf(Photo)

class Job(base.Job):
    photo = OneOf(Photo)

class Response(base.Response):
    photo = OneOf(Photo)

    def validate(self):
        """
        True or false question, no validation needed.
        """
        return True

class Manager(base.Manager):

    ################
    # HIT SETTINGS #
    ################

    # Batching
    batch_size = 1
    max_wait = 5 * MINUTE

    # Payment
    reward = .05
    duplication = 3

    # Advertising
    qualifications = [min_approval(98), min_completed(100), locale('US')]
    keywords = ['picture', 'identify', 'food']
    title = 'Draw a box around each food on a plate'
    description = 'Help us figure out if there is any food on a plate.'

    #########
    # LOGIC #
    #########
    def setup(self):
        pass

    def work(self):
        for input in self.assigned:
            self.new_job(photo=input.photo, from_input=input)

        for hit in self.completed_hits:
            for job in hit.jobs.all():
                answers = job.valid_responses
                self.finish(box_groups=[answer.box_group for answer in answers], from_job=job)
