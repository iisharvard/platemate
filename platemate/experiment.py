from management.run import run
from food.models import chiefs
import sys

photoset = sys.argv[1]
mode = sys.argv[-1]

run(
    chief_module   = chiefs.from_static,
    args           = {'photoset': photoset,'sandbox': (mode != 'real')},
    operation      = photoset,
)
