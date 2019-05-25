import logging
import os
import weakref


class Application:
    def __init__(self, name, singleton=None, file=None):
        self._file = file
        self.name = name
        self.singleton = singleton
        self._windows = []

    def add_window(self, window):
        print("[Application] Adding window", window)
        self._windows.append(weakref.ref(window))

    def add_menu(self, menu):
        print("[Application] Adding menu", menu)

    def run(self):
        from workspace.util.application_runner import ApplicationRunner

        runner = ApplicationRunner(self.name)
        runner.run(self)

    def logger(self):
        logger = logging.getLogger(self.name)
        return logger

    def directory(self, name=""):
        self.logger().debug(self._file)
        dir_path = os.path.dirname(self._file)
        if name:
            dir_path = os.path.join(dir_path, name)
        return dir_path

    def file(self, name=""):
        parts = name.rsplit("/", 1)
        if len(parts) == 1:
            parts.insert(0, "")
        dir_name, file_name = parts
        dir_path = self.directory(dir_name)
        return os.path.join(dir_path, file_name)
