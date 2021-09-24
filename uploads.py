from management.run import run
from food.models import chiefs
from logger import *
import sys

# Example usage: "python uploads.py sandbox"
operation = sys.argv[1]
mode = sys.argv[-1]

try:
    run(
        chief_module=chiefs.from_uploads,
        args={'sandbox': (mode != 'real')},
        operation=operation
    )
except:
    logger.exception("Fatal error in processor")
