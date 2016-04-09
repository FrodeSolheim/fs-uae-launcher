from launcher.option import Option
from launcher.ui.behaviors.amigaenablebehavior import AmigaEnableBehavior
import fsui
from launcher.ui.options import ConfigWidgetFactory
from ..cd_manager import CDManager
from ..floppy_manager import FloppyManager
from ..i18n import gettext
from .FloppySelector import FloppySelector


class FloppiesGroup(fsui.Group):

    def __init__(self, parent, drives=2, cd_mode=False):
        fsui.Group.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        self.cd_mode = cd_mode
        self.num_drives = drives

        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)

        if cd_mode:
            title = gettext("CD-ROM Drive")
            drive_count_option = Option.CDROM_DRIVE_COUNT
        else:
            title = gettext("Floppy Drives")
            drive_count_option = Option.FLOPPY_DRIVE_COUNT

        self.label = fsui.HeadingLabel(self, title)
        hori_layout.add(self.label, margin=10)
        hori_layout.add_spacer(0, expand=True)

        hori_layout.add(ConfigWidgetFactory().create(
            self, drive_count_option, text=gettext("Drive Count")),
            fill=True, margin_right=20)

        self.multi_select_button = fsui.Button(
            self, gettext("Multi-Select..."))
        if self.cd_mode:
            self.multi_select_button.set_tooltip(
                gettext("Add Multiple CD-ROMs at Once"))
        else:
            self.multi_select_button.set_tooltip(
                gettext("Add Multiple Floppies at Once"))
        AmigaEnableBehavior(self.multi_select_button)
        self.multi_select_button.activated.connect(self.on_multi_select_button)

        hori_layout.add(self.multi_select_button, margin_right=10)

        self.layout.add_spacer(0)

        self.selectors = []
        for i in range(drives):
            selector = FloppySelector(parent, i)
            if cd_mode:
                selector.set_cd_mode(True)
            self.selectors.append(selector)
            self.layout.add(selector, fill=True, margin=10, margin_bottom=0)

    def on_multi_select_button(self):
        if self.cd_mode:
            CDManager.multiselect(self.get_window())
        else:
            FloppyManager.multiselect(self.get_window())

    def update_heading_label(self):
        if self.cd_mode:
            if self.num_drives > 1:
                self.label.set_text(gettext("CD-ROM Drives"))
            else:
                self.label.set_text(gettext("CD-ROM Drive"))
        else:
            self.label.set_text(gettext("Floppy Drives"))
