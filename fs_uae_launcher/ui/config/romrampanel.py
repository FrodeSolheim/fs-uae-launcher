from fs_uae_launcher.Options import Option
from fs_uae_launcher.ui.config.configpanel import ConfigPanel
from fs_uae_launcher.ui.Skin import Skin
# import fsui as fsui
from .KickstartGroup import KickstartGroup
from .MemoryGroup import MemoryGroup
# from .config.ExpansionsGroup import ExpansionsGroup


class RomRamPanel(ConfigPanel):

    def __init__(self, parent):
        ConfigPanel.__init__(self, parent)

        self.kickstart_group = KickstartGroup(self)
        self.memory_group = MemoryGroup(self)
        # self.expansions_group = ExpansionsGroup(panel)

        self.layout.add(self.kickstart_group, fill=True)
        self.layout.add_spacer(10)
        self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        self.layout.add(self.memory_group, fill=True)

        self.layout.add_spacer(-10)

        # self.add_option(Option.ACCELERATOR_MEMORY)

        # panel.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        # panel.layout.add(self.expansions_group, fill=True)
