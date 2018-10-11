from management.models.manager import Input
from food.models import *
from management.models.smart_model import OneOf, ManyOf, SmartModel
from django.core.serializers import serialize

# Takes a list of models
def dump(models):

    models_seen = set()

    while models:
        dict = {}

        model = models.pop()
        if model in models_seen:
            continue

        dict['pk'] = model.pk
        dict['model'] = model.__class__.__name__

        for field, type in model._fields:
            dict[field] = []
            if isinstance(type, ManyOf):
                for value in getattr(model, field).all():
                    dict[field].append(value.pk)
                    models.append(value)

            else:
                value = getattr(model, field)
                if isinstance(value, SmartModel):
                    models.append(value)
                    dict[field] = value.pk
                else:
                    dict[field] = value

        print dict
