import logging
import pprint

# Set various logging levels. For reference, these are the standard levels:
# CRITICAL 50
# ERROR 40
# WARNING 30
# INFO 20
# DEBUG 10
# NOTSET 0

LOGGING_LEVEL = 10
FOOD_CONTROL = 40
MANAGER_CONTROL = 30
TURK_CONTROL = 25
LOOP_CONTROL = 20
LOOP_SETUP = 30
CONTENT_TYPE_WARNING = 15
TURK_WARNING = 50

logger = logging.getLogger('django')

content_type_logger = logging.getLogger('content_type_logger')
content_type_logger.setLevel(logging.INFO)

def log(message, level, *args):
    if level >= LOGGING_LEVEL:
        logger.log(level, message)
        for arg in args:
            logger.log(level, pprint.pformat(arg))

def log_content_type_info(message):
    content_type_logger.info(message)
