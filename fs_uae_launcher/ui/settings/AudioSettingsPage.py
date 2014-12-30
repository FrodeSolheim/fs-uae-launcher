import fsui as fsui
from ...I18N import gettext
from .OptionUI import OptionUI
from fsui.extra.iconheader import IconHeader


class AudioSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("audio-settings", "pkg:fs_uae_workspace"),
            gettext("Audio Settings"),
            "")
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        def add_option(name):
            self.layout.add(OptionUI.create_group(self, name), fill=True,
                            margin_top=10, margin_bottom=10)

        # label = fsui.HeadingLabel(self, _("Audio Settings"))
        # self.layout.add(label, margin=10, margin_bottom=20)

        add_option("volume")
        add_option("stereo_separation")

        label = fsui.HeadingLabel(
            self, gettext("Floppy Drive Sound Emulation"))
        self.layout.add(label, margin_top=20, margin_bottom=20)

        add_option("floppy_drive_volume")

        label = fsui.HeadingLabel(
            self, gettext("Advanced Audio Options"))
        self.layout.add(label, margin_top=20, margin_bottom=20)

        add_option("audio_frequency")
        add_option("audio_buffer_target_size")
