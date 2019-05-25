import weakref

# noinspection PyUnresolvedReferences
from fsui.qt import Signal


class SignalInhibitor:
    def __init__(self):
        self._inhibited = False

    def __enter__(self):
        self._inhibited = True

    def __exit__(self, exc_type, exc_value, traceback):
        self._inhibited = False

    def __bool__(self):
        return self._inhibited


class SignalWrapper:
    def __init__(self, parent, name):
        self.parent = weakref.ref(parent)
        self.name = name
        self.inhibit = SignalInhibitor()

    def connect(self, obj):
        getattr(self.parent(), self.name + "_signal").connect(obj)

    def emit(self, *args, **kwargs):
        getattr(self.parent(), self.name + "_signal").emit(*args, **kwargs)
