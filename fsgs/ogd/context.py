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
