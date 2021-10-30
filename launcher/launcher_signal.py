import threading
from typing import Any, List

from fsbc.signal import Signal as BaseSignal

main_thread_id = threading.current_thread().ident


class LauncherSignal(object):
    # listeners: Dict[str, List[SimpleCallable]] = {}

    @classmethod
    def add_listener(cls, signal: str, listener: Any):
        # cls.listeners.setdefault(signal, []).append(listener)
        BaseSignal(signal).connect(listener)

    @classmethod
    def remove_listener(cls, signal: str, listener: Any):
        # cls.listeners[signal].remove(listener)
        BaseSignal(signal).disconnect(listener)

    @classmethod
    def broadcast(cls, signal: str, *args: List[Any]):
        if signal == "config":
            # temporary, while restructuring
            from fsgamesys.context import fsgs

            key, value = args
            fsgs.signal.notify("fsgs:config:" + key, value)

        # if threading.current_thread().ident == main_thread_id:
        #     cls.do_broadcast(signal, *args)
        # else:
        #     def function():
        #         cls.do_broadcast(signal, *args)
        #     fsui.call_after(function)
        BaseSignal(signal).notify(*args)
