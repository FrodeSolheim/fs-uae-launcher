from enum import Enum

from typing_extensions import Literal

import fsui
from fsui.qt.icon import Icon
from fswidgets.panel import Panel
from fswidgets.widget import Widget


class IconPosition(Enum):
    LEFT = 0
    RIGHT = 1


class IconHeader(Panel):
    # Legacy names
    ICON_LEFT = IconPosition.LEFT
    ICON_RIGHT = IconPosition.RIGHT

    def __init__(
        self,
        parent: Widget,
        icon: fsui.Icon,
        title: str,
        subtitle: str = "",
        icon_position: IconPosition = IconPosition.LEFT,
    ) -> None:
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
        if icon_position == IconPosition.RIGHT:
            self.layout.add_spacer(20)
            self.layout.add(self.image_view)


class NewIconHeader(Panel):
    # Legacy names
    ICON_LEFT = IconPosition.LEFT
    ICON_RIGHT = IconPosition.RIGHT

    def __init__(
        self,
        parent: Widget,
        icon: Icon,
        title: str,
        subtitle: str = "",
        icon_position: IconPosition = IconPosition.RIGHT,
    ) -> None:
        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()

        image = icon.image(48)
        self.image_view = fsui.ImageView(self, image)
        if icon_position == IconPosition.LEFT:
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
        if icon_position == IconPosition.RIGHT:
            self.layout.add_spacer(20)
            self.layout.add(self.image_view)
