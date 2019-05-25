from fsbc.util import unused
import fsui
import fsbc.system
from .Constants import Constants
from .skin import Skin


class TabPanel(fsui.Panel):
    def __init__(self, parent, spacing=10):
        unused(spacing)
        fsui.Panel.__init__(self, parent, paintable=True)
        Skin.set_background_color(self)
        self.layout = fsui.HorizontalLayout()
        # self.layout.add_spacer(spacing)
        # self.layout.padding_left = 10
        # self.layout.padding_right = 10

        # self.set_background_color((0xdd, 0xdd, 0xdd))
        self.set_min_height(Constants.TAB_HEIGHT)

    def select_tab(self, index):
        counter = 0
        for child in self.layout.children:
            child = child.element
            if hasattr(child, "type"):
                if child.type == child.TYPE_TAB:
                    if counter == index:
                        child.select()
                    counter += 1

    def set_selected_tab(self, tab):
        for child in self.layout.children:
            child = child.element
            if hasattr(child, "type"):
                if child.type == child.TYPE_TAB:
                    if child == tab:
                        child.state = child.STATE_SELECTED
                        child.refresh()
                    elif child.state == child.STATE_SELECTED:
                        if child.group_id == tab.group_id:
                            child.state = child.STATE_NORMAL
                            child.refresh()

    def add(self, button, expand=False):
        self.layout.add(button, expand=expand)

    def add_spacer(self, spacer=0, expand=False):
        self.layout.add_spacer(spacer, 0, expand=expand)

    def on_paint(self):
        dc = self.create_dc()
        self.draw_background(self, dc)
        # self.draw_border(self, dc)

    @classmethod
    def draw_border(cls, widget, dc):
        size = widget.size()

        line_color_1 = Skin.get_background_color()
        if Skin.fws() or Skin.windows_10():
            from workspace.ui.theme import WorkspaceTheme

            theme = WorkspaceTheme.instance()
            line_color_1 = theme.title_separator_color
            line_color_2 = line_color_1
        elif line_color_1 is not None:
            line_color_1 = line_color_1.mix(fsui.Color(0xFF, 0xFF, 0xFF))
            line_color_2 = line_color_1
        else:
            line_color_1 = fsui.Color(0xFF, 0xFF, 0xFF, 0xA0)
            line_color_2 = line_color_1

        # line_color_1 = fsui.Color(0xff, 0x00, 0x00, 0xff)
        # line_color_2 = fsui.Color(0x00, 0xff, 0x00, 0xff)

        dc.draw_line(0, size[1] - 2, size[0], size[1] - 2, line_color_1)
        dc.draw_line(0, size[1] - 1, size[0], size[1] - 1, line_color_2)

    @classmethod
    def draw_background(
        cls, widget, dc, selected=False, hover=False, button_style=True
    ):
        unused(button_style)
        if selected:
            cls.draw_selected_tab(widget, dc)
        else:
            cls.draw_border(widget, dc)

        size = widget.size()
        x = 0
        y = 0
        w = size[0]
        h = size[1] - 2

        if Skin.fws() or Skin.windows_10():
            from workspace.ui.theme import WorkspaceTheme

            theme = WorkspaceTheme.instance()
            white = fsui.Color(0xFF, 0xFF, 0xFF)
            if selected:
                bg_color = theme.window_background
                bd_color = theme.title_separator_color
            elif hover:
                bg_color = theme.window_background.copy().mix(
                    theme.title_background
                )
                bd_color = theme.title_separator_color.copy().mix(
                    theme.title_background
                )
            else:
                bg_color = theme.title_background
                bd_color = theme.title_background

            # dc.draw_rectangle(0, 0, w, h, bd_color)
            if selected or hover:
                dc.draw_vertical_gradient(0, 0, 2, size[1], white, bd_color)
                dc.draw_vertical_gradient(
                    size[0] - 2,
                    0,
                    2,
                    size[1],
                    theme.title_background,
                    bd_color,
                )
                # dc.draw_rectangle(2, 2, w - 4, h - 2, bg_color)
                dc.draw_vertical_gradient(
                    2,
                    0,
                    size[0] - 4,
                    size[1],
                    theme.title_background,
                    bg_color,
                )
                if hover and not selected:
                    dc.draw_rectangle(
                        0, size[1] - 2, size[0], 2, theme.title_separator_color
                    )
            else:
                dc.draw_rectangle(0, 0, w, h, bd_color)
            return

        if fsbc.system.macosx:
            # dc.draw_line(0, 0, w, 0, fsui.Color(198, 198, 198))
            # dc.draw_line(0, 0, w, 0, fsui.Color(188, 188, 188))
            dc.draw_line(0, 0, w, 0, fsui.Color(248, 248, 248))
            y += 1
            h -= 1

        if selected:
            x += 2
            w -= 4
            h += 2

        # if button_style and hover:
        #     x += 6
        #     y += 6
        #     w -= 12
        #     h -= 12

        color_1 = Skin.get_background_color()
        if fsbc.system.macosx and False:
            if selected:
                color_2 = color_1
                color_1 = fsui.Color(0xA7, 0xA7, 0xA7)
            elif hover:
                color_1 = fsui.Color(0xA7, 0xA7, 0xA7)
                color_2 = fsui.Color(0xEF, 0xEF, 0xEF)
            else:
                color_1 = fsui.Color(0xA7, 0xA7, 0xA7)
                color_2 = fsui.Color(0xC0, 0xC0, 0xC0)
        elif color_1 is not None:
            if selected:
                color_2 = color_1
            elif hover:
                color_2 = color_1.copy().lighten()
            else:
                color_2 = color_1.copy().darken(0.08)
        else:
            if selected:
                return
                # color_1 = fsui.Color(0x00, 0x00, 0x00, 0x00)
                # color_2 = color_1
            elif hover:
                color_1 = fsui.Color(0xFF, 0xFF, 0xFF, 0x00)
                color_2 = fsui.Color(0xFF, 0xFF, 0xFF, 0x40)
            else:
                color_1 = fsui.Color(0x00, 0x00, 0x00, 0x00)
                color_2 = fsui.Color(0x00, 0x00, 0x00, 0x20)
        dc.draw_vertical_gradient(x, y, w, h, color_1, color_2)

        if fsbc.system.macosx and False and not selected and not hover:
            dc.draw_line(
                x, y + h - 1, x + w, y + h - 1, fsui.Color(0xA8, 0xA8, 0xA8)
            )

    @classmethod
    def draw_selected_tab(cls, widget, dc):
        line_color_1 = Skin.get_background_color()
        if Skin.fws() or Skin.windows_10():
            from workspace.ui.theme import WorkspaceTheme

            theme = WorkspaceTheme.instance()
            line_color_1 = theme.title_separator_color
            line_color_2 = line_color_1
        elif fsbc.system.macosx and False:
            line_color_1 = fsui.Color(0xA7, 0xA7, 0xA7)
            line_color_2 = Skin.get_background_color().mix(
                fsui.Color(0xFF, 0xFF, 0xFF)
            )
        elif line_color_1 is not None:
            line_color_2 = Skin.get_background_color().mix(
                fsui.Color(0xFF, 0xFF, 0xFF)
            )
        else:
            line_color_1 = fsui.Color(0xFF, 0xFF, 0xFF, 0x00)
            line_color_2 = fsui.Color(0xFF, 0xFF, 0xFF, 0xA0)

        size = widget.size()
        dc.draw_vertical_gradient(0, 0, 2, size[1], line_color_1, line_color_2)
        dc.draw_vertical_gradient(
            size[0] - 2, 0, 2, size[1], line_color_1, line_color_2
        )
