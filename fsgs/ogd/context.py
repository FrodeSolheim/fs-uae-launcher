from .client import OGDClient


class SynchronizerContext(object):
    meta = {}

    def __init__(self):
        pass

    @property
    def username(self):
        return OGDClient.auth()[0]

    @property
    def password(self):
        return OGDClient.auth()[1]
