import queue
import traceback
from typing import Any, Callable

from fsui.qt import QCoreApplication, QEvent, QObject


class CustomEvent(QEvent):
    def __init__(self):
        QEvent.__init__(self, QEvent.User)


class EventHandler(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.queue = queue.Queue()

    def customEvent(self, _):
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

    def post_callback(self, function, args, kwargs):
        self.queue.put((function, args, kwargs))
        QCoreApplication.instance().postEvent(self, CustomEvent())


event_handler = EventHandler()


def call_after(function: Any, *args: Any, **kwargs: Any):
    event_handler.post_callback(function, args, kwargs)


def callAfter(function: Callable[[], None]) -> None:
    event_handler.post_callback(function, [], {})
