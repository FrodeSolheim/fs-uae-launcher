import weakref
from fsui import default_window_center, default_window_parent
from fsui.qt import QMainWindow, QObject, QSignal, QWidget, Qt, QDesktopWidget
from fsui.qt import QPainter, QPoint, QRect
from fsui.qt.Color import Color
from fsui.qt.Image import Image


# noinspection PyProtectedMember
from fsui.qt.helpers import QParent

windows = set()
_use_fws = False


class Margins:

    def __init__(self):
        self.top = 0
        self.left = 0
        self.right = 0
        self.bottom = 0

    def set(self, value):
        self.top = value
        self.left = value
        self.right = value
        self.bottom = value


# noinspection PyProtectedMember
class RealWindow(QMainWindow):

    def __init__(self, parent, child, minimizable=True, maximizable=True,
                 border=True):
        super().__init__(parent)
        self.margins = Margins()

        flags = Qt.Window
        if border:
            flags | Qt.CustomizeWindowHint
            flags |= Qt.WindowCloseButtonHint
            flags |= Qt.WindowTitleHint
            if minimizable:
                flags |= Qt.WindowMinimizeButtonHint
            if maximizable:
                flags |= Qt.WindowMaximizeButtonHint
        else:
            flags |= Qt.FramelessWindowHint
            flags |= Qt.NoDropShadowWindowHint
        self.setWindowFlags(flags)

        self._child = weakref.ref(child)
        self.already_closed = False

    def child(self):
        return self._child()

    def resizeEvent(self, event):
        child = self.child()
        size = event.size()
        x = self.margins.left
        y = self.margins.top
        width = size.width() - self.margins.left - self.margins.right
        height = size.height() - self.margins.top - self.margins.bottom
        assert isinstance(child._real_widget, QWidget)
        if child.title_panel is not None:
            title_height = child.title_panel.height()
            # child.title_panel.setGeometry(x, y, width, title_height)
            child.title_panel.set_position_and_size(
                (x, y), (width, title_height))
            y += title_height
            height -= title_height
        child._real_widget.setGeometry(x, y, width, height)

    def set_size(self, size):
        width = size[0] + self.margins.left + self.margins.right
        height = size[1] + self.margins.top + self.margins.bottom
        child = self.child()
        if child.title_panel is not None:
            title_height = child.title_panel.height()
            height += title_height
        self.resize(width, height)

    def position(self):
        return self.pos().x(), self.pos().y()

    def set_position(self, position):
        self.move(position[0], position[1])

    def width(self):
        return super().width() - self.margins.left - self.margins.right

    def height(self):
        height = super().height() - self.margins.top - self.margins.bottom
        if self.child().title_panel is not None:
            height -= 40
        return height

    def closeEvent(self, event):
        # print(str(self) + ".closeEvent")
        event.accept()
        self._on_close()

    def _on_close(self):
        child = self.child()
        print("WindowMixin.cleanup_on_close_event")
        if self.already_closed:
            print("Looks like a duplicate event, ignoring this one")
            return
        print("closed.emit")
        child.closed.emit()
        child.on_close()
        self.already_closed = True

    def is_maximized(self):
        return self.windowState() == Qt.WindowMaximized

    def restore_margins(self):
        self.margins.set(0)

    def set_maximized(self, maximize=True):
        print("set_maximized", maximize)
        if maximize:
            self.margins.set(0)
            self.showMaximized()
        else:
            self.restore_margins()
            self.setWindowState(Qt.WindowNoState)

    def minimize(self):
        self.setWindowState(Qt.WindowMinimized)


# noinspection PyProtectedMember
class RealWidget(QWidget):

    def __init__(self, parent, owner):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self._owner = weakref.ref(owner)
        self._centered_on_initial_show = False

    def owner(self):
        return self._owner()

    def resizeEvent(self, event):
        self.owner().on_resize()

    def showEvent(self, _):
        if not self._centered_on_initial_show:
            if self.parent():
                self.owner().center_on_parent()
            self._centered_on_initial_show = True

        self.owner().set_initial_size_from_layout()
        self.owner().on_resize()


