from food.models.common import *
import management.models as base
from food.models import tag

# Roughly means, if boxes are within 30% side length of each other and very close, approve.
MIN_SIMILARITY = 0.7

class Input(base.Input):
    photo = OneOf(Photo)

class Output(base.Output):
    box_group = OneOf(BoxGroup)
    
class Manager(base.Manager):

    def setup(self):
        self.hire(tag.box_draw,'draw')
        self.hire(tag.box_vote,'vote')
    
    def work(self):
        for input in self.assigned:
            self.employee('draw').assign(photo=input.photo)
        
        for output in self.employee('draw').finished:
            bg1,bg2 = output.box_groups.all()[:2]
            similarity = BoxGroup.similarity(bg1,bg2)
            
            # If responses are similar enough, don't bother voting
            if similarity > MIN_SIMILARITY:
                log('Box groups have similarity %.2f so skipping vote' % similarity, FOOD_CONTROL)
            	self.finish(box_group = bg1)
                
            # Otherwise, we need to vote
            else:
                log('Box groups have similarity %.2f so voting' % similarity, FOOD_CONTROL)
            	self.employee('vote').assign(box_groups = [bg1,bg2])
        
        for output in self.employee('vote').finished:
            self.finish(box_group = output.box_group)