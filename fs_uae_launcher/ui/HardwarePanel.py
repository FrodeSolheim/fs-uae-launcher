import fsui as fsui
from .config.KickstartGroup import KickstartGroup
from .config.MemoryGroup import MemoryGroup
from .config.ExpansionsGroup import ExpansionsGroup
from .Skin import Skin


class HardwarePanel(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)

        self.kickstart_group = KickstartGroup(self)
        self.memory_group = MemoryGroup(self)
        self.expansions_group = ExpansionsGroup(self)

        self.layout = fsui.VerticalLayout()
        self.layout.add(self.kickstart_group, fill=True)
        self.layout.add_spacer(10)
        self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        self.layout.add(self.memory_group, fill=True)
        self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        self.layout.add(self.expansions_group, fill=True)
