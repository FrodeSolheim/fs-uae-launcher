import functools
import os
import sys

import fsboot
import fsbc.application
import fsbc.desktop
from fsbc.settings import Settings
import fstd.desktop

import_order = ["PyQT5"]
if "--qt-bindings=pyqt5" in sys.argv:
    import_order = ["PyQT5"]
elif "--qt-bindings=pyqt4" in sys.argv:
    import_order = ["PyQT4"]
elif "--qt-bindings=pyside" in sys.argv:
    import_order = ["PySide"]
for name in import_order:
    if name == "PyQT5":
        try:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            import PyQt5
        except ImportError:
            continue
        else:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtCore import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtGui import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtWidgets import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtCore import pyqtSignal as Signal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtCore import pyqtSignal as QSignal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt5.QtOpenGL import *
            try:
                # noinspection PyUnresolvedReferences, PyPackageRequirements
                from PyQt5.QtX11Extras import *
            except ImportError:
                pass
    elif name == "PyQT4":
        try:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            import PyQt4
        except ImportError:
            continue
        else:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            import sip
            sip.setapi("QString", 2)
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtCore import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtGui import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtCore import pyqtSignal as Signal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtCore import pyqtSignal as QSignal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PyQt4.QtOpenGL import *
    elif name == "PySide":
        try:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            import PySide
        except ImportError:
            continue
        else:
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PySide.QtCore import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PySide.QtCore import Signal as QSignal
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PySide.QtGui import *
            # noinspection PyUnresolvedReferences, PyPackageRequirements
            from PySide.QtOpenGL import *
    else:
        raise Exception("unknown QT python bindings specified")
    break
else:
    raise Exception("no QT python bindings found")


def open_url_in_browser(url):
    print("[QT] open_url_in_browser", url)
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    QDesktopServices.openUrl(QUrl(url))


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


class QtBaseApplication(QApplication):
    pass


@functools.lru_cache()
def init_qt():

    if sys.platform == "darwin":
        # qt_plugins_dir = os.path.join(
        #     BaseApplication.executable_dir(), "..", "Resources",
        #     "qt_plugins")
        # print(qt_plugins_dir)
        # if os.path.exists(qt_plugins_dir):
        #     QApplication.setLibraryPaths([qt_plugins_dir])
        if os.path.exists(os.path.join(fsboot.executable_dir(),
                                       "platforms", "libqcocoa.dylib")):
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QApplication.setLibraryPaths([fsboot.executable_dir()])

    if getattr(sys, "frozen", False):
        # noinspection PyCallByClass,PyTypeChecker
        QApplication.setLibraryPaths([fsboot.executable_dir()])

    # Should not be necessary with Qt 5.2.x:
    # fix_qt_for_maverick()

    fsbc.desktop.set_open_url_in_browser_function(open_url_in_browser)
    qapplication = QtBaseApplication([])
    initialize_qt_style(qapplication)
    return qapplication


# noinspection PyUnboundLocalVariable
def initialize_qt_style(qapplication):
    # from fsui.qt import QStyleFactory, QPalette, QColor, Qt, QFont
    fusion_variant = ""

    launcher_theme = Settings.instance().get("launcher_theme")
    if launcher_theme == "standard":
        use_fusion_theme = False
    elif launcher_theme == "native":
        # native is an older deprecated name for standard
        use_fusion_theme = False
    elif launcher_theme == "fusion-adwaita":
        use_fusion_theme = True
        fusion_variant = "adwaita"
    elif launcher_theme == "fusion-plain":
        use_fusion_theme = True
    elif launcher_theme == "fusion-dark":
        use_fusion_theme = True
        fusion_variant = "dark"
    elif launcher_theme == "fws":
        use_fusion_theme = True
        fusion_variant = "fws"
        from fsui.qt.window import FwsWindow
        FwsWindow.set_default()
    else:
        use_fusion_theme = True
        if fstd.desktop.is_running_gnome_3():
            fusion_variant = "adwaita"

    if "--launcher-theme=fusion-dark" in sys.argv:
        use_fusion_theme = True
        fusion_variant = "dark"

    font = qapplication.font()
    print("FONT: Default is {} {}".format(font.family(), font.pointSize()))

    if use_fusion_theme:
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        qapplication.setStyle(QStyleFactory.create("Fusion"))
        if fusion_variant == "adwaita":
            pa = QPalette()
            pa.setColor(QPalette.Window, QColor(237, 237, 237))
            pa.setColor(QPalette.AlternateBase, QColor(237, 237, 237))
            pa.setColor(QPalette.Button, QColor(237, 237, 237))
            qapplication.setPalette(pa)
        elif fusion_variant == "fws":
            pa = QPalette()
            pa.setColor(QPalette.Window, QColor(242, 242, 242))
            pa.setColor(QPalette.AlternateBase, QColor(242, 242, 242))
            pa.setColor(QPalette.Button, QColor(242, 242, 242))
            qapplication.setPalette(pa)
        elif fusion_variant == "dark":
            pa = QPalette()
            pa.setColor(QPalette.Window, QColor(53, 53, 53))
            pa.setColor(QPalette.WindowText, Qt.white)
            pa.setColor(QPalette.Base, QColor(25, 25, 25))
            pa.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            pa.setColor(QPalette.ToolTipBase, Qt.white)
            pa.setColor(QPalette.ToolTipText, Qt.white)
            pa.setColor(QPalette.Text, Qt.white)
            pa.setColor(QPalette.Button, QColor(53, 53, 53))
            pa.setColor(QPalette.ButtonText, Qt.white)
            pa.setColor(QPalette.BrightText, Qt.red)
            pa.setColor(QPalette.Link, QColor(42, 130, 218))
            pa.setColor(QPalette.Highlight, QColor(42, 130, 218))
            pa.setColor(QPalette.HighlightedText, Qt.black)
            qapplication.setPalette(pa)
            qapplication.setStyleSheet(
                "QToolTip { color: #ffffff; background-color: #2a82da; "
                "border: 1px solid white; }")

        try:
            launcher_font_size = int(
                    Settings.instance().get("launcher_font_size"))
        except ValueError:
            if fusion_variant == "fws":
                launcher_font_size = 13
            else:
                launcher_font_size = 0
        if launcher_font_size:
            print("FONT: Override size {}".format(launcher_font_size))
            font.setPointSize(launcher_font_size)
            if fusion_variant == "fws":
                font = QFont("Roboto")
                font.setPointSizeF(10.5)
                font.setHintingPreference(QFont.PreferNoHinting)
            qapplication.setFont(font)
