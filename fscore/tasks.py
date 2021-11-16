import inspect
import logging
from threading import Lock, Thread
from typing import Any, Callable, Generic, Optional, TypeVar

from fscore.mainloop import MainLoop

log = logging.getLogger(__name__)

T = TypeVar("T")


class TaskCancelledException(Exception):
    pass


TaskError = Exception
TaskProgress = str


class Task(Generic[T]):
    def __init__(self) -> None:
        self._cancelled = False
        self._completed = False

        def onResult(_: T) -> None:
            pass

        def onError(_: Exception) -> None:
            pass

        def onProgress(_: str) -> None:
            pass

        self.onResult: Callable[[T], None] = onResult
        self.onError: Callable[[Exception], None] = onError
        self.onProgress: Callable[[str], None] = onProgress

    def main(self) -> T:
        raise NotImplementedError()

    def maybeCancel(self) -> None:
        if self.isCancelled():
            raise TaskCancelledException()

    def setOnResult(self, onResult: Callable[[T], None]) -> None:
        self.onResult = onResult

    def setOnError(self, onError: Callable[[Exception], None]) -> None:
        self.onError = onError

    def setOnProgress(self, onProgress: Callable[[str], None]) -> None:
        self.onProgress = onProgress

    def cancel(self) -> None:
        self._cancelled = True

    def complete(self) -> None:
        if self._completed:
            return
        self._completed = True

    def isCancelled(self) -> bool:
        if self._cancelled:
            print("Task.isCancelled was True")
        return self._cancelled

    def setProgress(self, progress: str) -> None:
        if self.isCancelled():
            return
        self.onProgress(progress)

    #     # if isinstance(self, TaskProgress):
    #     #     self.onProgress(progress)
    #     # else:
    #     #     self.onProgress(TaskProgress(self, progress))

    def setError(self, error: Exception) -> None:
        print("Task.setError", error)
        # if self.isCancelled():
        #     return
        self.onError(error)

    def setResult(self, result: T) -> None:
        print("Task.setResult")
        # if self.isCancelled():
        #     return
        self.onResult(result)

    # def run(self):
    #     self.main()

    def run(self) -> None:
        print("Task.run")
        try:
            result = self.main()
        except TaskCancelledException:
            # FIXME: How to notify? onError? onFinished? onCancelled?
            pass
        except Exception as e:
            log.exception("Exception while running task %r", self)
            self.setError(e)
        # self.complete()
        else:
            self.setResult(result)


class AsyncSingleTaskRunner:
    def __init__(
        self,
        task: Task[T],
        onResult: Callable[[T], None],
        onError: Optional[Callable[[TaskError], None]] = None,
        onProgress: Optional[Callable[[TaskProgress], None]] = None,
    ) -> None:
        # super().__init__(name="AsyncSingleTaskRunner")
        self._onResult = onResult
        self._onError = onError
        self._onProgress = onProgress
        self._cancelled = False
        self._lock = Lock()
        self._task = task
        self._thread = Thread(
            name=f"AsyncSingleTaskRunner<{repr(self._task)}>", target=self.run
        )

    def cancel(self) -> None:
        # """Returns False if the task runner was already cancelled."""
        print("AsyncSingleTaskRunner.cancel")
        if self._cancelled:
            return
        with self._lock:
            print("AsyncSingleTaskRunner.isCancelled -> True")
            self._cancelled = True
            self._task.cancel()

    def isCancelled(self) -> bool:
        print("AsyncSingleTaskRunner.isCancelled", self._cancelled)
        return self._cancelled

    def start(self) -> "AsyncSingleTaskRunner":
        print("AsyncSingleTaskRunner.start")
        # super().start()
        self._thread.start()
        return self

    def run(self):
        print("AsyncSingleTaskRunner.run")

        if self.isCancelled():
            print("Tried to run task but runner was cancelled")
            return

        #  with self._lock:
        #     if self.isCancelled():
        #         print("Tried to run task but runner was cancelled")
        #         task.cancel()
        #         return
        #     # self._tasks.append(task)
        # if task is not None:
        #     self.tasks.append(task)
        # for task in self.tasks:

        self._task.setOnResult(self._onTaskResult)  # type: ignore
        self._task.setOnError(self._onTaskError)  # type: ignore
        self._task.setOnProgress(self._onTaskProgress)  # type: ignore
        print("Running task", self._task)
        self._task.run()
        print("AsyncSingleTaskRunner done")

        # def threadFunction():
        #     print("AsyncTaskRunner.threadFunction")
        #     try:
        #         self.currentTask = task
        #         task.setOnResult(self.onTaskResult)
        #         task.setOnError(self.onTaskError)
        #         task.setOnProgress(self.onTaskProgress)
        #         print("Running task", task)
        #         task.run()
        #     except Exception as e:
        #         self.onTaskRunnerError(e)
        #     self.onTaskRunnerComplete()
        #     with self._lock:
        #         self._tasks.remove(task)

        # threadName = repr(self)
        # threading.Thread(target=threadFunction, name=threadName).start()

    def _executeCallback(
        self, callback: Callable[..., None], value: Any
    ) -> None:
        if self.isCancelled():
            print("executeCallback - isCancelled")
            return
        print("callback", callback, value)
        sig = inspect.signature(callback)
        print(sig.parameters)
        if len(sig.parameters) == 0:
            callback()
        elif len(sig.parameters) == 1:
            callback(value)
        else:
            callback(value, task=self._task)

    def _onTaskResult(self, result: Any) -> None:
        print("AsyncTaskRunner.onTaskResult", result)
        onResult = self._onResult
        if onResult is None:
            return

        def runInMain():
            self._executeCallback(onResult, result)

        MainLoop.schedule(runInMain)

    def _onTaskError(self, error: TaskError):
        print("AsyncTaskRunner.onTaskError", error)
        onError = self._onError
        if onError is None:
            return

        def runInMain():
            self._executeCallback(onError, error)

        MainLoop.schedule(runInMain)

    def _onTaskProgress(self, progress: TaskProgress):
        print("AsyncTaskRunner.onTaskProgress", progress)
        onProgress = self._onProgress
        if onProgress is None:
            return

        def runInMain():
            self._executeCallback(onProgress, progress)

        MainLoop.schedule(runInMain)

    # # ----------------

    # def onTaskRunnerError(self, error: TaskError):
    #     print("AsyncTaskRunner.onTaskRunnerError", error)

    #     def runInMain():
    #         if self.isCancelled():
    #             return
    #         if self.onError is not None:
    #             self.onError(error)

    #     MainLoop.schedule(runInMain)

    # def onTaskRunnerComplete(self):
    #     # print("AsyncTaskRunner.onTaskRunnerResult", result)
    #     pass
