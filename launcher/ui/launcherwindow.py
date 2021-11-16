# type: ignore

import os
import sys
import time

import fstd.desktop
import fsui
from fsbc.application import Application
from fsbc.util import unused
from fsgamesys.ogd.locker import is_locker_enabled
from fsgamesys.product import Product
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.launcher_settings import LauncherSettings
from launcher.launcher_signal import LauncherSignal
from launcher.netplay.netplay_dialog import NetplayDialog
from launcher.option import Option
from launcher.panels.additionalconfigpanel import AdditionalConfigPanel
from launcher.panels.cdpanel import CDPanel
from launcher.panels.expansionspanel import ExpansionsPanel
from launcher.panels.floppiespanel import FloppiesPanel
from launcher.panels.harddrivespanel import HardDrivesPanel
from launcher.panels.inputpanel import InputPanel
from launcher.panels.mainpanel import MainPanel
from launcher.panels.quicksettingspanel import QuickSettingsPanel
from launcher.panels.romrampanel import RomRamPanel
from launcher.ui.aboutdialog import AboutDialog
from launcher.ui.book import Book
from launcher.ui.config.configscrollarea import ConfigScrollArea
from launcher.ui.Constants import Constants
from launcher.ui.kickstartimportdialog import KickstartImportDialog
from launcher.ui.launch import LaunchGroup
from launcher.ui.skin import Skin
from launcher.ui.statusbar.StatusBar import StatusBar
from launcher.update_manager import UpdateManager
from workspace.apps.adf_creator_app import ADFCreatorWindow
from workspace.apps.hdf_creator_app import HDFCreatorWindow
from workspace.apps.locker_uploader import LockerUploaderWindow
from workspace.apps.login import LoginWindow
from workspace.apps.logout import LogoutWindow

USE_MAIN_MENU = 1
QUICK_SETTINGS_WIDTH = 200
CONFIG_BROWSER_WIDTH = 200
GAME_INFO_PANEL_MIN_WIDTH = 500

SCREENSHOT_WIDTH = 212
SCREENSHOT_SPACING = 20
MARGIN = 20
CONFIGURATIONS_PANEL_WIDTH_1 = (
    SCREENSHOT_WIDTH * 2 + SCREENSHOT_SPACING * 1 + MARGIN
)
CONFIGURATIONS_PANEL_WIDTH_2 = (
    SCREENSHOT_WIDTH * 3 + SCREENSHOT_SPACING * 2 + MARGIN
)
CONFIGURATIONS_PANEL_WIDTH_THRESHOLD_2 = 1600


