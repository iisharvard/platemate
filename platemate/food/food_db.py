from django.core.exceptions import ObjectDoesNotExist
from fatsecret import *

class PlateMateApp(FatSecretApplication):
    key = "a622119cca9648ee8c7aef7fc7aeb957"
    secret = "25a32e5a93f5401caa753852a5f3a4dc"

class FoodDb:    
    def __init__(self):
        self._client = FatSecretClient().setApplication(PlateMateApp)
        self._client.connect()
            
    def search(self, query):
        return self._client.request("foods.search", search_expression=query, max_results=25)
    
    def get(self, food_id):
        return self._client.request("food.get", food_id=food_id)