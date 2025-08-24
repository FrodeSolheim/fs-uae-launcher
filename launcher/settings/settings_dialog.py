import fsgs
import fsui
from fsbc import settings
from launcher.i18n import gettext
from launcher.launcher_settings import LauncherSettings
from launcher.launcher_signal import LauncherSignal
from launcher.option import Option
from launcher.settings.advanced_settings_page import AdvancedSettingsPage
from launcher.settings.advanced_video_settings import AdvancedVideoSettingsPage
from launcher.settings.arcade_settings_page import ArcadeSettingsPage
from launcher.settings.audio_settings_page import AudioSettingsPage
from launcher.settings.fs_uae_settings_page import FSUAESettingsPage
from launcher.settings.gamedatabasesettingspage import GameDatabaseSettingsPage
from launcher.settings.gameplatformssettingspage import (
    GamePlatformsSettingsPage,
)
from launcher.settings.joystick_settings_page import JoystickSettingsPage
from launcher.settings.keyboard_settings_page import KeyboardSettingsPage
from launcher.settings.language_settings_page import LanguageSettingsPage
from launcher.settings.launchersettingspage import LauncherSettingsPage
from launcher.settings.mouse_settings_page import MouseSettingsPage
from launcher.settings.netplay_settings_page import NetplaySettingsPage
from launcher.settings.plugins_settings_page import PluginsSettingsPage
from launcher.settings.scan_settings_page import ScanSettingsPage
from launcher.settings.video_settings_page import VideoSettingsPage
from launcher.settings.whdload_settings_page import WHDLoadSettingsPage
from launcher.ui.pageddialog import PagedDialog

SPACE = ""


class SettingsDialog(PagedDialog):
    @classmethod
    def open(cls, parent=None):
        return fsui.open_window_instance(cls, parent)

    def __init__(self, parent, index=0):
        PagedDialog.__init__(
            self,
            parent,
            "{} - {} Launcher".format(gettext("Settings"), fsgs.product),
        )

        # FIXME: remove this once the dialog uses Window as base class
        # self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        # self.add_page(
        #     # gettext("Appearance"), LanguageSettingsPage,
        #     gettext("Language"), LanguageSettingsPage,
        #     fsui.Icon("language-settings", "pkg:workspace"))
        self.add_page(
            gettext("Common"),
            LanguageSettingsPage,
            fsui.Icon("language-settings", "pkg:workspace"),
            bold=True,
        )
        self.add_page(
            gettext("Controllers"),
            JoystickSettingsPage,
            fsui.Icon("gamepad", "pkg:workspace"),
        )
        self.add_page(
            gettext("Plugins"),
            PluginsSettingsPage,
            fsui.Icon("settings", "pkg:workspace"),
        )
        # self.add_page(
        #     gettext("Directories"),
        #     DirectoriesSettingsPage,
        #     fsui.Icon("folder", "pkg:launcher"),
        # )
        self.add_page(
            gettext("Advanced"),
            AdvancedSettingsPage,
            fsui.Icon("settings", "pkg:workspace"),
        )
        self.add_page(
            "FS-UAE",
            FSUAESettingsPage,
            fsui.Icon("fs-uae", "pkg:launcher"),
            bold=True,
        )
        self.add_page(
            gettext("Keyboard"),
            KeyboardSettingsPage,
            fsui.Icon("keyboard-settings", "pkg:workspace"),
        )
        self.add_page(
            gettext("Mouse"),
            MouseSettingsPage,
            fsui.Icon("mouse-settings", "pkg:workspace"),
        )
        self.add_page(
            gettext("Audio"),
            AudioSettingsPage,
            fsui.Icon("audio-settings", "pkg:workspace"),
        )
        self.add_page(
            gettext("Video"),
            VideoSettingsPage,
            fsui.Icon("video-settings", "pkg:workspace"),
        )
        self.add_page(
            gettext("Advanced Video"),
            AdvancedVideoSettingsPage,
            fsui.Icon("video-settings", "pkg:workspace"),
        )
        # self.add_page(
        #     gettext("Synchronization"), VideoSyncSettingsPage,
        #     fsui.Icon("video-settings", "pkg:workspace"))
        # self.add_page(
        #     gettext("Filters & Scaling"), FilterSettingsPage,
        #     fsui.Icon("video-settings", "pkg:workspace"))
        # self.add_page(gettext("OpenGL Settings"), OpenGLSettingsPage)
        # if Settings.get("database_feature") == "1":
        # self.add_page(
        #     gettext("Logging"), LoggingSettingsPage,
        #     fsui.Icon("settings", "pkg:workspace"))
        self.add_page(
            "{} Launcher".format(fsgs.product),
            LauncherSettingsPage,
            fsui.Icon("fs-uae-launcher", "pkg:launcher"),
            bold=True,
        )
        self.add_page(
            gettext("File Database"),
            ScanSettingsPage,
            fsui.Icon("indexing-settings", "pkg:workspace"),
        )
        self.add_page(
            gettext("Game Database"),
            GameDatabaseSettingsPage,
            fsui.Icon("database-settings", "pkg:workspace"),
        )
        if fsgs.openretro or settings.get(Option.PLATFORMS_FEATURE) == "1":
            self.add_page(
                gettext("Game Platforms"),
                GamePlatformsSettingsPage,
                fsui.Icon("database-settings", "pkg:workspace"),
            )
        # self.add_page(gettext("Custom Settings"), CustomSettingsPage)
        if LauncherSettings.get(Option.NETPLAY_FEATURE) != "0":
            self.add_page(
                gettext("Net Play"),
                NetplaySettingsPage,
                fsui.Icon("netplay-settings", "pkg:workspace"),
            )
        self.add_page(
            "WHDLoad", WHDLoadSettingsPage, fsui.Icon("hd", "pkg:launcher")
        )
        # self.add_page(
        #     gettext("Experimental Features"), ExperimentalFeaturesPage,
        #     fsui.Icon("settings", "pkg:workspace"))
        # self.add_page(
        #     gettext("Maintenance"), MaintenanceSettingsPage,
        #     fsui.Icon("maintenance", "pkg:workspace"))
        self.add_page(
            "{} Arcade".format(fsgs.product),
            ArcadeSettingsPage,
            fsui.Icon("fs-uae-arcade", "pkg:launcher"),
            bold=True,
        )

        # Old texts
        # gettext("Video Synchronization")
        # gettext("Synchronization")
        gettext("Advanced")

        last_index = self.get_page_index_by_title(
            LauncherSettings.get("last_settings_page")
        )
        index = last_index or index
        self.list_view.set_index(index)

        defaults_button = fsui.Button(self, gettext("Reset to Defaults"))
        defaults_button.activated.connect(self.__defaults_activated)
        self.button_layout.insert(0, defaults_button, fill=True)

        defaults_label = fsui.Label(
            self, gettext("Choices marked with (*) is the default setting")
        )
        self.button_layout.insert(1, defaults_label, margin_left=20)

        self.set_size((940, 560))
        # self.center_on_parent()

        self.closed.connect(self.__closed)
        self.page_changed.connect(self.__page_changed)

    def __page_changed(self):
        index = self.get_index()
        LauncherSettings.set("last_settings_page", self.get_page_title(index))

    def __closed(self):
        LauncherSignal.broadcast("settings_updated")

    def __defaults_activated(self):
        self.page.reset_to_defaults()
