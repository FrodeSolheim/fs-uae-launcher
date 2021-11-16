import threading
import traceback

from .signal import Signal

local_tasks = threading.local()


class TaskFailure(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


class TaskStopped(Exception):
    def __init__(self):
        Exception.__init__(self)


class Task(object):
    Failure = TaskFailure
    Stopped = TaskStopped

    def __init__(self, name: str) -> None:
        self.__name = name
        self.stop_flag = False
        self.started = Signal()
        self.succeeded = Signal()
        self.progressed = Signal()
        self.failed = Signal()
        self.stopped = Signal()
        self.finished = Signal()

    def get_task_name(self) -> str:
        return self.__name

    def stop(self) -> None:
        self.stop_flag = True

    def stop_check(self) -> None:
        if self.stop_flag:
            print("raising TaskStopped for", self)
            raise TaskStopped()

    def start(self) -> None:
        threading.Thread(
            target=self.__run,
            name="TaskThread({0})".format(self.get_task_name()),
        ).start()

    def __run(self) -> None:
        local_tasks.task = self
        try:
            print(self, "starting")
            self.started()
            try:
                self.run()
            except TaskStopped:
                self.stopped()
            except TaskFailure as e:
                print(self, "failed", e.message)
                self.failed(e.message)
            except Exception as e:
                print(self, "failed", repr(str(e)))
                traceback.print_exc()
                self.failed(
                    "Task: {}\nError: {}\nMessage: {}\n\n"
                    "The log file may contain more details.".format(
                        self.get_task_name(), type(e).__name__, str(e)
                    )
                )
            else:
                print(self, "succeeded")
                self.succeeded()
            self.finished.notify()
        finally:
            del local_tasks.task

    def set_progress(self, text: str) -> None:
        print(" --", text, "--")
        self.progressed.notify(text)

    def run(self) -> None:
        raise NotImplementedError("Task.run is not implemented")

    def __repr__(self):
        return '<Task "{0}">'.format(self.get_task_name())


class CurrentTaskProxy(object):
    @property
    def task(self):
        try:
            t = local_tasks.task
        except AttributeError:
            t = null_task
        return t

    @property
    def stop_flag(self):
        return self.task.stop_flag

    def set_progress(self, text):
        self.task.set_progress(text)

    def set_download_indicator(self, progress):
        pass

    def set_upload_indicator(self, progress):
        pass


null_task = Task("Null Task")
current_task = CurrentTaskProxy()
