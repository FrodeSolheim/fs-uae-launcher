from fsgs.application import ApplicationMixin
from fsui import Application as BaseApplication


class Application(ApplicationMixin, BaseApplication):
    instance = None
    name = None

    @classmethod
    def init(cls, name):
        cls.name = name

    def __init__(self):
        BaseApplication.__init__(self, Application.name)
