import fsui
from launcher.ui.skin import Skin
from launcher.ui.config.InputGroup import InputGroup


class InputPanel(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)
        self.layout = fsui.VerticalLayout()
        self.input_group = InputGroup(self, refresh_button=True)
        self.layout.add(self.input_group, fill=True)
        self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        self.input_group = InputGroup(self, parallel_ports=True)
        self.layout.add(self.input_group, fill=True)
        self.input_group = InputGroup(self, custom_ports=True)
        self.layout.add(self.input_group, fill=True)
