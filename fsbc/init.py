from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import platform
import fsbc.debug
import fsbc.logging
import fsbc.unicode
from fsbc.Application import Application

init_called = False
unicode_patched = False
logging_enabled = False
exception_handler_enabled = False


def initialize_application(
        name=None, version=None, series=None, patch_unicode=True,
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

    if series is not None:
        Application.app_series = series
        print(series)

    if enable_exception_handler:
        fsbc.debug.enable_exception_handler()
        exception_handler_enabled = True

    if patch_unicode:
        # patch system libraries (and argv) to work better with
        # unicode-enabled programs
        fsbc.unicode.patch_all()
        unicode_patched = True

    print(platform.uname())
    print(sys.argv)
