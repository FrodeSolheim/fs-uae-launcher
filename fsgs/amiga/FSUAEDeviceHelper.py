from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import subprocess
from fsbc.system import windows, macosx
from fsbc.Application import Application
from .FSUAE import FSUAE

try:
    getcwd = os.getcwdu
except AttributeError:
    getcwd = os.getcwd


class FSUAEDeviceHelper(object):

    @classmethod
    def start_with_args(cls, args, **kwargs):
        print("FSUAE.start_with_args:", args)
        exe = cls.find_executable()
        print("current dir (cwd): ", getcwd())
        print("using fs-uae executable:", exe)
        args = [exe] + args
        print(args)

        proc = subprocess.Popen(args, **kwargs)
        return proc

    @classmethod
    def find_executable(cls):
        return FSUAE.find_executable("fs-uae-device-helper")
