from management.run import run
from food.models import chiefs
import sys

run(
    chief_module   = chiefs.preview,
    operation      = 'preview',
)
