from oauth import oauth
import urllib
import httplib
try:
    import json
except ImportError:
    import simplejson as json

class FatSecretError(ValueError):
    def __init__(self, code, message, errorObj):
        self.errorCode = int(code)
        self.errorMessage = message
        self.errorObj = errorObj

    def __str__(self):
        return 'Error %d: %s' % (self.errorCode, self.errorMessage)

class FatSecretAuthError(FatSecretError):
    pass

class FatSecretOAuthError(FatSecretAuthError):
    pass

class FatSecretApplicationError(FatSecretOAuthError):
    pass

class FatSecretUsageError(FatSecretError):
    pass

class FatSecretUnknownMethodError(FatSecretError):
    pass

class FatSecretInvalidParameterError(FatSecretUsageError):
    pass

class FatSecretInvalidRangeError(FatSecretInvalidParameterError):
    pass

class FatSecretInvalidIDError(FatSecretInvalidParameterError):
    pass

class FatSecretInvalidTypeError(FatSecretInvalidParameterError):
    pass

class FatSecretInvalidActivityError(FatSecretInvalidParameterError):
    pass

class FatSecretInvalidTemplateError(FatSecretInvalidActivityError):
    pass

__ERROR_LOOKUP__ = {
    2: FatSecretOAuthError,
    3: FatSecretOAuthError,
    4: FatSecretOAuthError,
    5: FatSecretApplicationError,
    6: FatSecretOAuthError,
    7: FatSecretOAuthError,
    8: FatSecretOAuthError,
    9: FatSecretOAuthError,
    10: FatSecretUnknownMethodError,
    101: FatSecretInvalidParameterError,
    106: FatSecretInvalidIDError,
    107: FatSecretInvalidRangeError,
    108: FatSecretInvalidTypeError,
    201: FatSecretInvalidActivityError,
    202: FatSecretInvalidParameterError,
    204: FatSecretInvalidTemplateError,
    205: FatSecretInvalidRangeError,
    206: FatSecretInvalidRangeError
}

def BuildError(result):
    cls = FatSecretError
    cls = __ERROR_LOOKUP__.get(result['error']['code'], FatSecretError)
    return cls(
        result['error']['code'],
        result['error']['message'],
        result
    )
