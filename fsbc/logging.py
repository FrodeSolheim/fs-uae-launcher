import os
import sys
import logging
import threading

import time

import fsboot

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
        self.new_line = False

    def flush(self):
        return self.file.flush()

    def isatty(self):
        return False

    def write(self, msg):
        if isinstance(msg, str):
            self.write(msg.encode("UTF-8"))
            return
        # FIXME: legacy hack, should be removed in the future
        if b"database_password" in msg:
            return

        if self.new_line:
            elapsed = time.perf_counter() - fsboot.perf_counter_epoch
            self.file.write("{:0.3f} ".format(elapsed).encode("ASCII"))

        self.file.write(msg)
        self.new_line = msg.endswith(b"\n")


class NullOutput(object):
    def flush(self):
        pass

    def isatty(self):
        return False

    def write(self, msg):
        pass


def setup_logging(log_name):
    # if sys.platform == "win32" and "FS_FORCE_STDOUT" not in os.environ:
    #     # noinspection PyUnresolvedReferences
    #     # import win32console
    #     if hasattr(sys, "frozen"):
    #         # or win32console.GetConsoleWindow() == 0:
    #         sys.stdout = NullOutput()
    #         sys.stderr = NullOutput()

    # FIXME: remove dependency on fsgs here!
    from fsgs.FSGSDirectories import FSGSDirectories

    logs_dir = FSGSDirectories.get_logs_dir()
    log_file = os.path.join(logs_dir, log_name)
    print("[LOGGING] Logging to", log_file)
    try:
        f = open(log_file, "wb")
    except Exception:
        print("[LOGGING] Could not open log file")
        # use MultiplexedOutput here too, for the mutex handling
        sys.stdout = MultiplexedOutput(sys.stdout)
        sys.stderr = MultiplexedOutput(sys.stderr)
    else:
        sys.stdout = MultiplexedOutput(FileOutput(f), sys.stdout)
        sys.stderr = MultiplexedOutput(FileOutput(f), sys.stderr)

    logging.basicConfig(stream=sys.stdout, level=logging.NOTSET)
