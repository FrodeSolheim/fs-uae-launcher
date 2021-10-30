# FIXME: Use pluggable main loop implementation

import datetime
import logging
import threading
from typing import Callable, Optional

from fscore.events import Event, EventHelper

log = logging.getLogger(__name__)


class ExitEvent(Event):
    type = "exit"

    def __init__(self) -> None:
        super().__init__()
        log.debug("ExitEvent created at %r", datetime.datetime.now())


class MainLoop:
    def __init__(self) -> None:
        self.exitEvent = EventHelper(ExitEvent)

    def done(self) -> None:
        self.exitEvent(ExitEvent())

    @classmethod
    def schedule(cls, action: Callable[[], None]) -> None:
        print("MainLoop.schedule", action)
        from fsui.qt.callafter import callAfter

        callAfter(action)

    @classmethod
    def run(
        cls, function: Callable[[], None], timeout: Optional[float] = None
    ) -> bool:
        print("runInMainLoop", function)
        if threading.main_thread() == threading.currentThread():
            # Or maybe throw error/warning? Maybe require that this is used with
            # background threads only
            function()
            return True

        event = threading.Event()

        def action() -> None:
            print("Function", function, "is going to run on main thread")
            try:
                function()
            except Exception:
                # FIXME: Define if errors are rethrown to caller?
                log.exception(
                    "Exception occured when running function in main loop"
                )
                pass
            finally:
                print("Function", function, "is done on main thread")
                event.set()

        cls.schedule(action)
        return event.wait(timeout)


_mainLoop: Optional[MainLoop] = None


# FIXME: Make into decorator
# def runsInMainLoop(function: Callable[[], None], timeout: Optional[float] = None):
#     print("runInMainLoop", function)
#     if threading.main_thread() == threading.currentThread():
#         # Or maybe throw error/warning? Maybe require that this is used with
#         # background threads only
#         function()
#         return

#     event = threading.Event()

#     def action():
#         print("Function", function, "is going to run on main thread")
#         try:
#             function()
#         except Exception:
#             # FIXME: Define if errors are rethrown to caller?
#             log.exception("Exception occured when running function in main loop")
#             pass
#         finally:
#             print("Function", function, "is done on main thread")
#             event.set()

#     from fsui.qt.callafter import callAfter

#     callAfter(action)
#     return event.wait(timeout)


def useMainLoop() -> MainLoop:
    global _mainLoop
    if _mainLoop is None:
        _mainLoop = MainLoop()
    return _mainLoop
