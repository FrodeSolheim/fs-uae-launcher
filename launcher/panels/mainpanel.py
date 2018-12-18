import fsui
from launcher.ui.removablemediagroup import RemovableMediaGroup
from launcher.ui.skin import Skin
from launcher.ui.config.InputGroup import InputGroup
from launcher.ui.config.modelgroup import ModelGroup


class MainPanel(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)
        self.layout = fsui.VerticalLayout()
        self.model_group = ModelGroup(self)
        self.layout.add(self.model_group, fill=True)
        self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        self.removable_media_group = RemovableMediaGroup(self, 2, main=True)
        self.layout.add(self.removable_media_group, fill=True)
        self.layout.add_spacer(10)
        self.input_group = InputGroup(
            self, refresh_button=True, autofire_button=False)
        self.layout.add(self.input_group, fill=True)
