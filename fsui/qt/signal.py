import weakref
from types import TracebackType
from typing import Any, Optional, Type

# noinspection PyUnresolvedReferences
from fsui.qt.qt import QSignal

# from fswidgets.widget import Widget


Signal = QSignal


class SignalWrapper:
    """The signal wrapper makes it easy to temporarily disable a signal."""

    # FIXME: Using any due to circular deps
    def __init__(self, parent: Any, name: str) -> None:
        self.parent = weakref.ref(parent)
        self.name = name
        self.inhibit = SignalInhibitor()

    def connect(self, obj: Any) -> None:
        getattr(self.parent(), self.name + "_signal").connect(obj)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        getattr(self.parent(), self.name + "_signal").emit(*args, **kwargs)


class SignalInhibitor:
    """Helper class for SignalWrapper."""

    def __init__(self) -> None:
        self._inhibited = False

    def __enter__(self) -> None:
        self._inhibited = True

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._inhibited = False

    def __bool__(self) -> bool:
        return self._inhibited
