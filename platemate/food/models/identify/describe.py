from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
from urllib import unquote

class Input(base.Input):
    box = OneOf(Box)

class Output(base.Output):
    box = OneOf(Box)
    desc = CharField(max_length=500)
    ingredients = TextField()

class Job(base.Job):
    box = OneOf(Box)
    iteration = IntegerField(default=1)
    desc = CharField(max_length=500, default='')
    ingredients = TextField(default='')

class Response(base.Response):
    desc = CharField(max_length=500)
    ingredients = TextField()

    # What should we do if they don't change anything?
    def validate(self):
        self.raw = (self.desc, self.ingredients)

        if self.desc == '':
            return "No description for desc item"
        elif self.ingredients == '':
            return "No description for ingredients"
        #elif self.desc == self.to_job.desc and self.ingredients == self.to_job.ingredients: #or?
        #    return "You didn't change anything"
        else:
            return True

class Manager(base.Manager):
    #########
    # STATE #
    #########
    num_iterations = 2

    ################
    # HIT SETTINGS #
    ################

    # Batching
    batch_size = 2
    max_wait = 5 * MINUTE

    # Payment
    reward = .13
    duplication = 1

    # Advertising
    qualifications = [min_approval(98), min_completed(100), locale('US')]
    keywords = ['picture', 'describe', 'food', 'identify']
    title = 'Describe a food and its ingredients from a photograph'
    description = 'Look at a picture of food, and tell us what kind of food it is and what the ingredients are'

    #########
    # LOGIC #
    #########
    def work(self):
        for input in self.assigned:
            self.new_job(
                iteration=1,
                box=input.box,
                desc='',
                ingredients='',
                from_input=input,
            )

        for job in self.completed_jobs:
            response = job.valid_responses.all()[0]
            if job.iteration == self.num_iterations:
                self.finish(
                    box=job.box,
                    desc=response.desc,
                    ingredients=response.ingredients,
                    from_job=job,
                )
            else:
                # Prevent turkers who worked on earlier steps from contributing to later steps
                forbidden_workers = list(job.forbidden_workers.all())
                forbidden_workers.append(response.assignment.worker)

                self.new_job(
                    iteration=job.iteration + 1,
                    box=job.box,
                    desc=response.desc,
                    ingredients=response.ingredients,
                    forbidden_workers=forbidden_workers,
                    from_input=job.from_input,
                )
