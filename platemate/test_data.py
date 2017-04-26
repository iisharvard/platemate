import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.conf import settings

from django.db import connection
from django.contrib.auth.models import User
from management.models import *
from food.models.common import *
from food.models import *

# Tag - Draw
p = Photo.from_string("http://www.platebrain.com/pictures/pilot/pilot1.jpg")
p2 = Photo.from_string("http://www.platebrain.com/pictures/pilot/pilot2.jpg")
p3 = Photo.from_string("http://www.platebrain.com/pictures/pilot/pilot3.jpg")
p4 = Photo.from_string("http://www.platebrain.com/pictures/pilot/pilot4.jpg")
p5 = Photo.from_string("http://www.platebrain.com/pictures/pilot/pilot5.jpg")
"""
draw_m = tag.box_draw.Manager()
draw_m.save()

draw_h = Hit(manager = draw_m)
draw_h.save()

tag.box_draw.Job(photo = p, manager = draw_m, hit = draw_h).save()
tag.box_draw.Job(photo = p2, manager = draw_m, hit = draw_h).save()
tag.box_draw.Job(photo = p3, manager = draw_m, hit = draw_h).save()
tag.box_draw.Job(photo = p4, manager = draw_m, hit = draw_h).save()
tag.box_draw.Job(photo = p5, manager = draw_m, hit = draw_h).save()

print "Tag-Draw: /hit/" + str(draw_h.pk)

# Tag - Vote
vote = tag.box_vote

vote_m = vote.Manager()
vote_m.save()

vote_h = Hit(manager = vote_m)
vote_h.save()

bg1 = BoxGroup.from_json('{"0":{"x1":59,"y1":29,"x2":269,"y2":135,"width":210,"height":106},"1":{"x1":240,"y1":66,"x2":400,"y2":207,"width":160,"height":141},"2":{"x1":129,"y1":137,"x2":332,"y2":274,"width":203,"height":137},"3":{"x1":9,"y1":78,"x2":153,"y2":274,"width":144,"height":196}}', p)
bg2 = BoxGroup.from_json('{"0":{"x1":2,"y1":30,"x2":400,"y2":295,"width":398,"height":265}}', p)

vote_j = vote.Job(manager = vote_m, hit = vote_h, photo=p)
vote_j.save()
vote_j.box_groups.add(bg1)
vote_j.box_groups.add(bg2)
vote_j.save()

print "Tag-Vote: /hit/" + str(vote_h.pk)


# Identify - Describe
desc_m = identify.describe.Manager()
desc_m.save()

desc_h = Hit(manager = desc_m)
desc_h.save()

box1 = bg1.boxes.all()[0]

desc_j = identify.describe.Job(manager=desc_m, hit=desc_h, box=box1, photo=p)
desc_j.save()

print "Identify-Describe: /hit/" + str(desc_h.pk)

# Identify - Match
match = identify.match

match_m = match.Manager()
match_m.save()

match_h = Hit(manager = match_m)
match_h.save()

match_j = match.Job(manager = match_m, hit = match_h, box = box1, photo=p)
match_j.save()

print "Identify-Match: /hit/" + str(match_h.pk)

# Identify - Vote

ivote_m = identify.match_vote.Manager()
ivote_m.save()

ivote_h = Hit(manager = ivote_m)
ivote_h.save()

i = Ingredient(food = Food.get_food(5777))
i.save()

i_potato = Ingredient(food = Food.get_food(36493))
i_potato.save()

i_butter = Ingredient(food = Food.get_food(33814))
i_butter.save()

i_salt = Ingredient(food = Food.get_food(33908))
i_salt.save()

list1 = IngredientList()
list1.save()

list1.ingredients.add(i)

list2 = IngredientList()
list2.save()

list2.ingredients.add(i_potato)
list2.ingredients.add(i_butter)
list2.ingredients.add(i_salt)

list3 = IngredientList()
list3.save()
list3.ingredients.add(i_potato)

list4 = IngredientList()
list4.save()
list4.ingredients.add(i_potato)
list4.ingredients.add(i_butter)

ivote_j = identify.match_vote.Job(manager = ivote_m, hit = ivote_h, box = box1, photo=p)
ivote_j.save()
ivote_j.ingredient_lists.add(list1)
ivote_j.ingredient_lists.add(list2)
ivote_j.ingredient_lists.add(list3)
ivote_j.ingredient_lists.add(list4)

print "Match-Vote: /hit/" + str(ivote_h.pk)

# Measure - Measure
measure_m = measure.estimate.Manager()
measure_m.save()

measure_h = Hit(manager = measure_m)
measure_h.save()

measure_j = measure.estimate.Job(manager = measure_m, hit = measure_h, box = box1, photo=p, ingredient=i)
measure_j.save()

print "Measure-Estimate: /hit/" + str(measure_h.pk)
"""

