from fsbc.signal import Signal
from .ContextAware import ContextAware


class SignalContext(ContextAware):

    def __init__(self, context):
        ContextAware.__init__(self, context)

    def connect(self, signal, listener):
        signal = "fsgs:" + signal
        Signal(signal).connect(listener)

    def disconnect(self, signal, listener):
        signal = "fsgs:" + signal
        Signal(signal).disconnect(listener)

    def notify(self, signal, args):
        signal = "fsgs:" + signal
        Signal(signal).notify(*args)

    def process(self):
        Signal.process_all_signals()
