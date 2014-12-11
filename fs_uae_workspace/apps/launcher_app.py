from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fs_uae_launcher.ui.MainWindow import MainWindow


def application(uri, args):
    window = MainWindow(None)
    window.show()
