from enum import Enum
from typing import cast

from fsui import Color, Panel, Signal, VerticalLayout
from fsui.context import get_theme
from fsui.qt.image import Image
from fswidgets.widget import Widget
from launcher.ui2.launcher2colors import Launcher2Colors
from launcher.ui.skin import Skin


class TabType(Enum):
    TAB = 0
    BUTTON = 1


class TabState(Enum):
    NORMAL = 0
    SELECTED = 1


class TabButton(Panel):
    activated = Signal()

    TYPE_TAB = TabType.TAB
    TYPE_BUTTON = TabType.BUTTON

    STATE_NORMAL = TabState.NORMAL
    STATE_SELECTED = TabState.SELECTED

    def __init__(
        self,
        parent: Widget,
        icon: Image,
        button_type: TabType = TYPE_TAB,
        left_padding: int = 0,
        right_padding: int = 0,
    ) -> None:
        Panel.__init__(self, parent, paintable=True)
        Skin.set_background_color(self)
        self.layout = VerticalLayout()
        # self.set_background_color((0xdd, 0xdd, 0xdd))
        # self.set_min_width(Constants.TAB_WIDTH + left_padding + right_padding)
        # self.set_min_height(Constants.TAB_HEIGHT)
        self.set_min_size((64, 48))
        self.group_id = 0
        self.icon = icon
        self.type = button_type
        self.state = self.STATE_NORMAL
        self.hover = False
        self.left_padding = left_padding
        self.right_padding = right_padding

        self.bgcolor = get_theme(self).window_bgcolor()
        # self.set_background_color(self.bgcolor)

    def select(self) -> None:
        from launcher.ui2.tabpanel import TabPanel

        parentTabPanel = cast(TabPanel, self.getParent())
        parentTabPanel.set_selected_tab(self)
        self.on_select()

    def on_paint(self) -> None:
        size = self.size()
        dc = self.create_dc()
        selected = self.state == self.STATE_SELECTED
        if selected:
            backgroundcolor = Color(Launcher2Colors.CONFIG_PANEL_COLOR)
        elif self.hover:
            backgroundcolor = Color(0xB2B2B2)
        else:
            backgroundcolor = self.bgcolor
        dc.draw_rectangle(0, 0, size[0], size[1], backgroundcolor)
        # TabPanel.draw_background(
        #     self,
        #     dc,
        #     selected=selected,
        #     hover=self.hover,
        #     button_style=(self.type == self.TYPE_BUTTON),
        # )

        # TabPanel.draw_border(self, dc)

        x = (
            self.left_padding
            + (
                size[0]
                - self.left_padding
                - self.right_padding
                - self.icon.size[0]
            )
            // 2
        )
        # subtracting two because of bottom border
        y = (size[1] - 2 - self.icon.size[1]) // 2
        dc.draw_image(self.icon, x, y)

    def check_hover(self) -> None:
        # FIXME: check if mouse is hovering, used for example after having
        # dismissed a popup menu
        self.hover = False
        self.refresh()

    def on_mouse_enter(self) -> None:
        self.hover = True
        self.refresh()

    def on_mouse_leave(self) -> None:
        self.hover = False
        self.refresh()

    def on_select(self) -> None:
        pass

    def on_left_down(self) -> None:
        if self.type == self.TYPE_TAB:
            self.select()

    def on_left_up(self) -> None:
        if self.type == self.TYPE_BUTTON:
            # FIXME: hack to avoid sticky hover due to mouse leave not
            # being sent if on_activate opens modal dialog
            # self.hover = False
            # self.refresh()
            self.on_activate()

    def on_activate(self) -> None:
        self.activated.emit()
