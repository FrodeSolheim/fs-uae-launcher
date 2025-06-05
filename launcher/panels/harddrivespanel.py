import fsui
from launcher.i18n import gettext
from launcher.ui.config.HardDriveGroup import HardDriveGroup
from launcher.ui.config.WHDLoadGroup import WHDLoadGroup
from launcher.ui.skin import Skin


class HardDrivesPanel(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        Skin.set_background_color(self)
        self.layout = fsui.VerticalLayout()

        heading_label = fsui.HeadingLabel(self, gettext("Hard Drives"))
        self.layout.add(heading_label, margin=10)
        self.layout.add_spacer(0)
        self.hard_drive_groups = []
        for i in range(4):
            self.hard_drive_groups.append(HardDriveGroup(self, i))
            self.layout.add(self.hard_drive_groups[i], fill=True, margin=10)

        self.layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)
        heading_label = fsui.HeadingLabel(self, gettext("WHDLoad Arguments"))
        self.layout.add(heading_label, margin=10)
        self.layout.add_spacer(0)
        self.whdload_group = WHDLoadGroup(self)
        self.layout.add(self.whdload_group, fill=True)
