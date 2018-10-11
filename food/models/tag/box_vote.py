from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
import box_draw as draw

class Input(base.Input):
    box_groups = ManyOf(BoxGroup)

class Output(base.Output):
    box_group = OneOf(BoxGroup)

class Job(base.Job):
    box_groups = ManyOf(BoxGroup)

class Response(base.Response):
    box_group = OneOf(BoxGroup)

    def validate(self):
        self.raw = self.box_group_id
        if self.box_group_id == '':
            return 'No vote provided'
        else:
            self.box_group = BoxGroup.objects.get(id=self.box_group_id)
            return True

class Manager(base.Manager):

    ################
    # HIT SETTINGS #
    ################

    # Batching
    batch_size = 2
    max_wait = 5 * MINUTE

    # Payment
    reward = .04
    duplication = 3

    # Advertising
    qualifications = [min_approval(98), min_completed(100), locale('US')]
    keywords = ['picture', 'vote', 'box', 'food']
    title = 'Pick which set of boxes matches the foods on a plate'
    description = 'Help us figure out how many different foods are on the same plate.'

    #########
    # LOGIC #
    #########
    def setup(self):
        pass

    def work(self):

        for input in self.assigned:
            self.new_job(box_groups=input.box_groups.all(), from_input=input)

        for job in self.completed_jobs:
            if self.duplication > 1:
                choices = [response.box_group for response in job.valid_responses]
                bg = mode(choices)
            else:
                bg = job.valid_response.box_group

            self.finish(box_group=bg, from_job=job)
