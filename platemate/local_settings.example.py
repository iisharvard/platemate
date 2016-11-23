BASE_PATH = r"/Users/eric/Dropbox/PlateMate/platemate/trunk/platemate"
# BASE_PATH = r"D:\Code\platemate"

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
