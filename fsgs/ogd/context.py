from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

# from fsbc.Application import app
from .client import OGDClient


class SynchronizerContext(object):

    meta = {}

    def __init__(self):
        pass

    @property
    def username(self):
        return OGDClient.get_credentials()[0]

    @property
    def password(self):
        return OGDClient.get_credentials()[1]
