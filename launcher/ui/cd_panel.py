import fsui
from launcher.option import Option
from launcher.ui.config.configpanel import ConfigPanel
from .FloppiesGroup import FloppiesGroup
from .MediaListGroup import MediaListGroup
from .skin import Skin


class CDPanel(ConfigPanel):

    def __init__(self, parent):
        super().__init__(parent)
        Skin.set_background_color(self)
        self.layout = fsui.VerticalLayout()
        self.drives_group = FloppiesGroup(self, 1, cd_mode=True)
        self.layout.add(self.drives_group, fill=True)
        self.layout.add_spacer(10)
        self.add_option(Option.CDROM_DRIVE_0_DELAY)
        self.layout.add_spacer(10)
        self.media_list_group = MediaListGroup(self, cd_mode=True)
        self.layout.add(self.media_list_group, expand=True, fill=True)
