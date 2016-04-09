import fsui
from launcher.option import Option
from launcher.ui.settings.launcher_settings_page import LauncherSettingsPage
from launcher.ui.settings.plugins_settings_page import PluginsSettingsPage
from .advanced_settings_page import AdvancedSettingsPage
from .advanced_video_settings import AdvancedVideoSettingsPage
from .audio_settings_page import AudioSettingsPage
from ..PagedDialog import PagedDialog
from ...i18n import gettext
from ...launcher_settings import LauncherSettings
from ...launcher_signal import LauncherSignal
from .game_database_settings_page import GameDatabaseSettingsPage
from .joystick_settings_page import JoystickSettingsPage
from .keyboard_settings_page import KeyboardSettingsPage
from .language_settings_page import LanguageSettingsPage
from .logging_settings_page import LoggingSettingsPage
from .maintenance_settings_page import MaintenanceSettingsPage
from .mouse_settings_page import MouseSettingsPage
from .netplay_settings_page import NetplaySettingsPage
from .scan_settings_page import ScanSettingsPage
from .video_settings_page import VideoSettingsPage
from .whdload_settings_page import WHDLoadSettingsPage

SPACE = ""


class SettingsDialog(PagedDialog):

    @classmethod
    def open(cls, parent=None):
        return fsui.open_window_instance(cls, parent)

    def __init__(self, parent, index=0):
        PagedDialog.__init__(self, parent, "{} - FS-UAE Launcher".format(
                gettext("Settings")))

        # FIXME: remove this once the dialog uses Window as base class
        # self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.add_page(
            # gettext("Appearance"), LanguageSettingsPage,
            gettext("Language"), LanguageSettingsPage,
            fsui.Icon("language-settings", "pkg:workspace"))
        self.add_page(
            gettext("Joysticks & Gamepads"), JoystickSettingsPage,
            fsui.Icon("joystick-settings", "pkg:workspace"))
        self.add_page(
            gettext("Keyboard"), KeyboardSettingsPage,
            fsui.Icon("keyboard-settings", "pkg:workspace"))
        self.add_page(
            gettext("Mouse"), MouseSettingsPage,
            fsui.Icon("mouse-settings", "pkg:workspace"))
        self.add_page(
            gettext("Audio"), AudioSettingsPage,
            fsui.Icon("audio-settings", "pkg:workspace"))
        self.add_page(
            gettext("Video"), VideoSettingsPage,
            fsui.Icon("video-settings", "pkg:workspace"))
        self.add_page(
            gettext("Advanced Video"), AdvancedVideoSettingsPage,
            fsui.Icon("video-settings", "pkg:workspace"))
        # self.add_page(
        #     gettext("Synchronization"), VideoSyncSettingsPage,
        #     fsui.Icon("video-settings", "pkg:workspace"))
        # self.add_page(
        #     gettext("Filters & Scaling"), FilterSettingsPage,
        #     fsui.Icon("video-settings", "pkg:workspace"))
        # self.add_page(gettext("OpenGL Settings"), OpenGLSettingsPage)
        # if Settings.get("database_feature") == "1":
        self.add_page(
            gettext("Logging"), LoggingSettingsPage,
            fsui.Icon("settings", "pkg:workspace"))
        self.add_page(
            "FS-UAE Launcher", LauncherSettingsPage,
            fsui.Icon("settings", "pkg:workspace"))
        self.add_page(
            gettext("File Database"), ScanSettingsPage,
            fsui.Icon("indexing-settings", "pkg:workspace"))
        self.add_page(
            gettext("Game Database"), GameDatabaseSettingsPage,
            fsui.Icon("database-settings", "pkg:workspace"))
        # self.add_page(gettext("Custom Settings"), CustomSettingsPage)
        if LauncherSettings.get(Option.NETPLAY_FEATURE) != "0":
            self.add_page(
                gettext("Net Play"), NetplaySettingsPage,
                fsui.Icon("netplay-settings", "pkg:workspace"))
        self.add_page(
            "WHDLoad", WHDLoadSettingsPage,
            fsui.Icon("settings", "pkg:workspace"))
        self.add_page(
            gettext("Plugins"), PluginsSettingsPage,
            fsui.Icon("settings", "pkg:workspace"))
        # self.add_page(
        #     gettext("Experimental Features"), ExperimentalFeaturesPage,
        #     fsui.Icon("settings", "pkg:workspace"))
        self.add_page(
            gettext("Maintenance"), MaintenanceSettingsPage,
            fsui.Icon("maintenance", "pkg:workspace"))
        self.add_page(
            gettext("Advanced Settings"), AdvancedSettingsPage,
            fsui.Icon("settings", "pkg:workspace"))

        # Old texts
        # gettext("Video Synchronization")
        # gettext("Synchronization")
        gettext("Advanced")

        last_index = self.get_page_index_by_title(
            LauncherSettings.get("last_settings_page"))
        index = last_index or index
        self.list_view.set_index(index)

        self.set_size((940, 560))
        # self.center_on_parent()

        self.closed.connect(self.__closed)
        self.page_changed.connect(self.__page_changed)

    def __page_changed(self):
        index = self.get_index()
        LauncherSettings.set("last_settings_page", self.get_page_title(index))

    def __closed(self):
        LauncherSignal.broadcast("settings_updated")

    # def on_close(self):
    #     self.destroy()
