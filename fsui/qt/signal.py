import weakref
from typing import Any

# noinspection PyUnresolvedReferences
from fsui.qt.qt import QSignal

Signal = QSignal


class SignalWrapper:
    """The signal wrapper makes it easy to temporarily disable a signal."""

    def __init__(self, parent, name):
        self.parent = weakref.ref(parent)
        self.name = name
        self.inhibit = SignalInhibitor()

    def connect(self, obj):
        getattr(self.parent(), self.name + "_signal").connect(obj)

    def emit(self, *args: Any, **kwargs: Any):
        getattr(self.parent(), self.name + "_signal").emit(*args, **kwargs)


class SignalInhibitor:
    """Helper class for SignalWrapper."""

    def __init__(self):
        self._inhibited = False

    def __enter__(self):
        self._inhibited = True

    def __exit__(self, exc_type, exc_value, traceback):
        self._inhibited = False

    def __bool__(self):
        return self._inhibited
