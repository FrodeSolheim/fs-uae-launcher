from launcher.system.special.login import WidgetSizeSpinner
from launcher.experimental.flexbox.flexcontainer import (
    FlexContainer,
    VerticalFlexContainer,
)
from launcher.experimental.flexbox.label import Label
from launcher.experimental.flexbox.imageview import ImageView
import fsui
from fsbc.application import app
from fsgamesys.ogd.client import OGDClient

# from workspace.shell import SimpleApplication
from launcher.res import gettext
from launcher.ui.widgets import CloseButton
from workspace.ui.theme import WorkspaceTheme
from launcher.experimental.flexbox.window import Window
from launcher.system.classes.windowcache import WindowCache
from launcher.experimental.flexbox.spacer import Spacer
from launcher.experimental.flexbox.button import Button


def wsopen(window=None, **kwargs):
    WindowCache.open(LogoutWindow, center_on_window=window)


class LogoutWindow(Window):
    def __init__(self, parent=None):
        super().__init__(
            title=gettext("OpenRetro logout"),
            minimizable=False,
            maximizable=False,
        )
        # self.theme = WorkspaceTheme.instance()
        # self.layout = fsui.VerticalLayout()
        self.set_icon(fsui.Icon("password", "pkg:workspace"))

        with FlexContainer(
            parent=self,
            style={
                "backgroundColor": "#bbbbbb",
                "gap": 20,
                "padding": 20,
                "paddingBottom": 10,
            },
        ):
            with VerticalFlexContainer(style={"flexGrow": 1, "gap": 5}):
                Label(
                    gettext("Log out from your OpenRetro.org account"),
                    style={"fontWeight": "bold"},
                )
                Label(
                    gettext(
                        "While logged out you will not get database updates"
                    )
                )
            ImageView(fsui.Image("workspace:/data/48/password.png"))
        with FlexContainer(
            parent=self,
            style={
                "backgroundColor": "#bbbbbb",
                "gap": 10,
                "padding": 20,
                "paddingTop": 10,
            },
        ):
            # Spacer(style={"flexGrow": 1})
            self.errorLabel = Label(style={"flexGrow": 1})
            # FIXME: Set visible via stylesheet instead?
            self.spinner = WidgetSizeSpinner(visible=False)
            self.logoutButton = Button(
                gettext("Log out"), onClick=self.onLogoutActivated
            )

        # self.logoutButton.activated.connect(self.onLogoutActivated)

    def __del__(self):
        print("LogoutWindow.__del__")

    def setRunning(self, running):
        self.spinner.set_visible(running)
        self.logoutButton.set_enabled(not running)

    def onLogoutActivated(self):
        self.setRunning(True)
        authToken = app.settings["database_auth"]

        def onResult():
            self.setRunning(False)
            self.errorLabel.setText("")
            self.getWindow().close()

        def onError(error):
            self.setRunning(False)
            self.errorLabel.setText(f"Error: {str(error)}")

        def onProgress(progress, *, task):
            self.errorLabel.setText(progress)
            # task.cancel()

        self.addEventListener(
            "destroy",
            AsyncTaskRunner(onResult, onError, onProgress)
            .run(LogoutTask(authToken))
            .cancel,
        )

    # FIXME: Move to widget
    def addEventListener(self, eventName, listener):
        if eventName == "destroy":
            self.destroyed.connect(listener)

        # def onLogoutActivated(self):
        #     self.setRunning(True)
        #     authToken = app.settings["database_auth"]

        #     def onResult(result):
        #         print(result)
        #         self.setRunning(False)

        #     def onError(error):
        #         print(error)

        #     def onProgress(progress):
        #         print(progress)
        #         self.errorLabel.set_text(progress.value)

        #     self.addEventListener(
        #         "destroy",
        #         AsyncTaskRunner(onResult, onError, onProgress)
        #         .run(LogoutTask(authToken))
        #         .cancel,
        #     )

        # with AsyncTaskRunner(onResult, onError, onProgress):
        #     LogoutTask(authToken)

        # import time
        # time.sleep(3)
        # self.close()

        # LogoutTask(authToken).start()
        # LogoutTask(authToken).runAsync()

        # AsyncTaskRunner(onResult, onError, onProgress).run(
        #     LogoutTask(authToken)
        # ).cancelOn(self.destroy)

        # self.runTask(LogoutTask(authToken), onProgress, onError, onComplete)

        # self.disposable = (
        #     logoutTask(auth_token)
        #     .pipe(
        #         # rx.operators.subscribe_on(rx.scheduler.EventLoopScheduler()),
        #         rx.operators.subscribe_on(rx.scheduler.NewThreadScheduler()),
        #         rx.operators.observe_on(MainLoopScheduler()),
        #     )
        #     .subscribe(self.onNext, self.onError, self.onCompleted)
        # )
        # #  ).subscribe(self, scheduler=qtScheduler)

        return
        if auth_token:
            task = OGDClient().logout_task(auth_token)
            # task.progressed.connect(self.progress)
            task.succeeded.connect(self.close)
            # task.failed.connect(fsui.error_function(gettext("Login Failed")))
            task.failed.connect(self.on_failure)
            task.start()
        else:
            # this is not a normal case, no auth token stored, but clear
            # all auth-related settings just in case
            app.settings["database_auth"] = ""
            app.settings["database_username"] = ""
            # app.settings["database_email"] = ""
            app.settings["database_password"] = ""
            self.on_close()

    def onNext(self, value):
        import threading

        print("on_next", value, threading.currentThread())
        self.errorLabel.set_text(value)

        def disp():
            self.disposable.dispose()

        fsui.call_after(disp)

    def onError(self, error):
        print("on_error", repr(error))

        self.spinner.set_visible(False)
        self.logoutButton.set_enabled(True)
        self.errorLabel.set_text(f"Error: {str(error)}")

        # fsui.show_error(str(message), parent=self.getWindow())

    def onCompleted(self):
        import threading

        print("on_completed", threading.currentThread())

        self.spinner.set_visible(False)
        self.logoutButton.set_enabled(True)

    def on_failure(self, error):
        self.spinner.set_visible(False)
        self.logoutButton.set_enabled(True)
        self.errorLabel.set_text(str(error))

        fsui.show_error(error, parent=self.window)


