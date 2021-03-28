import os

from fscore.applicationdata import ApplicationData
from fsui import Color, Panel, Signal, get_window

# FIXME: Maybe, for TitleBarButton in particular, we want to disable the
# feature where you want keep the button pressed while returning to the widget,
# and then release the button to activate. Especially for the close button, we
# might want to require to press and release in place?


class TitleBarButton(Panel):
    activated = Signal()

    def __init__(
        self,
        parent,
        *,
        size,
        image=None,
        icon_name=None,
        fgcolor=None,
        fgcolor_inactive=None,
    ):
        super().__init__(parent)
        self.set_min_size((size))
        self._hovering = False
        self._pressed = False
        self.__refresh_state = None
        self._fgcolor = fgcolor
        self._fgcolor_inactive = fgcolor_inactive

        if image is not None:
            self._image = image
            self._svg = None
        else:
            self._image = None
            self._svg = Svg(
                ApplicationData.stream(f"Icons/{icon_name}.svg").read()
            )

        self.update_background_color()

    def set_fgcolor(self, color):
        self._fgcolor = color
        self.refresh_maybe()

    def set_fgcolor_inactive(self, color):
        self._fgcolor_inactive = color
        self.refresh_maybe()

    def set_size(self, size):
        self.set_min_size(size)

    def refresh_maybe(self):
        refresh_state = (
            self._hovering,
            self._pressed,
            self._fgcolor,
            self._fgcolor_inactive,
        )
        if refresh_state != self.__refresh_state:
            self.refresh()
            self.__refresh_state = refresh_state

    def update_background_color(self):
        if self._pressed and self._hovering:
            # FIXME: Get from theme?
            c = Color(0, 0, 0, 0x33)
        elif self._hovering:
            # FIXME: Get from theme?
            c = Color(0xFF, 0xFF, 0xFF, 0x33)
        else:
            c = None
        self.set_background_color(c)
        self.refresh_maybe()

    def on_activate(self):
        self.activated.emit()

    def on_mouse_enter(self):
        super().on_mouse_enter()
        self._hovering = True
        self.update_background_color()

    def on_mouse_leave(self):
        super().on_mouse_leave()
        self._hovering = False
        self.update_background_color()

    def on_mouse_motion(self):
        # Only getting mouse motion when mouse is pressed?
        # Well, that's OK...
        super().on_mouse_motion()
        # hovering = is_mouse_within_widget(self)
        hovering = self.is_under_mouse()
        if hovering != self._hovering:
            self._hovering = hovering
            self.update_background_color()

    def on_left_down(self):
        # FIXME: Capture mouse
        # Actually, mouse tracking is default on left down it seems
        super().on_left_down()
        self._pressed = True
        self.update_background_color()

    def on_left_up(self):
        super().on_left_up()
        self._pressed = False
        self.update_background_color()
        # if is_mouse_within_widget(self):
        if self.is_under_mouse():
            self.on_activate()

    def on_paint(self):
        dc = self.create_dc()
        w, h = self.size()
        if get_window(self).window_focus():
            color = self._fgcolor
            cacheslot = 0
        else:
            color = self._fgcolor_inactive
            cacheslot = 1
        if self._image:
            x = (w - self._image.width()) // 2
            y = (h - self._image.width()) // 2
            dc.draw_image(self._image, x, y)
        else:
            self._svg.draw_to_dc(dc, 0, 0, w, h, color, cacheslot)

    def set_image(self, image):
        self._image = image
        self.refresh()


class Svg:
    def __init__(self, data, cacheslots=2):
        self._data = data
        self._cache = [[None, None] for _ in range(cacheslots)]

    def draw_to_dc(self, dc, x, y, w, h, color, cacheslot):
        if (
            self._cache[cacheslot][0] is None
            or color != self._cache[cacheslot][1]
        ):
            from fsui.qt import QSvgRenderer

            data = self._data.replace(
                b"#000000", color.to_hex().encode("ASCII")
            )
            self._cache[cacheslot][0] = QSvgRenderer(data)
            self._cache[cacheslot][1] = color
        self._cache[cacheslot][0].render(dc.qpainter)
