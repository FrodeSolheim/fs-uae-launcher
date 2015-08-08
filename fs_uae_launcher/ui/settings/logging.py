import fsui as fsui
from ...I18N import gettext
from .OptionUI import OptionUI
from fsui.extra.iconheader import IconHeader


class LoggingSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()

        self.icon_header = IconHeader(
            self, fsui.Icon("maintenance", "pkg:fs_uae_workspace"),
            gettext("Logging"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        label = fsui.MultiLineLabel(self, gettext(
            "The following options may affect performance, "
            "so only enable them when needed for testing or  "
            "debugging purposes."), 640)
        self.layout.add(label, fill=True, margin_top=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        add_option("log_input")
