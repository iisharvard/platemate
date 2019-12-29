# platemate

PlateMate: crowdsourcing nutritional analyses from food photographs

## Setup

### Install requirements

```ShellSession
sudo apt-get install libjpeg-dev
pip install -r requirements.txt
```

This should install:

* Django 1.8.16
* Pillow (latest)
* Boto3 (latest)
* httpagentparser (latest)
* oauth latest

## Modify Local Settings

* In the platemate directory modify `local_settings.example.py` to your paths
  and rename to `local_settings.py`.
* Store your AWS access ID and secret key in the environment variables MTURK_ID
  and MTURK_KEY.

## Run local version of Postgres Server

If Postgres is installed with `brew` - `brew info postgresql@9.5`

```shell script
pg_ctl -D /usr/local/var/postgresql@9.5 start
```

Check if DB is accessible with `psql`:

```shell script
psql platemate platemate
```

## Create Database Tables

From the platemate directory, run:

```ShellSession
python manage.py migrate auth
python manage.py migrate
```

## Add an admin user

```ShellSession
python manage.py createsuperuser
# TODO add the user to initial data fixutre (or is there one?)
```

## Change password of existing user

```shell script
python manage.py changepassword <username>
```

## Run the project

```ShellSession
python manage.py runserver 0.0.0.0:8000
```

or

```ShellSession
./run.sh
```

## Create HITs on Amazon MTurk sandbox

```ShellSession
python experiment.py BATCH_NAME sandbox
```

where `BATCH_NAME` is a subdirectory under `static/uploaded`. This is
hardcoded and specifying any other path will break things.

## Issues

### Module Not Found

Cause: Likely an import statement in the module is failing because of a
missing library.

Fix: Try each import in the module individually.

### Database Locked

It seems that when both the runserver and the experiment scripts are running,
there is a race condition on the database that would crash one script if the
other is accessing the DB.

### Accessing the database through adminer on iis-dev:

http://adminer.iis-dev.seas.harvard.edu/adminer/

### Deleting all hits from mturk AND resetting the database

```ShellSession
python cleanup.py flush
```
