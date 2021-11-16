import weakref

# from fsgamesys.FSGameSystemContext import FSGameSystemContext


class ContextAware(object):
    # def __init__(self, context: FSGameSystemContext):
    def __init__(self, context):
        self.__context = weakref.ref(context)

    @property
    def gsc(self):
        return self.__context()

    @property
    def context(self):
        return self.__context()
