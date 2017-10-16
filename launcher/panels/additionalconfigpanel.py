import fsui
from launcher.i18n import gettext
from launcher.option import Option
from launcher.ui.IconButton import IconButton
from launcher.ui.behaviors.platformbehavior import AmigaShowBehavior
from launcher.ui.config.configpanel import ConfigPanel
from launcher.ui.config.configdialog import ConfigDialog


class AdditionalConfigPanel(ConfigPanel):
    def __init__(self, parent):
        ConfigPanel.__init__(self, parent)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        heading_label = fsui.HeadingLabel(
            self, gettext("Additional Configuration"))
        hori_layout.add(heading_label, margin=10)
        hori_layout.add_spacer(0, expand=True)
        hori_layout.add(CustomConfigButton(self), margin_right=10)
        self.layout.add_spacer(0)

        amiga_panel = fsui.Panel(self)
        # AmigaShowBehavior(amiga_panel)
        amiga_panel.layout = fsui.VerticalLayout()
        self.layout.add(amiga_panel, fill=True)

        self.add_amiga_option(Option.CPU, parent=amiga_panel)
        self.add_amiga_option(Option.JIT_COMPILER, parent=amiga_panel)
        self.add_amiga_option(Option.FLOPPY_DRIVE_SPEED, parent=amiga_panel)
        self.add_amiga_option(
            Option.FLOPPY_DRIVE_VOLUME_EMPTY, parent=amiga_panel)
        self.add_amiga_option(Option.FREEZER_CARTRIDGE, parent=amiga_panel)
        self.add_amiga_option(Option.DONGLE_TYPE, parent=amiga_panel)


class CustomConfigButton(IconButton):
    def __init__(self, parent):
        super().__init__(parent, "16x16/settings.png")
        self.activated.connect(self.__activated)

    def __activated(self):
        ConfigDialog.run(self.window)
