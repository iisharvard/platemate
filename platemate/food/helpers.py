import os, sys
from django.conf import settings
from PIL import Image
from models.common import *

def create_or_get_api_user():
    api_user_name = 'API_USER'
    api_user_exists = User.objects.filter(username=api_user_name).exists()
    if api_user_exists:
        return User.objects.get(username=api_user_name)
    else:
        api_user = User(username=api_user_name)
        api_user.save()
        return api_user

def photo_url_for_processed_photo_upload(photo, sub_dir, photo_name):
    photo_dir_name = os.path.join(settings.STATIC_DOC_ROOT, sub_dir)
    photo_path = os.path.join(settings.STATIC_DOC_ROOT, sub_dir, 'raw', photo_name)

    try:
        os.makedirs(photo_dir_name)
    except os.error:
        pass

    destination = open(photo_path, 'wb+')
    for chunk in photo.chunks():
        destination.write(chunk)
    destination.close()

    # Original image
    original = Image.open(photo_path)

    # Resize it to 400px wide (usually 300 high)
    width, height = original.size
    new_size = 400, int(height * 400.0 / width)
    smaller = original.resize(new_size, Image.ANTIALIAS)

    # Save it to photos directory
    out_dir = os.path.join(settings.STATIC_DOC_ROOT, sub_dir,'resized')
    try:
        os.makedirs(out_dir)
    except os.error:
        pass

    out_path = os.path.join(out_dir,photo_name)
    smaller.save(out_path)

    saved_photo_url = '%s/static/%s/resized/%s' % (settings.URL_PATH, sub_dir, photo_name)
    return saved_photo_url

def get_data_for_submission(submission):
    photo = submission.photo
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
