from django.db.models import *
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from food.food_db import *
from management.models import SmartModel, Manager
from management.helpers import *
import json
from management.models.smart_model import OneOf, ManyOf
from logger import *
from datetime import date

PHOTO_WIDTH = 400
PHOTO_HEIGHT = 300
PHOTO_DIAGONAL = 500

MEAL_CHOICES = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner'),
    ('S', 'Snacks'),
)

class Submission(SmartModel):
    # Submitted data
    user = OneOf(User)
    meal = CharField(max_length=1, choices=MEAL_CHOICES)
    date = DateField()
    photo = OneOf('Photo')

    # Turk answers
    manager = ForeignKey(Manager,related_name='submissions',null=True)
    tagged_boxes = OneOf('BoxGroup', null=True)
    identified_ingredients = ManyOf('Ingredient',related_name='identified_for_submissions')
    measured_ingredients = ManyOf('Ingredient',related_name='measured_for_submissions')

    # User answers
    manual = BooleanField(default=False)

    # Status
    submitted = DateTimeField(null=True)
    processed = DateTimeField(null=True)
    completed = DateTimeField(null=True)
    hidden = BooleanField(default=False)

    def breakdown(self):
        boxes = {None: []}
        if self.tagged_boxes:
            for box in self.tagged_boxes.boxes.all():
                boxes[box] = []
        for ingredient in self.measured_ingredients.all():
            boxes[ingredient.box] += [ingredient]
        return boxes

    def manual_ingredients(self):
        ingredients = []
        for ingredient in self.measured_ingredients.all():
            if not ingredient.box:
                ingredients.append(ingredient)
        return ingredients

    def mark_processed(self):
        self.processed = datetime.now()
        self.save()

    def check_completed(self):
        if self.completed is not None:
            return True

        if self.tagged_boxes is None:
            return False

        # Have all the tagged boxes been measured?

        matched_boxes = set([i.box for i in self.identified_ingredients.all()])
        tagged_boxes = self.tagged_boxes.boxes.all()

        if len(matched_boxes) != len(tagged_boxes):
            return False

        # Have all the measured boxes been identified?

        num_identified = self.identified_ingredients.count()
        num_measured = self.measured_ingredients.count()
        if num_measured == num_identified:
            self.completed = datetime.now()
            self.save()
            return True
        else:
            return False

    def announce_completed(self):
        if(self.user.email is None):
            pass
        else:
            self.user.email_user(
            subject = 'New nutrition estimates from PlateMate',
            message = """Hello,

    Your photograph from %s on %s has been analyzed, and our estimate of its nutritional breakdown is now available. To see it, check out http://iis2.seas.harvard.edu/platemate/ and log in. Feel free to respond to this email if you have any questions or concerns, and remember that you can edit the answers you get if they seem inaccurate or incomplete.

    Thanks,
    PlateMate""" % (self.get_meal_display(), self.date.strftime("%A")))

    def __str__(self):
        return self.get_meal_display() + " on " + str(self.date) + " for " + self.user.username

class Photo(SmartModel):
    photo_url = URLField(verbose_name="Photo URL")

    def __str__(self):
        return self.photo_url

    @property
    def submission(self):
        return Submission.objects.get(photo=self)

    @staticmethod
    def from_string(url):
        p = Photo()
        p.photo_url = url
        p.save()
        return p

class Box(SmartModel):
    x = IntegerField(null=True)
    y = IntegerField(null=True)
    width = IntegerField(null=True)
    height = IntegerField(null=True)
    photo = OneOf(Photo)
    desc = CharField(max_length=500,null=True,default=None)

    def __eq__(self,other):
        return self.x == other.x and self.y == other.y and self.width == other.width and self.height == other.height

    # True if SELF is completely inside OTHER
    def inside(self,other):
        left = self.x >= other.x
        right = self.x + self.width <= other.x + other.width
        top = self.y >= other.y
        bottom = self.y + self.width <= other.y + other.width

        return (left and right and top and bottom)

    @property
    def group(self):
        return self.groups.all()[0]

    @property
    def area(self):
        return self.width * self.height

    @property
    def hypotenuse(self):
           return math.sqrt(self.width**2 + self.height**2)

    @staticmethod
    def distance(box1,box2):
        x1, y1 = box1.center
        x2, y2 = box2.center
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    @property
    def center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    def __str__(self):
        return '(%d, %d) %d x %d' % (self.x, self.y, self.width, self.height)