# noinspection PyMethodMayBeStatic
class LauncherWindow:
    @classmethod
    def open(cls, parent=None):
        return fsui.open_window_instance(cls, parent)

    @classmethod
    def current(cls):
        return fsui.current_window_instance(cls)

    def onDestroy(self):
        # FIXME: Is this being run?
        print("LauncherWindow.on_destroy")
        LauncherSignal.remove_listener("scan_done", self)
        LauncherSignal.remove_listener("setting", self)
        super().onDestroy()

    checked_for_update = False

    def find_icon(self):
        icon = None

        def check_icon(path):
            path = os.path.join(path, "fs-uae-launcher.ico")
            if os.path.exists(path):
                return path
            return None

        if not icon:
            icon = check_icon("share/fs-uae-launcher")
        if not icon:
            icon = check_icon("launcher/share/fs-uae-launcher")

        # FIXME: should check data directories (XDG_DATA_DIRS) properly
        # instead
        if not icon:
            # FIXME: this encoding / decoding is a bit ridiculous, but, this is
            # for Python 2.x..
            icon = check_icon(
                os.path.expanduser(
                    "~/.local/share/fs-uae-launcher".encode(
                        sys.getfilesystemencoding()
                    )
                ).decode(sys.getfilesystemencoding())
            )

        # FIXME: Check relative to executable instead
        if not icon:
            icon = check_icon("/usr/local/share/fs-uae-launcher")
        if not icon:
            icon = check_icon("/usr/share/fs-uae-launcher")

        if sys.platform == "darwin":
            # Icons come from the app bundles
            icon = None
        return icon

    def on_scan_done_signal(self):
        print("LauncherWindow.on_scan_done_signal")
        LauncherConfig.update_kickstart()

    def is_editor_enabled(self):
        return "--editor" in sys.argv

    def create_menu(self):
        menu = fsui.PopupMenu()

        if LauncherSettings.get(Option.DATABASE_AUTH):
            menu.add_item(
                gettext("Update Game Database"), self.on_update_game_database
            )
        menu.add_item(
            gettext("Update File Database"), self.on_update_file_database
        )

        menu.add_separator()

        menu.add_item(gettext("ADF Creator"), self.on_adf_creator)
        menu.add_item(gettext("HDF Creator"), self.on_hdf_creator)
        if LauncherSettings.get(Option.NETPLAY_FEATURE) != "0":
            menu.add_item(gettext("Net Play"), self.on_net_play)

        menu.add_separator()
        menu.add_item(
            gettext("Import Kickstarts") + "...", self.on_import_kickstarts
        )
        menu.add_item(
            gettext("Amiga Forever Import") + "...", self.on_import_kickstarts
        )

        menu.add_separator()
        self.add_user_menu_content(menu)

        menu.add_separator()
        # menu.add_item(
        #         gettext("Kickstarts & ROMs"), self.on_import_kickstarts)

        if LauncherSettings.get(Option.LAUNCHER_SETUP_WIZARD_FEATURE):
            menu.add_item(
                gettext("Setup Wizard") + "...", self.on_setup_wizard
            )

        menu.add_preferences_item(gettext("Settings"), self.on_settings_button)

        menu.add_separator()
        menu.add_item(
            gettext("About {name}").format(name="OpenRetro.org"),
            self.on_what_is_this,
        )
        app_name = "{} Launcher".format(Product.base_name)
        menu.add_about_item(
            gettext("About {name}").format(name=app_name), self.on_about
        )

        menu.add_separator()
        menu.add_about_item(gettext("Quit"), self.on_quit)
        return menu

    def add_scroll_page(
        self, column, content_class, icon_name, title, tooltip=""
    ):
        book = self.books[column]
        instance = ConfigScrollArea(book)
        content_instance = content_class(instance)
        instance.set_widget(content_instance)
        # if content_class == MainPanel:
        #     self.main_panel = instance
        return self._add_page(book, instance, icon_name, title, tooltip)

    def on_custom_button(self):
        from .config.configdialog import ConfigDialog

        ConfigDialog.run(self.get_window())

    def menu(self):
        self._menu = self.create_menu()
        return self._menu

    def open_main_menu(self):
        if fsui.System.windows:
            if time.time() - getattr(self, "main_menu_close_time", 0) < 0.2:
                return
        self._menu = self.create_menu()
        if Skin.use_unified_toolbar():
            self.popup_menu(self._menu, (0, -2))
        else:
            self.menu_button.popup_menu(
                self._menu, (0, self.menu_button.size()[1] - 2)
            )
        if fsui.System.windows:
            self.main_menu_close_time = time.time()
        return self._menu

    def toggle_quick_settings_sidebar(self):
        print("Toggling settings sidebar")
        if self.quick_settings_panel.visible():
            self.quick_settings_panel.hide()
            LauncherSettings.set(Option.QUICK_SETTINGS, "0")
        else:
            self.quick_settings_panel.show()
            LauncherSettings.set(Option.QUICK_SETTINGS, "1")
        self.layout.update()

    # def open_user_menu(self):
    #     if fsui.System.windows:
    #         if time.time() - getattr(self, "user_menu_close_time", 0) < 0.2:
    #             return
    #     user_menu = self.create_user_menu()
    #     self.user_button.popup_menu(
    #         user_menu, (0, self.user_button.get_size()[1] - 2))
    #     if fsui.System.windows:
    #         self.user_menu_close_time = time.time()

    def add_user_menu_content(self, menu):
        if LauncherSettings.get(Option.DATABASE_AUTH):
            # menu.add_item(_("Log In / Register"), self.on_log_in)
            # menu.add_item(gettext("Update Game Database"),
            #               self.on_game_database_refresh)
            if is_locker_enabled():
                menu.add_item(
                    gettext("Upload Files to OpenRetro Locker"),
                    self.on_upload_locker_files,
                )
                # menu.add_separator()
            menu.add_item(gettext("Log Out"), self.on_log_out)
        else:
            menu.add_item(gettext("Log In / Register"), self.on_log_in)

    def create_user_menu(self):
        menu = fsui.Menu()
        self.add_user_menu_content(menu)
        return menu

    def on_log_in(self):
        print("on_log_in")
        LoginWindow.open(self)

    def on_log_out(self):
        print("on_log_out")
        LogoutWindow.open(self)

    def on_what_is_this(self):
        print("on_what_is_this")
        fstd.desktop.open_url_in_browser("https://openretro.org/about")

    def on_scan_button(self):
        from .scan import ScanDialog

        ScanDialog(self.get_window()).show()

    def on_settings_button(self):
        from launcher.settings.settings_dialog import SettingsDialog

        SettingsDialog.open(self)

    def on_setup_wizard(self):
        from launcher.setup.setupwizarddialog import SetupWizardDialog

        SetupWizardDialog.open(self)

    def on_about(self):
        dialog = AboutDialog(self.get_window())
        dialog.show()

    def on_quit(self):
        self.close()

    def on_import_kickstarts(self):
        KickstartImportDialog(self.get_window()).show()

    def on_update_file_database(self):
        self.on_scan_button()

    def on_update_game_database(self):
        wsopen("SYS:Tools/DatabaseUpdater")

    def on_upload_locker_files(self):
        print("on_upload_locker_files")
        LockerUploaderWindow.open(self)

    def on_adf_creator(self):
        print("on_adf_creator")
        ADFCreatorWindow.open(self)

    def on_hdf_creator(self):
        print("on_hdf_creator")
        HDFCreatorWindow.open(self)

    def on_net_play(self):
        print("on_net_play")
        NetplayDialog.open()
