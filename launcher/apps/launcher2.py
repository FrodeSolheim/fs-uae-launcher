import os
import sys
import traceback

from fsboot import executable_dir
from fscore.applicationdata import ApplicationData
from fscore.settings import Settings
from fsgamesys.options.constants import WORKSPACE_ON_STARTUP
from fsui.qt import QFontDatabase, init_qt
from launcher.context import get_global_theme
from launcher.launcherapp import LauncherApp
from system.classes.theme import initialize_qt_style
from system.exceptionhandler import (
    install_exception_display_function,
    software_failure,
)
from system.wsopen import wsopen


class Application:
    pass


def app_main(appname=None):
    print("prefs")
    # FIXME: Create QApplication only so we can show error messages if anything
    # goes wrong?

    qapplication = init_qt()

    print("FIXME: Saira - read from proper data location")

    # We need to wait until Qt is initialized before we can show warnings

    try:
        _app_main_1()
    except Exception as e:
        # We should be able to show a Qt error message dialog at least now
        # pylint: disable=no-name-in-module
        from PyQt6.QtWidgets import QMessageBox

        message = (
            f"An error of type {type(e).__name__} occurred during startup."
            "\n\n"
            "Please see the log file(s) for actual error messages and stack "
            "traces."
        )
        QMessageBox.critical(None, "Software Failure", message)
        raise

    # FIXME: Here?
    install_exception_display_function()

    # _app_main_2 runs with software_failure decorator
    _app_main_2(qapplication, appname)


def add_font(filename):
    QFontDatabase.addApplicationFontFromData(
        ApplicationData.stream(filename).read()
    )


def _app_main_1():
    add_font("Fonts/SairaCondensed-Medium.ttf")
    add_font("Fonts/SairaCondensed-Medium.ttf")
    add_font("Fonts/SairaCondensed-SemiBold.ttf")
    add_font("Fonts/SairaCondensed-Bold.ttf")
    add_font("Fonts/SairaSemiCondensed-Medium.ttf")


def debug_sys_stdout():
    org_sys_write = sys.stdout.write

    def write_wrapper(msg):
        org_sys_write(msg)
        traceback.print_stack()

    sys.stdout.write = write_wrapper


@software_failure
def _app_main_2(qapplication, appname):
    launcherapp = LauncherApp()

    theme = get_global_theme()
    initialize_qt_style(qapplication, theme)

    # debug_sys_stdout()

    app = Application()

    if appname.lower().endswith(":launcher"):
        if Settings.get(WORKSPACE_ON_STARTUP) == "1":
            wsopen("C:LoadWB")

    if appname:
        wsopen(appname)
    else:
        wsopen("SYS:Launcher")

    qapplication.exec()


def wsopen_main(appname):
    app_main(appname=appname)
