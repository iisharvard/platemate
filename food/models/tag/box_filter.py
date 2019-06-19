
from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
from collections import Counter

class Input(base.Input):
    photo = OneOf(Photo)

class Output(base.Output):
    photo = OneOf(Photo)

class Job(base.Job):
    photo = OneOf(Photo)

class Response(base.Response):
    photo = OneOf(Photo)
    has_food = BooleanField(default=False)

    def validate(self):
        """
        True or false question, no validation needed.
        """
        self.photo_id = self.to_job.photo_id
        self.photo = Photo.objects.get(id=self.photo_id)

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
    duplication = 1

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

# TODO: Create table for food_exist
# TODO: Found reportign API and short circuit no food photo.
# TODO: Reports other images that doesn't go through the flow.
        for hit in self.completed_hits:
            for job in hit.jobs.all():
                answers = job.valid_responses

                cnt = Counter()
                # TODO recording photo id correctly
                for answer in answers:
                    if answer.has_food:
                        cnt[answer.photo] += 1

                self.finish(photo=[photo for photo, num in cnt if num > 1], from_job=job)
