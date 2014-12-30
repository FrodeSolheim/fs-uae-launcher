import weakref


class ContextAware(object):

    def __init__(self, context):
        self.__context = weakref.ref(context)

    @property
    def context(self):
        return self.__context()
