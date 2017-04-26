from food.models.common import *
import management.models as base
from food.models import tag, identify, measure

from django.conf import settings
import os, glob

class Output(base.Output):
    photo = OneOf(Photo)
    box = OneOf(Box)
    ingredient_list = OneOf(IngredientList)

class Manager(base.Manager):

    

    def setup(self):
        self.hire(identify.describe,'describe')
        
        
        
        
        
    def work(self):
        pass
        