import os

from fscore.system import System


class GameCenter(object):
    @classmethod
    def register_user_activity(cls):
        if System.windows:
            pass
        elif System.macos:
            pass
        else:
            path = "/tmp/fs-game-center-activity"
            if not os.path.exists(path):
                try:
                    with open(path, "wb") as _:
                        pass
                except Exception:
                    pass
                try:
                    os.chmod(path, 0o666)
                except Exception:
                    pass
            os.utime("/tmp/fs-game-center-activity", None)
