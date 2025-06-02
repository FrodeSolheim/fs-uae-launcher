import threading
import traceback
from weakref import ref
from typing import Dict, List, Any, Tuple


main_thread_id = threading.current_thread().ident
_signal_id = 0


def new_signal_id():
    global _signal_id
    _signal_id += 1
    return str(_signal_id)


class Listener(object):
    def __init__(self, signal, listener):
        self.description = "<Listener {0}>".format(listener)

        if signal == "config":
            # FIXME: temporary hack for legacy code
            listener = listener.on_config
        elif signal == "setting":
            # FIXME: temporary hack for legacy code
            listener = listener.on_setting
        try:
            # FIXME: temporary hack for legacy code
            listener = getattr(listener, "on_" + signal + "_signal")
        except AttributeError:
            pass

        if hasattr(listener, "__self__") and hasattr(listener, "__func__"):
            self.instance = ref(listener.__self__)
            self.function = ref(listener.__func__)
        else:
            self.instance = None
            self.function = ref(listener)

    def __call__(self, *args, **kwargs):
        if self.instance is not None:
            # noinspection PyCallingNonCallable
            instance = self.instance()
            function = self.function()
            if function is None or instance is None:
                return False
            function(instance, *args, **kwargs)
            return True
        else:
            function = self.function()
            if function is None:
                return False
            function(*args, **kwargs)
            return True

    def __repr__(self):
        return self.description


class Signal:
    # FIXME: should have type Dict[str, Callable]
    # or # type_xxx: Dict[str, Function]
    signal_listeners = {}  # type: Dict[str, Any]
    # listeners = {}
    notifications = []  # type: List[Tuple[str, Any]]
    lock = threading.Lock()

    quit = None  # type: Signal

    def __init__(self, signal=None):
        if not signal:
            signal = new_signal_id()
        self.signal = signal

    def connect(self, function):
        listener = Listener(self.signal, function)
        with self.lock:
            # if hasattr(listener, "__self__") and hasattr(listener,
            # "__func__"):
            #     listener = (listener.__self__, listener.__func__)

            # Signal.signal_listeners.setdefault(
            #     self.signal, []).append(ref(listener))
            Signal.signal_listeners.setdefault(self.signal, []).append(
                listener
            )

            # Signal.listeners.setdefault(listener, []).append(self.signal)

    def disconnect(self, function):
        listener = Listener(self.signal, function)
        with self.lock:
            listeners = Signal.signal_listeners[self.signal]
            # print("removing listener", listener)
            for i, v in enumerate(listeners):
                if (
                    v.function == listener.function
                    and v.instance == listener.instance
                ):
                    del listeners[i]
                    break

            if len(Signal.signal_listeners[self.signal]) == 0:
                del Signal.signal_listeners[self.signal]

            # Signal.listeners[listener].remove(self.signal)
            # if len(Signal.listeners[listener]) == 0:
            #     del Signal.listeners[listener]

    # @classmethod
    # def disconnect_all(cls, listener):
    #     with Signal.lock:
    #         for signal in Signal.listeners[listener]:
    #             Signal.signal_listeners[signal].remove(listener)
    #         del Signal.listeners[listener]

    def __call__(self, *args):
        self.notify(*args)

    def notify(self, *args):
        if threading.current_thread().ident == main_thread_id:
            Signal.process_signal(self.signal, *args)

        else:
            with Signal.lock:
                Signal.notifications.append((self.signal, args))
            # FIXME: this is just a hack, fsui.call_after should be
            # replaced with an Application-specified callback function
            try:
                fsui = __import__("fsui")
                fsui.call_after(Signal.process_all_signals)
            except AttributeError:
                pass

    @classmethod
    def process_all_signals(cls):
        with Signal.lock:
            if len(Signal.notifications) == 0:
                return
            notifications = Signal.notifications[:]
            Signal.notifications = []
        # print(notifications)
        for signal, args in notifications:
            remove_listeners = cls.process_signal(signal, *args)
            if len(remove_listeners) > 0:
                with Signal.lock:
                    for listener in remove_listeners:
                        print("FIXME: remove dead listener", listener)
                        Signal.signal_listeners[signal].remove(listener)
                    if len(Signal.signal_listeners[signal]) == 0:
                        del Signal.signal_listeners[signal]

    @classmethod
    def process_signal(cls, signal, *args):
        # print(self.listeners.setdefault(signal, []))
        remove_listeners = []
        for listener_ref in Signal.signal_listeners.setdefault(signal, []):
            # print(listener, signal, args)
            # listener = listener_ref()
            # if not listener:
            #     # FIXME: remove reference
            #     continue
            listener = listener_ref
            # print(signal, listener, listener.instance, listener.function)

            try:
                # instance = listener.instance() if listener.instance else None
                # function = listener.function()
                # print(signal, instance, function)
                # if function is None:
                #     # FIXME: remove listener / dead listener
                #     continue
                #
                # if instance is not None:
                #     if signal == "config":
                #         # FIXME: temporary hack for legacy code
                #         instance.on_config(*args)
                #         continue
                #     elif signal == "setting":
                #         # FIXME: temporary hack for legacy code
                #         instance.on_setting(*args)
                #         continue
                #     try:
                #         # FIXME: temporary hack for legacy code
                #         func = getattr(instance, "on_" + signal + "_signal")
                #     except AttributeError:
                #         pass
                #     else:
                #         func(*args)
                #         continue

                result = listener(*args)
                if not result:
                    remove_listeners.append(listener)
            except Exception:
                traceback.print_exc()
        return remove_listeners


Signal.quit = Signal("quit")
