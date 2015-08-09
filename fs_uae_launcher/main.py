#!/usr/bin/env python3

import sys

if sys.version_info[0] < 3 or sys.version_info[1] < 2:
    print("You need at least Python 3.2 to run FS-UAE Launcher")
    sys.exit(1)

# Workaround to make import typing work without having it on the default
# python path (would confuse mypy).

import fstd.typing
sys.modules["typing"] = fstd.typing

if "--server" in sys.argv:
    sys.argv.remove("--server")
    app = "fs-uae-netplay-server"
elif "--fs-uae-arcade" in sys.argv:
    sys.argv.remove("--fs-uae-arcade")
    app = "fs-uae-arcade"
elif "--fs-game-center" in sys.argv:
    sys.argv.remove("--fs-game-center")
    app = "fs-game-center"
elif sys.argv[0].endswith("fs-game-center"):
    app = "fs-game-center"
else:
    app = "fs-uae-launcher"


def main():
    version = "2.5.38dev"

    # if "--fs-uae-workspace=real" in sys.argv:
    #     try:
    #         # noinspection PyUnresolvedReferences
    #         from gi.repository import Gdk
    #     except ImportError:
    #         Gdk = None

    for arg in sys.argv:
        # if not isinstance(arg, unicode):
        if isinstance(arg, bytes):
            arg = arg.decode(sys.getfilesystemencoding())
        if arg.startswith("--") and "=" in arg:
            key, value = arg[2:].split("=", 1)
            key = key.replace("-", "_")
            if key == "fake_version":
                version = value

    from fsgs.FSGSDirectories import FSGSDirectories
    FSGSDirectories.initialize()

    import socket
    socket.setdefaulttimeout(30.0)

    from fsbc.init import initialize_application
    initialize_application(app, version=version)

    if app == "fs-uae-netplay-server":
        from fs_uae_launcher.server.game import run_server
        run_server()

    elif app == "fs-game-center":
        print("FS Game Center")

        from fsui import Application
        application = Application("fs-game-center")

        from fsgs.http.server import http_server_main
        import threading

        def http_server_thread():
            return http_server_main()
        
        threading.Thread(target=http_server_thread).start()

        # from fsgs.ui.mainwindow import FSGSMainWindow
        # window = FSGSMainWindow()
        from fsgs.ui.qwindow import GameCenterView
        window = GameCenterView()
        from fsui.qt import Qt
        # window.setFlags(Qt.FramelessWindowHint)
        window.setFlags(Qt.Window | 
                        Qt.FramelessWindowHint | 
                        Qt.WindowMinimizeButtonHint | 
                        Qt.WindowSystemMenuHint)
        # window.show()
        window.showMaximized()
        # window.showFullScreen()
        # window.setWindowState(Qt.WindowFullScreen)
        # window.setVisible(True)

        # from fs_uae_launcher.FSUAELauncher import FSUAELauncher
        # application = FSUAELauncher()

        # if application.start():
        application.run()
        # application.save_settings()

        from fsbc.signal import Signal
        Signal("quit").notify()

    elif app == "fs-uae-arcade":
        try:
            import game_center.main
            game_center.main.main()
            print("main returned")

        finally:
            from fsbc.Application import Application
            application = Application.instance()
            if application:
                print("calling Application stop")
                Application.get().stop()

            from fsbc.signal import Signal
            print("sending quit signal")
            Signal("quit").notify()

    else:
        print("FS-UAE Launcher {0}".format(version))

        # if "--workspace" in sys.argv:
        #     if "--qt" not in sys.argv:
        #         sys.argv.insert(1, "--qt")

        from fs_uae_launcher.ConfigChecker import ConfigChecker
        ConfigChecker()

        from fs_uae_launcher.FSUAELauncher import FSUAELauncher
        application = FSUAELauncher()

        if "--fs-uae-workspace=real" in sys.argv:
            from fs_uae_workspace.realdesktop.taskbarwindow import TaskBarWindow
            from fs_uae_workspace.realdesktop.titlebarwindow import TitleBarWindow
            # from fs_uae_workspace.realdesktop.realdesktopwindow import RealDesktopWindow
            from fs_uae_workspace.realdesktop.realwindowhandler import RealWindowHandler
            # from fs_uae_workspace.shellui.shellwidget import ShellWidget

            from fs_uae_workspace.shellui.taskbarwidget import TaskBarWidget
            from fs_uae_workspace.shellui.titlebarwidget import TitleBarWidget
            # from fs_uae_workspace.shellui.desktopwidget import DesktopWidget

            window_handler = RealWindowHandler()

            title_bar_window = TitleBarWindow()
            title_bar_widget = TitleBarWidget(title_bar_window, window_handler)
            title_bar_window.setCentralWidget(title_bar_widget)
            title_bar_window.show()

            task_bar_window = TaskBarWindow()
            task_bar_widget = TaskBarWidget(task_bar_window, window_handler)
            task_bar_window.setCentralWidget(task_bar_widget)
            task_bar_window.show()

            # desktop_window = RealDesktopWindow()
            # shell_widget = ShellWidget(desktop_window, window_handler)
            # desktop_window.set_shell_widget(shell_widget)

            # desktop_window.show()
            application.run()

            sys.exit(0)

        elif "--workspace" in sys.argv:
            if ":" in sys.argv[-1]:
                from fs_uae_workspace.shell import shell_open
                shell_open(sys.argv[-1])

        if application.start():
            application.run()
        application.save_settings()

        from fs_uae_launcher.netplay.IRC import IRC
        IRC.stop()

        from fsbc.signal import Signal
        Signal("quit").notify()
