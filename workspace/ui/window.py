import pkg_resources
import fsui
from fsui.qt.window import RealWindow
from .application import Application
from .theme import WorkspaceTheme


TEXT_SPACING = 2


class WindowImages:
    def __init__(self):
        self.nw = fsui.Image("pkg://workspace.ui/data/window-shadow-nw.png")
        self.n = fsui.Image("pkg://workspace.ui/data/window-shadow-n.png")
        self.ne = fsui.Image("pkg://workspace.ui/data/window-shadow-ne.png")
        self.e = fsui.Image("pkg://workspace.ui/data/window-shadow-e.png")
        self.se = fsui.Image("pkg://workspace.ui/data/window-shadow-se.png")
        self.s = fsui.Image("pkg://workspace.ui/data/window-shadow-s.png")
        self.sw = fsui.Image("pkg://workspace.ui/data/window-shadow-sw.png")
        self.w = fsui.Image("pkg://workspace.ui/data/window-shadow-w.png")


class WindowBorder(RealWindow):

    _images = None

    @classmethod
    def images(cls):
        if cls._images is None:
            cls._images = WindowImages()
        return cls._images

    def __init__(self, parent, title, child):
        super().__init__(parent, child, title, border=False)
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

    def paintEvent(self, event):
        # noinspection PyNoneFunctionAssignment
        images = self.images()
        w = self.width()
        h = self.height()
        from fsui.qt import QPainter, QPoint, QRect

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

    # def on_close(self):
    #     self.child.on_window_close()
    #     del self.child


class WindowHeader(fsui.Panel):
    def __init__(
        self,
        parent,
        title="",
        menu=False,
        minimizable=True,
        maximizable=True,
        separator=True,
        closable=True,
        background=None,
    ):
        super().__init__(parent)

        if background is None:
            background = (0xFF, 0xFF, 0xFF)
        background_color = fsui.Color(background)
        if background_color.to_hsl().l >= 0.6:
            self.foreground_color = (0x00, 0x00, 0x00)
        else:
            self.foreground_color = (0xFF, 0xFF, 0xFF)
        self.background_color = background_color
        self.set_background_color(background_color)

        self.set_normal_cursor()

        self.layout = fsui.VerticalLayout()
        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, fill=True)

        self.menu_button = WindowMenuButton(self)
        hor_layout.add(self.menu_button)
        if not menu:
            self.menu_button.hide()
            hor_layout.add_spacer(20 - TEXT_SPACING)

        self.title_panel = WindowTitlePanel(self)
        hor_layout.add(self.title_panel, expand=True)

        self.minimize_button = WindowMinimizeButton(self)
        hor_layout.add(self.minimize_button)
        if not minimizable:
            self.minimize_button.hide()

        self.maximize_button = WindowMaximizeButton(self)
        hor_layout.add(self.maximize_button)
        if not maximizable:
            self.maximize_button.hide()

        self.close_button = WindowCloseButton(self)
        hor_layout.add(self.close_button)
        if not closable:
            self.close_button.hide()

        if separator:
            self.separator = TitleSeparator(self)
            self.layout.add(self.separator, fill=True)

    def height(self):
        return self.layout.get_min_height()


class Window(fsui.Window):
    def __init__(
        self,
        parent,
        title="",
        minimizable=True,
        maximizable=True,
        menu=False,
        border=True,
        header=True,
        below=False,
        closable=True,
        color=None,
    ):
        if isinstance(parent, Application):
            parent.add_window(self)
            parent = None
        super().__init__(
            parent,
            title,
            minimizable=minimizable,
            maximizable=maximizable,
            native=False,
            separator=False,
            menu=menu,
            border=border,
            header=header,
            below=below,
            closable=closable,
            color=color,
        )
        self.__menu = None

    def add(self, child):
        if hasattr(self, "set_layout"):
            self.set_layout(child)
        else:
            self.layout = child

    def menu(self):
        return self.__menu

    def set_menu(self, menu):
        self.__menu = menu


