from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404, render
from models.common import *
from management.models import Manager
#from django.contrib.auth.decorators import login_required
from django import forms
from datetime import date, datetime
from django.db import transaction

from helpers import *

#for api
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


import food_db, random, os
from PIL import Image

def login_required(f):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("%s/login/?next=%s/" % (settings.URL_PATH,settings.URL_PATH))
        return f(request, *args, **kwargs)
    wrap.__doc__= f.__doc__
    wrap.__name__= f.__name__
    return wrap


def food_search(request, query):
    fdb = food_db.FoodDb()
    results = fdb.search(query)
    return render(request, "food_search.json", context={
        "foods": Food.search(query),
    },
    content_type="application/json")

def food_autocomplete(request):
    fdb = food_db.FoodDb()
    query = request.GET["term"]
    results = fdb.search(query)
    return render(request, "food_autocomplete.json", context={
        "foods": Food.search(query),
    },
    content_type="application/json")

def show_pipeline(request, operation, photo=None):
    chief = Manager.objects.get(operation=operation,name='chief').downcast()
    outputs = chief.get_outputs()

    # Only show managers doing hits
    outputs = filter(lambda o: o.manager.employees.count() == 0, outputs)

    def sortvalue(output):
        photo = Photo()
        box = Box()
        ingredient = Ingredient()
        step = output.step
        id = output.pk

        def exists(obj,attr):
            return hasattr(obj,attr) and getattr(obj,attr)

        if exists(output,'photo'):
            photo = output.photo
        if exists(output,'box_group'):
            photo = output.box_group.photo
        if exists(output,'box_groups'):
            photo = output.box_groups.all()[0].photo
        if exists(output,'box'):
            box = output.box
            photo = box.photo
        if exists(output,'ingredient_list'):
            box = output.ingredient_list.ingredients.all()[0].box
            photo = box.photo
        if exists(output,'ingredient_lists'):
            box = output.ingredient_lists.all()[0].ingredients.all()[0].box
            photo = box.photo
        if exists(output,'ingredient'):
            ingredient = output.ingredient
            box = ingredient.box
            photo = box.photo

        return (photo.pk,box.pk,ingredient.pk,step)


    return render(request, 'outputs.html', context={
        "outputs": sorted(outputs,key=sortvalue),
        "path": settings.URL_PATH,
    })

@login_required
def fe_main(request):
    return fe_day(request, date.today().isoformat())

@login_required
def fe_day(request, day):
    try:
        d = datetime.strptime(day, "%Y-%m-%d").date()
        submissions = Submission.objects.filter(user = request.user, date = d)
        meal_types = ["Total", "Breakfast", "Lunch", "Dinner", "Snacks"]

        meals_dict = {}
        for meal_type in meal_types:
            meals_dict[meal_type] = {"submissions": [], "calories": 0.0, "fat": 0.0, "carbohydrate": 0.0, "protein": 0.0}

        for s in submissions:
            meals_dict[s.get_meal_display()]["submissions"].append(s)
            for box, ingredients in s.breakdown().items():
                for ingredient in ingredients:
                    if ingredient.serving and ingredient.amount:
                        meals_dict[s.get_meal_display()]["calories"] += ingredient.serving.calories * ingredient.amount
                        meals_dict[s.get_meal_display()]["fat"] += ingredient.serving.fat * ingredient.amount
                        meals_dict[s.get_meal_display()]["carbohydrate"] += ingredient.serving.carbohydrate * ingredient.amount
                        meals_dict[s.get_meal_display()]["protein"] += ingredient.serving.protein * ingredient.amount

                        meals_dict["Total"]["calories"] += ingredient.serving.calories * ingredient.amount
                        meals_dict["Total"]["fat"] += ingredient.serving.fat * ingredient.amount
                        meals_dict["Total"]["carbohydrate"] += ingredient.serving.carbohydrate * ingredient.amount
                        meals_dict["Total"]["protein"] += ingredient.serving.protein * ingredient.amount

        meals = [{
            "meal": meal_type,
            "submissions": meals_dict[meal_type]["submissions"],
            "calories": meals_dict[meal_type]["calories"],
            "fat": meals_dict[meal_type]["fat"],
            "carbohydrate": meals_dict[meal_type]["carbohydrate"],
            "protein": meals_dict[meal_type]["protein"],
        } for meal_type in meal_types]

        c = {
            "user": request.user,
            "meals": meals,
            "day": d,
            "path": settings.URL_PATH,
            "form": SubmissionForm(initial = {"date": d}),
            "debug": "debug" in request.REQUEST,
        }
        c.update(csrf(request))
        return render(request, "fe/index.html", context=c)
    except ValueError:
        return HttpResponseNotFound("Invalid date")

