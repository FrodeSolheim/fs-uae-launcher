from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import six
import logging
import threading

# using this lock to serialize logging from different threads
lock = threading.Lock()


class MultiplexedOutput:

    def __init__(self, *files):
        self.files = files

    def flush(self):
        with lock:
            for f in self.files:
                try:
                    f.flush()
                except Exception:
                    pass

    def isatty(self):
        return False

    def write(self, msg):
        with lock:
            for f in self.files:
                try:
                    f.write(msg)
                except Exception:
                    pass


class FileOutput(object):

    def __init__(self, file_obj):
        self.file = file_obj

    def flush(self):
        return self.file.flush()

    def isatty(self):
        return False

    def write(self, msg):
        if isinstance(msg, six.text_type):
            # FIXME: legacy hack, should be removed in the future
            if "database_password" in msg:
                return
            self.file.write(msg.encode("UTF-8"))
        else:
            # FIXME: legacy hack, should be removed in the future
            if b"database_password" in msg:
                return
            self.file.write(msg)


class NullOutput(object):

    def flush(self):
        pass

    def isatty(self):
        return False

    def write(self, msg):
        pass


def setup_logging(log_name):

    if sys.platform == "win32" and not "FS_FORCE_STDOUT" in os.environ:
        # noinspection PyUnresolvedReferences
        import win32console
        if hasattr(sys, "frozen") or win32console.GetConsoleWindow() == 0:
            sys.stdout = NullOutput()
            sys.stderr = NullOutput()

    # FIXME: remove dependency on fsgs here!
    from fsgs.FSGSDirectories import FSGSDirectories
    logs_dir = FSGSDirectories.get_logs_dir()
    log_file = os.path.join(logs_dir, log_name)
    try:
        f = open(log_file, "wb")
    except Exception:
        print("could not open log file")
        # use MultiplexedOutput here too, for the mutex handling
        sys.stdout = MultiplexedOutput(sys.stdout)
        sys.stderr = MultiplexedOutput(sys.stderr)
    else:
        sys.stdout = MultiplexedOutput(FileOutput(f), sys.stdout)
        sys.stderr = MultiplexedOutput(FileOutput(f), sys.stderr)

    logging.basicConfig(stream=sys.stdout, level=logging.NOTSET)
