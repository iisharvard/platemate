# platemate

PlateMate: crowdsourcing nutritional analyses from food photographs

## Prerequisites

* libjpeg-dev for image manipulation
* PostgreSQL for storage, with empty database named `platemate`
* Python 2.7
* Pip and Virtualenv packages

## Setup

Setup and enter virtual environment:

    python -m virtualenv venv
    source venv/bin/activate

Then install requirements:

    pip install -r requirements.txt

Next, set up environment variables for local settings:

    cp .env.example .env
    nano .env

Next, migrate the database:

    python manage.py migrate auth
    python manage.py migrate

and add an admin user:

    python manage.py createsuperuser

Finally, to run the dev server:

    python manage.py runserver

See below for more info on development environment workflows.

## Resetting the Database

Ensure that no connections are open (stop development server and/or scripts). Then drop and recreate the database with:

    dropdb platemate
    createdb platemate

Then re-run migrations:

    python manage.py migrate auth
    python manage.py migrate
    python manage.py createsuperuser

Remember the username and password for the superuser account as you may need it later.

## Stubbing Mechanical Turk

To speed up development you may want to complete HITs directly rather than go through Mechanical Turk's sandbox environment.

You can accomplish this as follows:

First, ensure `DEBUG=True` in your `.env` file.

In one console tab, run dev server using the `STUB_TURK` env variable.

    source venv/bin/activate
    STUB_TURK=1 python manage.py runserver

In another console tab, tail the app log:

    tail -f log/app.log

In a third console tab, run the background script, also with the `STUB_TURK` env variable:

    source venv/bin/activate
    STUB_TURK=1 python uploads.py sandbox

To add a new photo submission:

    curl -F "upload=@static/photos/alpha2/pilot8.jpg" -F "caption=grilled+chicken,+rice,+and+veggies" -H "X-Api-Key: xxx" "http://localhost:8000/api/upload_photo"

(Change `xxx` to your API key if applicable.)

You should see fake HIT creation in the app log:

    [2021-11-29 14:32:31] INFO [django:25] (Not actually creating HIT on Turk b/c in stub mode.)
    [2021-11-29 14:32:31] INFO [django:25] Created HIT 1 with 1 jobs and 3 assignments
                    External URL: http://localhost:8000/hit/1/
                    Turk ID: 3869167084222035276
                    Turk URL: https://workersandbox.mturk.com/mturk/preview?groupId=7567002453003033515
                    Type: box_filter_Manager
    [2021-11-29 14:32:31] INFO [django:25] Stubbed HIT URL 1: http://localhost:8000/hit/1/?assignmentId=1156712811778504304
    [2021-11-29 14:32:31] INFO [django:25] Stubbed HIT URL 2: http://localhost:8000/hit/1/?assignmentId=3399088044964261634
    [2021-11-29 14:32:31] INFO [django:25] Stubbed HIT URL 3: http://localhost:8000/hit/1/?assignmentId=7694945927389101546

Now visit each of the `Stubbed HIT URL`s printed in the log and perform the job.
Most terminal applications provide a shortcut for doing this. On Mac OS X, it's Cmd+Double-click.

When you submit the form, it should say the data was saved to a temporary file.
You should then see the app's log find the data and process it.

Wait for each submission to be processed before submitting another one. Otherwise multiple submissions for the same HIT may overwrite each other.
  It may take several iterations of the background loop for a new HIT to be generated or for the
app to report that the submission is complete.

If new HITs are created, visit the new stub URLs, and repeat the process above.