class BoxGroup(SmartModel):
    boxes = ManyOf(Box,related_name='groups')
    photo = OneOf(Photo)

    @property
    def submission(self):
        return self.photo.submission

    def __str__(self):
        try:
            return str([str(b) for b in self.boxes.all()])
        except:
            return "<Box group object>"


    @staticmethod
    def from_json(json_str, photo=None):
        new_group = BoxGroup()
        new_group.save()
        json_obj = json.loads(json_str)
        for json_box in json_obj.values():
            new_group.boxes.create(
                photo = photo,
                x = json_box["x1"],
                y = json_box["y1"],
                width = json_box["width"],
                height = json_box["height"],
            )
        new_group.photo = photo
        new_group.save()
        return new_group

    @staticmethod
    def similarity(bg1,bg2):
        num_boxes = bg1.boxes.count()
        if bg2.boxes.count() != num_boxes:
            return 0.0

        # No boxes in both
        if num_boxes == 0:
            return 1.0

        boxes1 = list(bg1.boxes.all())
        boxes2 = list(bg2.boxes.all())

        def distance_pct(box1,box2):
            #print 'distance',Box.distance(box1,box2) / float(PHOTO_DIAGONAL),box1.center,box2.center
            return Box.distance(box1,box2) / float(PHOTO_DIAGONAL)

        def area_pct(box1,box2):
            if box1.area > box2.area:
                bigger = box1
                smaller = box2
            else:
                bigger = box2
                smaller = box1

            #print 'area',float(smaller.area) / bigger.area,smaller.area,bigger.area,
            return float(smaller.area) / bigger.area


        score = 1
        for box1 in boxes1:
            closest_box = max(boxes2, key=lambda box: -distance_pct(box1,box))
            distance_score = 1 - distance_pct(box1,closest_box)
            area_score = area_pct(box1,closest_box)
            combined_score = distance_score**2 * math.sqrt(area_score)
            #log('score = %.3f = %.3f sqrt(area) * %.3f distance' % (combined_score, math.sqrt(area_score), distance_score),FOOD_CONTROL)

            score *= combined_score

        return score**(1.0/num_boxes)


"""
The food models are a little weird, so here's a quick rundown of how they work:
    * Food, Serving, FoodSearchResults, and FoodSearchResult represent our
      local cache of the food database.  No instance of these models is ever
      HIT-specific.
      - Food contains all the data in the food db for one food.  It is
        primary-keyed to the FatSecret food_id, so only one instance should
        exist for any different food item.
      - Serving contains the types of servings for each Food.
      - FoodSearchResults and FoodSearchResult contain metadata to allow us
        to cache search results in addition to food details from FatSecret.
        These models should never be accessed outside of internal static
        methods in Food.
    * Ingredient and IngredientList encapsulate Food and Serving objects
      to store data about the foods in each photo.
      - Ingredient refers to a Food and Serving type of that Food, and
        contains the amount.  After a Match operation, an Ingredient is
        populated only with the Food.  Serving and amount get filled in
        after Measure.
      - IngredientList is a list of ingredients in a Box.
"""

class Food(SmartModel):
    food_id = IntegerField(primary_key = True) # matches food_id from FatSecret
    food_name = CharField(max_length="500") # matches food_name from FatSecret
    food_description = CharField(max_length="500") #matches food_description from FatSecret

    def __str__(self):
        return self.food_name

    @staticmethod
    def search(query):
        try:
            food_results = FoodSearchResults.objects.get(pk=query)
        except ObjectDoesNotExist:
            fdb = FoodDb()
            results = fdb.search(query)
            if not results.has_key('foods') or not results['foods'].has_key('food'):
                results_list = []
            elif results["foods"]["total_results"] == "1":
                results_list = [results["foods"]["food"]]
            else:
                results_list = results["foods"]["food"]
            food_results = FoodSearchResults.from_db_results(query, results_list)
        return food_results.get_results()

    @staticmethod
    def get_food(food_id):
        try:
            food = Food.objects.get(pk=food_id)
            if len(Serving.objects.filter(food=food)) == 0:
                food.add_serving_data(FoodDb())
        except ObjectDoesNotExist:
            fdb = FoodDb()
            result = fdb.get(food_id)
            food = Food.from_search_result(result["food"])
            food.add_serving_data(fdb)
            food.save()
        return food

    @staticmethod
    def from_search_result(result):
        try:
            existing_food = Food.objects.get(pk=result["food_id"])
            return existing_food
        except ObjectDoesNotExist:
            food = Food()
            food.food_id = result["food_id"]
            food.food_name = result["food_name"]
            if ("food_description" in result.keys()):
                food.food_description = result["food_description"]
            if result["food_type"] == "Brand":
                food.food_name = result["brand_name"] + " " + food.food_name
            food.save()
            return food

    def servings(self):
        return Serving.objects.filter(food=self)

    def add_serving_data(self, fdb):
        result = fdb.get(self.food_id)["food"]
        if result["servings"]["serving"].__class__.__name__ == "dict":
            servings = [result["servings"]["serving"]]
        else:
            servings = result["servings"]["serving"]
        for s in servings:
            new_serving = Serving(
                food = self,
                measurement_description = s["measurement_description"],
                metric_serving_amount = s.get("metric_serving_amount",0),
                metric_serving_unit = s.get("metric_serving_unit",''),
                number_of_units = s["number_of_units"],
                serving_description = s["serving_description"],
                serving_id = s["serving_id"],
            )

            for nutrient in ["calories","carbohydrate","fat","fiber","protein","saturated_fat","sugar","calcium","cholesterol","iron","monounsaturated_fat","polyunsaturated_fat","potassium","vitamin_a","vitamin_c"]:
                if nutrient in s:
                    setattr(new_serving,nutrient,s[nutrient])

            new_serving.save()

