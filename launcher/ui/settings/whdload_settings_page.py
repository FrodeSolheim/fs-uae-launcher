import fsui
from launcher.i18n import gettext
from launcher.ui.settings.settings_page import SettingsPage
from fsgs.FSGSDirectories import FSGSDirectories


class WHDLoadSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("settings", "pkg:workspace")
        # gettext("WHDLoad Settings")
        title = gettext("WHDLoad")
        subtitle = gettext("Options for WHDLoad support in FS-UAE Launcher")
        self.add_header(icon, title, subtitle)

        label = fsui.MultiLineLabel(self, gettext(
            "The following options only apply when you use the automatic "
            "WHDLoad support in FS-UAE Launcher, for example in relation with "
            "the online game database."), 640)
        self.layout.add(label, fill=True, margin_top=0)

        self.add_option("whdload_splash_delay")

        label = fsui.Label(
            self, gettext("Directory for WHDLoad.key file (if you have it):"))
        self.layout.add(label, margin_top=10)
        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, margin_top=4, fill=True)
        label = fsui.Label(
            self, FSGSDirectories.get_base_dir())
        hor_layout.add_spacer(0, expand=True)
        hor_layout.add(label)
