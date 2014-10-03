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

    photoset = CharField(max_length=100)

    def setup(self):
        self.hire(tag.draw_always_vote,'tag')
        self.hire(identify.describe_and_match,'identify')
        
        photo_search = os.path.join(settings.STATIC_DOC_ROOT,'photos',self.photoset,'*.jpg')
        for path in glob.glob(photo_search):
            filename = os.path.basename(path)
            url = '%s/static/photos/%s/%s' % (settings.URL_PATH,self.photoset,filename)
            photo = Photo.factory(photo_url=url)
            self.employee('tag').assign(photo=photo)
        
        
    def work(self):
       
        for output in self.employee('tag').finished:
            for box in output.box_group.boxes.all():
                self.employee('identify').assign(photo = output.photo, box=box)
       
        for output in self.employee('identify').finished:
            self.finish(
                photo = output.photo,
                box = output.box,
                ingredient_list = output.ingredient_list,
            )