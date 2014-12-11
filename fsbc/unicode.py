from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import six
import codecs
import locale
import threading
import subprocess

from fsbc.path import unicode_path, str_path

# True if we are running on Python 3
PY3 = sys.version_info[0] == 3
subprocess_popen = None


def patch_sys_argv():
    """Converts all program arguments to unicode."""
    if PY3:
        return
    for i, arg in enumerate(sys.argv):
        sys.argv[i] = unicode_path(arg)


#noinspection PyPep8Naming
def Popen(args, bufsize=0, executable=None, stdin=None, stdout=None,
          stderr=None, preexec_fn=None, close_fds=False, shell=False,
          cwd=None, env=None, universal_newlines=False, startupinfo=None,
          creationflags=0):
    """Python 2 does not generally work with unicode strings given to Popen,
    so we convert everything to strings here."""
    if isinstance(args, basestring):
        args = str_path(args)
    else:
        args = [str_path(x) for x in args]
    if executable is not None:
        executable = str_path(executable)
    if cwd is not None:
        cwd = str_path(cwd)
    if env is not None:
        new_env = {}
        for key in env:
            # str_path will use file system encoding, which seems suitable
            # here (utf-8 or mbcs).
            new_env[str_path(key)] = str_path(env[key])
        env = new_env

    return subprocess_popen(
        args, bufsize=bufsize, executable=executable, stdin=stdin,
        stdout=stdout, stderr=stderr, preexec_fn=preexec_fn,
        close_fds=close_fds, shell=shell, cwd=cwd, env=env,
        universal_newlines=universal_newlines, startupinfo=startupinfo,
        creationflags=creationflags)


def patch_subprocess_popen():
    if PY3:
        return
    global subprocess_popen
    subprocess_popen = subprocess.Popen
    #noinspection PyPep8Naming
    subprocess.Popen = Popen


class UnicodeSafeOutput(object):

    def __init__(self, file_obj, in_charset, out_charset):
        try:
            self.writer = codecs.getwriter(out_charset)
        except LookupError:
            self.writer = codecs.getwriter("ASCII")
        self.in_charset = in_charset
        self.outfile = self.writer(file_obj, errors="replace")
        self.thread_local = threading.local()

    def flush(self):
        if hasattr(self.thread_local, "write_func"):
            return
        try:
            if hasattr(self.outfile, "flush"):
                self.outfile.flush()
        except Exception:
            pass

    def isatty(self):
        if hasattr(self.thread_local, "write_func"):
            return False
        return self.outfile.isatty()

    def redirect_thread_output(self, write_func):
        if write_func is None:
            del self.thread_local.write_func
        else:
            self.thread_local.write_func = write_func

    def write(self, msg):
        # if msg == "0":
        #     import traceback
        #     traceback.print_stack()
        if hasattr(self.thread_local, "write_func"):
            if isinstance(msg, six.text_type):
                self.thread_local.write_func(msg)
                return
            msg = six.text_type(str(msg), self.in_charset, "replace")
            self.thread_local.write_func(msg)
            return
        try:
            if isinstance(msg, six.text_type):
                self.outfile.write(msg)
            else:
                msg = six.text_type(str(msg), self.in_charset, "replace")
                self.outfile.write(msg)
        except Exception:
            try:
                self.outfile.write(repr(msg))
            except Exception as e:
                self.outfile.write("EXCEPTION IN SAFEOUTPUT: %s\n" % repr(e))


def patch_stdout_and_stderr():
    if PY3:
        return

    sys._replaced_stdout = sys.stdout
    sys._replaced_stderr = sys.stderr

    try:
        if sys.platform == "win32":
            sys.stdout = UnicodeSafeOutput(sys.stdout, "mbcs", "cp437")
        else:
            sys.stdout = UnicodeSafeOutput(
                sys.stdout, "ISO-8859-1", locale.getpreferredencoding())
    except Exception:
        sys.stdout = UnicodeSafeOutput(sys.stdout, "ISO-8859-1", "ASCII")

    try:
        if sys.platform == "win32":
            sys.stderr = UnicodeSafeOutput(sys.stderr, "mbcs", "cp437")
        else:
            sys.stderr = UnicodeSafeOutput(
                sys.stderr, "ISO-8859-1", locale.getpreferredencoding())
    except Exception:
        sys.stderr = UnicodeSafeOutput(sys.stderr, "ISO-8859-1", "ASCII")


def patch_all():
    patch_stdout_and_stderr()
    patch_sys_argv()
    patch_subprocess_popen()
