from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from fsbc.desktop import set_open_url_in_browser_function
from fsbc.system import macosx
from fsui.qt import QApplication, QFont, QDesktopServices, QUrl
from fsbc.Application import Application as BaseApplication


def open_url_in_browser(url):
    print("[QT] open_url_in_browser", url)
    QDesktopServices.openUrl(QUrl(url))


class QtBaseApplication(QApplication):
    pass


# def fix_qt_for_maverick():
#     """ Fixes Qt 4 for Mac OS X 10.9.
#     http://successfulsoftware.net/2013/10/23/fixing-qt-4-for-mac-os-x-10-9-mavericks/
#     """
#     if not macosx:
#         return
#     #if QSysInfo.MacintoshVersion <= QSysInfo.MV_10_8:
#     #    return
#
#     # fix Mac OS X 10.9 (mavericks) font issue
#     # https://bugreports.qt-project.org/browse/QTBUG-32789
#     QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")


class Application(BaseApplication):

    def __init__(self, name):
        BaseApplication.__init__(self, name)

        if macosx:
            #qt_plugins_dir = os.path.join(
            #    BaseApplication.executable_dir(), "..", "Resources",
            #    "qt_plugins")
            #print(qt_plugins_dir)
            #if os.path.exists(qt_plugins_dir):
            #    QApplication.setLibraryPaths([qt_plugins_dir])
            if os.path.exists(os.path.join(BaseApplication.executable_dir(),
                                           "platforms", "libqcocoa.dylib")):
                QApplication.setLibraryPaths(
                    [BaseApplication.executable_dir()])

        # should not be necessary with Qt 5.2.x:
        # fix_qt_for_maverick()
        set_open_url_in_browser_function(open_url_in_browser)
        self.qapplication = QtBaseApplication([])

        self.on_create()

    def on_create(self):
        pass

    def run(self):
        self.qapplication.exec_()
        self.stop()

    def set_icon(self, icon):
        self.qapplication.setWindowIcon(icon.qicon())

    def run_in_main(self, function, *args, **kwargs):
        from fsui.qt import call_after
        call_after(function, *args, **kwargs)
