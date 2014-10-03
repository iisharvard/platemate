from oauth import oauth
import cgi

class FSToken(oauth.OAuthToken):
    def from_string(s):
        """ Returns a token from something like:
        oauth_token_secret=xxx&oauth_token=xxx

        Overridden to allow parsing of auth_secret in addition to auth_token_secret
        """
        params = cgi.parse_qs(s, keep_blank_values=False)
        key = params['oauth_token'][0]
        secret = params.get('oauth_token_secret', params.get('oauth_secret'))[0] 
        token = oauth.OAuthToken(key, secret)
        try:
            token.callback_confirmed = params['oauth_callback_confirmed'][0]
        except KeyError:
            pass # 1.0, no callback confirmed.
        return token
    from_string = staticmethod(from_string)

class FSRequest(oauth.OAuthRequest):
    @classmethod
    def from_consumer_and_token(cls, oauth_consumer, token=None,
            callback=None, verifier=None, http_method=oauth.HTTP_METHOD,
            http_url=None, parameters=None):
        """ Overridden to allow optional oauth_callback and oauth_verifier """
        if not parameters:
            parameters = {}

        defaults = {
            'oauth_consumer_key': oauth_consumer.key,
            'oauth_timestamp': oauth.generate_timestamp(),
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_version': oauth.OAuthRequest.version,
        }

        defaults.update(parameters)
        parameters = defaults

        if token:
            parameters['oauth_token'] = token.key
            if getattr(token, 'callback', None):
                parameters['oauth_callback'] = token.callback
            elif callback:
                parameters['oauth_callback'] = callback;
            if verifier:
                # 1.0a support for verifier.
                parameters['oauth_verifier'] = verifier
        elif callback:
            # 1.0a support for callback in the request token request.
            parameters['oauth_callback'] = callback

        return cls(http_method, http_url, parameters)

from Thread import FSThread 
import BaseHTTPServer
import cgi
import time


def RunHTTPServer(httpd):
    httpd.serve_forever()

class MyHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self, *args):
        print args
        path = self.path.strip('/?')
        try:
            params = cgi.parse_qs(path)
            self.server.tokens.append(params)        
            print "Added %s to tokens"%str(params)
        except:
            pass

def WaitForPingback(timeout = 45):
    httpd = BaseHTTPServer.HTTPServer(('localhost', 0), MyHTTPHandler)
    httpd.tokens = []
    print "listening on %s:%d"%(httpd.server_name, httpd.server_port)
    t = FSThread(target=httpd.serve_forever) 
    t.start()
    t0 = time.time()
    while not len(httpd.tokens):
        if time.time() - t0 > timeout:
            raise ValueError('Timeout waiting for pingback...')
        time.sleep(1.0)
    t.terminate()
    print httpd.tokens


