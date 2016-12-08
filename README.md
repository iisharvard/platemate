platemate
=========

PlateMate: crowdsourcing nutritional analyses from food photographs

## Setup

### Install requirements
    sudo apt-get install libjpeg-dev
    pip install -r requirements.txt

This should install:

+ Django 1.8.16
+ Pillow (latest)
+ Boto (latest)
+ httpagentparser (latest)
+ oauth latest

## Modify Local Settings
In the platemate directory modify `local_settings.example.py` to your paths and rename to `local_settings.py`. In the platemate directory, add your Amazon Mechanical Turk keys in `amt_keys.example.py` and save it as `amt_keys.py`

## Create Database Tables
From the platemate directory, run:
    python manage.py syncdb --noinput

## Add an admin user
    python manage.py createsuperuser
    //TODO add the user to initial data fixutre (or is there one?)

## Run the project
    python manage.py runserver 0.0.0.0:8000

or
    ./run.sh


## Create HITs on Amazon MTurk sandbox
    python experiment.py BATCH_NAME sandbox

where `BATCH_NAME` is a subdirectory under `static/uploaded`. This is hardcoded and specifying any other path will break things.

## Issues

### Module no found
Cause: Likely an import statement in the module is failing because of a missing library.
Fix: Try each import in the module individually.

### Database Locked
It seems that when both the runserver and the experiment scripts are running, there is a race condition on the database that would crash one script if the other is accessing the DB.

### Accessing the database through adminer on iis-dev:

http://adminer.iis-dev.seas.harvard.edu/adminer/

### Deleting all hits from mturk AND resetting the database

python cleanup.py flush
