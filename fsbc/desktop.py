from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import webbrowser
_url_open_function = None


def open_url_in_browser(url):
    if _url_open_function:
        _url_open_function(url)
    else:
        webbrowser.open(url)


def set_open_url_in_browser_function(func):
    global _url_open_function
    _url_open_function = func
