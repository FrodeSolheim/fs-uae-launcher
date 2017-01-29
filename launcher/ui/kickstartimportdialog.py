import fsui
from launcher.i18n import gettext
from launcher.ui.imports.ImportGroup import ImportGroup
from launcher.ui.scan import ScanKickstartGroup
from launcher.ui.skin import LauncherTheme
from launcher.ui.widgets import CloseButton


class KickstartImportDialog(fsui.DialogWindow):
    def __init__(self, parent):
        super().__init__(parent, gettext("Import Kickstarts"))
        self.theme = LauncherTheme.get()
        self.layout = fsui.VerticalLayout(padding=20)
        self.panel = SetupPanel(self)
        self.panel.set_min_width(620)
        self.layout.add(self.panel)


class SetupPanel(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        self.import_rom_group = ImportGroup(self)
        self.layout.add(self.import_rom_group, fill=True)
        self.layout.add_spacer(20)
        self.import_af_group = ImportGroup(self, ImportGroup.AMIGA_FOREVER)
        self.layout.add(self.import_af_group, fill=True)
        self.layout.add_spacer(20)
        self.scan_kickstart_group = ScanKickstartGroup(self)
        self.layout.add(self.scan_kickstart_group, fill=True)
        CloseButton.add_to_layout(self, self.layout, margin_top=20)