class Serving(SmartModel):
    food = ForeignKey('Food')
    measurement_description = CharField(max_length="200")
    metric_serving_amount = FloatField(null=True)
    metric_serving_unit = CharField(max_length="10")
    number_of_units = FloatField(null=True)
    serving_description = CharField(max_length="200")
    serving_id = IntegerField()

    calories = FloatField(null=True)
    carbohydrate = FloatField(null=True)
    fiber = FloatField(null=True)
    protein = FloatField(null=True)
    fat = FloatField(null=True)
    sugar = FloatField(null=True)
    saturated_fat = FloatField(null=True)
    sodium = FloatField(null=True)


    calcium = FloatField(null=True)
    cholesterol = FloatField(null=True)
    iron = FloatField(null=True)
    monounsaturated_fat = FloatField(null=True)
    polyunsaturated_fat = FloatField(null=True)
    potassium = FloatField(null=True)
    vitamin_a = FloatField(null=True)
    vitamin_c = FloatField(null=True)

    def __str__(self):
        return '%s of %s (%d cal)' % (self.serving_description, self.food.food_name, self.calories)


        #self.food.food_name + ': ' + self.measurement_description + ' (' + str(self.calories) + ' cal)'

class FoodSearchResults(SmartModel):
    search_term = CharField(max_length="200", primary_key = True)
    search_results = ManyToManyField(Food, through='FoodSearchResult')

    def __str__(self):
        return self.search_term + "(" + str(len(self.search_results.all())) + " results)"

    def get_results(self):
        return [r.food for r in FoodSearchResult.objects.filter(results=self).order_by('ordering')]

    @staticmethod
    def from_db_results(query, results):
        results_item = FoodSearchResults(search_term = query)
        results_item.save()
        for (counter, result) in enumerate(results):
            food_item = Food.from_search_result(result)
            res = FoodSearchResult(food = food_item, results = results_item, ordering = counter)
            res.save()
        return results_item

class FoodSearchResult(SmartModel):
    food = ForeignKey(Food)
    results = ForeignKey(FoodSearchResults)
    ordering = IntegerField()

    def __str__(self):
        return self.food.food_name + "(" + str(self.ordering) + ")"

class Ingredient(SmartModel):
    food = OneOf(Food)
    serving = OneOf(Serving)
    amount = FloatField(null=True)
    box = OneOf(Box)
    from_turk = BooleanField(default=True) # False when user added
    hidden = BooleanField(default=False) # True when user deleted

    @property
    def submission(self):
        return self.box.photo.submission

    @property
    def calories(self):
        return self.serving.calories * self.amount

    def list_others(self):
        return [i for i in self.list.all()[0].ingredients.all() if i != self]

    def __str__(self):
        if self.serving and self.amount:
            return '%.2f * %s of %s = %d cal' % (self.amount, self.serving.serving_description, self.food, self.calories)
        else:
            return str(self.food)

class IngredientList(SmartModel):
    ingredients = ManyOf(Ingredient,related_name='list')
    box = OneOf(Box)

    def __eq__(self,other):
        return [i.food.pk for i in self.ingredients.all()] == [i.food.pk for i in other.ingredients.all()]

    def __str__(self):
        try:
            return str([str(b) for b in self.boxes.all()])
        except:
            return "<Ingredient List Object>"

    @staticmethod
    def from_json(json_str, box=None):
        new_list = IngredientList()
        new_list.save()
        json_obj = json.loads(json_str)
        for id, name in json_obj.items():
            food = Food.get_food(id)
            new_ingredient = Ingredient(food = food)
            new_ingredient.box = box
            new_ingredient.save()
            new_list.ingredients.add(new_ingredient)
        new_list.box = box
        new_list.save()
        return new_list