# noinspection PyPep8Naming
class Window(QObject):

    closed = QSignal()

    def __init__(self, parent, title="", border=True, minimizable=True,
                 maximizable=True, separator=True, menu=False,
                 native=None, **kwargs):
        super().__init__()

        if parent is None and len(default_window_parent) > 0:
            parent = default_window_parent[-1]
            print("using default parent", parent)

        # FIXME
        self._window = weakref.ref(self)

        if native is None:
            native = not _use_fws
        if native:
            self._real_window = RealWindow(
                QParent(parent, True), self, minimizable=minimizable,
                maximizable=maximizable)
        else:
            self._real_window = FwsWindow(QParent(parent, True), self)

        self._real_widget = RealWidget(self._real_window, self)

        # Widget.__init__(self, parent)
        # self.init_widget(parent)

        # MixinBase.__init__(self)

        self.set_title(title)

        self.layout = None
        self._size_specified = False
        self.close_listeners = []
        # _windows.add(self)
        self.destroyed.connect(self.__destroyed)

        # self.setAttribute(Qt.WA_DeleteOnClose, True)
        # if not border:
        #     self.setWindowFlags(Qt.FramelessWindowHint |
        #                         Qt.NoDropShadowWindowHint)
        #     # self.setWindowFlags(Qt.FramelessWindowHint)

        self._centered_on_initial_show = False
        if hasattr(self, "accepted"):
            self.accepted.connect(self.__accepted)
        if hasattr(self, "rejected"):
            self.rejected.connect(self.__rejected)

        # Add a keep-alive reference
        print("Adding window reference", self)
        windows.add(self)
        self.closed.connect(self.__closed)

        if not native:
            self.real_window()._window = weakref.ref(self)
            from fws.gui.window import WindowHeader
            self.title_panel = WindowHeader(
                self.real_window(), menu=menu, minimizable=minimizable,
                maximizable=maximizable, separator=separator)
            self.set_background_color(Color(0xf2, 0xf2, 0xf2))
        else:
            self.title_panel = None

    def __closed(self):
        print("Removing window reference", self)
        windows.remove(self)

    def close(self):
        self._real_window.close()

    def real_window(self):
        return self._real_window

    def real_widget(self):
        return self._real_widget

    # DEPRECATED
    def get_container(self):
        return self.real_widget()

    # FIXME: Is this used?
    def center_on_initial_show(self):
        if self._centered_on_initial_show:
            return
        if self.layout and not self._size_specified:
            self.set_size(self.layout.get_min_size())
        self.on_resize()
        self.center_on_parent()
        self._centered_on_initial_show = True

    def __destroyed(self):
        print(str(self) + ".__destroyed")

    def add_close_listener(self, function):
        # self.close_listeners.append(function)
        self.closed.connect(function)

    def top_level(self):
        return self

    def set_icon(self, icon):
        self.real_window().setWindowIcon(icon.qicon())

    def position(self):
        # position = self._real_window.position()
        # return position.x(), position.y()
        return self._real_window.position()

    def set_position(self, position):
        self._real_window.set_position(position)

