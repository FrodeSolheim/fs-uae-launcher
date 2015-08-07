import os
import sys
import time
import threading
from fsbc.Paths import Paths
from fsbc.system import windows, macosx
from fsbc.util import memoize
import fsbc.Settings


class Application(object):

    app_name = ""
    app_version = ""
    _instance = None

    @classmethod
    def instance(cls):
        """
        :rtype : Application
        """
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        :deprecated
        """
        return cls._instance

    @classmethod
    def get(cls):
        """
        :deprecated
        """
        return cls._instance

    @classmethod
    def set_instance(cls, instance):
        """
        :type instance: Application
        """
        if cls._instance:
            raise RuntimeError("An application instance already exists")
            # print("WARNING: An application instance already exists")

        # noinspection PyAttributeOutsideInit
        cls._instance = instance
        fsbc.Settings.set_path(instance.get_settings_path())

    def __init__(self, name="", version=""):
        # if Application.instance is not None:
        #     raise Exception("An application instance already exists")
        # Application.instance = self
        self.stop_flag = False
        self.name = name or Application.app_name
        self.version = version or Application.app_version
        self.__settings = None
        self._data_dirs = None
        Application.set_instance(self)

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.stop()
        if self == Application._instance:
            Application._instance = None

    def set_stop_flag(self):
        self.stop_flag = True

    def stop(self):
        self.set_stop_flag()

    def wait(self):
        self.wait_for_threads()

    def wait_for_threads(self):

        def get_threads():
            result = []
            for thread in threading.enumerate():
                if thread.daemon:
                    continue
                if not thread.is_alive():
                    continue
                result.append(repr(thread))
            return result

        t_list = get_threads()
        print(t_list)
        while len(t_list) > 1:
            t_list_2 = get_threads()
            if t_list_2 != t_list:
                t_list = t_list_2
                print(t_list)
            time.sleep(0.1)

    def stopping(self):
        return self.stop_flag

    def run_in_main(self, function, *args, **kwargs):
        raise NotImplementedError("Application.run_in_main")

    # def timer(self, timeout, function, *args, **kwargs):
    #     raise NotImplementedError("Application.call_later")

    @staticmethod
    @memoize
    def executable_dir():
        print("executable_dir")
        print("sys.executable =", sys.executable)
        if "python" in os.path.basename(sys.executable):
            print("using sys.argv[0] instead of python interpreter path")
            # We do not want the directory of the (installed) python
            # interpreter, but rather the main application script
            dir_path = os.path.dirname(sys.argv[0])
            print(dir_path)
            dir_path = os.path.join(os.getcwd(), dir_path)
            print(dir_path)
            dir_path = os.path.normpath(dir_path)
        else:
            dir_path = os.path.dirname(sys.executable)
        print("executable_dir =", dir_path)
        return dir_path

    def cache_dir(self):
        return os.path.join(Paths.get_base_dir(), "Cache")

    @memoize
    def data_dirs(self):
        if self._data_dirs is not None:
            return self._data_dirs
        data_dirs = []
        base_dirs = []

        if len(sys.argv) > 0:
            script_dir = os.path.dirname(sys.argv[0])
            base_dirs.append(os.path.join(script_dir, "share"))

        data_dirs.append(self.executable_dir())
        if windows:
            base_dirs.append(os.path.join(self.executable_dir(), "share"))
        elif macosx:
            base_dirs.append(os.path.join(self.executable_dir(), "..",
                                          "Resources", "share"))
        else:
            # FIXME: $XDG_DATA_DIRS, $XDG_DATA_HOME
            base_dirs.append(
                os.path.normpath(os.path.join(
                    self.executable_dir(), "..", "share")))
        for dir_name in base_dirs:
            data_dir = os.path.join(dir_name, self.name)
            print("* checking for data dir", data_dir)
            if os.path.exists(data_dir):
                data_dirs.append(data_dir)
        self._data_dirs = data_dirs
        print("data dirs:", data_dirs)
        return data_dirs

    @memoize
    def data_file(self, name):
        """Looks up an application data file in several places depending on
        platform.

        :rtype : str
        """
        for data_dir in self.data_dirs():
            path = os.path.join(data_dir, name)
            print("- checking", path)
            if os.path.exists(path):
                return path
        raise LookupError(name)

    def get_settings_path(self):
        print("WARNING: Application.get_settings_path not implemented")

    @property
    def settings(self):
        if self.__settings is None:
            fsbc.Settings.load()
            from fsbc.Settings import Settings
            # return Settings.instance()
            # self.__settings = Settings(self)
            # noinspection PyProtectedMember
            self.__settings = fsbc.Settings._settings
        return self.__settings


def call_after(func, *args, **kwargs):
    return Application.instance().run_in_main(func, *args, **kwargs)


class ApplicationInstanceProxy(object):

    def __getattr__(self, name):
        return getattr(Application.instance(), name)

    def __setattr__(self, name, value):
        raise Exception("not currently allowed to set attributes on app")
        # return setattr(Application.instance(), name, value)

app = ApplicationInstanceProxy()
