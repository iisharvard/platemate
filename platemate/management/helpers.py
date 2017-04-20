import pprint, sys, random, os, re, inspect
from datetime import datetime
import math


# Timing

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

# General functions

def with_probability(p):
    r = random.random()
    return r < p

def argmax(elts,func):
    #return sorted(elts, key=func)[0]
    return max(elts,key=func)

def argmin(elts,func):
    return min(elts, key=func)

def counts(elts):
    counts = {}
    for elt in elts:
        counts.setdefault(elt,0)
        counts[elt] += 1
    return counts
    
def mode(elts):
    c = counts(elts)
    return argmax(elts,lambda elt: c[elt])
    
def mean(elts):
    return (sum(elts) + 0.0)/len(elts)
    
def median(elts):
    if len(elts) % 2:
        return elts[len(elts) / 2]
    else:
        return mean(elts[len(elts) / 2: len(elts) / 2 + 1])

# Debugging

def var_dump(obj):
    pprint.pprint(vars(obj))
    
# Modules

def get_models(module,base):
    return [(name, cls) for name, cls in inspect.getmembers(module) if inspect.isclass(cls) and issubclass(cls, base)]

def get_modules(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == '.py' and name != '__init__':
                path = os.path.relpath(os.path.join(root,name),dir)
                mod_name = path.replace(os.sep,'.')
                yield mod_name