class Window2(fsui.Panel):
    def __init__(self, parent, title="", maximizable=True):
        if isinstance(parent, Application):
            parent.add_window(self)
            # parent = None
        self.__border = WindowBorder(None, title, self)
        super().__init__(self.__border)
        self.set_background_color(fsui.Color(0xF2, 0xF2, 0xF2))

        self.layout = fsui.VerticalLayout()
        self.__title_layout = fsui.HorizontalLayout()
        self.layout.add(self.__title_layout, fill=True)

        self.__menu_button = WindowMenuButton(self)
        self.__title_layout.add(self.__menu_button)

        self.__title_panel = WindowTitlePanel(self)
        self.__title_layout.add(self.__title_panel, expand=True)

        self.__minimize_button = WindowMinimizeButton(self)
        self.__title_layout.add(self.__minimize_button)

        self._maximize_button = WindowMaximizeButton(self)
        self.__title_layout.add(self._maximize_button)
        if not maximizable:
            print("hiding")
            self._maximize_button.hide()

        self.__close_button = WindowCloseButton(self)
        self.__title_layout.add(self.__close_button)

        self.__content_added = False
        self.__menu = None

    def title(self):
        return self.__border.get_title()

    def minimize(self):
        self.__border.minimize()

    def maximized(self):
        return self.__border.is_maximized()

    def set_maximized(self, maximized):
        self.__border.maximize(maximized)

    def close(self):
        self.__border.close()

    def set_layout(self, layout):
        assert self.__content_added is False
        self.layout.add(layout, fill=True, expand=True)
        self.__content_added = True

    def menu(self):
        return self.__menu

    def set_menu(self, menu):
        self.__menu = menu

    def show(self):
        self.__border.show()

    def position(self):
        return self.__border.get_position()

    def set_position(self, position):
        return self.__border.set_position(position)

    def on_window_close(self):
        pass

    # def set_size(self, size):
    #     self.__border.set_size(size)


