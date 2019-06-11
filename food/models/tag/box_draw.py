from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
from urllib import unquote

class Input(base.Input):
    photo = OneOf(Photo)

class Output(base.Output):
    box_groups = ManyOf(BoxGroup)

class Job(base.Job):
    photo = OneOf(Photo)

class Response(base.Response):
    box_group = OneOf(BoxGroup)

    def validate(self):
        # Try to Parse JSON
        if not self.box_group_json:
            #return "No boxes drawn"
            self.box_group = BoxGroup.factory(photo=self.to_job.photo)
            return True
        else:
            self.box_group = BoxGroup.from_dict(self.box_group_json, photo=self.to_job.photo)

        # Remove duplicates
        boxes = self.box_group.boxes.all()[:]
        for i, box in enumerate(boxes):
            after = boxes[i + 1:]
            if box in after:
                self.box_group.boxes.remove(box)
                self.box_group.save()

        # Remove boxes inside other boxes
        boxes = self.box_group.boxes.all()[:]
        for i, box in enumerate(boxes):
            after = boxes[i + 1:]
            before = boxes[:i]
            for other in before + after:
                if box.inside(other):
                    self.box_group.boxes.remove(box)
                    self.box_group.save()

        # Remove tiny boxes
        for box in self.box_group.boxes.all():
            if box.area < 100:
                self.box_group.boxes.remove(box)
                self.box_group.save()

        # If there's anything left, approve
        if self.box_group.boxes.count() == 0:
            #return "No boxes drawn"
            return True
        else:
            return True

class Manager(base.Manager):

    ################
    # HIT SETTINGS #
    ################

    # Batching
    batch_size = 2
    max_wait = 5 * MINUTE

    # Payment
    reward = .13
    duplication = 2

    # Advertising
    qualifications = [min_approval(98), min_completed(100), locale('US')]
    keywords = ['picture', 'draw', 'box', 'food']
    title = 'Draw a box around each food on a plate'
    description = 'Help us figure out how many different foods are on the same plate.'

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
