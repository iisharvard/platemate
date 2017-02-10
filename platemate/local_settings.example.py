BASE_PATH = r"/Users/eric/Dropbox/PlateMate/platemate/trunk/platemate"
# BASE_PATH = r"D:\Code\platemate"

DEBUG = True # Should be False for production

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

TEMPLATE_DIRS = (
    BASE_PATH + "/templates",
)

STATIC_DOC_ROOT = BASE_PATH + "/static"

URL_PATH = ""

DATABASES = {
    'default': {
        # Engines include '.postgresql_psycopg2', '.postgresql', '.mysql', '.sqlite3' or '.oracle'.
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

PYTHONVAR = 'python'

# Hostnames that users can connect to your site with.
ALLOWED_HOSTS = [u'platemate.example.com']

API_KEY = '9904d30797e14dbad1c3d8b40b449cbeecf24dbfbfaa6f3341848789c74f7ad9f3f71c9daaa7279da754d37ecd1610458787e34fbc669ddc1a80266ce412fad8dfec51add9b6f5ec345ba4be7e5e40fe1fffc9144ad616c64f4aea760e8696e0805e2023a71d04e0804961d83bf90820d9a3737d3b00b0125fe3c1bd60c1d58d'
