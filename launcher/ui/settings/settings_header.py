import fsui
from launcher.ui.Skin import Skin


class SettingsHeader(fsui.Group):

    ICON_LEFT = 0
    ICON_RIGHT = 1

    def __init__(self, parent, icon, title, subtitle="",
                 icon_position=ICON_RIGHT):
        fsui.Group.__init__(self, parent)
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
        if Skin.fws():
            font = fsui.Font("Roboto", 26)
            self.title_label.set_font(font)
            self.layout.add(
                self.title_label, expand=True, fill=False, valign=0.0)
        else:
            font = self.title_label.get_font()
            font.increase_size(3)
            self.title_label.set_font(font)
            self.layout.add(
                self.title_label, expand=True, fill=False, valign=0.5)

        if icon_position == self.ICON_RIGHT:
            self.layout.add_spacer(20)
            self.layout.add(self.image_view)
