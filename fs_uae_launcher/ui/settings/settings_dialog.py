import weakref

import fsui
from .advanced_settings_page import AdvancedSettingsPage
from .advanced_video_settings import AdvancedVideoSettingsPage
from .audio_settings_page import AudioSettingsPage
from ..PagedDialog import PagedDialog
from ...I18N import gettext
from ...Settings import Settings
from ...Signal import Signal
# from .CustomSettingsPage import CustomSettingsPage
from .experimental_features_page import ExperimentalFeaturesPage
# from .FilterSettingsPage import FilterSettingsPage
from .game_database_settings_page import GameDatabaseSettingsPage
from .joystick_settings_page import JoystickSettingsPage
from .keyboard_settings_page import KeyboardSettingsPage
from .language_settings_page import LanguageSettingsPage
from .logging_settings_page import LoggingSettingsPage
from .maintenance_settings_page import MaintenanceSettingsPage
from .mouse_settings_page import MouseSettingsPage
from .netplay_settings_page import NetplaySettingsPage
from .scan_settings_page import ScanSettingsPage
from .video_sync_settings_page import VideoSyncSettingsPage
from .video_settings_page import VideoSettingsPage
from .whdload_settings_page import WHDLoadSettingsPage

SPACE = ""


class SettingsDialog(PagedDialog):

    weak_instance = None  # type: SettingsDialog

    @classmethod
    def open(cls, parent):
        if cls.weak_instance is not None:
            # noinspection PyCallingNonCallable
            instance = cls.weak_instance()
            if instance is not None:
                instance.raise_and_activate()
                return
        instance = SettingsDialog(parent)
        instance.show()
        cls.weak_instance = weakref.ref(instance)

    def __del__(self):
        print("SettingsDialog.__del__")

    def __init__(self, parent, index=0):
        PagedDialog.__init__(self, parent, gettext("FS-UAE Launcher Settings"))

        # FIXME: remove this once the dialog uses Window as base class
        # self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.add_page(
            gettext("Appearance"), LanguageSettingsPage,
            # gettext("Language"), LanguageSettingsPage,
            fsui.Icon("language-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Joystick"), JoystickSettingsPage,
            fsui.Icon("joystick-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Keyboard"), KeyboardSettingsPage,
            fsui.Icon("keyboard-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Mouse"), MouseSettingsPage,
            fsui.Icon("mouse-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Audio"), AudioSettingsPage,
            fsui.Icon("audio-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Video"), VideoSettingsPage,
            fsui.Icon("video-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Advanced Video"), AdvancedVideoSettingsPage,
            fsui.Icon("video-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Synchronization"), VideoSyncSettingsPage,
            fsui.Icon("video-settings", "pkg:fs_uae_workspace"))
        # self.add_page(
        #     gettext("Filters & Scaling"), FilterSettingsPage,
        #     fsui.Icon("video-settings", "pkg:fs_uae_workspace"))
        # self.add_page(gettext("OpenGL Settings"), OpenGLSettingsPage)
        # if Settings.get("database_feature") == "1":
        self.add_page(
            gettext("File Database"), ScanSettingsPage,
            fsui.Icon("indexing-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Game Database"), GameDatabaseSettingsPage,
            fsui.Icon("database-settings", "pkg:fs_uae_workspace"))
        # self.add_page(gettext("Custom Settings"), CustomSettingsPage)
        self.add_page(
            gettext("Maintenance"), MaintenanceSettingsPage,
            fsui.Icon("maintenance", "pkg:fs_uae_workspace"))
        if Settings.get("netplay_feature") == "1":
            self.add_page(
                gettext("Net Play"), NetplaySettingsPage,
                fsui.Icon("netplay-settings", "pkg:fs_uae_workspace"))
        self.add_page(
            "WHDLoad", WHDLoadSettingsPage,
            fsui.Icon("settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Logging"), LoggingSettingsPage,
            fsui.Icon("settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Experimental Features"), ExperimentalFeaturesPage,
            fsui.Icon("settings", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Advanced Settings"), AdvancedSettingsPage,
            fsui.Icon("settings", "pkg:fs_uae_workspace"))

        # Old texts
        # gettext("Video Synchronization")
        # gettext("Synchronization")
        gettext("Advanced")

        last_index = self.get_page_index_by_title(
            Settings.get("last_settings_page"))
        index = last_index or index
        self.list_view.set_index(index)

        self.set_size((940, 560))
        # self.center_on_parent()

        self.closed.connect(self.__closed)
        self.page_changed.connect(self.__page_changed)

    def __page_changed(self):
        index = self.get_index()
        Settings.set("last_settings_page", self.get_page_title(index))

    def __closed(self):
        Signal.broadcast("settings_updated")

    # def on_close(self):
    #     self.destroy()
