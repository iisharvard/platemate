from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from food.models.common import *
from django.template.loader import get_template, render_to_string
from django.template import defaultfilters

register = template.Library()

@register.filter
def annotate_photo(value):
    "Shows the boxes from a BoxGroup or Box on a photo"
    class_name = value.__class__.__name__
    if class_name == 'BoxGroup':
        boxes = value.boxes.all()
        if len(boxes) == 0:
            return mark_safe("<div class='container'><img class='mainphoto' src='" + value.photo.photo_url + "' /></div>")
        photo_url = boxes[0].photo.photo_url
        other_boxes = []
    elif class_name == 'Box':
        bg = value.group
        boxes = [value]
        other_boxes = list(bg.boxes.all())
        other_boxes.remove(value)
        photo_url = value.photo.photo_url
    else:
        return ''

    #photo_url = arg.photo_url
    ret = "<div class='container'><img class='mainphoto' src='" + photo_url + "' />"
    for box in boxes:
        ret += "<span class='box' style='background-image: url(" + photo_url + "); background-position: -" + str(box.x) + "px -" + str(box.y) + "px; top: " + str(box.y) + "px; left: " + str(box.x) + "px; width: " + str(box.width) + "px; height: " + str(box.height) + "px;'></span>"
        ret += "<span class='box-border' style='top: " + str(box.y) + "px; left: " + str(box.x) + "px; width: " + str(box.width) + "px; height: " + str(box.height) + "px;'></span>"
    for box in other_boxes:
        ret += "<span class='box-border other' style='top: " + str(box.y) + "px; left: " + str(box.x) + "px; width: " + str(box.width) + "px; height: " + str(box.height) + "px;'></span>"
    ret += "</div>"
    return mark_safe(ret)

@register.filter
def mult(value, arg):
    "Multiplies the arg and the value"
    return float(value) * float(arg)

@register.filter
def sub(value, arg):
    "Subtracts the arg from the value"
    return float(value) - float(arg)

@register.filter
def div(value, arg):
    "Divides the value by the arg"
    return float(value) / float(arg)

@register.filter
def measurement_options(f, selected=None):
    "Displays the measurement types of Servings for a Food as options for a select"
    food = Food.get_food(f.pk)
    servings = food.servings()
    ret = "<option value=''>--SELECT ONE--</option>"
    for serving in servings:
        if selected == serving.pk:
            ret += "<option value='%d' title='%d' selected>%s</option>\n" % (serving.pk, serving.calories, serving.serving_description)
        else:
            ret += "<option value='%d' title='%d'>%s</option>\n" % (serving.pk, serving.calories, serving.serving_description)
    return mark_safe(ret)

@register.filter
def show_submission(submission, debug=False):
    return render_to_string('../templates/fe/submission.html', {'submission': submission, 'path': settings.URL_PATH, 'debug': debug})

@register.filter
def should_show(submission, debug):
    return debug or (submission.completed and not submission.manual)

@register.filter
def show_ingredient_row(ingredient, do_indent):
    return render_to_string('../templates/fe/ingredient_row.html', {
        'ingredient': ingredient,
        'path': settings.URL_PATH,
        'do_indent': do_indent > 0,
    })

@register.filter
def format_list(list):
    return render_to_string('list.html', {'list': list})

@register.filter
def format_dict(dict):
    return render_to_string('dictionary.html', {'dict': dict})

@register.filter
def format_model(model):

    name_of = lambda x: x.__class__.__name__.lower()
    display_of = lambda x: render_to_string('common/%s.html' % name_of(x), {name_of(x): x, 'other': model})
    d = {}

    for field, type in model._fields:

        if isinstance(type, ManyOf):
            values = getattr(model, field).all()
            displays = [display_of(value) for value in values]
            d[field] = format_list(displays)

        elif isinstance(type, OneOf):
            value = getattr(model, field)
            if value:
                d[field] = display_of(value)
            else:
                d[field] = '(empty)'

        elif isinstance(type, TextField):
            value = getattr(model, field)
            d[field] = defaultfilters.linebreaksbr(value)

        else:
            value = getattr(model, field)
            d[field] = str(value)

    return format_dict(d)

@register.filter
def display_job(job):
    return format_model(job)

@register.filter
def display_response(response):
    return format_model(response)
