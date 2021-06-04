from typing_extensions import Literal

import fsui
from fswidgets.panel import Panel
from fswidgets.widget import Widget


class IconHeader(Panel):
    ICON_LEFT = 0
    ICON_RIGHT = 1

    def __init__(
        self,
        parent: Widget,
        icon: fsui.Icon,
        title: str,
        subtitle: str = "",
        icon_position: Literal[0, 1] = ICON_LEFT,
    ):
        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()

        image = icon.image(48)
        self.image_view = fsui.ImageView(self, image)
        if icon_position == self.ICON_LEFT:
            self.layout.add(self.image_view)
            self.layout.add_spacer(20)
        vert_layout = fsui.VerticalLayout()
        self.layout.add(vert_layout, expand=True, fill=False, valign=0.5)
        self.title_label = fsui.HeadingLabel(self, title)
        vert_layout.add(self.title_label)
        vert_layout.add_spacer(2)
        self.subtitle_label = fsui.Label(self, subtitle)
        vert_layout.add(self.subtitle_label, fill=True)
        if icon_position == self.ICON_RIGHT:
            self.layout.add_spacer(20)
            self.layout.add(self.image_view)


class NewIconHeader(Panel):
    ICON_LEFT = 0
    ICON_RIGHT = 1

    def __init__(
        self,
        parent: Widget,
        icon,
        title: str,
        subtitle: str = "",
        icon_position: Literal[0, 1] = ICON_RIGHT,
    ):
        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()

        image = icon.image(48)
        self.image_view = fsui.ImageView(self, image)
        if icon_position == self.ICON_LEFT:
            self.layout.add(self.image_view)
            self.layout.add_spacer(20)

        # vert_layout = fsui.VerticalLayout()
        # self.layout.add(
        #     vert_layout, expand=True, fill=False, valign=0.5)
        self.title_label = fsui.HeadingLabel(self, title)
        font = self.title_label.get_font()
        font.increase_size(3)
        self.title_label.set_font(font)

        self.layout.add(self.title_label, expand=True, fill=False, valign=0.5)
        if icon_position == self.ICON_RIGHT:
            self.layout.add_spacer(20)
            self.layout.add(self.image_view)
