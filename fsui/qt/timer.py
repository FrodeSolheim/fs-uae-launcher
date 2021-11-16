import logging

from fsui.qt.core import QObject, QTimerEvent
from fsui.qt.signal import Signal

log = logging.getLogger(__name__)


class IntervalTimer(QObject):
    activated = Signal()

    def __init__(self, interval: int) -> None:
        super().__init__()
        self.startTimer(interval)

    def __del__(self) -> None:
        log.debug("IntervalTimer.__del__ %r", self)

    def timerEvent(self, a0: QTimerEvent) -> None:
        self.activated.emit()

    def stop(self) -> None:
        log.debug("[TIMER] Stop")
        self.activated.disconnect()
