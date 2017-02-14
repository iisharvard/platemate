from django.db import models
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from logger import *
import sys
import traceback
import inspect

# modified very slightly from http://code.google.com/p/django-polymorphic-models/

class PolymorphicMetaclass(ModelBase):
    def __new__(cls, name, bases, dct):
        def save(self, *args, **kwargs):
            test_logging = True
            #try:
            if(not self.content_type):
                log("self.content_type is false", CONTENT_TYPE_WARNING)
                attrs = str(self.__dict__)
                log_string = "Before setting content type: %s : %s" % (self, attrs)
                log(log_string, CONTENT_TYPE_WARNING)
                #("model: %s" % model_as_string, CONTENT_TYPE_WARNING)
                found_content_type = ContentType.objects.get_for_model(self.__class__)
                log("Found content_type: %s" % found_content_type.__dict__, CONTENT_TYPE_WARNING)
                #raise RuntimeError('self.content_type is false')
                self.content_type_id = found_content_type.id
            #except Exception as e: #I think we have to raise excption to get backtrace?
                log("Backtrace:", CONTENT_TYPE_WARNING)
                traceback.print_stack()
            models.Model.save(self, *args, **kwargs)
        def downcast(self):
            model = self.content_type.model_class()
            if (model == self.__class__):
                return self
            return model.objects.get(pk=self.pk)

        if issubclass(dct.get('__metaclass__', type), PolymorphicMetaclass):
          dct['content_type'] = models.ForeignKey(ContentType, editable=False, null=True)
          dct['save'] = save
          dct['downcast'] = downcast

        return super(PolymorphicMetaclass, cls).__new__(cls, name, bases, dct)

class DowncastMetaclass(PolymorphicMetaclass):
    def __new__(cls, name, bases, dct):
        dct['objects'] = DowncastManager()
        return super(DowncastMetaclass, cls).__new__(cls, name, bases, dct)

class DowncastManager(models.Manager):
    use_for_related_fields = True #changed from original
    def get_queryset(self):
        return DowncastQuerySet(self.model)

class DowncastQuerySet(QuerySet):
    def __getitem__(self, k):
        try:
            result = super(DowncastQuerySet, self).__getitem__(k)
        except IndexError:
            raise ObjectDoesNotExist
        if isinstance(result, models.Model) :
            return result.downcast()
        else :
            return result
    def __iter__(self):
        for item in super(DowncastQuerySet, self).__iter__():
            yield item.downcast()
