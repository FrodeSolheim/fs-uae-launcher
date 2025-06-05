import sys


def app_main():
    print("FS Game Center")

    from fsui import Application

    application = Application("fs-game-center")

    import threading

    from fsgs.http.server import http_server_main

    def http_server_thread():
        return http_server_main()

    threading.Thread(target=http_server_thread).start()

    if sys.platform.startswith("linux"):
        # Must load OpenGL to work around crash with Qt Quick on
        # Nvidia / Linux (due to libgl.so from mesa being loaded).
        import ctypes

        ctypes.CDLL("libGL.so.1", ctypes.RTLD_GLOBAL)

    from fsgs.ui.qwindow import GameCenterView

    window = GameCenterView()
    from fsui.qt import Qt

    # window.setFlags(Qt.FramelessWindowHint)
    window.setFlags(
        Qt.Window
        | Qt.FramelessWindowHint
        | Qt.WindowMinimizeButtonHint
        | Qt.WindowSystemMenuHint
    )
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
