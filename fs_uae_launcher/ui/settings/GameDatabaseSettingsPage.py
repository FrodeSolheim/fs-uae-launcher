import fsui as fsui
from fsui.extra.iconheader import IconHeader
from ...I18N import gettext
from .OptionUI import OptionUI


class GameDatabaseSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("database-settings", "pkg:fs_uae_workspace"),
            gettext("Game Database Settings"),
            "")
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        # label = fsui.HeadingLabel(self, _("Game Database Settings"))
        # self.layout.add(label, margin=10, margin_bottom=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        # add_option("database_username")
        # add_option("database_password")
        add_option("database_show_games")
        add_option("database_show_adult")
        add_option("database_server")
