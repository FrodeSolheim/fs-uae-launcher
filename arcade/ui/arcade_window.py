import sys
import time
import weakref

import fsui
from arcade.callbacks import Callbacks
from arcade.glui.imageloader import ImageLoader
from arcade.glui.input import InputHandler
from arcade.ui.event import Event
from arcade.ui.gl_widget import GLWidget
from fsbc.settings import Settings
from fsbc.system import macosx
from fsui.qt import init_qt, Qt, QWidget, QKeyEvent

CURSOR_SHOW_DURATION = 5.0


def check_argument(name, options=None):
    name = name.replace("_", "-")
    if options is not None:
        for option in options:
            if "--" + name + "=" + option in sys.argv:
                return option
    if "--" + name in sys.argv:
        return "1"
    if "--" + name + "=1" in sys.argv:
        return "1"
    if "--no-" + name in sys.argv:
        return "0"
    if "--" + name + "=0" in sys.argv:
        return "0"
    return ""


def fullscreen():
    # If we have explicitly used --window as arguments, do
    # not enable fullscreen regardless of settings.
    if check_argument("window", ["maximize"]) in ["1", "maximize"]:
        return False
    # if check_argument("maximize") == "1":
    #     return False
    value = check_argument("fullscreen")
    if not value:
        value = Settings.instance().get("arcade_fullscreen")
    return value != "0"


def maximized():
    # if check_argument("fullscreen") == "1":
    #     return False
    # if check_argument("window") == "1":
    #     return False
    # value = check_argument("window") == "maximize"
    value = check_argument("window", ["maximize"]) == "maximize"
    if value:
        return True
    else:
        value = Settings.instance().get("arcade_maximized")
        return value == "1"


def monitor():
    value = check_argument("monitor")
    if not value:
        value = Settings.instance().get("monitor")
    if not value:
        value = "middle-left"
    return value


def decorations():
    return not maximized()


def screen_geometry():
    q_app = init_qt()
    desktop = q_app.desktop()
    screens = []
    for i in range(desktop.screenCount()):
        geom = desktop.screenGeometry(i)
        screens.append([geom.x(), i, geom])
    screens.sort()
    if monitor() == "left":
        mon = 0
    elif monitor() == "middle-right":
        mon = 2
    elif monitor() == "right":
        mon = 3
    else:  # middle-left
        mon = 1
    display = round(mon / 3 * (len(screens) - 1))
    geom = screens[display][2]
    return geom.x(), geom.y(), geom.width(), geom.height()

    # main_window.setGeometry(geometry)


class ArcadeWindow(fsui.Window):
    @classmethod
    def open(cls, parent=None):
        return fsui.open_window_instance(cls, parent)

    def __init__(self, parent=None):
        # if app.name == "fs-uae-arcade":
        title = "FS-UAE Arcade"
        # else:
        #    title = "FS Game Center"

        border = True
        if maximized():
            border = False

        super().__init__(
            parent,
            title,
            separator=False,
            border=border,
            menu=True,
            color=(0x00, 0x00, 0x00),
        )
        self.set_background_color(fsui.Color(0x00, 0x00, 0x00))
        self.layout = fsui.HorizontalLayout()
        self.quit_flag = False
        callbacks = Callbacks()
        callbacks.set_window(self)

        interval = 16
        self.qt_window = QtWindow(callbacks, interval, window=self)
        self.adapter = fsui.Adapter(self, self.qt_window)
        self.adapter.set_min_size((960, 540))
        self.layout.add(self.adapter, expand=True, fill=True)

        # self.set_size((960, 540))
        # qt_window.setFocus()
        self.adapter.focus()
        self.shown.connect(self.on_show)
        self.closed.connect(self.on_close)

    def on_show(self):
        self.qt_window.create_gl_window()

    def show_auto(self):
        if fullscreen():
            geometry = screen_geometry()
            self.set_fullscreen(True, geometry)
            Settings.instance().set("__cursor_x", geometry[2])
            Settings.instance().set("__cursor_y", geometry[3])
        elif maximized():
            x, y, w, h = screen_geometry()
            self.set_maximized(True, (x, y, 960, 540))
        else:
            super().show()

    def quit(self):
        self.quit_flag = True
        self.qt_window.quit_flag = True
        # self.window().close()

    def on_close(self):
        # self.qt_window.killTimer(self.qt_window.timer_id)

        # FIXME: In order to clean up resources in the GL thread, we want
        # want to intercept the close event, and close by telling glui to
        # quit, so proper cleanup can be performed there.
        # It may not be a problem though, if the Qt OpenGL context simply
        # releases all resources.
        pass

        ImageLoader.get().stop()


