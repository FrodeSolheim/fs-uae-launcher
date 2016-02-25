import fsui.qt


class IntervalTimer(fsui.qt.QObject):

    activated = fsui.qt.QSignal()

    def __init__(self, interval):
        super().__init__()
        self.startTimer(interval)

    def __del__(self):
        print("IntervalTimer.__del__", self)

    # noinspection PyPep8Naming
    def timerEvent(self, _):
        self.activated.emit()

    def stop(self):
        print("[TIMER] Stop")
        self.activated.disconnect()
