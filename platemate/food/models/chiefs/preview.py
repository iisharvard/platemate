from food.models.common import *
import management.models as base
from food.models import tag, identify, measure

class Manager(base.Manager):

    def setup(self):
        # Common test data
        photos = [
            Photo.factory(photo_url="http://www.platebrain.com/pictures/pilot/pilot1.jpg"),
            Photo.factory(photo_url="http://www.platebrain.com/pictures/pilot/pilot2.jpg"),
            Photo.factory(photo_url="http://www.platebrain.com/pictures/pilot/pilot3.jpg"),
            Photo.factory(photo_url="http://www.platebrain.com/pictures/pilot/pilot4.jpg"),
            Photo.factory(photo_url="http://www.platebrain.com/pictures/pilot/pilot5.jpg"),
        ]
        
        boxgroups = [
            BoxGroup.from_json('{"0":{"x1":59,"y1":29,"x2":269,"y2":135,"width":210,"height":106},"1":{"x1":240,"y1":66,"x2":400,"y2":207,"width":160,"height":141},"2":{"x1":129,"y1":137,"x2":332,"y2":274,"width":203,"height":137},"3":{"x1":9,"y1":78,"x2":153,"y2":274,"width":144,"height":196}}', photos[0]),
            BoxGroup.from_json('{"0":{"x1":2,"y1":30,"x2":400,"y2":295,"width":398,"height":265}}', photos[0]) 
        ]
        
        boxes = list(boxgroups[0].boxes.all())
        
        potato = Ingredient.factory(food = Food.get_food(36493),box=boxes[0])
        butter = Ingredient.factory(food = Food.get_food(33814),box=boxes[0])
        salt = Ingredient.factory(food = Food.get_food(33908),box=boxes[0])
        
        ingredientlist1 = IngredientList.factory(ingredients=[potato,butter,salt],box=boxes[0])
        ingredientlist2 = IngredientList.factory(ingredients=[potato],box=boxes[0])
        
        
        
        # Supervisors to use
        self.hire(tag.box_draw,'tag.box_draw')
        self.hire(tag.box_vote,'tag.box_vote')
        self.hire(identify.describe,'identify.describe')
        self.hire(identify.match,'identify.match')
        self.hire(identify.match_vote,'identify.match_vote')
        self.hire(measure.estimate,'measure.estimate')
            
        # Assign some stuff to the supervisors
        for photo in photos:
            self.employee('tag.box_draw').assign(photo=photo)
        
        self.employee('tag.box_vote').assign(
            box_groups = boxgroups,
        )
        
        for box in boxes:
            self.employee('identify.describe').assign(box=box)
            
        self.employee('identify.match').assign(
            box=boxes[0],
            desc='Mashed Potatoes',
            ingredients='Potato\nButter\nSalt\nChives',
        )
        
        self.employee('identify.match').assign(
            box=boxes[1],
            desc='Steamed Broccoli',
            ingredients='Broccoli flowers',
        )
        
        self.employee('identify.match_vote').assign(
            ingredient_lists = [ingredientlist1, ingredientlist2]
        )
        
        for ingredient in [potato,butter,salt]:
            self.employee('measure.estimate').assign(
                ingredient=ingredient,
            )