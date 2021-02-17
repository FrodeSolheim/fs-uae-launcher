from fscore.memoize import memoize
import fsboot

class Application:

    @staticmethod
    @memoize
    def executable_dir():
        return fsboot.executable_dir()
