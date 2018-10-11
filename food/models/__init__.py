from management.models import SmartModel
from management.helpers import *

self = sys.modules[__name__]
my_path = os.path.dirname(__file__)
for module_name in get_modules(my_path):
    module = __import__(module_name, globals(), locals(), [], -1)
    for name, model in get_models(module, SmartModel):
        setattr(self, name, model)
