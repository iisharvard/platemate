from food.models.common import *
import management.models as base
from food.models import tag, identify, measure
from logger import *
from django.conf import settings
import os, glob, random
from PIL import Image

class Manager(base.Manager):

    # Never stop running
    @property
    def done(self):
        return False

    def setup(self):
        self.hire(tag.draw_maybe_vote,'tag')
        self.hire(identify.describe_match_maybe_vote,'identify')
        self.hire(measure.estimate,'measure')

    def work(self):
        # New submissions -> Tag
        for submission in Submission.objects.filter(processed=None):
            submission.manager = self
            submission.mark_processed()
            log('New submission %s now processing!' % submission,MANAGER_CONTROL)
            self.employee('tag').assign(photo=submission.photo)

        # Tag -> Identify
        for output in self.employee('tag').finished:
            submission = output.box_group.submission
            submission.tagged_boxes = output.box_group
            submission.save()
            for box in output.box_group.boxes.all():
                self.employee('identify').assign(box=box)

       # Identify -> Measure
        for output in self.employee('identify').finished:
            submission = output.ingredient_list.box.photo.submission
            for ingredient in output.ingredient_list.ingredients.all():
                submission.identified_ingredients.add(ingredient)
            submission.save()
            for ingredient in output.ingredient_list.ingredients.all():
                self.employee('measure').assign(ingredient = ingredient)

        # Measure -> active submission
        for output in self.employee('measure').finished:
            submission = output.ingredient.submission
            submission.measured_ingredients.add(output.ingredient)
            submission.save()
            if submission.check_completed() and not submission.manual and not submission.hidden:
                log('Submission %s completed!' % submission,MANAGER_CONTROL)
                #Disable submission announcement because email not set up for generic url and ssl
                #submission.announce_completed()