class Task:
    def __init__(self):
        self._cancelled = False
        self._completed = False

        def onResult(result):
            pass

        def onError(error):
            pass

        def onProgress(progress):
            pass

        self.onResult = onResult
        self.onError = onError
        self.onProgress = onProgress

    def setOnResult(self, onResult):
        self.onResult = onResult

    def setOnError(self, onError):
        self.onError = onError

    def setOnProgress(self, onProgress):
        self.onProgress = onProgress

    def cancel(self):
        self._cancelled = True

    def complete(self):
        if self._completed:
            return
        self._completed = True

    def isCancelled(self) -> bool:
        if self._cancelled:
            print("Task.isCancelled was True")
        return self._cancelled

    def main(self):
        pass

    def setProgress(self, progress):
        if self.isCancelled():
            return
        self.onProgress(progress)
        # if isinstance(self, TaskProgress):
        #     self.onProgress(progress)
        # else:
        #     self.onProgress(TaskProgress(self, progress))

    def setError(self, error):
        if self.isCancelled():
            return
        self.onError(error)

    def setResult(self, result):
        if self.isCancelled():
            return
        self.onResult(result)

    # def run(self):
    #     self.main()

    def run(self):
        try:
            result = self.main()
        except Exception as e:
            self.setError(e)
        # self.complete()
        else:
            self.setResult(result)


TYPE_RESULT = 0
TYPE_ERROR = 1
TYPE_PROGRESS = 2


class TaskResult:
    def __init__(self, task, result):
        self.type = TYPE_RESULT
        self.task = task
        self.value = result


class TaskError:
    def __init__(self, task, progress):
        self.type = TYPE_ERROR
        self.task = task
        self.value = progress


class TaskProgress:
    def __init__(self, task, progress):
        self.type = TYPE_PROGRESS
        self.task = task
        self.value = progress


from fscore.mainloop import MainLoop

from inspect import signature


