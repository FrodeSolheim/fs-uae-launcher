import fsui
from launcher.ui.config.configpanel import ConfigPanel
from launcher.ui.config.InputGroup import InputGroup
from launcher.ui.config.modelgroup import ModelGroup
from launcher.ui.removablemediagroup import RemovableMediaGroup
from launcher.ui.skin import Skin


class MainPanel(ConfigPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # Skin.set_background_color(self)

        # self.layout = fsui.VerticalLayout()
        self.model_group = ModelGroup(self)
        self.layout.add(self.model_group, fill=True)
        self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)

        self.removable_media_group = RemovableMediaGroup(self, 2, main=True)
        self.layout.add(self.removable_media_group, fill=True)
        self.layout.add_spacer(10)

        self.input_group = InputGroup(
            self, refresh_button=True, autofire_button=False
        )
        self.layout.add(self.input_group, fill=True)
