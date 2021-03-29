import os

from fsui.qt import QFontDatabase, init_qt
from system.classes.theme import initialize_qt_style


class Application:
    pass


def app_main():
    print("prefs")
    qapplication = init_qt()

    print("FIXME: Saira - read from proper data location")
    with open(
        os.path.expanduser(
            "~/openretro/git/fsemu/data/SairaCondensed-Medium.ttf"
        ),
        "rb",
    ) as f:
        QFontDatabase.addApplicationFontFromData(f.read())
    with open(
        os.path.expanduser(
            "~/openretro/git/fsemu/data/SairaCondensed-Medium.ttf"
        ),
        "rb",
    ) as f:
        QFontDatabase.addApplicationFontFromData(f.read())
    with open(
        os.path.expanduser(
            "~/openretro/git/fsemu/data/SairaCondensed-SemiBold.ttf"
        ),
        "rb",
    ) as f:
        QFontDatabase.addApplicationFontFromData(f.read())
    with open(
        os.path.expanduser(
            "~/openretro/git/fsemu/data/SairaCondensed-Bold.ttf"
        ),
        "rb",
    ) as f:
        QFontDatabase.addApplicationFontFromData(f.read())

    initialize_qt_style(qapplication)

    from launcher.launcherapp import LauncherApp

    launcherapp = LauncherApp()

    # from launcher.ui.launcherwindow import LauncherWindow
    # launcherwindow = LauncherWindow()
    # launcherwindow.show()

    # window = PrefsWindow(app)
    # window.show()

    app = Application()
    from system.wsopen import wsopen

    wsopen("SYS:Prefs/WHDLoad")

    qapplication.exec_()
