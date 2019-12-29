# Django settings for platemate project.
import os
import urlparse

from dotenv import load_dotenv
load_dotenv()

from management.mturk import MTurkClient

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Should be False for production
DEBUG = (lambda : os.getenv("DEBUG", "false").lower() == "true")()

ADMINS = (
    (os.getenv("ADMIN_NAME", "John Doe"), os.getenv("ADMIN_EMAIL", "user@example.com")),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_PATH, "templates"),
)

STATIC_DOC_ROOT = os.path.join(BASE_PATH, "static")

URL_PATH = os.getenv("BASE_URL", "http://localhost")

DATABASES = {
    'default': {
        # Engines include '.postgresql_psycopg2', '.postgresql', '.mysql', '.sqlite3' or '.oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'platemate',
        'USER': os.getenv("DB_USER", "platemate"),                      # Not used with sqlite3.
        'PASSWORD': os.getenv("DB_PASSWORD", ""),                  # Not used with sqlite3.
        'HOST': os.getenv("DB_HOST", "127.0.0.1"),                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': os.getenv("DB_PORT", "5432"),                      # Set to empty string for default. Not used with sqlite3.
        # 'OPTIONS': {
        #     'timeout': 20
        # }
    }
}

PYTHONVAR = "python"

# Hostnames that users can connect to your site with.
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["localhost", os.getenv("HOST", "localhost")]

API_KEY = os.getenv("API_KEY", "")

TEMPLATE_DEBUG = DEBUG

MTURK_ID = os.getenv('MTURK_ID')
MTURK_KEY = os.getenv('MTURK_KEY')

if MTURK_ID is None or MTURK_KEY is None:
    raise Exception("Your MTurk credentials are not present. Setup MTURK_ID and MTURK_KEY as environment variables")

TURK_REAL = MTurkClient(
    aws_access_key=MTURK_ID,
    aws_secret_key=MTURK_KEY,
    aws_mode='real',
)

TURK_SANDBOX = MTurkClient(
    aws_access_key=MTURK_ID,
    aws_secret_key=MTURK_KEY,
    aws_mode='sandbox',
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 've%nw*o%0h*32nwqlsi^w5&b__t(9n-s2r8&_0byf$aivj+o*^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django_pdb.middleware.PdbMiddleware'
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    #'django.contrib.sites',
    #'django.contrib.messages',
    #'django.contrib.admin',
    #'django.contrib.admindocs',
    'management',
    'food',
    'django.contrib.auth',
    'django.contrib.sessions',
    'sslserver',
    'django_extensions',
    'django_pdb'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

LOGIN_REDIRECT_URL = urlparse.urljoin(URL_PATH, "/")
LOGIN_URL = urlparse.urljoin(URL_PATH, "/login/")

# EMAIL STUFF

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'harvardplatemate@gmail.com'
EMAIL_HOST_PASSWORD = 'bananaS5'
EMAIL_PORT = 587
