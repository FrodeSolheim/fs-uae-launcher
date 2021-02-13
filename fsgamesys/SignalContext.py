import weakref

from fsbc.signal import Signal

from .contextaware import ContextAware


class SignalBehavior:
    def __init__(self, context, parent, names):
        parent.__signal_enable_behavior = self
        self._context = context
        self._parent = weakref.ref(parent)
        self._names = set(names)
        try:
            parent.destroyed.connect(self.on_parent_destroyed)
        except AttributeError:
            print(
                "WARNING:SignalBehavior without remove_listener "
                "implementation"
            )
        for signal in self._names:
            self._context.connect(
                signal, getattr(self._parent(), "on_{}_signal".format(signal))
            )
            # self._context.connect(signal, self._parent())

    def on_parent_destroyed(self):
        for signal in self._names:
            self._context.disconnect(
                signal, getattr(self._parent(), "on_{}_signal".format(signal))
            )
            # self._context.disconnect(signal, self._parent())


# noinspection PyMethodMayBeStatic
class SignalContext(ContextAware):
    def __init__(self, context):
        ContextAware.__init__(self, context)

    def signal_name(self, signal):
        # FIXME: use fsgs-context-instance-specific signals
        # return "fsgs:{}{}".format(id(signal), signal)
        return "fsgs:{}".format(signal)

    def connect(self, signal, listener):
        Signal(self.signal_name(signal)).connect(listener)

    def disconnect(self, signal, listener):
        Signal(self.signal_name(signal)).disconnect(listener)

    def emit(self, signal, args):
        Signal(self.signal_name(signal)).notify(*args)

    # FIXME: Deprecated
    def notify(self, signal, args):
        return self.emit(signal, args)

    def process(self):
        Signal.process_all_signals()

    def add_behavior(self, parent, names):
        SignalBehavior(self, parent, names)
