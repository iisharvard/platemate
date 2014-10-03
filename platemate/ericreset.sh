#!/bin/bash
rm food/fixtures/initial_data.json
python manage.py dumpdata food.Food food.FoodSearchResults food.FoodSearchResult food.Serving --indent 4 --format=json > food/fixtures/initial_data.json
rm db
python manage.py syncdb
python test_data.py