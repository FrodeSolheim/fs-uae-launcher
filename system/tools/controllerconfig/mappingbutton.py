import logging
from typing import Optional, Tuple

from typing_extensions import Literal

import fsui
from fswidgets.widget import Widget

log = logging.getLogger(__name__)


class MappingButton(fsui.Panel):
    def __init__(
        self,
        parent: Widget,
        position: Tuple[int, int],
        direction: Literal[-1, 1],
        name: str,
    ) -> None:
        super().__init__(parent)

        size = (150, 22)
        self.set_size(size)
        if direction < 0:
            position = (position[0] - size[0], position[1])
        self.set_position(position)

        self.key_name = name
        self.event_name: Optional[str] = None
        self.text = ""
        self.direction = direction

        self.set_hand_cursor()
        # self.set_background_color(fsui.Color(0xFF, 0xFF, 0xFF))
        self.set_background_color(fsui.Color(0xFF, 0xFF, 0xFF, 0x00))

    def on_left_down(self) -> None:
        print("on_left_down")
        # self.get_window().map_event(self.key_name)
        self.getParent().getParent().map_event(self.key_name)
        self.getParent().getParent().getParent().startMapping()

    def on_paint(self) -> None:
        dc = self.create_dc()
        dc.set_font(self.get_font())
        if self.text:
            text = self.text
            dc.set_text_color(fsui.Color(0x00, 0x80, 0x00))
        elif self.event_name:
            text = self.event_name
            dc.set_text_color(fsui.Color(0x80, 0x80, 0x80))
        else:
            text = "click to configure"
            dc.set_text_color(fsui.Color(0xFF, 0x00, 0x00))
        tw, th = dc.measure_text(text)
        y = (self.get_size()[1] - th) / 2
        if self.direction > 0:
            x = 4
        else:
            x = self.get_size()[0] - 4 - tw
        dc.draw_text(text, x, y)
