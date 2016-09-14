import sys
import platform
import fsbc.debug
import fsbc.logging
# import fsbc.unicode
from fsbc.application import Application

init_called = False
unicode_patched = False
logging_enabled = False
exception_handler_enabled = False


def initialize_application(
        name=None, version=None, patch_unicode=True,
        enable_logging=True, enable_exception_handler=True):

    global init_called, unicode_patched, logging_enabled, \
        exception_handler_enabled
    init_called = True

    if name and enable_logging:
        fsbc.logging.setup_logging(name + ".log.txt")
        logging_enabled = True

    if name is not None:
        Application.app_name = name
        print(name)

    if version is not None:
        Application.app_version = version
        print(version)

    if enable_exception_handler:
        fsbc.debug.enable_exception_handler()
        exception_handler_enabled = True

    if patch_unicode:
        # patch system libraries (and argv) to work better with
        # unicode-enabled programs
        # FIXME: removed for Python 3
        # fsbc.unicode.patch_all()
        unicode_patched = True

    print(platform.uname())
    print(sys.argv)
