import fsboot
from fscore.memoize import memoize


class Application:
    @staticmethod
    @memoize
    def executable_dir():
        return fsboot.executable_dir()

    @staticmethod
    def share_dir_name():
        raise NotImplementedError()
