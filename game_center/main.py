import os
import sys
import time
import fsui
import weakref
from fsui.qt import Qt, QCursor
import traceback
import threading
from fsbc.system import macosx, windows
from collections import deque
from game_center.Application import Application
from fsbc.Application import app
from game_center.glui.imageloader import ImageLoader
from game_center.glui.input import InputHandler
from .gnome3 import running_in_gnome_3, handle_gnome_extensions


class MainQueueItem(object):
    done = False
    exception = None
    result = None


_main_thread = threading.currentThread()


class Main(object):

    queue = deque()
    lock = threading.Lock()

    @classmethod
    def process(cls):
        with cls.lock:
            for i in range(len(cls.queue)):
                item = cls.queue.popleft()
                try:
                    item.result = item.func(*item.args, **item.kwargs)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    item.exception = e
                item.done = True

    @classmethod
    def call(cls, func, *args, **kwargs):
        if threading.currentThread() == _main_thread:
            return func(*args, **kwargs)
        item = MainQueueItem()
        item.func = func
        item.args = args
        item.kwargs = kwargs
        with cls.lock:
            cls.queue.append(item)
        while not item.done:
            time.sleep(0.01)
        if item.exception:
            raise item.exception
        return item.result


class Callbacks():

    def __init__(self):
        self.width = 320
        self.height = 200
        self.window = None

    def initialize(self):
        from game_center.gamecenter import GameCenter
        GameCenter.init()

        import game_center.glui
        game_center.glui.main(g_callbacks)

    def resize(self, width, height):
        print("Callbacks.resize", width, height)
        from game_center.glui.window import on_resize
        self.width = width
        self.height = height
        on_resize((width, height))

    def render(self):
        from game_center.glui.window import main_loop_iteration
        if main_loop_iteration():
            main_window.close()

    def timer(self):
        InputHandler.update()

    def restore_window_if_necessary(self):
        pass
        # noinspection PyCallingNonCallable
        # window = self.window()
        # under Gnome 3, the window is minized when launching FS-UAE
        # full-screen from full-screen arcade/game center.
        # window.restore_window_if_necessary()

    def set_window(self, window):
        self.window = weakref.ref(window)


def check_setting(name):
    name = name.replace("_", "-")
    if "--" + name in sys.argv:
        return "1"
    if "--" + name + "=1" in sys.argv:
        return "1"
    if "--no-" + name in sys.argv:
        return "0"
    if "--" + name + "=0" in sys.argv:
        return "0"
    return ""