#    def set_position_and_size(self, position, size):
#        self.widget().setGeometry(position[0], position[1], size[0], size[1])

    def size(self):
        return self.width(), self.height()

    def width(self):
        return self._real_window.width()

    def height(self):
        return self._real_window.height()

    def set_size(self, size):
        self._size_specified = True
        # self.SetClientSize(size)
        # print("FIXME:\n\nDialog.set_size")
        # self.resize(size[0], size[1])
        print("set size", size[0], size[1])
        self._real_window.set_size(size)
        self._real_widget.resize(size[0], size[1])

    def set_initial_size_from_layout(self):
        if self.layout and not self._size_specified:
            self.set_size_from_layout()

    def set_size_from_layout(self):
        self.set_size(self.layout.get_min_size())

    def title(self):
        return self._real_window.windowTitle()

    def set_title(self, title):
        self._real_window.setWindowTitle(title)

    def show(self, maximized=False):
        if maximized:
            self._real_window.showMaximized()
        else:
            self._real_window.show()

    def is_maximized(self):
        # return self._real_window.windowState() == Qt.WindowMaximized
        return self._real_window.is_maximized()

    def set_maximized(self, maximize=True):
        self._real_window.set_maximized(maximize)

    def minimize(self):
        # self.setWindowState(Qt.WindowMinimized)
        return self._real_window.minimize()

    def get_window_center(self):
        position = self.position()
        size = self.size()
        return position[0] + size[0] // 2, position[1] + size[1] // 2

    def center_on_parent(self):
        self.set_initial_size_from_layout()
        real_parent = self.real_window().parent()
        print("center_on_parent real_parent = ", real_parent, default_window_center)
        if real_parent:
            pp = real_parent.x(), real_parent.y()
            ps = real_parent.width(), real_parent.height()
            ss = self.size()
            print(pp, ps, ss)
            self.set_position((pp[0] + (ps[0] - ss[0]) // 2,
                               pp[1] + (ps[1] - ss[1]) // 2))
        elif len(default_window_center) > 0:
            x, y = default_window_center[-1]
            ss = self.size()
            self.set_position((x - ss[0] // 2, y - ss[1] // 2))

    def center_on_screen(self):
        frame_rect = self._real_window.frameGeometry()
        frame_rect.moveCenter(QDesktopWidget().availableGeometry().center())
        self._real_window.move(frame_rect.topLeft())

    def set_background_color(self, color):
        p = self.real_widget().palette()
        p.setColor(self.real_widget().backgroundRole(), color)
        self.real_widget().setPalette(p)

    def is_shown(self):
        return self._real_window.isVisible()

    def raise_and_activate(self):
        self._real_window.raise_()
        self._real_window.activateWindow()

    def on_close(self):
        pass

    def __rejected(self):
        print(str(self) + ".__rejected")
        self.__on_close()

    def __accepted(self):
        print(str(self) + ".__accepted")
        self.__on_close()

    def on_resize(self):
        if self.layout:
            self.layout.set_size(self.get_size())
            self.layout.update()

    # DEPRECATED
    def resize(self, width, height):
        self.set_size((width, height))

    # DEPRECATED
    def get_size(self):
        return self.size()

    # DEPRECATED
    def get_window(self):
        return self.top_level()

    # DEPRECATED
    def get_position(self):
        return self.position()

    # DEPRECATED
    def maximized(self):
        return self.is_maximized()

    # DEPRECATED
    def get_parent(self):
        return None

    # DEPRECATED
    def set_icon_from_path(self, _):
        print("FIXME: Window.set_icon_from_path")

    # DEPRECATED
    def get_title(self):
        return self.title()

    # DEPRECATED
    def maximize(self, maximize=True):
        return self.set_maximized(maximize)


class WindowImages:

    def __init__(self):
        self.nw = Image("pkg://fws.gui/data/window-shadow-nw.png")
        self.n = Image("pkg://fws.gui/data/window-shadow-n.png")
        self.ne = Image("pkg://fws.gui/data/window-shadow-ne.png")
        self.e = Image("pkg://fws.gui/data/window-shadow-e.png")
        self.se = Image("pkg://fws.gui/data/window-shadow-se.png")
        self.s = Image("pkg://fws.gui/data/window-shadow-s.png")
        self.sw = Image("pkg://fws.gui/data/window-shadow-sw.png")
        self.w = Image("pkg://fws.gui/data/window-shadow-w.png")


class FwsWindow(RealWindow):

    def __init__(self, parent, child):
        super().__init__(parent, child, border=False)
        self.restore_margins()
        # self.child = child

        # self.layout = fsui.VerticalLayout(20)
        # self.hori_layout = fsui.HorizontalLayout()
        # self.layout.add(self.hori_layout, fill=True)
        # self.layout.add(child, fill=True, expand=True)

        # self.setWindowFlags(Qt.FramelessWindowHint)
        from fsui.qt import Qt
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def restore_margins(self):
        self.margins.set(20)

    def paintEvent(self, event):
        # noinspection PyNoneFunctionAssignment
        images = self.images()
        size = self.size()
        w = size.width()
        h = size.height()
        painter = QPainter(self)
        painter.drawImage(QPoint(0, 0), images.nw.qimage)
        painter.drawImage(QRect(40, 0, w - 80, 20), images.n.qimage)
        painter.drawImage(QPoint(w - 40, 0), images.ne.qimage)
        painter.drawImage(QRect(w - 20, 40, 20, h - 80), images.e.qimage)
        painter.drawImage(QPoint(w - 40, h - 40), images.se.qimage)
        painter.drawImage(QRect(40, h - 20, w - 80, 20), images.s.qimage)
        painter.drawImage(QPoint(0, h - 40), images.sw.qimage)
        painter.drawImage(QRect(0, 40, 20, h - 80), images.w.qimage)

    def maximize(self, maximized):
        # FIXME: Better to this via event or something
        if maximized:
            self.layout.set_padding(0)
        else:
            self.layout.set_padding(20)
        super().maximize(maximized)

    _images = None

    @classmethod
    def images(cls):
        if cls._images is None:
            cls._images = WindowImages()
        return cls._images

    @classmethod
    def set_default(cls):
        global _use_fws
        try:
            import fws
        except ImportError:
            pass
        else:
            _use_fws = True