class AsyncTaskRunner:
    def __init__(self, onResult, onError=None, onProgress=None):
        self.onResult = onResult
        self.onError = onError
        self.onProgress = onProgress
        self._tasks = []  # type: List[Task]
        self._cancelled = False
        self._lock = threading.Lock()
        self.currentTask = None  # type: Optional[Task]

    def cancel(self):
        # """Returns False if the task runner was already cancelled."""
        print("AsyncTaskRunninger.cancel")
        if self._cancelled:
            return False
        with self._lock:
            print("AsyncTaskRunninger.isCancelled -> True")
            self._cancelled = True
            for task in self._tasks:
                task.cancel()
        return True

    def isCancelled(self):
        print("AsyncTaskRunninger.isCancelled", self._cancelled)
        return self._cancelled

    def run(self, task: Task):
        print("AsyncTaskRunner.run")
        with self._lock:
            if self.isCancelled():
                print("Tried to run task but runner was cancelled")
                task.cancel()
                return
            self._tasks.append(task)
        # if task is not None:
        #     self.tasks.append(task)
        # for task in self.tasks:

        def threadFunction():
            print("AsyncTaskRunner.threadFunction")
            try:
                self.currentTask = task
                task.setOnResult(self.onTaskResult)
                task.setOnError(self.onTaskError)
                task.setOnProgress(self.onTaskProgress)
                print("Running task", task)
                task.run()
            except Exception as e:
                self.onTaskRunnerError(e)
            self.onTaskRunnerComplete()
            with self._lock:
                self._tasks.remove(task)

        threadName = repr(self)
        threading.Thread(target=threadFunction, name=threadName).start()
        # For chaining method calls
        return self

    def executeCallback(self, callback, value):
        if self.isCancelled():
            print("executeCallback - isCancelled")
            return
        print("callback", callback, value)
        sig = signature(callback)
        print(sig.parameters)
        if len(sig.parameters) == 0:
            callback()
        elif len(sig.parameters) == 1:
            callback(value)
        else:
            callback(value, task=self.currentTask)

    def onTaskResult(self, result):
        print("AsyncTaskRunner.onTaskResult", result)

        def runInMain():
            if self.onResult is not None:
                self.executeCallback(self.onResult, result)

        MainLoop.schedule(runInMain)

    def onTaskError(self, error):
        print("AsyncTaskRunner.onTaskError", error)

        def runInMain():
            if self.onError is not None:
                self.executeCallback(self.onError, error)

        MainLoop.schedule(runInMain)

    def onTaskProgress(self, progress):
        print("AsyncTaskRunner.onTaskProgress", progress)

        def runInMain():
            if self.onProgress is not None:
                self.executeCallback(self.onProgress, progress)

        MainLoop.schedule(runInMain)

    # ----------------

    def onTaskRunnerError(self, error):
        print("AsyncTaskRunner.onTaskRunnerError", error)

        def runInMain():
            if self.isCancelled():
                return
            self.onError(error)

        MainLoop.schedule(runInMain)

    def onTaskRunnerComplete(self):
        # print("AsyncTaskRunner.onTaskRunnerResult", result)
        pass


# class AsyncTask(Task):
#     def __init__(self):
#         pass

#     def start(self):
#         def threadFunction():
#             try:
#                 self.main()
#             except Exception as e:
#                 self.error(e)
#             self.complete()

#         threadName = repr(self)
#         threading.Thread(target=threadFunction, name=threadName)

from fscore.settings import Settings

class LogoutTask(Task):
    def __init__(self, authToken):
        super().__init__()
        self.authToken = authToken

    def main(self):
        self.setProgress("Logging out from openretro.org...")
        OGDClient().deauth(self.authToken)

        Settings.set("error_report_user_id", "")
        Settings.set("database_username", "")
        Settings.set("database_auth", "")

        # Clear legacy key
        Settings.set("database_password", "")
        return

        print("LogoutTask.main")
        self.setProgress("Starting logout process...")
        time.sleep(1)
        if self.isCancelled():
            return
        self.setProgress("Logging out...")
        time.sleep(1)
        if self.isCancelled():
            return
        raise Exception("Fail")
        self.setProgress("Completing...")
        time.sleep(1)
        if self.isCancelled():
            return
        self.setProgress("Done...")


import rx
import rx.operators
import rx.scheduler
from fscore.observable import Disposable, MainLoopScheduler, Observable
from rx.scheduler.mainloop import QtScheduler
from rx.disposable import CompositeDisposable
from fsui.qt import QtCore

qtScheduler = QtScheduler(QtCore)

from rx.core.typing import Observer as ObserverType
from rx.core.typing import Scheduler as SchedulerType
from rx.core.typing import Disposable as DisposableType
from rx.scheduler import CurrentThreadScheduler
from typing import Any, List, Optional

import threading


