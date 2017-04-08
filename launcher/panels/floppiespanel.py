import fsui
from launcher.ui.floppiesgroup import FloppiesGroup
from launcher.ui.MediaListGroup import MediaListGroup
from launcher.ui.skin import Skin


class FloppiesPanel(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)
        self.layout = fsui.VerticalLayout()
        self.floppies_group = FloppiesGroup(self, 4)
        self.layout.add(self.floppies_group, fill=True)
        self.media_list_group = MediaListGroup(self, False)
        self.layout.add(self.media_list_group, expand=True, fill=True)
