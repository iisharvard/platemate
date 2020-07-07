import os, sys
from django.conf import settings
from PIL import Image
from models.common import *
from logger import *
import platemate_constants

def is_authenticated_api_request(request):
    return ('HTTP_X_API_KEY' in request.META and request.META['HTTP_X_API_KEY'] == settings.API_KEY)

def create_or_get_api_user():
    api_user_name = platemate_constants.API_USER_NAME
    api_user_exists = User.objects.filter(username=api_user_name).exists()
    if api_user_exists:
        return User.objects.get(username=api_user_name)
    else:
        api_user = User(username=api_user_name)
        api_user.save()
        return api_user

def process_photo_and_get_url(photo, sub_dir, photo_name):
    photo_dir_name = os.path.join(settings.STATIC_DOC_ROOT, sub_dir)
    raw_dir = os.path.join(photo_dir_name, 'raw')

    try:
        os.makedirs(raw_dir)
    except os.error:
        pass

    raw_photo_path = os.path.join(raw_dir, photo_name)
    destination = open(raw_photo_path, 'wb+')
    for chunk in photo.chunks():
        destination.write(chunk)
    destination.close()

    # Raw image
    raw_photo = Image.open(raw_photo_path)

    logger.info("Processsing image")
    logger.info(raw_photo)

    if raw_photo.mode in ("RGBA", "P"):
        raw_photo = raw_photo.convert("RGB")

    # Resize it to 400px wide (usually 300 high)
    width, height = raw_photo.size
    new_size = 400, int(height * 400.0 / width)
    smaller = raw_photo.resize(new_size, Image.ANTIALIAS)

    # Save it to photos directory
    out_dir = os.path.join(photo_dir_name, 'resized')
    try:
        os.makedirs(out_dir)
    except os.error:
        pass

    out_path = os.path.join(out_dir, photo_name)
    smaller.save(out_path)

    saved_photo_url = '%s/static/%s/resized/%s' % (settings.URL_PATH, sub_dir, photo_name)
    return saved_photo_url

def get_data_for_submission(submission):
    photo = submission.photo
    box_group = BoxGroup.objects.filter(photo=photo)
    boxes = Box.objects.filter(photo=photo)
    ingredient_boxes = []
    for b in boxes:
        box = {'id': b.id}
        ingredients = Ingredient.objects.filter(box=b)
        valid_ingredients = {}
        if len(ingredients) > 0:
            for i in ingredients:
                if i.amount:
                    if i.food not in valid_ingredients:
                        valid_ingredients[i.food] = []
                    valid_ingredients[i.food].append(i)
            ingredient_list = []
            for k, v in valid_ingredients.iteritems():
                num_entry = len(v) * 1.0
                food_entry = {
                    'description': k.food_name,
                }
                food_entry['calories'] = round(sum([e.serving.calories * e.amount for e in v]) / num_entry, 1)
                food_entry['fat'] = round(sum([e.serving.fat * e.amount for e in v]) / num_entry, 1)
                food_entry['carbohydrate'] = round(sum([e.serving.carbohydrate * e.amount for e in v]) / num_entry, 1)
                food_entry['protein'] = round(sum([e.serving.protein * e.amount for e in v]) / num_entry, 1)

                ingredient_list.append(food_entry)

            box['ingredients'] = ingredient_list

            ingredient_boxes.append(box)
    data = {'calories':0, 'fat':0, 'carbohydrate':0, 'protein':0}
    for b in ingredient_boxes:
        for i in b['ingredients']:
            data['calories'] += i['calories']
            data['fat'] += i['fat']
            data['carbohydrate'] += i['carbohydrate']
            data['protein'] += i['protein']
    return data

def get_status_for_submission(submission):
    is_completed = submission.check_completed()
    if is_completed:
        return 'COMPLETED'
    elif submission.processed is not None:
        return 'PROCESSING'
    else:
        return 'SUBMITTED'
