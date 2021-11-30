from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
from urllib import unquote
from django.core.exceptions import ObjectDoesNotExist

class Input(base.Input):
    ingredient_list = OneOf(IngredientList)

class Output(base.Output):
    ingredient_list = OneOf(IngredientList)

class Job(base.Job):
    selected_ingredients = OneOf(IngredientList)
    unselected_ingredients = OneOf(IngredientList)
    iteration = IntegerField(default=1)

class Response(base.Response):
    selected_ingredients = OneOf(IngredientList)
    unselected_ingredients = OneOf(IngredientList)

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

    num_iterations = 2

    ################
    # HIT SETTINGS #
    ################

    # Batching
    batch_size = 2
    max_wait = 5 * MINUTE

    # Payment
    reward = .10
    duplication = 1 # Job will be iterated twice, but only one at a time.

    # Advertising
    qualifications = [min_approval(98), min_completed(200), locale('US')]
    keywords = ['picture', 'identify', 'food', 'database', 'match']
    title = 'Remove duplicate entries in a list of ingredients'
    description = 'Remove duplicate entries in a list of ingredients for a photograph of a meal'

    #########
    # LOGIC #
    #########
    def work(self):
        for assignment in self.assigned:
            self.new_job(
                iteration=1,
                selected_ingredients=assignment.ingredient_list,
                unselected_ingredients=None,
                from_input=assignment,
            )

        for job in self.completed_jobs:
            response = job.valid_responses.all()[0]
            if job.iteration == self.num_iterations:
                self.finish(
                    ingredient_list=response.selected_ingredients,
                    from_job=job,
                )
            else:
                # Prevent turkers who worked on earlier steps from contributing to later steps
                forbidden_workers = list(job.forbidden_workers.all())
                forbidden_workers.append(response.assignment.worker)

                self.new_job(
                    iteration=job.iteration + 1,
                    selected_ingredients=response.selected_ingredients,
                    unselected_ingredients=response.unselected_ingredients,
                    forbidden_workers=forbidden_workers,
                    from_input=job.from_input,
                )
