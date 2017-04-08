import fsui
from launcher.cd_manager import CDManager
from launcher.floppy_manager import FloppyManager
from launcher.i18n import gettext
from launcher.option import Option
from launcher.ui.behaviors.platformbehavior import AMIGA_PLATFORMS, \
    CDEnableBehavior, FloppyEnableBehavior
from launcher.ui.floppyselector import FloppySelector
from launcher.ui.options import ConfigWidgetFactory


class FloppiesGroup(fsui.Group):
    FLOPPY_MODE = FloppySelector.FLOPPY_MODE
    CD_MODE = FloppySelector.CD_MODE
    TAPE_MODE = FloppySelector.TAPE_MODE
    CARTRIDGE_MODE = FloppySelector.CARTRIDGE_MODE

    def __init__(self, parent, drives=2, cd_mode=False,
                 removable_media=False):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        self.cd_mode = cd_mode
        self.num_drives = drives

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        self.mode = self.FLOPPY_MODE
        if cd_mode:
            self.mode = self.CD_MODE

        if self.mode == self.CD_MODE:
            title = gettext("CD-ROM Drive")
            drive_count_option = Option.CDROM_DRIVE_COUNT
            behavior_class = CDEnableBehavior
        elif self.mode == self.TAPE_MODE:
            title = gettext("Tape Drive")
            drive_count_option = None
            behavior_class = None
        elif self.mode == self.CARTRIDGE_MODE:
            title = gettext("Cartridge")
            drive_count_option = None
            behavior_class = None
        else:
            title = gettext("Floppy Drives")
            drive_count_option = Option.FLOPPY_DRIVE_COUNT
            behavior_class = FloppyEnableBehavior

        if removable_media:
            # Removable media group will change type dynamically
            behavior_class = None

        self.label = fsui.HeadingLabel(self, title)
        hori_layout.add(self.label, margin=10)
        hori_layout.add_spacer(0, expand=True)

        if drive_count_option and not removable_media:
            # FIXME: Drive count option does not work on the main page when
            # changing to CD mode. Workaround for now is to not include it.
            hori_layout.add(ConfigWidgetFactory().create(
                self, drive_count_option, text=gettext("Drive Count"),
                platforms=AMIGA_PLATFORMS),
                fill=True, margin_right=20)

        self.multi_select_button = fsui.Button(
            self, gettext("Multi-Select..."))
        if self.cd_mode:
            self.multi_select_button.set_tooltip(
                gettext("Add Multiple CD-ROMs at Once"))
        else:
            self.multi_select_button.set_tooltip(
                gettext("Add Multiple Floppies at Once"))
        if behavior_class:
            behavior_class(self.multi_select_button)
        self.multi_select_button.activated.connect(self.on_multi_select_button)

        hori_layout.add(self.multi_select_button, margin_right=10)

        self.layout.add_spacer(0)

        self.selectors = []
        for i in range(drives):
            selector = FloppySelector(parent, i, show_path=not removable_media)
            if behavior_class:
                behavior_class(selector)
            selector.set_mode(self.mode)
            self.selectors.append(selector)
            self.layout.add(selector, fill=True, margin=10, margin_bottom=0)

    def on_multi_select_button(self):
        if self.cd_mode:
            CDManager.multi_select(self.get_window())
        else:
            FloppyManager.multi_select(self.get_window())

    def update_heading_label(self):
        if self.mode == self.CD_MODE:
            if self.num_drives > 1:
                self.label.set_text(gettext("CD-ROM Drives"))
            else:
                self.label.set_text(gettext("CD-ROM Drive"))
        elif self.mode == self.TAPE_MODE:
            self.label.set_text(gettext("Tape Drive"))
        elif self.mode == self.CARTRIDGE_MODE:
            self.label.set_text(gettext("Cartridge"))
        else:
            self.label.set_text(gettext("Floppy Drives"))
        # Need to update the layout to account for label widget size change.
        self.layout.update()
