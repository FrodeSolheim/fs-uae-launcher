import fsboot
from fscore.memoize import memoize


class Application:
    @staticmethod
    @memoize
    def executableDir() -> str:
        return fsboot.executable_dir()

    @staticmethod
    def shareDirName() -> str:
        raise NotImplementedError()
