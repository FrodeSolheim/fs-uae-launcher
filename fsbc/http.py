try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

try:
    from urllib.request import HTTPBasicAuthHandler, build_opener, Request, \
        urlopen
except ImportError:
    from urllib2 import HTTPBasicAuthHandler, build_opener, Request, urlopen

try:
    from urllib.parse import quote_plus, unquote, unquote_plus
except ImportError:
    from urllib import quote_plus, unquote, unquote_plus
