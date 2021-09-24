import logging
import pprint

# Set various logging levels. For reference, these are the standard levels:
# CRITICAL 50
# ERROR 40
# WARNING 30
# INFO 20
# DEBUG 10
# NOTSET 0

MIN_LEVEL = 10

FOOD_CONTROL = 20
LOOP_CONTROL = 10
LOOP_SETUP = 20
MANAGER_CONTROL = 20
TURK_CONTROL = 20

logger = logging.getLogger('django')

content_type_logger = logging.getLogger('content_type_logger')
content_type_logger.setLevel(logging.INFO)

def log(message, level, *args):
    if level >= MIN_LEVEL:
        logger.log(level, message)
        for arg in args:
            logger.log(level, pprint.pformat(arg))

def log_content_type_info(message):
    content_type_logger.info(message)
