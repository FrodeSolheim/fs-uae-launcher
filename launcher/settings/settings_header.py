import fsui
from fsbc.util import unused
from fsui.extra.iconheader import IconPosition
from fsui.qt.icon import Icon
from fswidgets.panel import Panel
from fswidgets.widget import Widget
from launcher.ui.skin import Skin


class SettingsHeader(Panel):
    ICON_LEFT = IconPosition.LEFT
    ICON_RIGHT = IconPosition.RIGHT

    def __init__(
        self,
        parent: Widget,
        icon: Icon,
        title: str,
        subtitle: str = "",
        icon_position: IconPosition = ICON_RIGHT,
    ):
        unused(subtitle)
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
        if Skin.fws() or True:
            font = fsui.Font("Roboto", 26)
            self.title_label.set_font(font)
            self.layout.add(
                self.title_label, expand=True, fill=False, valign=0.0
            )
        else:
            font = self.title_label.get_font()
            font.increase_size(3)
            self.title_label.set_font(font)
            self.layout.add(
                self.title_label, expand=True, fill=False, valign=0.5
            )

        if icon_position == self.ICON_RIGHT:
            self.layout.add_spacer(20)
            self.layout.add(self.image_view)
