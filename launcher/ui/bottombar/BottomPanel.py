import fsui

from ..skin import Skin

BORDER_COLOR = (0xE5, 0xE5, 0xE5, 0xFF)


class BottomPanel(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent, paintable=True)
        Skin.set_background_color(self)

        self.color_2 = Skin.get_background_color()
        if self.color_2 is not None:
            self.color_1 = self.color_2.copy().darken(0.08)
            if fsui.System.macosx:
                self.line_color_1 = self.color_2.copy().mix(
                    fsui.Color(0x00, 0x00, 0x00), 0.25
                )
                self.line_color_2 = self.color_2.copy().mix(
                    fsui.Color(0xFF, 0xFF, 0xFF), 0.25
                )
            else:
                self.line_color_1 = self.color_2.copy().mix(
                    fsui.Color(0xFF, 0xFF, 0xFF)
                )
                self.line_color_2 = self.line_color_1
        else:
            # self.color_1 = fsui.Color(0x00, 0x00, 0x00, 0x20)
            # self.color_2 = fsui.Color(0x00, 0x00, 0x00, 0x00)
            self.color_1 = fsui.Color(0xFF, 0xFF, 0xFF, 0x60)
            self.color_2 = fsui.Color(0xFF, 0xFF, 0xFF, 0x00)
            self.line_color_1 = fsui.Color(0xFF, 0xFF, 0xFF, 0xA0)
            self.line_color_2 = self.line_color_1

        self.border_color = fsui.Color(*BORDER_COLOR)
        self.white_color = fsui.Color(0xFF, 0xFF, 0xFF, 0xFF)

    def on_paint(self):
        dc = self.create_dc()
        self.draw_background(dc)

    def draw_background(self, dc):
        size = self.size()
        if Skin.fws():
            dc.draw_rectangle(0, 0, size[0], 2, self.border_color)
            dc.draw_rectangle(0, 2, size[0], size[1] - 2, self.white_color)
            return
        dc.draw_line(0, 0, size[0], 0, self.line_color_1)
        dc.draw_line(0, 1, size[0], 1, self.line_color_2)
        dc.draw_vertical_gradient(
            0, 2, size[0], size[1] - 2, self.color_1, self.color_2
        )
