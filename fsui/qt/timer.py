from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsui.qt import QObject, QSignal


class IntervalTimer(QObject):

    activated = QSignal()

    def __init__(self, interval):
        super().__init__()
        self.startTimer(interval)

    def __del__(self):
        print("IntervalTimer.__del__", self)

    # noinspection PyPep8Naming
    def timerEvent(self, _):
        self.activated.emit()