# noinspection PyPep8Naming
class QtWindow(QWidget):
    def __init__(self, callbacks, interval, window):
        super().__init__()
        set_black_background(self)
        self.gl_widget = None
        self.timer_id = None
        self.callbacks = callbacks
        self.interval = interval
        self.quit_flag = False
        self.first_time = None
        # self.setCursor(Qt.BlankCursor)
        self._window = weakref.ref(window)
        self.set_blank_cursor()
        self.show_cursor_until = None
        self.setMouseTracking(True)
        # self.window_created_at = time.time()
        self.first_motion_event = True

    def set_blank_cursor(self, blank=True):
        if blank:
            cursor = Qt.BlankCursor
        else:
            cursor = Qt.ArrowCursor
        self.setCursor(cursor)
        if self.gl_widget is not None:
            self.gl_widget.setCursor(cursor)
        if blank:
            # Fool app to think mouse has moved to neutral position,
            # in order to "de-focus" focused item.
            InputHandler.add_event(
                Event.create_fake_mouse_event(
                    "mouse-motion", 960, 540, (self.width(), self.height())
                )
            )

    def window(self) -> ArcadeWindow:
        # return self.parent().window()
        return self._window()

    def create_gl_window(self):
        self.timer_id = self.startTimer(self.interval)

    def create_gl_window_2(self):
        if self.gl_widget is not None:
            return True
        # Delaying creating of the GLWidget solves some initial sizing
        # issues when maximizing / setting fullscreen on Linux at least.
        # EDIT: The problem may no longer exist, but it is fine to delay
        # anyway so the black screen has time to show before the main thread
        # will block a short while (while resources are loaded).
        if time.time() - self.first_time > 0.5:
            self.gl_widget = GLWidget(self, self.callbacks)
            self.gl_widget.setMouseTracking(True)
            # if "--show-cursor" not in sys.argv:
            # self.gl_widget.setCursor(Qt.BlankCursor)
            self.set_blank_cursor()
            self.gl_widget.setGeometry(
                0, 0, self.size().width(), self.size().height()
            )
            self.gl_widget.show()
        return False

    def restore_window_if_necessary(self):
        pass

    def resizeEvent(self, event):
        size = event.size()
        print("QtWindow.resizeEvent size =", (size.width(), size.height()))
        # if (size.width(), size.height()) == (100, 30):
        # traceback.print_stack()
        if self.gl_widget is not None:
            self.gl_widget.setGeometry(0, 0, size.width(), size.height())

    def timerEvent(self, event):
        if self.first_time is None:
            self.first_time = time.time()
        if not self.create_gl_window_2():
            return
        self.callbacks.timer()
        if self.quit_flag:
            self.killTimer(self.timer_id)
            self.window().close()
            return
        if self.callbacks.active():
            self.gl_widget.updateGL()
        if self.show_cursor_until is not None:
            if self.show_cursor_until < time.time():
                print("hide cursor again")
                self.set_blank_cursor()
                self.show_cursor_until = None

    def ensure_cursor_visible(self):
        if self.show_cursor_until is None:
            print("show cursor until", time.time() + CURSOR_SHOW_DURATION)
            self.set_blank_cursor(False)
        self.show_cursor_until = time.time() + CURSOR_SHOW_DURATION

    def mouseMoveEvent(self, event):
        if self.first_motion_event:
            # Ignore initial motion event, so the cursor is not visible
            # at startup.
            self.first_motion_event = False
            return
        InputHandler.add_event(
            Event.create_mouse_event(event, (self.width(), self.height()))
        )
        self.ensure_cursor_visible()

    def mousePressEvent(self, event):
        if self.show_cursor_until is None:
            # Ignore clicks when cursor is hidden
            return
        InputHandler.add_event(
            Event.create_mouse_event(event, (self.width(), self.height()))
        )
        self.ensure_cursor_visible()

    def mouseReleaseEvent(self, event):
        if self.show_cursor_until is None:
            # Ignore clicks when cursor is hidden
            return
        InputHandler.add_event(
            Event.create_mouse_event(event, (self.width(), self.height()))
        )
        self.ensure_cursor_visible()

    def keyPressEvent(self, event):
        def modifier():
            if macosx:
                # This should correspond to the Cmd key(s) on OS X
                return int(event.modifiers()) & Qt.ControlModifier
            else:
                return int(event.modifiers()) & Qt.AltModifier

        assert isinstance(event, QKeyEvent)
        # print(event.isAutoRepeat(), event.type())
        if event.isAutoRepeat():
            return
        if modifier():
            if event.key() == Qt.Key.Key_Return:
                self.window().set_fullscreen(not self.window().is_fullscreen())
                return
            if event.key() == Qt.Key.Key_Q:
                self.window().close()
                return

        InputHandler.add_event(Event.create_key_event(event))
        text = event.text()
        if text and text in TEXT_WHITE_LIST:
            # We don't want special characters such as return, backspace
            # and escape (etc) to be sent as text events. For now, we use
            # a simple white list.
            InputHandler.add_event({"type": "text", "text": event.text()})

    def keyReleaseEvent(self, event):
        assert isinstance(event, QKeyEvent)
        # print(QKeyEvent, event.isAutoRepeat(), event.type())
        if event.isAutoRepeat():
            return
        InputHandler.add_event(Event.create_key_event(event))


TEXT_WHITE_LIST = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,- "
)


def set_black_background(widget):
    palette = widget.palette()
    # FIXME
    palette.setColor(widget.backgroundRole(), Qt.blue)
    widget.setPalette(palette)
    widget.setAutoFillBackground(True)
    widget.setStyleSheet("background-color: black;")
