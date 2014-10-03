class TokenDatastore(object):
    def putToken(self, key, token):
        raise NotImplementedError()
    def getToken(self, key):
        raise NotImplementedError()

class TokenSimpleCache(TokenDatastore):
    def __init__(self):
        self.cache = {}
    def putToken(self, key, token):
        self.cache[key] = token
    def getToken(self, key):
        try:
            return self.cache.get(key, None)
        except:
            return None

try:
    import shelve
    class TokenShelf(TokenSimpleCache):
        def __init__(self, filename='tokens.dat'):
            self.cache = shelve.open(filename, writeback = False)
    
except:
    pass

