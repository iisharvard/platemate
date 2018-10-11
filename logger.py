import sys
import logging

LOGGING_LEVEL = 10

FOOD_CONTROL = 40
MANAGER_CONTROL = 30
TURK_CONTROL = 25
LOOP_CONTROL = 20
LOOP_SETUP = 30

CONTENT_TYPE_WARNING = 15

TURK_WARNING = 50

content_type_logger = logging.getLogger('content_type_logger')
content_type_logger.setLevel(logging.INFO)
fh = logging.FileHandler('log/content_type_info.log')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
content_type_logger.addHandler(fh)

def log(message, level):
    if level >= LOGGING_LEVEL:
        print message
        sys.stdout.flush()

def log_content_type_info(message):
    content_type_logger.info(message)
