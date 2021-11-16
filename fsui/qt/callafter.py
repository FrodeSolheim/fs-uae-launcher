import queue
import traceback
from queue import Queue
from typing import Any, Callable, Dict, Tuple

from fsui.qt import QCoreApplication, QEvent, QObject


class CustomEvent(QEvent):
    def __init__(self) -> None:
        QEvent.__init__(self, QEvent.User)


class EventHandler(QObject):
    def __init__(self) -> None:
        QObject.__init__(self)
        self.queue: Queue[
            Tuple[Callable[..., Any], Tuple[Any, ...], Dict[Any, Any]]
        ] = Queue()

    def customEvent(self, a0: QEvent) -> None:
        while True:
            try:
                function, args, kwargs = self.queue.get_nowait()
                print(function, args, kwargs)
            except queue.Empty:
                break
            try:
                function(*args, **kwargs)
            except Exception:
                # log.warn("callback event failed: %r %r",
                #         self.callback, self.args, exc_info=True)
                print("-- callback exception --")
                traceback.print_exc()

    def post_callback(
        self,
        function: Callable[..., Any],
        args: Tuple[Any, ...],
        kwargs: Dict[Any, Any],
    ) -> None:
        self.queue.put((function, args, kwargs))
        qCoreApplication = QCoreApplication.instance()
        assert qCoreApplication is not None
        qCoreApplication.postEvent(self, CustomEvent())


event_handler = EventHandler()


def call_after(
    function: Callable[..., Any], *args: Any, **kwargs: Any
) -> None:
    event_handler.post_callback(function, args, kwargs)


def callAfter(function: Callable[[], None]) -> None:
    event_handler.post_callback(function, (), {})
