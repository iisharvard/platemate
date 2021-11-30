from food.models.common import *
import management.models as base
from food.models import identify

class Input(base.Input):
    box_group = OneOf(BoxGroup)

class Output(base.Output):
    ingredient_list = OneOf(IngredientList)

class Manager(base.Manager):
    def setup(self):
        self.hire(identify.describe_match_maybe_vote, 'describe_match_maybe_vote')

    def work(self):
        # Each time we get assigned a new box group, send each box through the describe/match/vote flow
        for assignment in self.assigned:
            for box in assignment.box_group.boxes.all():
                self.employee('describe_match_maybe_vote').assign(box=box)

        # Each time a box is completed with matching, check if the submission has all ingredients
        # identified. If so, we are done and we merge all the ingredient lists into one.
        for output in self.employee('describe_match_maybe_vote').finished:
            box_group = output.ingredient_list.box.groups.get()
            submission = box_group.submission
            if submission.check_all_identified() and not submission.ingredients_combined:
                submission.ingredients_combined = True
                submission.save()
                self.finish(ingredient_list=self.combined_ingredient_list(box_group))

    def combined_ingredient_list(self, box_group):
        # We need to include a box with the ingredient list so that subsequent code
        # can access the submission. This is a big code smell but we're just dealing with it for now.
        result = IngredientList()
        result.box = box_group.boxes.first()
        result.save()

        for food in self.unique_foods(box_group):
            ingredient = Ingredient(food=food)
            # We also need to include a box with the individual ingredients for the same reason as above.
            # The box we set here may not be the same box the ingredient originally came from,
            # but that doesn't matter since we're no longer highlighting any of the boxes in the measure step.
            ingredient.box = result.box
            ingredient.save()
            result.ingredients.add(ingredient)
        result.save()
        return result

    def unique_foods(self, box_group):
        result = set()
        for box in box_group.boxes.all():
            # A given box can have multiple ingredient lists (e.g. one as an input and one as an output)
            # So here we select for ingredient lists that are associated with the Output
            # of describe_match_maybe_vote.
            for ingredient_list in box.ingredient_list.all():
                if identify.describe_match_maybe_vote.Output.objects.filter(ingredient_list_id=ingredient_list.id).exists():
                    for ingredient in ingredient_list.ingredients.all():
                        result.add(ingredient.food)
        return result
