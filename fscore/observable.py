# from rx import Observable as BaseObservable
import rx
import rx.disposable
import rx.operators

from fscore.mainloop import MainLoop

amapOperator = rx.operators.map


def mapOperator(*args):
    return rx.operators.map(*args)


# class Observable(BaseObservable):
#     pass


Observable = rx.Observable
Disposable = rx.disposable.Disposable


def isObservable(obj):
    return hasattr(obj, "subscribe")


class Disposer:
    def __init__(self, *args):
        self.disposables = args

    def __call__(self):
        print("Disposer.__call__")
        for disposable in self.disposables:
            print(disposable, "-> dispose()")
            disposable.dispose()


import logging
from datetime import timedelta
from typing import Any, Optional, Set

from rx.core import typing
from rx.disposable import (
    CompositeDisposable,
    Disposable,
    SingleAssignmentDisposable,
)
from rx.scheduler.periodicscheduler import PeriodicScheduler

log = logging.getLogger(__name__)


# FIXME: Might also put this in fsui instead?


class MainLoopScheduler(PeriodicScheduler):
    def __init__(self):
        super().__init__()
        # elf._qtcore = qtcore
        # FIXME
        # timer_class: Any = self._qtcore.QTimer
        # self._periodic_timers: Set[timer_class] = set()

    def schedule(
        self,
        action: typing.ScheduledAction,
        state: Optional[typing.TState] = None,
    ) -> typing.Disposable:
        """Schedules an action to be executed.

        Args:
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """
        print("MainLoopScheduler.schedule")

        # print("schedule_relative", duetime, action, state)
        # msecs=1
        # msecs = max(0, int(self.to_seconds(duetime) * 1000.0))
        sad = SingleAssignmentDisposable()
        is_disposed = False

        def invoke_action() -> None:
            print("invoke_action")
            if not is_disposed:
                sad.disposable = action(self, state)

        # Use static method, let Qt C++ handle QTimer lifetime
        # self._qtcore.QTimer.singleShot(msecs, invoke_action)
        MainLoop.schedule(invoke_action)

        def dispose() -> None:
            nonlocal is_disposed
            is_disposed = True

        return CompositeDisposable(sad, Disposable(dispose))

    def schedule_relative(
        self,
        duetime: typing.RelativeTime,
        action: typing.ScheduledAction,
        state: Optional[typing.TState] = None,
    ) -> typing.Disposable:
        """Schedules an action to be executed after duetime.

        Args:
            duetime: Relative time after which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """
        raise NotImplementedError
        print("schedule_relative", duetime, action, state)
        msecs = 1
        msecs = max(0, int(self.to_seconds(duetime) * 1000.0))
        sad = SingleAssignmentDisposable()
        is_disposed = False

        def invoke_action() -> None:
            print("invoke_action")
            if not is_disposed:
                sad.disposable = action(self, state)

        log.debug("relative timeout: %sms", msecs)

        # Use static method, let Qt C++ handle QTimer lifetime
        self._qtcore.QTimer.singleShot(msecs, invoke_action)

        def dispose() -> None:
            nonlocal is_disposed
            is_disposed = True

        return CompositeDisposable(sad, Disposable(dispose))

    def schedule_absolute(
        self,
        duetime: typing.AbsoluteTime,
        action: typing.ScheduledAction,
        state: Optional[typing.TState] = None,
    ) -> typing.Disposable:
        """Schedules an action to be executed at duetime.

        Args:
            duetime: Absolute time at which to execute the action.
            action: Action to be executed.
            state: [Optional] state to be given to the action function.

        Returns:
            The disposable object used to cancel the scheduled action
            (best effort).
        """
        raise NotImplementedError

        delta: timedelta = self.to_datetime(duetime) - self.now
        return self.schedule_relative(delta, action, state=state)

    def schedule_periodic(
        self,
        period: typing.RelativeTime,
        action: typing.ScheduledPeriodicAction,
        state: Optional[typing.TState] = None,
    ) -> typing.Disposable:
        """Schedules a periodic piece of work to be executed in the loop.

        Args:
             period: Period in seconds for running the work repeatedly.
             action: Action to be executed.
             state: [Optional] state to be given to the action function.

         Returns:
             The disposable object used to cancel the scheduled action
             (best effort).
        """
        raise NotImplementedError
        msecs = max(0, int(self.to_seconds(period) * 1000.0))
        sad = SingleAssignmentDisposable()

        def interval() -> None:
            nonlocal state
            state = action(state)

        log.debug("periodic timeout: %sms", msecs)

        timer = self._qtcore.QTimer()
        timer.setSingleShot(not period)
        timer.timeout.connect(interval)
        timer.setInterval(msecs)
        self._periodic_timers.add(timer)
        timer.start()

        def dispose() -> None:
            timer.stop()
            self._periodic_timers.remove(timer)
            timer.deleteLater()

        return CompositeDisposable(sad, Disposable(dispose))
