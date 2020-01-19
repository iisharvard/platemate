from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
from urllib import unquote
from fractions import Fraction

class Input(base.Input):
    ingredient = OneOf(Ingredient) # without Serving or amount filled in

class Output(base.Output):
    ingredient = OneOf(Ingredient) # with Serving and amount filled in

class Job(base.Job):
    ingredient = OneOf(Ingredient) # without Serving or amount filled in

class Response(base.Response):
    ingredient = OneOf(Ingredient) # with Serving and amount filled in

    def validate(self):
        self.raw = (self.measurement, self.serving)

        self.measurement = self.measurement.strip()

        if self.measurement in [None, '']:
            return "No measurement entered."

        def parse(str):
            return float(sum([Fraction(part.strip()) for part in str.split()]))

        try:
            self.measurement = parse(self.measurement)
        except:
            return "You didn't enter a properly formatted number."

        if self.measurement < 0 or self.measurement > 1000:
            return "Impossible measurement entered"

        if self.serving in [None, '']:
            return "No serving size entered."

        serving = Serving.objects.get(pk=self.serving)

        self.ingredient = Ingredient.factory(
            food=self.to_job.ingredient.food,
            serving=serving,
            amount=self.measurement,
            box=self.to_job.ingredient.box,
        )

        self.save()
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
    duplication = 3

    # Advertising
    qualifications = [min_approval(98), min_completed(200), locale('US')]
    keywords = ['picture', 'measure', 'food', 'amount', 'portion']
    title = 'Estimate how much of a food is in a photo'
    description = 'Measure the amount of a particular food in a photo'

    #########
    # LOGIC #
    #########
    def work(self):

        for assignment in self.assigned:
            self.new_job(ingredient=assignment.ingredient, from_input=assignment)

        for job in self.completed_jobs:
            responses = job.valid_responses

            calories = [r.ingredient.calories for r in responses]
            avg_calories = mean(sorted(calories)[1: -1])
            avg_serving = mode([r.ingredient.serving for r in responses])

            i = Ingredient.factory(
                food=job.ingredient.food,
                box=job.ingredient.box,
                serving=avg_serving,
                amount=avg_calories / avg_serving.calories if avg_serving.calories else 0,
            )

            self.finish(ingredient=i, from_job=job)