@csrf_exempt
def api_submission_statuses(request):
    if not is_authenticated_api_request(request):
        return HttpResponse('Unauthorized - Missing or invalid api key, please try again.', status=401)
    try:
        json_data = json.loads(request.body)
        submission_ids = json_data['ids']
        response_json = {}
        for submission_id in submission_ids:
            try:
                submission = Submission.objects.get(pk=submission_id)
                data = get_data_for_submission(submission)
                status = get_status_for_submission(submission)
            except:
                status = 'NOT_FOUND'
                data = {}
            response_json[submission_id] = {"status": status, "data": data}
        return JsonResponse(response_json, safe=False)
    except ValueError:
        return HttpResponseBadRequest("There was an error, please try again.")


def photo_summary(request, photo_id):
    photo = Photo.objects.filter(id = photo_id)[0]
    box_group = BoxGroup.objects.filter(photo = photo)
    boxes = Box.objects.filter(photo = photo)
    ingredient_boxes =[]
    for b in boxes:
        box = {'id': b.id}
        ingredients = Ingredient.objects.filter(box = b)
        valid_ingredients = {}
        if len(ingredients) > 0:
            for i in ingredients:
                if i.amount:
                    if i.food not in valid_ingredients:
                        valid_ingredients[i.food] = []
                    valid_ingredients[i.food].append(i)
            ingredient_list = []
            for k, v in valid_ingredients.iteritems():
                num_entry = len(v)*1.0
                food_entry = {
                    'description': k.food_name,
                }
                food_entry['calories'] = round(sum([e.serving.calories * e.amount for e in v])/num_entry,1)
                food_entry['fat'] = round(sum([e.serving.fat * e.amount for e in v])/num_entry, 1)
                food_entry['carbohydrate'] = round(sum([e.serving.carbohydrate * e.amount for e in v])/num_entry,1)
                food_entry['protein'] = round(sum([e.serving.protein * e.amount for e in v])/num_entry,1)

                ingredient_list.append(food_entry)

            box['ingredients'] = ingredient_list

            ingredient_boxes.append(box)
    total = {'calories':0, 'fat':0, 'carbohydrate':0, 'protein':0}
    for b in ingredient_boxes:
        for i in b['ingredients']:
            total['calories'] += i['calories']
            total['fat'] += i['fat']
            total['carbohydrate'] += i['carbohydrate']
            total['protein'] += i['protein']
    c = {
        'ingredient_boxes': ingredient_boxes,
        'total': total,
        'box_group': box_group[0]
    }
    return render(request, "fe/food_summary.html", context=c)


@login_required
def edit_ingredient(request):
    # TODO: Actually check that the logged in user owns this ingredient
    ingredient = get_object_or_404(Ingredient, pk=request.REQUEST["ingredient_id"])
    if "food_id" in request.REQUEST and request.REQUEST["food_id"] != ingredient.food.pk:
        ingredient.food = Food.get_food(request.REQUEST["food_id"])
        ingredient.serving = None
        ingredient.amount = 0.0
        ingredient.save()
    elif "amount" in request.REQUEST and request.REQUEST["amount"] != ingredient.amount:
        ingredient.amount = request.REQUEST["amount"]
        ingredient.save()
    elif "serving_id" in request.REQUEST and (ingredient.serving == None or request.REQUEST["serving_id"] != ingredient.serving.pk):
        ingredient.serving = get_object_or_404(Serving, pk=request.REQUEST["serving_id"])
        ingredient.save()

    return render(request, "fe/ingredient_row_editable.html", context={
        "ingredient": ingredient,
        "path": settings.URL_PATH,
    })

@login_required
def add_ingredient(request):
    submission = get_object_or_404(Submission, pk=request.REQUEST["submission_id"])
    if submission.user != request.user:
        return HttpResponseBadRequest("There was an error, please try again.")

    new_ingredient = Ingredient(
        food = Food.get_food(request.REQUEST["food_id"]),
        amount = 0.0,
        from_turk = False,
    )
    new_ingredient.save()
    submission.measured_ingredients.add(new_ingredient)

    return render(request, "fe/ingredient_row_editable.html", context={
        "ingredient": new_ingredient,
        "path": settings.URL_PATH,
        "full_row": True
    })

