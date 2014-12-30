import fsui as fsui
from fsui.extra.iconheader import IconHeader
from ...I18N import gettext
from .OptionUI import OptionUI


class VideoSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("video-settings", "pkg:fs_uae_workspace"),
            gettext("Video Settings"),
            "")
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        add_option("fullscreen")

        label = fsui.HeadingLabel(self, gettext("Scaling"))
        self.layout.add(label, margin_top=20, margin_bottom=20)

        add_option("zoom")
        add_option("keep_aspect")

        label = fsui.HeadingLabel(self, gettext("Filters"))
        self.layout.add(label, margin_top=20, margin_bottom=20)

        add_option("scanlines")
        add_option("rtg_scanlines")

        # add_option("video_format")
        #
        # add_option("video_sync")
        # add_option("low_latency_vsync")
        #
        # label = fsui.HeadingLabel(self, gettext("OpenGL Settings"))
        # self.layout.add(label, margin_top=20, margin_bottom=20)
        #
        # add_option("fsaa")
        # add_option("texture_filter")
        # add_option("video_sync_method")
        # add_option("texture_format")
