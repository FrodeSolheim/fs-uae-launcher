import fsui as fsui
from launcher.i18n import gettext
from launcher.ui.settings.settings_page import SettingsPage


class NetplaySettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("netplay-settings", "pkg:workspace")
        gettext("Net Play Settings")
        title = gettext("Net Play")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("irc_nick")
        self.add_option("netplay_tag")
        self.add_option("irc_server")
