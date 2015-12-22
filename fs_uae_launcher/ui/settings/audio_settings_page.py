import fsui as fsui
from fs_uae_launcher.I18N import gettext
from fs_uae_launcher.ui.settings.settings_page import SettingsPage


class AudioSettingsPage(SettingsPage):
    def __init__(self, parent):
        super().__init__(parent)
        icon = fsui.Icon("audio-settings", "pkg:fs_uae_workspace")
        gettext("Audio Settings")
        title = gettext("Audio")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        self.add_option("volume")
        self.add_option("stereo_separation")

        self.add_section(gettext("Floppy Drive Sound Emulation"))
        self.add_option("floppy_drive_volume")
        self.add_option("floppy_drive_volume_empty")

        self.add_section(gettext("Advanced Audio Options"))
        self.add_option("audio_frequency")
        self.add_option("audio_buffer_target_size")
