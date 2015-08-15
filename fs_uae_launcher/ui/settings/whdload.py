from fs_uae_launcher.ui.settings.OptionUI import OptionUI
from fsgs.FSGSDirectories import FSGSDirectories
import fsui as fsui
from fsui.extra.iconheader import NewIconHeader
from ...I18N import gettext


class WHDLoadSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = NewIconHeader(
            self, fsui.Icon("settings", "pkg:fs_uae_workspace"),
            gettext("WHDLoad Settings"),
            gettext("Options for WHDLoad support in FS-UAE Launcher"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        label = fsui.MultiLineLabel(self, gettext(
            "The following options only apply when you use the automatic "
            "WHDLoad support in FS-UAE Launcher, for example in relation with "
            "the online game database."), 640)
        self.layout.add(label, fill=True, margin_top=0)

        # label = fsui.MultiLineLabel(self, gettext(
        #     " When you use your own hard drive installation with WHDLoad "
        #     "manually installed, you need to configure WHDLoad within the "
        #     "Amiga environment instead."), 640)
        # self.layout.add(label, fill=True, margin_top=10)

        add_option("whdload_splash_delay")

        label = fsui.Label(
            self, gettext("Directory for WHDLoad.key file (if you have it):"))
        self.layout.add(label, margin_top=10)

        hor_layout = fsui.HorizontalLayout()
        self.layout.add(hor_layout, margin_top=4, fill=True)
        label = fsui.Label(
            self, FSGSDirectories.get_base_dir())
        hor_layout.add_spacer(0, expand=True)
        hor_layout.add(label)
