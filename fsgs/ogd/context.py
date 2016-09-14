from .client import OGDClient


class SynchronizerContext(object):
    meta = {}

    def __init__(self):
        pass

    @property
    def username(self):
        return OGDClient.credentials()[0]

    @property
    def password(self):
        return OGDClient.credentials()[1]
