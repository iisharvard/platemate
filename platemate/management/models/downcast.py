from django.db import models
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

# modified very slightly from http://code.google.com/p/django-polymorphic-models/

class PolymorphicMetaclass(ModelBase):
    def __new__(cls, name, bases, dct):
        def save(self, *args, **kwargs):
            if(not self.content_type):
                self.content_type = ContentType.objects.get_for_model(self.__class__)
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
    def get_query_set(self):
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