import functools
import sys

# noinspection PyUnresolvedReferences, PyPackageRequirements
from PyQt6.QtCore import *  # type: ignore # noqa: F403
from PyQt6.QtCore import Qt, QUrl

# noinspection PyUnresolvedReferences, PyPackageRequirements
from PyQt6.QtCore import pyqtSignal as QSignal  # noqa: F401

# noinspection PyUnresolvedReferences, PyPackageRequirements
from PyQt6.QtCore import pyqtSignal as Signal  # noqa: F401

# noinspection PyUnresolvedReferences, PyPackageRequirements
from PyQt6.QtGui import *  # type: ignore # noqa: F403
from PyQt6.QtGui import QColor, QDesktopServices, QFont, QPalette

# noinspection PyUnresolvedReferences, PyPackageRequirements
from PyQt6.QtOpenGL import *  # type: ignore # noqa: F403

# noinspection PyUnresolvedReferences, PyPackageRequirements
from PyQt6.QtWidgets import *  # type: ignore # noqa: F403
from PyQt6.QtWidgets import QApplication, QStyleFactory

import fsbc.application
import fsbc.desktop
import fstd.desktop
from fsbc.settings import Settings
from fsgs.option import Option

try:
    # noinspection PyUnresolvedReferences, PyPackageRequirements
    from PyQt6.QtX11Extras import *  # type: ignore # noqa: F403
except ImportError:
    pass


def open_url_in_browser(url):
    print("[QT] open_url_in_browser", url)
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    QDesktopServices.openUrl(QUrl(url))


class QtBaseApplication(QApplication):
    pass


@functools.lru_cache()
def init_qt():
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
    #     # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    #     QApplication.setLibraryPaths([fsboot.executable_dir()])

    # Should not be necessary with Qt 5.2.x:
    # fix_qt_for_maverick()

    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    fsbc.desktop.set_open_url_in_browser_function(open_url_in_browser)
    qapplication = QtBaseApplication(sys.argv)
    initialize_qt_style(qapplication)
    return qapplication


# noinspection PyUnboundLocalVariable
def initialize_qt_style(qapplication):
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
        from fsui.qt.window import FwsWindow

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

    font = qapplication.font()
    print("FONT: Default is {} {}".format(font.family(), font.pointSize()))

    if use_fusion_theme:
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        qapplication.setStyle(QStyleFactory.create("Fusion"))
        pa = QPalette()

        if fusion_variant == "adwaita":
            background = QColor("#f2f2f2")
            pa.setColor(QPalette.ColorRole.Window, background)
            pa.setColor(QPalette.ColorRole.AlternateBase, background)
            pa.setColor(QPalette.ColorRole.Button, background)

            # pa.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))

            # No Disabled role any more?
            # pa.setColor(
            #     QPalette.ColorRole.Disabled, QPalette.ColorRole.Base, QColor(241, 241, 241)
            # )

            # pa.setColor(QPalette.Window, QColor("#aeaeae"))
            # pa.setColor(QPalette.AlternateBase, QColor("#aeaeae"))
            # pa.setColor(QPalette.Button, ("#aeaeae"))

        elif fusion_variant == "fws" or fusion_variant == "windows10":
            pa.setColor(QPalette.ColorRole.Window, QColor(242, 242, 242))
            pa.setColor(
                QPalette.ColorRole.AlternateBase, QColor(242, 242, 242)
            )
            pa.setColor(QPalette.ColorRole.Button, QColor(242, 242, 242))
        elif fusion_variant == "dark":
            pa.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            pa.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            pa.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            pa.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            pa.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            pa.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            pa.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            pa.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            pa.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            pa.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            pa.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            pa.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            pa.setColor(
                QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black
            )
            qapplication.setStyleSheet(
                "QToolTip { color: #ffffff; background-color: #2a82da; "
                "border: 1px solid white; }"
            )

        else:
            background = QColor("#f2f2f2")
            pa.setColor(QPalette.ColorRole.Window, background)
            pa.setColor(QPalette.ColorRole.AlternateBase, background)
            pa.setColor(QPalette.ColorRole.Button, background)

        qapplication.setPalette(pa)

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
                font.setHintingPreference(
                    QFont.HintingPreference.PreferNoHinting
                )
            qapplication.setFont(font)

    import fsui

    if use_fusion_theme:
        fsui.theme = "fusion"
        fsui.theme_variant = fusion_variant