# FE Test Data

boxes1 = BoxGroup.from_json('{"0":{"x1":59,"y1":29,"x2":269,"y2":135,"width":210,"height":106},"1":{"x1":240,"y1":66,"x2":400,"y2":207,"width":160,"height":141},"2":{"x1":129,"y1":137,"x2":332,"y2":274,"width":203,"height":137},"3":{"x1":9,"y1":78,"x2":153,"y2":274,"width":144,"height":196}}', p)

box = boxes1.boxes.all()[0]
box.desc = "Mashed Potatoes"
box.save()

i = Ingredient(food = Food.get_food(5777))
i.serving = i.food.servings()[7]
i.amount = 4.0
i.box = box
i.save()

i_butter = Ingredient(food = Food.get_food(33814))
i_butter.serving = i_butter.food.servings()[1]
i_butter.amount = 1
i_butter.box = box
i_butter.save()

list1 = IngredientList()
list1.box = box
list1.save()

list1.ingredients.add(i)
list1.ingredients.add(i_butter)

s = Submission(
    tagged_boxes = boxes1,
    user = User.objects.get(username='admin'),
    meal = 'D',
    photo = p,
    date = datetime.strptime("2011-03-31", "%Y-%m-%d").date(),
    identified_ingredients = list1,
    submitted = datetime.now(),
    processed = datetime.now(),
    completed = datetime.now(),
)
s.save()
s.measured_ingredients.add(i)
s.measured_ingredients.add(i_butter)


photo8 = Photo.from_string("http://www.platebrain.com/pictures/pilot/pilot8.jpg")
boxes8 = BoxGroup.from_json('{"0":{"x1":165,"y1":1,"x2":332,"y2":128,"width":167,"height":127},"1":{"x1":227,"y1":90,"x2":370,"y2":261,"width":143,"height":171},"2":{"x1":146,"y1":150,"x2":256,"y2":297,"width":110,"height":147},"3":{"x1":105,"y1":207,"x2":204,"y2":298,"width":99,"height":91},"4":{"x1":81,"y1":4,"x2":214,"y2":199,"width":133,"height":195}}', photo8)
box8 = boxes8.boxes.all()[0]

carrots_f = Food.get_food(6037)
carrots_i = Ingredient(food = carrots_f, serving = carrots_f.servings()[1], amount = 0.5, box = box8)
carrots_i.save()
carrots_l = IngredientList(box = box8)
carrots_l.save()
carrots_l.ingredients.add(carrots_i)

s2 = Submission(
    photo = photo8,
    tagged_boxes = boxes8,
    user = User.objects.get(username='admin'),
    meal = 'L',
    date = datetime.strptime("2011-03-31", "%Y-%m-%d").date(),
    identified_ingredients = carrots_l,
    submitted = datetime.now(),
    processed = datetime.now(),
    completed = datetime.now(),
)
s2.save()
s2.measured_ingredients.add(carrots_i)
