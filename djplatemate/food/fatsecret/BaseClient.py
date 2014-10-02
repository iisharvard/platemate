from Errors import *
from TokenStore import *
from oauth import oauth
from OAuth import *
import urllib
import httplib
try:
    import json
except ImportError:
    import simplejson as json

class FatSecretClient(object):
    SERVER       = 'platform.fatsecret.com'
    PORT         = 80
    SIGNER       = oauth.OAuthSignatureMethod_HMAC_SHA1()
    HTTP_METHOD  = 'GET'
    HTTP_HEADERS = {}
    HTTP_HEADERS_POST = {"Content-type": "application/x-www-form-urlencoded", }
    HTTP_HEADERS_GET  = {}
    HTTP_URL     = 'http://platform.fatsecret.com/rest/server.api'
    HTTP_RELURL  = 'rest/server.api'
    
    OAUTH_REQTOK_URL = 'http://www.fatsecret.com/oauth/request_token'
    OAUTH_UAUTH_URL = 'http://www.fatsecret.com/oauth/authorize'
    OAUTH_ACCESS_URL = 'http://www.fatsecret.com/oauth/access_token'    

    class _MethodProxy(object):
        def __init__(self, client, path):
            self.__client, self.__path = client, path
        def __getattr__(self, name):
            return FatSecretClient._MethodProxy(self.__client, self.__path+'.'+name)
        def __call__(self, *args, **kwargs):
            return self.request(self.__path, *args, **kwargs)

    def __getattr__(self, name):
        return self.__dict__.get(name, FatSecretClient._MethodProxy(self, name))

    def authorize(self, key = None):
        if not self.loadToken(key):
            token = self.getRequestToken()
            verifier = self.getUserAuthentication(token)
            self.authorizeRequestToken(verifier)
        result = self.profile.get()
        self.saveToken(key, self.token)
        return result

    def getRequestTokenCallback(self):
        #return 'http://localhost:56711'
        return 'oob'

    def getRequestToken(self):
        result = self._auth_request(OAUTH_CALLBACK=self.getRequestTokenCallback(),
                                    HTTP_METHOD='GET', 
                                    HTTP_URL=self.OAUTH_REQTOK_URL)
        return self.token 
   
    def getUserAuthentication(self, token):
        import webbrowser
        webbrowser.open('%s?%s'%(self.OAUTH_UAUTH_URL, token))
        return raw_input('Enter verification code: ')
                
    def authorizeRequestToken(self, verifier):
        result = self._auth_request(HTTP_METHOD='GET',
                                    VERIFIER=verifier,
                                    HTTP_URL=self.OAUTH_ACCESS_URL)
        return self.token 


    AUTH_NONE = 0
    AUTH_SIGNED = 1
    AUTH_DELEGATE = 2
    __methods__ = {
        'food.add_favorite': AUTH_DELEGATE,
        'food.delete_favorite': AUTH_DELEGATE,
        'food.get':  AUTH_SIGNED,
        'foods.get_favorites': AUTH_DELEGATE,
        'foods.get_most_eaten': AUTH_DELEGATE,
        'foods.get_recently_eaten': AUTH_DELEGATE,
        'foods.search': AUTH_SIGNED,
        'recipe.add_favorite': AUTH_DELEGATE,
        'recipe.delete_favorite': AUTH_DELEGATE,
        'recipe.get': AUTH_SIGNED,
        'recipes.get_favorites': AUTH_DELEGATE,
        'recipes.search': AUTH_SIGNED,
        'recipe_types.get': AUTH_SIGNED,
        'saved_meal.create': AUTH_DELEGATE,
        'saved_meal.delete': AUTH_DELEGATE,
        'saved_meal.edit': AUTH_DELEGATE,
        'saved_meals.get': AUTH_DELEGATE,
        'saved_meal_item.create': AUTH_DELEGATE,
        'saved_meal_item.create': AUTH_DELEGATE,
        'saved_meal_items.create': AUTH_DELEGATE,
        'exercises.get': AUTH_SIGNED,
        'profile.create': AUTH_SIGNED,
        'profile.get': AUTH_DELEGATE,
        'profile.get_auth': AUTH_SIGNED,
        'profile.request_script_session_key': AUTH_SIGNED,
        'food_entries.copy': AUTH_DELEGATE,
        'food_entries.copy_saved_meal': AUTH_DELEGATE,
        'food_entries.get': AUTH_DELEGATE,
        'food_entries.get_month': AUTH_DELEGATE,
        'food_entry.create': AUTH_DELEGATE,
        'food_entry.delete': AUTH_DELEGATE,
        'food_entry.edit': AUTH_DELEGATE,
        'exercise_entries.commit_day': AUTH_DELEGATE,
        'exercise_entries.get': AUTH_DELEGATE,
        'exercise_entries.get_month': AUTH_DELEGATE,
        'exercise_entries.save_template': AUTH_DELEGATE,
        'exercies_entry.edit': AUTH_DELEGATE,
        'weight.update': AUTH_SIGNED,
        'weights.get_month': AUTH_DELEGATE,
    }
    def __init__(self):
        self.application = None
        self.token = None
        self.datastore = None
        self._adjustAuthLevel()


    def setDatastore(self, datastore):
        self.datastore = datastore
        return self

    def getDatastore(self):
        return self.datastore

    def loadToken(self, key):
        if key and self.datastore:
            token = self.datastore.getToken(key)
            if token:
                self.setToken(token)
                return token
        return None 

    def saveToken(self, key, token = None):
        if key and self.datastore:
            token = token or self.token
            self.datastore.putToken(key, token)
        return self       

    def connect(self):
        self.connection = httplib.HTTPConnection('%s:%d'%(self.SERVER, self.PORT))
        return self

    def setApplication(self, application):
        assert (issubclass(application, FatSecretApplication) or
                isinstance(application, FatSecretApplication) or
                application == None)

        if application:
            assert application.key != None
            assert application.secret != None

        self.application = application
        self._adjustAuthLevel()
        return self

    def setToken(self, token):
        assert (isinstance(token, oauth.OAuthToken) or token == None)
        self.token = token;
        self._adjustAuthLevel()
        return self

    def _adjustAuthLevel(self):
        if self.token:
            self._authLevel = FatSecretClient.AUTH_DELEGATE
        elif self.application:
            self._authLevel = FatSecretClient.AUTH_SIGNED
        else:
            self._authLevel = FatSecretClient.AUTH_NONE

    def getMethods(self, current_auth = None):
        current_auth = current_auth or self.getCurrentAuthLevel()
        return [method for method, required_auth in self.__methods__.iteritems() 
                if required_auth <= current_auth] 
            
    def getCurrentAuthLevel(self):
        return self._authLevel


    def _rpath(self, result, *args):
        args = list(args)
        while len(args):
            arg = args.pop(0)
            if arg in result:
                result = result[arg]
            else:
                return None

        if not len(args):
            return result
        else:
            return None


    def _auth_request(self, **parameters):
        http_method  = parameters.pop('HTTP_METHOD', self.HTTP_METHOD)
        http_url     = parameters.pop('HTTP_URL', self.HTTP_URL)
        http_headers = parameters.pop('HTTP_HEADERS', self.HTTP_HEADERS) 
        callback     = parameters.pop('OAUTH_CALLBACK', None) 
        verifier     = parameters.pop('VERIFIER', None)

        # Generate OAuth Request
        req = FSRequest.from_consumer_and_token(
            self.application,
            token = self.token,
            verifier = verifier,
            callback = callback,
            http_method = http_method,
            http_url = http_url,
            parameters = parameters)

        # Sign It
        req.sign_request(self.SIGNER, self.application, self.token)

        # Build HTTP Headers from OAuth + POST (if necessary)
        headers = req.to_header()
        headers.update(getattr(self, 'HTTP_HEADERS_%s'%self.HTTP_METHOD))

        # Customize httplib parameters as necessary
        if self.HTTP_METHOD in ['POST']:
            http_url = req.http_url
            postdata = req.to_postdata()
        else:
            http_url = req.to_url()
            postdata = None

        # Let's go!
        follow_redirects = 3
        arrived = False
        while not arrived and follow_redirects:
            self.connection.request(req.http_method,
                                    http_url,
                                    postdata, 
                                    headers)
            resp = self.connection.getresponse()
            if resp.status in [301, 307]:
                resp.read()
                http_url = resp.getheader('Location', http_url)
                follow_redirects -= 1 
            else:
                # All other codes either we're good or we failed...
                arrived = True

        result = resp.read()
        try:
            if result.find('oauth_token') != -1:
                self.setToken(FSToken.from_string(result))
        except:
            # TODO: Figure out why we got this exception and how to fix it...
            raise

        return result
 

    def request(self, method, **parameters):
        #assert method in self.getMethods()
        parameters['method'] = method
        parameters['format'] = 'json'

        if self.getCurrentAuthLevel() <= FatSecretClient.AUTH_NONE:
            req = FSRequest(self.HTTP_METHOD, self.HTTP_URL, parameters)
        else:
            req = FSRequest.from_consumer_and_token(
                self.application,
                token = self.token,
                http_method = self.HTTP_METHOD,
                http_url = self.HTTP_URL,
                parameters = parameters)
              
            req.sign_request(self.SIGNER, self.application, self.token)

        # Generate httplib arguments
        headers = req.to_header()
        headers.update(getattr(self, 'HTTP_HEADERS_%s'%self.HTTP_METHOD))
        if self.HTTP_METHOD in ['POST']:
            http_url = req.http_url
            postdata = req.to_postdata()
        else:
            http_url = req.to_url()
            postdata = None


        # Make the request
        self.connection.request(req.http_method,
                                http_url,
                                postdata, 
                                headers)
        resp = self.connection.getresponse()
    
        # Post-process the result
        result = json.load(resp)
        _rp = self._rpath
        if 'error' in result:
            raise BuildError(result)
        if _rp(result, 'profile', 'auth_token') and _rp(result, 'profile', 'auth_secret'):
            self.setToken(FSToken(_rp(result, 'profile', 'auth_token').encode('utf8'),
                                  _rp(result, 'profile', 'auth_secret').encode('utf8'))) 

        return result
    
class FatSecretApplication(oauth.OAuthConsumer):
    def __init__(self):
        assert self.key != None
        assert self.secret != None
