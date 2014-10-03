from food.models.common import *
from management.helpers import *
from management.qualifications import *
import management.models as base
from urllib import unquote

class Input(base.Input):
    box = OneOf(Box)
    desc = CharField(max_length=500)
    ingredients = TextField()
    
class Output(base.Output):
    ingredient_lists = ManyOf(IngredientList)
    
class Job(base.Job):
    box = OneOf(Box)
    desc = CharField(max_length=500)
    ingredients = TextField()
    
class Response(base.Response):
    ingredient_list = OneOf(IngredientList)
    
    def validate(self):   
        self.selections = unquote(self.selections)
        self.raw = self.selections
        
        if self.selections in ['','[]','{}']:
            return "No foods matched!"
        else:
            box = self.to_job.box
            box.desc = self.to_job.desc
            box.save()
            self.ingredient_list = IngredientList.from_json(self.selections,box=box)
            
        num = self.ingredient_list.ingredients.count()
        if num <= 4:
            return True
        else:
            return "Too many ingredients entered. Max is 4, you listed %d" % num

class Manager(base.Manager):
    
    ################
    # HIT SETTINGS #
    ################
    
    # Batching
    batch_size = 2
    max_wait = 5 * MINUTE
        
    # Payment
    reward = .06
    duplication = 2
    
    # Advertising
    qualifications = [min_approval(98),min_completed(200),locale('US')]
    keywords = ['picture','identify','food','database','match']
    title = 'Match up food descriptions and pictures with a food database'
    description = 'Use descriptions written by other Turkers to match up a photograph with foods from a database'
    
    #########
    # LOGIC #
    #########
    def work(self):
    
        for input in self.assigned:
            self.new_job(
                box = input.box,
                desc = input.desc,
                ingredients = input.ingredients,
                from_input = input,
            )
            
        for job in self.completed_jobs:
            responses = job.valid_responses.all()
            self.finish(
                ingredient_lists = [response.ingredient_list for response in responses],
                from_job=job,
            )