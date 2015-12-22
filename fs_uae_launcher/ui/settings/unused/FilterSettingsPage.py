import fsui as fsui
from fs_uae_launcher.I18N import gettext
from fs_uae_launcher.ui.settings.option_ui import OptionUI
from fsui.extra.iconheader import NewIconHeader


class FilterSettingsPage(fsui.Panel):
    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = NewIconHeader(
            self, fsui.Icon("video-settings", "pkg:fs_uae_workspace"),
            gettext("Scaling Options"),
            "")
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        add_option("zoom")
        add_option("keep_aspect")

        label = fsui.HeadingLabel(self, gettext("Filters"))
        self.layout.add(label, margin_top=20, margin_bottom=20)

        add_option("scanlines")
        add_option("rtg_scanlines")
        # FIXME: gamma
        # FIXME: brightness / contrast / saturation
