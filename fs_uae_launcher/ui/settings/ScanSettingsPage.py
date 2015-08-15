import fsui as fsui
from ...I18N import gettext
from .ScanPathsGroup import ScanPathsGroup
from fsui.extra.iconheader import NewIconHeader


class ScanSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = NewIconHeader(
            self, fsui.Icon("indexing-settings", "pkg:fs_uae_workspace"),
            gettext("File Database Settings"),
            gettext("Choose what folders you want to scan for Amiga "
                    "files"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        # label = fsui.Label(self, gettext("List of Folders to Index:"))
        # self.layout.add(label, margin=10)

        self.layout.add(fsui.MultiLineLabel(
            self, gettext("Choose what folders you want to scan for Amiga "
                          "files")), fill=True, margin_bottom=10)

        self.scan_paths_group = ScanPathsGroup(self)
        self.layout.add(self.scan_paths_group, fill=True, expand=True)

        # label = fsui.HeadingLabel(self, gettext("Additional Options"))
        # self.layout.add(label, margin=10, margin_bottom=20)
        #
        # def add_option(name):
        #     self.layout.add(
        #         OptionUI.create_group(self, name), fill=True, margin=10)
        #
        # add_option("builtin_configs")
        # add_option("kickstart_setup")
