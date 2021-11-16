from typing import Optional

from fsui import Color, Panel, get_mouse_position, get_theme
from fsui.context import get_window
from fswidgets.parentstack import ParentStack
from fswidgets.widget import Widget


class WindowResizeHandle(Panel):
    def __init__(self, parent: Optional[Widget] = None):
        parent = parent or ParentStack.top()
        super().__init__(parent)
        # parent.resized.connect(self.__parent_resized)
        self.getWindow().resized.connect(self.__parent_resized)
        self.setSize((16, 16))
        # self.set_background_color(Color(0x999999))
        # self.set_background_color(Color(0xFF0000))
        # self.set_background_color(Color(0xAEAEAE))

        self.start_position = None
        self.start_size = (0, 0)
        self.minimum_window_size = (0, 0)
        self.set_resize_cursor()

        self.color1 = Color(0x666666)
        self.color2 = Color(0xD4D4D4)
        self.bgcolor = get_theme(self).window_bgcolor()
        self.set_background_color(self.bgcolor)

    def on_left_down(self):
        window = get_window(self)
        self.start_position = get_mouse_position()
        if hasattr(window, "layout"):
            self.minimum_window_size = window.layout.get_min_size()
        else:
            print("Fake minimum size")
            self.minimum_window_size = (200, 200)
        self.start_size = window.size()

    def on_left_up(self):
        self.start_position = None

    def on_mouse_motion(self):
        if self.start_position is not None:
            if self.start_size is not None:
                pass
            position = get_mouse_position()
            dx = position[0] - self.start_position[0]
            dy = position[1] - self.start_position[1]
            w = max(self.minimum_window_size[0], self.start_size[0] + dx)
            h = max(self.minimum_window_size[1], self.start_size[1] + dy)
            get_window(self).set_size((w, h))

    def on_paint(self):
        dc = self.create_dc()
        dc.clear()
        w, h = self.size()

        dc.setAntialiasing(False)

        for i in range(16):
            s = i % 3
            if s == 0:
                dc.draw_line(0, h + i - 1, w, i - 1, self.color1)
            elif s == 1:
                dc.draw_line(0, h + i - 1, w, i - 1, self.color2)
            else:
                pass

        dc.draw_line(0, h - 1, w, h - 1, self.bgcolor)
        dc.draw_line(w - 1, 0, w - 1, h, self.bgcolor)

    def __parent_resized(self):
        width, height = get_window(self).size()
        self.set_position(width - 16, height - 16)
