import functools
import os
import sys

import fsbc.application
import fsbc.desktop
import fstd.desktop
from fsbc.settings import Settings
from fsgamesys.options.option import Option

# # pylint: disable=unused-wildcard-import
# if os.environ.get("QT_API", "").lower() == "pyside2":
#     # noinspection PyUnresolvedReferences
#     from fsui.qt.pyside2 import *
# else:
#     from fsui.qt.pyqt5 import *
from fsui.qt.pyqt5 import *

# from fsui.qt.pyqt5 import (
#     QAbstractListModel,
#     QApplication,
#     QBrush,
#     QCheckBox,
#     QColor,
#     QColorDialog,
#     QComboBox,
#     QCoreApplication,
#     QCursor,
#     QDesktopServices,
#     QDesktopWidget,
#     QDialog,
#     QEvent,
#     QFileDialog,
#     QFont,
#     QFontDatabase,
#     QFontMetrics,
#     QFrame,
#     QIcon,
#     QImage,
#     QLabel,
#     QLinearGradient,
#     QLineEdit,
#     QListView,
#     QMainWindow,
#     QMenu,
#     QMessageBox,
#     QObject,
#     QPainter,
#     QPalette,
#     QPen,
#     QPixmap,
#     QPoint,
#     QPushButton,
#     QRect,
#     QScrollArea,
#     QSignal,
#     QSize,
#     QSpinBox,
#     QStandardItem,
#     QStandardItemModel,
#     QStyleFactory,
#     QSvgRenderer,
#     Qt,
#     QTextCursor,
#     QTextEdit,
#     QTimer,
#     QUrl,
#     QWidget,
# )


def open_url_in_browser(url: str) -> None:
    print("[QT] open_url_in_browser", url)
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    QDesktopServices.openUrl(QUrl(url))


class QtBaseApplication(QApplication):
    pass


@functools.lru_cache()
def init_qt() -> QApplication:
    # if sys.platform == "darwin":
    #     # qt_plugins_dir = os.path.join(
    #     #     BaseApplication.executable_dir(), "..", "Resources",
    #     #     "qt_plugins")
    #     # print(qt_plugins_dir)
    #     # if os.path.exists(qt_plugins_dir):
    #     #     QApplication.setLibraryPaths([qt_plugins_dir])
    #     if os.path.exists(
    #         os.path.join(
    #             fsboot.executable_dir(), "platforms", "libqcocoa.dylib"
    #         )
    #     ):
    #         # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    #         QApplication.setLibraryPaths([fsboot.executable_dir()])

    # if getattr(sys, "frozen", False):
    #     if sys.platform == "darwin":
    #         # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    #         QApplication.setLibraryPaths(
    #             [os.path.join(fsboot.executable_dir(), "..", "PlugIns")]
    #         )
    #     else:
    #         # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    #         QApplication.setLibraryPaths([fsboot.executable_dir()])

    # Should not be necessary with Qt 5.2.x:
    # fix_qt_for_maverick()

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    fstd.desktop.set_open_url_in_browser_function(open_url_in_browser)
    qapplication = QtBaseApplication(sys.argv)

    initialize_qt_style(qapplication)
    return qapplication


# noinspection PyUnboundLocalVariable
def initialize_qt_style(qapplication: QApplication) -> None:
    # from fsui.qt import QStyleFactory, QPalette, QColor, Qt, QFont
    fusion_variant = ""

    launcher_theme = Settings.instance().get(Option.LAUNCHER_THEME)
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
    elif launcher_theme == "fusion-windows10":
        use_fusion_theme = True
        fusion_variant = "windows10"
    elif launcher_theme == "fws":
        use_fusion_theme = True
        fusion_variant = "fws"
        from fsui.qt.old_window import FwsWindow  # type: ignore

        FwsWindow.set_default()
    else:
        use_fusion_theme = True
        if fstd.desktop.is_running_gnome_3():
            fusion_variant = "adwaita"
        elif fstd.desktop.is_running_windows_10():
            fusion_variant = "windows10"

    if "--launcher-theme=fusion-dark" in sys.argv:
        use_fusion_theme = True
        fusion_variant = "dark"

    font = QApplication.font()
    print("FONT: Default is {} {}".format(font.family(), font.pointSize()))

    if use_fusion_theme:
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        if fusion_variant == "adwaita":
            pa = QPalette()
            # background = QColor("#f6f5f4")
            background = QColor("#eae7e5")
            pa.setColor(QPalette.Window, background)
            pa.setColor(QPalette.AlternateBase, background)
            pa.setColor(QPalette.Button, background)
            # pa.setColor(QPalette.Base, QColor(255, 255, 255))
            pa.setColor(
                QPalette.Disabled, QPalette.Base, QColor(241, 241, 241)
            )

            # pa.setColor(QPalette.Window, QColor("#aeaeae"))
            # pa.setColor(QPalette.AlternateBase, QColor("#aeaeae"))
            # pa.setColor(QPalette.Button, QColor("#aeaeae"))

            qapplication.setPalette(pa)
        elif fusion_variant == "fws" or fusion_variant == "windows10":
            pa = QPalette()
            pa.setColor(QPalette.Window, QColor(242, 242, 242))
            pa.setColor(QPalette.AlternateBase, QColor(242, 242, 242))
            pa.setColor(QPalette.Button, QColor(242, 242, 242))
            qapplication.setPalette(pa)
        elif fusion_variant == "dark":
            pa = QPalette()
            pa.setColor(QPalette.Window, QColor(0x50, 0x50, 0x50))
            pa.setColor(QPalette.WindowText, Qt.white)
            pa.setColor(QPalette.Base, QColor(25, 25, 25))
            pa.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            pa.setColor(QPalette.ToolTipBase, Qt.white)
            pa.setColor(QPalette.ToolTipText, Qt.white)
            pa.setColor(QPalette.Text, Qt.white)
            pa.setColor(QPalette.Button, QColor(0x58, 0x58, 0x58))
            pa.setColor(QPalette.ButtonText, Qt.white)
            pa.setColor(QPalette.BrightText, Qt.red)
            pa.setColor(QPalette.Link, QColor(42, 130, 218))
            pa.setColor(QPalette.Highlight, QColor(42, 130, 218))
            pa.setColor(QPalette.HighlightedText, Qt.black)
            qapplication.setPalette(pa)
            qapplication.setStyleSheet(
                "QToolTip { color: #ffffff; background-color: #2a82da; "
                "border: 1px solid white; }"
            )

        try:
            launcher_font_size = int(
                Settings.instance().get("launcher_font_size")
            )
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

    import fsui

    if use_fusion_theme:
        fsui.theme = "fusion"
        fsui.theme_variant = fusion_variant
