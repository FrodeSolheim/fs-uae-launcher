import weakref
import fsui as fsui
from ...I18N import gettext
from ...Settings import Settings
from ...Signal import Signal
from ..PagedDialog import PagedDialog
from .advanced import AdvancedSettingsPage
from .advanced_video import AdvancedVideoSettingsPage
from .AudioSettingsPage import AudioSettingsPage
# from .CustomSettingsPage import CustomSettingsPage
from .ExperimentalFeaturesPage import ExperimentalFeaturesPage
# from .FilterSettingsPage import FilterSettingsPage
from .GameDatabaseSettingsPage import GameDatabaseSettingsPage
from .joystick import JoystickSettingsPage
from .keyboard import KeyboardSettingsPage
from .language import LanguageSettingsPage
from .maintenance import MaintenanceSettingsPage
from .mouse import MouseSettingsPage
from .NetplaySettingsPage import NetplaySettingsPage
from .ScanSettingsPage import ScanSettingsPage
from .video_sync import VideoSyncSettingsPage
from .VideoSettingsPage import VideoSettingsPage
from .whdload import WHDLoadSettingsPage
from fsui.qt import Qt


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
        self.setAttribute(Qt.WA_DeleteOnClose, True)

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
            SPACE + gettext("Synchronization"), VideoSyncSettingsPage,
            fsui.Icon("blank", "pkg:fs_uae_launcher"))
        self.add_page(
            SPACE + gettext("Advanced"), AdvancedVideoSettingsPage,
            fsui.Icon("blank", "pkg:fs_uae_launcher"))
        # self.add_page(
        #     gettext("Filters & Scaling"), FilterSettingsPage,
        #     fsui.Icon("video-settings", "pkg:fs_uae_workspace"))
        # self.add_page(gettext("OpenGL Settings"), OpenGLSettingsPage)
        if Settings.get("netplay_feature") == "1":
            self.add_page(
                gettext("Net Play"), NetplaySettingsPage,
                fsui.Icon("netplay-settings", "pkg:fs_uae_workspace"))
        # if Settings.get("database_feature") == "1":
        self.add_page(
            gettext("Scan & Indexing"), ScanSettingsPage,
            fsui.Icon("indexing-settings", "pkg:fs_uae_workspace"))
        if True:
            self.add_page(
                gettext("Game Database"), GameDatabaseSettingsPage,
                fsui.Icon("database-settings", "pkg:fs_uae_workspace"))
        # self.add_page(gettext("Custom Settings"), CustomSettingsPage)
        self.add_page(
            gettext("Maintenance"), MaintenanceSettingsPage,
            fsui.Icon("maintenance", "pkg:fs_uae_workspace"))
        self.add_page(
            gettext("Advanced Settings"), AdvancedSettingsPage,
            fsui.Icon("settings", "pkg:fs_uae_workspace"))
        self.add_page(
            "WHDLoad", WHDLoadSettingsPage,
            fsui.Icon("blank", "pkg:fs_uae_launcher"))
        self.add_page(
            gettext("Experimental Features"), ExperimentalFeaturesPage,
            fsui.Icon("blank", "pkg:fs_uae_launcher"))

        last_index = self.get_page_index_by_title(
            Settings.get("last_settings_page"))
        index = last_index or index
        self.list_view.set_index(index)

        self.set_size((900, 560))
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
