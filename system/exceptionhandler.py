import sys
import traceback
from functools import wraps

from fspy.exception import (
    HandledException,
    handle_exception_after_display,
    handle_exception_before_display,
    set_exception_display_function,
)
from system.classes.exceptiondialog import ExceptionDialog

"""
TODO: Should have the option to snooze the exception dialog for 5 minutes, in
case spamming with many similar exceptions.
TODO: Or, be able to ignore further occurences of similar exception(s).

"""


def exception_display_function(type_, value, tb, recoverable=True):
    display_exception_2(type_, value, tb, recoverable=recoverable)


def install_exception_display_function():
    set_exception_display_function(exception_display_function)
    print("Installed exception display function")


class DisplayedException(Exception):
    pass


def withExceptionHandler(function):
    # FIXME: Is it possible to get a reference to the widget owning the
    # function (method) when the error occurs?
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except DisplayedException:
            # Already displayed
            raise
        except HandledException:
            raise
        except Exception as e:
            print(("exceptionhandler"))
            type_, value, tb = sys.exc_info()
            handle_exception_before_display(type_, value, tb)
            # traceback.print_exc()
            display_exception(e, recoverable=True)
            handle_exception_after_display(type_, value, tb)
            # Re-raise the exception in case the failed method was part of a
            # call chain. Since this one failed, it is not safe to continue.
            # We wrap it in another exception so we can ignore displaying it
            # again in cause of multiple layers of exception handlers.
            # raise DisplayedException() from e
            # print("-" * 79)

    return wrapper


exceptionhandler = withExceptionHandler


def software_failure(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except DisplayedException:
            # Already displayed
            raise
        except HandledException:
            raise
        except Exception as e:
            print(("software_failure"))
            type_, value, tb = sys.exc_info()
            handle_exception_before_display(type_, value, tb)
            # traceback.print_exc()
            display_exception(e, recoverable=False)
            handle_exception_after_display(type_, value, tb)
            # Re-raise the exception in case the failed method was part of a
            # call chain. Since this one failed, it is not safe to continue.
            # We wrap it in another exception so we can ignore displaying it
            # again in cause of multiple layers of exception handlers.
            # raise DisplayedException() from e
            # print("-" * 79)

    return wrapper


def display_exception(e, *, recoverable=False):
    # print("FIXME: Find active window, set that as parent and center on it")
    # print("FIXME: Maybe not set parent, but do center on it!")
    # print("FIXME: Or center on mouse cursor poisition")
    print("Exception dialog opening")
    try:
        ExceptionDialog(
            None,
            exception=e,
            backtrace=traceback.format_exc(),
            recoverable=recoverable,
        ).show_modal()
    except Exception as e1:
        traceback.print_exc()
        try:
            error_displaying_exception_1(e, e1)
        except Exception as e2:
            error_displaying_exception_2(e, e2)

    print("Exception dialog was closed")


def display_exception_2(type_, value, tb, *, recoverable=False):
    # print("FIXME: Find active window, set that as parent and center on it")
    # print("FIXME: Maybe not set parent, but do center on it!")
    # print("FIXME: Or center on mouse cursor poisition")
    # print("Exception dialog opening")
    try:
        ExceptionDialog(
            None,
            exception=value,
            backtrace="".join(traceback.format_exception(type_, value, tb)),
            recoverable=recoverable,
        ).show_modal()
    except Exception as e1:
        traceback.print_exc()
        try:
            error_displaying_exception_1(value, e1)
        except Exception as e2:
            error_displaying_exception_2(value, e2)

    print("Exception dialog was closed")


def error_displaying_exception_1(e, e1):
    print("error_displaying_exception")
    message = (
        f"An error of type {type(e).__name__} occurred. Then, another error "
        f"of type {type(e1).__name__} occurred while trying to display the "
        "error message."
        "\n\n"
        "Please see the log file(s) for full error messages and stack traces."
    )
    from fsui import show_error

    show_error(message, "Software Failure (1)")


def error_displaying_exception_2(e, e2):
    print("error_displaying_exception_2")
    message = (
        f"An error of type {type(e).__name__} occurred. Then, another error "
        f"of type {type(e2).__name__} occurred while trying to display the "
        "error message."
        "\n\n"
        "Please see the log file(s) for full error messages and stack traces."
    )
    # pylint: disable=no-name-in-module
    from PyQt5.QtWidgets import QMessageBox

    QMessageBox.critical(None, "Software Failure (2)", message)
