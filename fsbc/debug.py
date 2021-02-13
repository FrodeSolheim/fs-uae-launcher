import os
import sys
import threading
import traceback

from .signal import Signal

main_thread_id = threading.current_thread().ident
excepthook_installed = False


def is_running_in_debugger():
    return bool(sys.gettrace())


def enable_exception_handler(force=False):
    # # print("Not installing sys.excepthook")
    # # return

    # global excepthook_installed
    # if excepthook_installed:
    #     return
    # excepthook_installed = True

    # if not force and is_running_in_debugger():
    #     print("Running in debugger, not installing sys.excepthook")
    #     _let_thread_exceptions_be_unhandled()
    #     return False

    # print("Installing new sys.excepthook")
    # sys.excepthook = _handle_exception
    # _enable_thread_exception_handler()
    # return True
    import fspy.exception

    fspy.exception.install_excepthook()


def _let_thread_exceptions_be_unhandled():
    """Replace method in Thread class to let exceptions be picked up by
    the debugger. This is done by replacing the bootstrap function,
    which normally catches all exceptions."""

    print("let thread exceptions be unhandled (for debugger)")
    if sys.version.startswith("2.7"):
        threading.Thread._Thread__bootstrap = _thread_bootstrap_2_7
    else:
        print(
            "WARNING: no Thread bootstrap replacement for this "
            "python version. The debugger will not break on unhandled"
            "exceptions in threads other than the main thread."
        )


def _enable_thread_exception_handler():
    # print("enable tread exception handler")

    def run():
        self = threading.current_thread()
        try:
            self._run_()
        except:
            _handle_exception(*sys.exc_info())

    def set_ident(self):
        # self = threading.current_thread()
        self._run_ = self.run
        self.run = run
        self._set_ident_()

    # noinspection PyProtectedMember
    threading.Thread._set_ident_ = threading.Thread._set_ident
    threading.Thread._set_ident = set_ident


def _handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        print("KeyboardInterrupt caught by fsbc.debug._handle_exception")
        sys.exit(1)

    # FIXME: PYTHON3
    tb = traceback.extract_tb(exc_traceback)
    # print(exc_type, exc_value, tb)

    # FIXME: Handle the case where tb is empty
    # Traceback (most recent call last):
    #   File "fs-uae-launcher/fsbc/debug.py", line 79, in _handle_exception
    #     filename, line, function, dummy = tb.pop()
    # IndexError: pop from empty list

    filename, line, function, dummy = tb.pop()
    try:
        filename = filename.decode(sys.getfilesystemencoding())
    except:
        pass
    try:
        filename = str(filename)
    except:
        pass
    filename = os.path.basename(filename)
    thread = threading.currentThread()
    error_id = "{0}:{1}:{2}:{3}".format(
        exc_type.__name__, filename, function, line
    )

    # QtGui.QMessageBox.critical(None, "Error",
    # description = "<html>A critical error has occurred.<br/> "
    #                            + "<b>%s</b><br/><br/>" % error
    #                            + "It occurred at <b>line %d</b> of file "
    #                              "<b>%s</b>.<br/>" % (
    #                            line, filename)
    #                            + "</html>")
    #

    backtrace_string = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback)
    )

    message = "\nUnhandled exception detected in thread {0}:\n  {1}\n".format(
        thread.getName(), error_id
    )

    print(message)
    print(backtrace_string)

    print(message, file=sys.stderr)
    print(backtrace_string, file=sys.stderr)

    if thread.ident == main_thread_id:
        try:
            # FIXME
            # import wx
            # app = wx.GetApp()
            # if app is not None:
            #     wx.MessageBox(message + "\n" + backtrace_string)
            #     if app.IsMainLoopRunning():
            #         return
            #     print("The application will now close due to the above error")
            #     print("calling app.Exit")
            #     app.Exit()

            Signal("quit").notify()
        except Exception as e:
            print(repr(e))

        # sys.exit(1)


class AdditionalInfo(object):
    pass


def _thread_bootstrap_2_7(self):
    """This is a replacement "method" for the Thread class in Python 2.7,
    designed to let an exception fall through to the debugger."""

    # noinspection PyProtectedMember
    # noinspection PyUnresolvedReferences
    # noinspection PyProtectedMember
    # noinspection PyUnresolvedReferences
    from threading import (
        _active,
        _active_limbo_lock,
        _get_ident,
        _limbo,
        _profile_hook,
        _sys,
        _trace_hook,
    )

    try:
        self._set_ident()
        self._Thread__started.set()
        with _active_limbo_lock:
            _active[self._Thread__ident] = self
            del _limbo[self]
        if __debug__:
            self._note("%s.__bootstrap(): thread started", self)

        # if _trace_hook:
        #     self._note("%s.__bootstrap(): registering trace hook", self)
        #     _sys.settrace(_trace_hook)
        if _profile_hook:
            self._note("%s.__bootstrap(): registering profile hook", self)
            _sys.setprofile(_profile_hook)

        try:
            self.run()
        except SystemExit:
            if __debug__:
                self._note("%s.__bootstrap(): raised SystemExit", self)
        else:
            if __debug__:
                self._note("%s.__bootstrap(): normal return", self)
        finally:
            # Prevent a race in
            # test_threading.test_no_refcycle_through_target when
            # the exception keeps the target alive past when we
            # assert that it's dead.
            self._Thread__exc_clear()
    finally:
        with _active_limbo_lock:
            self._Thread__stop()
            try:
                # We don't call self.__delete() because it also
                # grabs _active_limbo_lock.
                del _active[_get_ident()]
            except:
                pass
