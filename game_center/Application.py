from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
#from fsbc.Application import Application as BaseApplication
from fsui import Application as BaseApplication
from fsgs.application import ApplicationMixin


class Application(ApplicationMixin, BaseApplication):

    instance = None
    name = None

    @classmethod
    def init(cls, name):
        cls.name = name

    def __init__(self):
        BaseApplication.__init__(self, Application.name)
