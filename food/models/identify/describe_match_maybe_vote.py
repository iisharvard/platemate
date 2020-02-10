from food.models.common import *
import management.models as base
from food.models import identify

class Input(base.Input):
    box = OneOf(Box)

class Output(base.Output):
    ingredient_list = OneOf(IngredientList)

class Manager(base.Manager):

    def setup(self):
        self.hire(identify.describe, 'describe')
        self.hire(identify.match, 'match')
        self.hire(identify.match_vote, 'vote')

    def work(self):
        for assignment in self.assigned:
            self.employee('describe').assign(box=assignment.box)

        for output in self.employee('describe').finished:
            self.employee('match').assign(
                box=output.box,
                desc=output.desc,
                ingredients=output.ingredients
            )

        for output in self.employee('match').finished:
            lists = output.ingredient_lists.all()
            if len(lists) == 1:
                self.finish(ingredient_list=lists[0])
            else:
                if lists[0] == lists[1]:
                    self.finish(ingredient_list=lists[0])
                else:
                    self.employee('vote').assign(ingredient_lists=lists)

        for output in self.employee('vote').finished:
            self.finish(ingredient_list=output.ingredient_list)
