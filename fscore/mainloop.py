# FIXME: Use pluggable main loop implementation

from typing import Callable


class MainLoop:
    @classmethod
    def schedule(cls, action: Callable[[], None]):
        print("MainLoop.schedule", action)
        from fsui import call_after

        call_after(action)
