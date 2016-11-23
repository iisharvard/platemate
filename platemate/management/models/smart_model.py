from django.db import models
from django.db.models import *
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from downcast import DowncastMetaclass
from pprint import pprint
import sys

class SmartMetaclass(DowncastMetaclass):

    debugMode = False

    class Meta:
        pass

    def __new__(cls, name, bases, attrs):
        # Stupid debugging
        if cls.debugMode:
            print 'name',name
            print 'bases',bases
            print 'attrs',attrs    
    
        # Lets us name classes built up out of modules
        path = attrs['__module__'].split('.')
        app = path[0]
        base_name = path[-1]
        category = path[-2]
        
        
        # Just for managers
        if name in ['Manager','Input','Output','Job','Response'] and app != 'management':
            if name == 'Manager':
                m = sys.modules[attrs['__module__']]
                attrs['Response'] = getattr(m,'Response',None)
                attrs['Job'] = getattr(m,'Job',None)
                attrs['Input'] = getattr(m,'Input',None)
                attrs['Output'] = getattr(m,'Output',None)
                
                # Wrap the key functions in a transaction
                if 'work' in attrs:
                    attrs['work'] = transaction.commit_on_success(attrs['work'])
                if 'setup' in attrs:
                    attrs['setup'] = transaction.commit_on_success(attrs['setup'])
                                
            if name == 'Job':
                attrs['template'] = '%s/%s' % (category,base_name)
                
            attrs['step'] = '%s.%s' % (category,base_name)
            name = '%s_%s' % (base_name,name)

        #if name in ['Job','Response','Input','Output']:
        attrs['_fields'] = [(field_name, value) for (field_name, value) in attrs.items() if hasattr(value,'__class__') and issubclass(value.__class__,Field)]
            
            
        # Lets us split modules into different files
        if 'Meta' not in attrs:
            attrs['Meta'] = cls.Meta
        attrs['Meta'].app_label = app
        
            
        # Automatic downcasting for polymorphic models
        # (handled by parent)
        return super(SmartMetaclass, cls).__new__(cls, name, bases, attrs)

class SmartModel(Model):
    __metaclass__ = SmartMetaclass
    
    @classmethod
    def factory(cls,**kwargs):
        m = cls()
        m.save()
        for field, value in kwargs.items():
            setattr(m,field,value)
        m.save()
        return m
    
    class Meta:
        abstract = True
        
class OneOf(ForeignKey):

    def __init__(self, *args, **kwargs):
        kwargs['related_name'] = '+'
        kwargs['null'] = True
        super(OneOf, self).__init__(*args, **kwargs)
        
class ManyOf(ManyToManyField):

    def __init__(self, *args, **kwargs):
        #if 'related_name' not in kwargs:
        #    kwargs['related_name'] = '+'
        super(ManyOf, self).__init__(*args, **kwargs)