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

    # We assume here that client side validation has caught any attempt to submit zero selected
    # ingredients.
    def validate(self):
        # Parse out ingredient parameters coming from form into nice clean dictionary.
        ingredient_params = {int(key[11:]): value == '1' for key, value in vars(self).items()
                             if key.startswith('ingredient_')}

        # Prepare lists
        box = self.to_job.selected_ingredients.box
        self.selected_ingredients = IngredientList(box=box)
        self.unselected_ingredients = IngredientList(box=box)
        self.selected_ingredients.save()
        self.unselected_ingredients.save()

        # Sort ingredients into lists
        for food_id, selected in ingredient_params.items():
            ingredient = Ingredient(food=Food.get_food(food_id))
            # We need to include a box with the ingredients so that subsequent code
            # can access the submission. This is a big code smell but we're just dealing with it for now.
            # The box we set here may not be the same box the ingredient originally came from,
            # but that doesn't matter since we're no longer highlighting any of the boxes in the measure step.
            ingredient.box = box
            ingredient.save()
            if selected:
                self.selected_ingredients.ingredients.add(ingredient)
            else:
                self.unselected_ingredients.ingredients.add(ingredient)
        self.selected_ingredients.save()
        self.unselected_ingredients.save()
        self.save()

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
