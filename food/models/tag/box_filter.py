
from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base

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
    duplication = 3

    # Advertising
    qualifications = [min_approval(98), min_completed(100), locale('US')]
    keywords = ['picture', 'identify', 'food']
    title = 'Identify if there are food on a plate'
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
        for job in self.completed_jobs:
            counter = 0
            for response in job.valid_responses:
                if response.has_food:
                    counter += 1

            # TODO check if no-food job must be closed.
            if self.duplication > 1:
                if counter > 1 :
                    self.finish(photo=response.photo, from_job=job)
            else:
                if counter > 0:
                    self.finish(photo=response.photo, from_job=job)
