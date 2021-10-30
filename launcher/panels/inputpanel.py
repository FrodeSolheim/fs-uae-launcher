import fsui
from launcher.ui.config.configpanel import ConfigPanel
from launcher.ui.config.InputGroup import InputGroup
from launcher.ui.skin import Skin


class InputPanel(ConfigPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # Skin.set_background_color(self)

        # self.layout = fsui.VerticalLayout()
        self.input_group = InputGroup(self)
        self.layout.add(self.input_group, fill=True)
        self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        self.input_group = InputGroup(self, parallel_ports=True)
        self.layout.add(self.input_group, fill=True)
        self.input_group = InputGroup(self, custom_ports=True)
        self.layout.add(self.input_group, fill=True)
