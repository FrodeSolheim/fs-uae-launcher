import fsui as fsui
from ...I18N import gettext
from .OptionUI import OptionUI
from fsui.extra.iconheader import IconHeader


class MouseSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("mouse-settings", "pkg:fs_uae_workspace"),
            gettext("Mouse Setting"),
            "")
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        # label = fsui.HeadingLabel(self, _("Mouse Settings"))
        # self.layout.add(label, margin=10, margin_bottom=20)

        add_option("automatic_input_grab")
        add_option("initial_input_grab")

        add_option("middle_click_ungrab")
        add_option("mouse_speed")
