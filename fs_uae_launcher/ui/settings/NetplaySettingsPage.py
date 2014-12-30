import fsui as fsui
from fsui.extra.iconheader import IconHeader
from ...I18N import gettext
from .OptionUI import OptionUI


class NetplaySettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("netplay-settings", "pkg:fs_uae_workspace"),
            gettext("Net Play Settings"),
            "")
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        add_option("irc_nick")
        add_option("netplay_tag")
        add_option("irc_server")
