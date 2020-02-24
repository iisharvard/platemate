from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
from urllib import unquote
from django.core.exceptions import ObjectDoesNotExist

class Input(base.Input):
    ingredient_lists = ManyOf(IngredientList)

class Output(base.Output):
    ingredient_list = OneOf(IngredientList)

class Job(base.Job):
    ingredient_lists = ManyOf(IngredientList)

class Response(base.Response):
    ingredient_list = OneOf(IngredientList)

    def validate(self):
        self.raw = self.ingredients_choice
        if self.ingredients_choice in ['', ' ', None]:
            return "No choice of ingredients provided"
        try:
            self.ingredient_list = IngredientList.objects.get(pk=self.ingredients_choice)
        except ObjectDoesNotExist:
            return "Invalid choice entered"

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
    qualifications = [min_approval(98), min_completed(200), locale('US')]
    keywords = ['picture', 'identify', 'food', 'database', 'match', 'vote']
    title = 'Pick which list of ingredients best matches a photo'
    description = 'Select the list of ingredients that best matches the highlighted portion of a picture'

    #########
    # LOGIC #
    #########
    def work(self):

        for assignment in self.assigned:
            self.new_job(
                ingredient_lists=assignment.ingredient_lists.all(),
                from_input=assignment,
            )

        for job in self.completed_jobs:

            if self.duplication > 1:
                choices = [response.ingredient_list for response in job.valid_responses]
                il = mode(choices)
            else:
                il = job.valid_response.ingredient_list

            self.finish(
                ingredient_list=il,
                from_job=job,
            )