class Task2(Observable):
    def __init__(self):
        self.disposed = False

        def subscribe(observer, scheduler):
            scheduler = scheduler or CurrentThreadScheduler.singleton()

            def action(scheduler, state):
                self.task()

            def dispose() -> None:
                import traceback

                traceback.print_stack()
                print("--------> dispose called <----------------")
                # nonlocal disposed
                # disposed = True

            # scheduler.schedule(action)
            return CompositeDisposable(
                scheduler.schedule(action), Disposable(dispose)
            )

        super().__init__(subscribe)

    def subscribe(self, *args, **kwargs):
        print("Task.subscribe")
        super().subscribe(*args, **kwargs)

    def run(self):
        pass

    def runInNewThread(self, task, onNext=None, onError=None, onComplete=None):
        self._disposable = self.pipe(
            rx.operators.subscribe_on(rx.scheduler.EventLoopScheduler()),
            rx.operators.observe_on(MainLoopScheduler()),
        ).subscribe(on_next=onNext, on_error=onError, on_completed=onComplete)

    def task(self):
        pass


# Observable(Task2()):
#     pass


class NewLogoutTask(Task2):
    def task(self):
        pass


# task = LogoutTask()


class ThreadTaskRunner:
    def __init__(self):
        self._disposable = None

    def runTask(self, task, onNext=None, onError=None, onComplete=None):
        self._disposable = task.pipe(
            rx.operators.subscribe_on(rx.scheduler.EventLoopScheduler()),
            rx.operators.observe_on(MainLoopScheduler()),
        ).subscribe(on_next=onNext, on_error=onError, on_completed=onComplete)


ThreadTaskRunner().runTask(NewLogoutTask(), onNext="")


def logoutTask(authToken) -> Observable:
    def subscribe(
        observer: ObserverType, scheduler: Optional[SchedulerType] = None
    ) -> DisposableType:
        # _scheduler = scheduler or scheduler_ or CurrentThreadScheduler.singleton()
        scheduler = scheduler or CurrentThreadScheduler.singleton()
        # iterator = iter(iterable)
        disposed = False

        def action(_: SchedulerType, __: Any = None) -> None:
            nonlocal disposed

            print("logoutTask/subscribe", threading.currentThread())
            print("a")
            observer.on_next("Started")
            print("b")
            observer.on_next("Started 2")
            print("c")
            print("calling on_next")
            time.sleep(0.2)
            if disposed:
                pass

            print("d")
            observer.on_next("Logging out...")
            time.sleep(1)
            print("e")
            observer.on_next("Almost done")
            time.sleep(1)

            # raise Exception("Gnit happened")

            observer.on_completed()

        def dispose() -> None:
            import traceback

            traceback.print_stack()
            print("--------> dispose called <----------------")
            nonlocal disposed
            disposed = True

        disp = Disposable(dispose)
        return CompositeDisposable(scheduler.schedule(action), disp)
        # scheduler.schedule(action)
        # return disp

    return Observable(subscribe)


# def logoutTask2(authToken):
#     def subscribe(observer, scheduler):
#         print("subscribe", observer, scheduler)
#         disposed = False

#         def dispose():
#             nonlocal disposed
#             disposed = True

#         def task():

#             print("logoutTask/subscribe", threading.currentThread())
#             print("a")
#             observer.on_next("Started")
#             print("b")
#             observer.on_next("Started 2")
#             print("c")
#             print("calling on_next")
#             time.sleep(0.2)
#             if disposed:
#                 pass

#             observer.on_next("Logging out...")
#             time.sleep(1)
#             observer.on_next("Almost done")
#             time.sleep(1)

#             # raise Exception("Gnit happened")

#             observer.on_completed()

#         scheduler.schedule(task)
#         return Disposable(dispose)

#     return rx.create(subscribe)


class ThreadedTaskRunner:
    pass


class TaskObservable:
    pass


import time


def task(observer):
    print("task step 1")
    time.sleep(1)


class Logout2Task:
    def __init__(self):
        pass

    def run(self):
        self.observable = TaskObservable()

    # def on_progress(self):
    #    print("on_progress")

    # def on_success(self):
    #     app.settings["database_auth"] = ""
    #     app.settings["database_username"] = ""
    #     app.settings["database_email"] = ""
    #     app.settings["database_password"] = ""
    #     self.close()


# application = SimpleApplication(LogoutWindow)
