from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import fsui as fsui
from .imports.ImportGroup import ImportGroup
from .ScanKickstartGroup import ScanKickstartGroup
from .Skin import Skin


class SetupPanel(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        self.scan_kickstart_group = ScanKickstartGroup(self)
        self.import_rom_group = ImportGroup(self)
        self.import_af_group = ImportGroup(self, ImportGroup.AMIGA_FOREVER)

        self.layout.add(self.import_rom_group, fill=True)
        self.layout.add_spacer(20)
        self.layout.add(self.import_af_group, fill=True)
        self.layout.add_spacer(20)
        self.layout.add(self.scan_kickstart_group, fill=True)
        # self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
