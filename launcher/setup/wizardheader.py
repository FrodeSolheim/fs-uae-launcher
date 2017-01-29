import fsui
from fsbc.util import unused
from launcher.ui.skin import Skin


class WizardHeader(fsui.Panel):

    def __init__(self, parent, icon, title):
        super().__init__(parent)
        self.layout = fsui.HorizontalLayout()
        # FIXME: From Theme
        self.set_background_color(fsui.Color(0xff, 0xff, 0xff))

        self.title_label = fsui.HeadingLabel(self, title)
        font = fsui.Font("Roboto", 26)
        self.title_label.set_font(font)
        self.layout.add(
            self.title_label, expand=True, fill=True, margin=20)
        self.layout.add_spacer(20)
        self.layout.add(fsui.ImageView(self, icon.image(48)), margin_right=20)