class WindowTitlePanel(fsui.Panel):
    def __init__(self, parent):
        super().__init__(parent, paintable=True)
        self.set_background_color(parent.background_color)
        self.set_min_width(40)
        self.set_min_height(40)

        # self.font = fsui.Font("Noto Sans", 15)
        # self.text_color = fsui.Color(0x80, 0x80, 0x80)

        self.pressed = False
        self.window_pos = (-1, -1)
        self.mouse_pos = (-1, -1)

    def on_paint(self):
        theme = WorkspaceTheme.instance()
        dc = self.create_dc()
        dc.set_font(theme.title_font)
        # text = self.parent().title()
        text = self.parent()._window().title()
        tw, th = dc.measure_text(text)
        # FIXME: measurements with Noto Sans is a bit off...
        th += 2
        # # print(self.size()[1], th)
        # if theme.title_glow_color is not None:
        #     dc.set_text_color(theme.title_glow_color)
        #     for dx in [-1, 1]:
        #         for dy in [-1, 1]:
        #             dc.draw_text(text, TEXT_SPACING + dx,
        #                          (self.size()[1] - th) // 2 + dy)
        # dc.set_text_color(theme.title_color)
        dc.set_text_color(self.parent().foreground_color)
        dc.draw_text(text, TEXT_SPACING, (self.size()[1] - th) // 2)

    def on_left_dclick(self):
        # self.parent().maximize(not self.parent().maximized())
        # noinspection PyProtectedMember
        self.parent().maximize_button.on_activate()

    def on_left_down(self):
        self.pressed = True
        window = self.parent().parent()
        self.window_pos = window.position()
        self.mouse_pos = fsui.get_mouse_position()

    def on_left_up(self):
        self.pressed = False

    def on_mouse_motion(self):
        if self.pressed:
            mouse_pos = fsui.get_mouse_position()
            window_pos = (
                self.window_pos[0] + mouse_pos[0] - self.mouse_pos[0],
                self.window_pos[1] + mouse_pos[1] - self.mouse_pos[1],
            )
            window = self.parent().parent()
            window.set_position(window_pos)


class WindowButton(fsui.Panel):
    def __init__(self, parent, name):
        super().__init__(parent, paintable=True)
        self.set_background_color(parent.background_color)
        self.set_min_width(40)
        self.set_min_height(40)
        self.hover = False
        self.pressed = False

        if parent.background_color.to_hsl().l >= 0.6:
            # FIXME: static resources / share between instances
            self.image = fsui.Image(
                "pkg://workspace.ui/data/window-{}.png".format(name)
            )
            self.image_hover = fsui.Image(
                "pkg://workspace.ui/data/window-{}-hover.png".format(name)
            )
            self.image_pressed = fsui.Image(
                "pkg://workspace.ui/data/window-{}-pressed.png".format(name)
            )
        else:
            self.image = fsui.Image(
                "pkg://workspace.ui/data/window-{}-dark.png".format(name)
            )
            self.image_hover = fsui.Image(
                "pkg://workspace.ui/data/window-{}-hover.png".format(name)
            )
            self.image_pressed = fsui.Image(
                "pkg://workspace.ui/data/window-{}-pressed.png".format(name)
            )

    def on_paint(self):
        dc = self.create_dc()
        if self.pressed and self.hover:
            image = self.image_pressed
        elif self.hover:
            image = self.image_hover
        else:
            image = self.image
        dc.draw_image(image, 0, 0)

    def on_activate(self):
        pass

    def on_left_down(self):
        self.pressed = True
        # For menu popups
        self.on_mouse_motion()
        self.refresh()

    def on_mouse_enter(self):
        if not self.hover:
            self.hover = True
            self.refresh()

    def on_mouse_leave(self):
        # Mouse leave event is received when a menu is popped up, so we
        # explicitly check for mouse position.
        self.on_mouse_motion()

    def on_mouse_motion(self):
        new_state = self.is_mouse_over()
        if self.hover != new_state:
            self.hover = new_state
            self.refresh()

    def on_left_up(self):
        self.pressed = False
        self.refresh()
        if self.is_mouse_over():
            self.on_activate()

    def on_left_dclick(self):
        self.on_left_down()


class WindowMenuButton(WindowButton):
    def __init__(self, parent):
        super().__init__(parent, "menu")

    def on_left_down(self):
        super().on_left_down()
        menu = self.window.menu()
        if menu is not None:
            print(menu)
            self.popup_menu(menu, (0, self.size()[1]))
            # Compensate for left up event not being received when menu is
            # closed. Also check is mouse is still hovering.
            self.pressed = False
            self.on_mouse_motion()
            self.refresh()


class WindowMinimizeButton(WindowButton):
    def __init__(self, parent):
        super().__init__(parent, "minimize")

    def on_activate(self):
        window = self.parent().parent()
        window.minimize()
        # FIXME: restore button state when window is is restored


class WindowMaximizeButton(WindowButton):
    def __init__(self, parent):
        super().__init__(parent, "maximize")

    def on_activate(self):
        if self.visible():
            window = self.parent().parent()
            print(window.is_maximized())
            window.set_maximized(not window.is_maximized())
            # FIXME: button is not refreshed when window is maximized
            # self.on_mouse_motion()


class WindowCloseButton(WindowButton):
    def __init__(self, parent):
        super().__init__(parent, "close")

    def on_activate(self):
        window = self.parent().parent()
        window.close()


# FIXME: Rename to TopPanel?
class TitlePanel(fsui.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.set_background_color(WorkspaceTheme.instance().title_background)


# FIXME: Rename to TopSeparator?
class TitleSeparator(fsui.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.set_background_color(
            WorkspaceTheme.instance().title_separator_color
        )
        self.set_min_height(2)
        self.set_min_width(100)
