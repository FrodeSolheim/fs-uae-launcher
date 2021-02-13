import fsui
from launcher.ui.config.configpanel import ConfigPanel
from launcher.ui.floppiesgroup import FloppiesGroup
from launcher.ui.MediaListGroup import MediaListGroup
from launcher.ui.skin import Skin


class FloppiesPanel(ConfigPanel):
    def __init__(self, parent):
        super().__init__(parent)

        # Skin.set_background_color(self)
        # self.layout = fsui.VerticalLayout()
        self.floppies_group = FloppiesGroup(self, 4)
        self.layout.add(self.floppies_group, fill=True)
        self.media_list_group = MediaListGroup(self, False)
        self.layout.add(self.media_list_group, expand=True, fill=True)

    def on_destroy(self):
        print("InputSelector / FloppiesPanel.on_destroy")
        super().on_destroy()
