import sys
import threading
import traceback

from fsbc.settings import get_setting
from fspy.decorators import initializer
from fspy.options import (
    AUTOMATIC_ERROR_REPORTING,
    AUTOMATIC_ERROR_REPORTING_INCLUDE_USER_ID,
    ERROR_REPORT_USER_ID,
)

# from typing import Func
main_thread_id = threading.current_thread().ident
excepthook_installed = False
# # type: Function
exception_display_function = None
automatic_error_reports = False


def set_automatic_error_reports(enable=True):
    global automatic_error_reports
    automatic_error_reports = True
    if automatic_error_reports:
        print("Automatic error reports enabled")


def is_running_in_debugger():
    return bool(sys.gettrace())


def set_exception_display_function(function):
    global exception_display_function
    exception_display_function = function


def excepthook(type_, value, tb):
    if type_ == HandledException:
        print("Exception hook: HandledException")
        return
    if type_ == KeyboardInterrupt:
        print("Exception hook: KeyboardInterrupt")
        sys.__excepthook__(type_, value, tb)
        sys.exit(1)
        return
    print("Exception hook:", type_)
    print("-" * 79)
    log_exception(type_, value, tb)
    maybe_send_exception(type_, value, tb)

    if exception_display_function is not None:
        # pylint: disable=not-callable
        exception_display_function(type_, value, tb)

    print("-" * 79)


def install_excepthook(force=False):
    # print("Not installing sys.excepthook")
    # return

    global excepthook_installed
    if excepthook_installed:
        return
    excepthook_installed = True

    if not force and is_running_in_debugger():
        print("Running in debugger, not installing sys.excepthook")
        # _let_thread_exceptions_be_unhandled()
        return False

    print("Installing new sys.excepthook")
    sys._excepthook_replaced_by_fs = sys.excepthook
    sys.excepthook = excepthook
    # _enable_thread_exception_handler()
    return True


@initializer
def initialize_sentry():
    try:
        import sentry_sdk
    except ImportError:
        pass

    # FIXME: Only init sentry when we know the user has accepted automatic bug
    # reports.
    # FIXME: Only send automated bug reports from official versions from
    # fs-uae.net (etc).
    # FIXME: Tag with version, stable/testing/devel, and disable for local test
    # versions.
    # Setting in FS-UAE Launcer -> Prefs -> Privacy ?
    # Or maybe a checkbox in exception dialogs?
    excepthook = sys.excepthook
    try:
        sentry_sdk.init(
            "https://de692f5459fc4ee2bc5c6bd86ed56394@sentry.io/4581716"
        )
    except Exception:
        traceback.print_exc()
    # Easiest way to disable the Sentry's excepthook integration? We want to
    # handle the excepthook ourselves.
    sys.excepthook = excepthook


def maybe_send_exception(type_, value, tb):
    # if not automatic_error_reports:
    if get_setting(AUTOMATIC_ERROR_REPORTING) != "1":
        print(
            "Not sending automatic error report"
            " (automatic_error_reports = False)"
        )
    try:
        from sentry_sdk import capture_exception, push_scope
    except ImportError:
        print("Error in maybe_send_exception")
        traceback.print_exc()
        return
    initialize_sentry()
    try:
        with push_scope() as scope:
            if get_setting(AUTOMATIC_ERROR_REPORTING_INCLUDE_USER_ID) == "1":
                if get_setting(ERROR_REPORT_USER_ID):
                    scope.user = {"id": get_setting(ERROR_REPORT_USER_ID)}
            print("maybe-send-exception -----------------")
            capture_exception(value)
    except Exception:
        print("Error in maybe_send_exception")
        traceback.print_exc()
        return


def log_exception(type_, value, tb):
    # FIXME: Send directly to log file instead (no stdout), and then log to
    # stderr in addition. We don't want to log twice to the console.
    traceback.print_exception(type_, value, tb)
    # print("-" * 79, file=sys.stderr)
    # traceback.print_exception(type_, value, tb, file=sys.stderr)


def handle_exception_before_display(type_, value, tb):
    print("-" * 79)
    log_exception(type_, value, tb)
    maybe_send_exception(type_, value, tb)


class HandledException(Exception):
    pass


def handle_exception_after_display(type_, value, tb):
    print("-" * 79)
    raise HandledException() from value
