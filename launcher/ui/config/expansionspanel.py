import fsui
from launcher.i18n import gettext
from launcher.option import Option
from launcher.ui.config.configpanel import ConfigPanel
from launcher.ui.config.ExpansionsGroup import ExpansionsGroup


class ExpansionsPanel(ConfigPanel):

    def __init__(self, parent):
        ConfigPanel.__init__(self, parent)

        # self.expansions_group = ExpansionsGroup(self)
        # self.layout.add(self.expansions_group, fill=True)

        heading_label = fsui.HeadingLabel(self, gettext("Expansions"))
        self.layout.add(heading_label, margin=10)
        self.layout.add_spacer(0)

        # self.add_option(Option.CPU)
        self.add_option(Option.ACCELERATOR)
        # self.add_option(Option.ACCELERATOR_MEMORY)
        self.add_option(Option.BLIZZARD_SCSI_KIT)
        self.add_option(Option.GRAPHICS_CARD)
        # self.add_option(Option.GRAPHICS_MEMORY)
        self.add_option(Option.SOUND_CARD)
        self.add_option(Option.NETWORK_CARD)
        self.add_option(Option.BSDSOCKET_LIBRARY)
