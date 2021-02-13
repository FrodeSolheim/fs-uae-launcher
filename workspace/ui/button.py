import fsui

from .canvas import Canvas
from .painter import Painter


class Button(fsui.Button):
    pass


class CustomButton(Canvas):

    activated = fsui.Signal

    def __init__(self, parent):
        super().__init__(parent)

        self.hover = False
        self.pressed = False

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
        new_state = self.is_under_mouse()
        if self.hover != new_state:
            self.hover = new_state
            self.refresh()

    def on_left_up(self):
        self.pressed = False
        self.refresh()
        if self.is_under_mouse():
            self.on_activate()

    def on_left_dclick(self):
        self.on_left_down()


class FlatButton(CustomButton):
    def __init__(self, parent):
        super().__init__(parent)
        # self.set_background_color(fsui.Color(0xff, 0xff, 0xff))
        self.set_min_width(40)
        self.set_min_height(34)
        self.border_colors = [
            fsui.Color(0xBC, 0xBC, 0xBC),
            fsui.Color(0xAD, 0xAD, 0xAD),
            fsui.Color(0x8C, 0x8C, 0x8C),
        ]
        self.fill_colors = [
            fsui.Color(0xFF, 0xFF, 0xFF),
            fsui.Color(0xE6, 0xE6, 0xE6),
            fsui.Color(0xD4, 0xD4, 0xD4),
        ]

    def on_paint(self):
        p = Painter(self)
        size = self.get_size()
        if self.hover and self.pressed:
            border_color = self.border_colors[2]
            fill_color = self.fill_colors[2]
        elif self.hover:
            border_color = self.border_colors[1]
            fill_color = self.fill_colors[1]
        else:
            border_color = self.border_colors[0]
            fill_color = self.fill_colors[0]
        # p.draw_rectangle(0, 0, size[0], size[1], border_color)
        # p.draw_rectangle(1, 1, size[0] - 2, size[1] - 2, fill_color)
        p.rounded_rectangle(
            0,
            0,
            size[0],
            size[1],
            fill_color,
            6,
            border_color=border_color,
            border_width=1.0,
        )