def main():
    global main_window, g_callbacks
    # import logging; logging.shutdown(); import sys; sys.exit()
    print("Fengestad Game System...")
    application = Application()
    fs_width, fs_height = fsui.get_screen_size()

    cursor_position = None
    use_window = False
    use_window_decorations = True
    use_fullscreen = True
    use_fullscreen_window = False
    use_top_clock = check_setting("top_clock") != "0"
    use_top_logo = check_setting("top_logo") != "0"

    if running_in_gnome_3():
        if check_setting("fullscreen") == "0":
            # we want a normal window
            pass
        else:
            use_fullscreen = False
            use_window_decorations = False
            use_window = "maximized"
            if check_setting("gnome_extensions") != "0":
                handle_gnome_extensions()
            cursor_position = fs_width - 1, fs_height - 1
        # use_top_clock = False
        # use_top_logo = False
        # app.settings["fs-uae:fullscreen-mode::default"] = "window"

    if windows:
        pass
    elif macosx:
        use_fullscreen_window = True
        app.settings["fs-uae:fullscreen-mode::default"] = "window"
    else:
        # app.settings["fs-uae:fullscreen-mode::default"] = "window"
        pass

    if check_setting("fullscreen"):
        use_fullscreen = check_setting("fullscreen") == "1"

    if "--fullscreen-mode=fullscreen" in sys.argv:
        use_fullscreen_window = False
    elif "--fullscreen-mode=window" in sys.argv:
        use_fullscreen_window = True

    if "--maximize" in sys.argv:
        use_window = "maximized"
        use_fullscreen = False

    if "--no-window-decorations" in sys.argv:
        use_window_decorations = False

    app.settings["game-center:fullscreen"] = \
        "1" if use_fullscreen else "0"
    if use_fullscreen_window:
        app.settings["game-center:fullscreen-mode"] = "window"
    else:
        app.settings["game-center:fullscreen-mode"] = ""
    app.settings["game-center:window-decorations"] = \
        "1" if use_window_decorations else "0"
    app.settings["game-center:maximize"] = \
        "1" if use_window == "maximized" else "0"
    app.settings["game-center:top-clock"] = "1" if use_top_clock else "0"
    app.settings["game-center:top-logo"] = "1" if use_top_logo else "0"

    monitor = "middle-left"
    for arg in sys.argv:
        if arg.startswith("--monitor="):
            monitor = arg[10:]
            app.settings["monitor"] = monitor
            break
    else:
        if app.settings["monitor"]:
            monitor = app.settings["monitor"]

    if macosx and use_fullscreen and use_fullscreen_window:
        # noinspection PyUnresolvedReferences
        import objc
        # noinspection PyUnresolvedReferences
        from Foundation import NSBundle
        bundle = NSBundle.bundleWithPath_(
            "/System/Library/Frameworks/Carbon.framework")
        objc.loadBundleFunctions(
            bundle, globals(), (("SetSystemUIMode", b"III", ""),))
        # kUIModeAllHidden = 3
        # kUIOptionAutoShowMenuBar = 1 << 0
        # noinspection PyUnresolvedReferences
        SetSystemUIMode(3, 1 << 0)

    from game_center.qtui.qtwindow import QtWindow
    # main_window = QtWindow(timer_callback, 16)
    g_callbacks = Callbacks()
    main_window = QtWindow(g_callbacks, 16)
    g_callbacks.set_window(main_window)

    if use_fullscreen:
        # must move the cursor after the window is created
        if cursor_position is not None:
            QCursor.setPos(cursor_position[0], cursor_position[1])
            # os.environ["FSGS_RETURN_CURSOR_TO"] = "{0},{1}".format(
            #     cursor_position[0], cursor_position[1])

    # main_window.show()
    if use_fullscreen:
        # fs_width += 1
        main_window.resize(fs_width, fs_height)

        desktop = application.qapplication.desktop()
        screens = []
        for i in range(desktop.screenCount()):
            geometry = desktop.screenGeometry(i)
            screens.append([geometry.x(), i, geometry])
        screens.sort()
        if monitor == "left":
            mon = 0
        elif monitor == "middle-right":
            mon = 2
        elif monitor == "right":
            mon = 3
        else:  # middle-left
            mon = 1
        display = round(mon / 3 * (len(screens) - 1))
        geometry = screens[display][2]

        main_window.setGeometry(geometry)

        if use_fullscreen_window:
            print("using fullscreen window")

            # main_window.setWindowFlags(Qt.X11BypassWindowManagerHint)

            # if "--always-on-top" in sys.argv:
            #     print("set always on top")
            #     main_window.setWindowFlags(
            #         main_window.windowFlags() | Qt.WindowStaysOnTopHint)

            main_window.setWindowFlags(
                main_window.windowFlags() | Qt.FramelessWindowHint)
            main_window.show()
            # main_window.activateWindow()
        else:
            main_window.showFullScreen()
        # main_window.windowHandle().setScreen(screen)
    else:
        if not use_window_decorations:
            main_window.setWindowFlags(Qt.FramelessWindowHint)

        if use_window == "maximized":
            main_window.showMaximized()
        else:
            main_window.resize(960, 540)
            main_window.show()

    if cursor_position is not None:
        os.environ["FSGS_RETURN_CURSOR_TO"] = "{0},{1}".format(
            cursor_position[0], cursor_position[1])

    # main_window.setTim
    # main_loop_iteration

    application.run()
    print("application.run returned")

    application.stop()
    ImageLoader.get().stop()

    application.wait()

    print(" --- game_center.glui.main is done ---")
    print(application.name)
    return