@login_required
def delete_ingredient(request):
    # TODO: Actually check that the logged in user owns this ingredient
    ingredient = get_object_or_404(Ingredient, pk=request.REQUEST["ingredient_id"])
    ingredient.hidden = True
    ingredient.save()
    return render(request, "fe/ingredient_row_editable.html", context={
        "ingredient": ingredient,
        "path": settings.URL_PATH,
    })

@login_required
def delete_submission(request):
    submission = get_object_or_404(Submission, pk=request.REQUEST["submission_id"])
    if submission.user != request.user:
        return HttpResponseBadRequest("There was an error, please try again.")

    submission.hidden = True
    submission.save()

    for ingredient in submission.measured_ingredients.all():
        ingredient.hidden = True
        ingredient.save()

    return render(request, "fe/submission.html", context={
        "submission": submission,
        "path": settings.URL_PATH,
    })

class SubmissionForm(forms.Form):
    photo = forms.ImageField()
    meal = forms.ChoiceField(choices=MEAL_CHOICES)

# This dict maps usernames to days to force manual mode.
# Only for use during our user evaluation.
MANUAL_DAYS = {
    "platemate1": ["2011-04-11", "2011-04-12"], # Monday and Tuesday
    "platemate2": ["2011-04-11", "2011-04-12"], # Monday and Tuesday
    "platemate3": ["2011-04-13", "2011-04-14"], # Wednesday and Thursday
    "platemate4": ["2011-04-13", "2011-04-14"], # Wednesday and Thursday
    "platemate5": ["2011-04-11", "2011-04-12"], # Monday and Tuesday
    "platemate6": ["2011-04-13", "2011-04-14"], # Wednesday and Thursday
    "platemate7": ["2011-04-11", "2011-04-12"], # Monday and Tuesday
    "platemate8": ["2011-04-13", "2011-04-14"], # Wednesday and Thursday
    "platemate9": ["2011-04-16", "2011-04-17"], # Saturday and Sunday
    "platemate10": ["2011-04-16", "2011-04-17"], # Saturday and Sunday
    "admin": ["2011-04-10", "2011-04-11"],
}

@transaction.atomic
@csrf_exempt
def api_photo_upload(request):
    if not is_authenticated_api_request(request):
        return HttpResponse('Unauthorized - Missing or invalid api key, please try again.', status=401)
    try:
        now = datetime.now()
        time_string = now.isoformat()
        photo = request.FILES['upload']
        random.seed()
        photo_name = str(random.randint(0,1000000)) + "_" + time_string + "_" + photo.name
        static_sub_dir = 'api/photos'
        saved_photo_url = process_photo_and_get_url(photo, static_sub_dir, photo_name)
        p = Photo.factory(photo_url = saved_photo_url)
        u = create_or_get_api_user()

        s = Submission(
            photo = p,
            meal = 'B',
            date = now,
            user = u,
            submitted = now,
            manual = False
        )
        s.save()

        data = dict({"submission_id" : s.id})

        return JsonResponse(data)
    except ValueError:
        return HttpResponseBadRequest("There was an error, please try again.")
    except IOError:
        return HttpResponse("There was an error saving data, please try again.", status=500)

@transaction.atomic
@login_required
def fe_upload(request, day):
    try:
        d = datetime.strptime(day, "%Y-%m-%d").date()
        if request.method == 'POST':
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                photo = request.FILES["photo"]
                random.seed()
                photo_name = str(random.randint(0,1000000)) + "_" + str(request.user.pk) + "_" + day + "_" + photo.name
                static_sub_dir = 'uploaded'
                saved_photo_url = process_photo_and_get_url(photo, static_sub_dir, photo_name)
                p = Photo.factory(photo_url = saved_photo_url)

                s = Submission(
                    photo = p,
                    meal = request.POST["meal"],
                    date = d,
                    user = request.user,
                    submitted = datetime.now(),
                    manual = request.user.username in MANUAL_DAYS and day in MANUAL_DAYS[request.user.username]
                )
                s.save()
                return HttpResponseRedirect(settings.URL_PATH + '/day/' + day + '/')
            else:
                raise ValueError
        else:
            raise ValueError
    except ValueError:
        return HttpResponseBadRequest("There was an error, please try again.")
