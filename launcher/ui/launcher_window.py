import os
import sys
import time
import weakref

import fstd.desktop
import fsui
import launcher.ui
from fsbc.application import Application
from fsbc.util import unused
from fsgs.context import default_context
from launcher.implicit_handler import ImplicitConfigHandler
from launcher.launcher_config import LauncherConfig
from launcher.netplay.netplay_dialog import NetplayDialog
from launcher.option import Option
from launcher.ui.bottombar.BottomPanel import BottomPanel
from launcher.ui.bottombar.GameInfoPanel import GameInfoPanel
from launcher.ui.bottombar.ScreenshotsPanel import ScreenshotsPanel
from launcher.ui.config.browser import ConfigBrowser
from launcher.ui.config.configscrollarea import ConfigScrollArea
from launcher.ui.launch import LaunchGroup
from launcher.ui.romram import RomRamPanel
from launcher.update_manager import UpdateManager
from workspace.apps.adf_creator_app import ADFCreatorWindow
from workspace.apps.hdf_creator_app import HDFCreatorWindow
from workspace.apps.locker_uploader import LockerUploaderWindow
from workspace.apps.login import LoginWindow
from workspace.apps.logout import LogoutWindow
from workspace.apps.refresh import RefreshWindow
from .book import Book
from .cd_panel import CDPanel
from .ConfigurationsPanel import ConfigurationsPanel
from .Constants import Constants
from .FloppiesPanel import FloppiesPanel
from .HardDrivesPanel import HardDrivesPanel
from .InputPanel import InputPanel
from .MainPanel import MainPanel
from .setup import SetupDialog
from .skin import Skin
from .WindowWithTabs import WindowWithTabs
from .about import AboutDialog
from .config.additionalconfigpanel import AdditionalConfigPanel
from .config.expansionspanel import ExpansionsPanel
from .statusbar.StatusBar import StatusBar
from ..i18n import gettext
from ..launcher_settings import LauncherSettings
from ..launcher_signal import LauncherSignal

USE_MAIN_MENU = 1


# noinspection PyMethodMayBeStatic
class LauncherWindow(WindowWithTabs):

    @classmethod
    def open(cls, parent=None):
        return fsui.open_window_instance(cls, parent)

    @classmethod
    def current(cls):
        return fsui.current_window_instance(cls)

    def __init__(self, fsgs=None):
        LauncherWindow._current = weakref.ref(self)
        # Old name
        if fsgs is not None:
            self.fsgs = fsgs
        else:
            self.fsgs = default_context()
        # New name
        self.gsc = self.fsgs

        from launcher.fs_uae_launcher import FSUAELauncher
        FSUAELauncher.pre_start()

        border = True
        maximize = None
        menu = False
        if launcher.ui.get_screen_size()[1] <= 768:
            if fstd.desktop.is_running_gnome_3():
                border = False
                if "--window-border" in sys.argv:
                    border = True
            maximize = True
        if Skin.fws():
            border = False
            menu = True
        if "--no-window-border" in sys.argv:
            border = False

        if Skin.fws():
            title = "FS-UAE Launcher"
        else:
            title = "FS-UAE Launcher {0}".format(
                Application.instance().version)

        WindowWithTabs.__init__(self, None, title, border=border, menu=menu)
        icon = self.find_icon()
        if icon:
            self.set_icon_from_path(icon)

        self.tab_panels = []
        self.books = []
        self._menu = None
        self.menu_button = None
        self.main_menu_close_time = 0
        self.user_menu_close_time = 0
        self.user_button = None
        self.main_panel = None
        self.config_browser = None
        self.main_layout = fsui.VerticalLayout()
        self.set_content(self.main_layout)

        self.column_layout = fsui.HorizontalLayout()
        self.main_layout.add(self.column_layout, fill=True, expand=True)

        # left border
        self.create_column(
            0, min_width=Skin.get_window_padding_left(), content=False)
        # left content
        # if fs_uae_launcher.ui.get_screen_size()[0] > 1024:
        #     left_width = 518
        # else:
        #     left_width = 400
        # FIXME: adjust
        left_width = 462
        self.create_column(1, min_width=left_width)

        # right content
        # right_width = Constants.SCREEN_SIZE[0] * 2 + 21 + 10 + 10
        extra_screenshot_width = Constants.SCREEN_SIZE[0] + 21
        need_width = 1280

        right_width = 518

        if self.is_editor_enabled():
            # need_width += extra_screen_width
            pass
        else:
            if launcher.ui.get_screen_size()[0] >= need_width:
                # make room for one more screenshot
                right_width += extra_screenshot_width
                pass

        # right_width = 518

        # if Skin.EXTRA_GROUP_MARGIN:
        #     self.main_layout.add_spacer(Skin.EXTRA_GROUP_MARGIN)

        self.create_column(2, min_width=right_width, expand=True)

        # right border
        self.create_column(3, min_width=Skin.get_window_padding_right(),
                           content=False)

        # if self.is_editor_enabled():
        #     from ..editor.EditorGroup import EditorGroup
        #     editor = EditorGroup(self)
        #     self.main_layout.add(editor, fill=True, expand=True,
        #                          margin_right=20)

        # if fs_uae_launcher.ui.get_screen_size()[1] >= 768:
        #     right_margin = 0

        if launcher.ui.get_screen_size()[1] >= 720:
            self.bottom_layout = fsui.HorizontalLayout()
            self.main_layout.add(self.bottom_layout, fill=True)

            bottom_panel = BottomPanel(self)
            bottom_panel.set_min_width(10)
            bottom_panel.set_min_height(Skin.get_bottom_panel_height())
            self.bottom_layout.add(bottom_panel, fill=True)

            self.screenshots_panel = ScreenshotsPanel(self)
            self.bottom_layout.add(self.screenshots_panel, fill=True)

            self.game_info_panel = GameInfoPanel(self)
            self.game_info_panel.set_min_width(500)
            self.bottom_layout.add(self.game_info_panel, fill=True, expand=True)

            bottom_panel = BottomPanel(self)
            bottom_panel.set_min_width(10)
            bottom_panel.set_min_height(Skin.get_bottom_panel_height())
            self.bottom_layout.add(bottom_panel, fill=True)
        else:
            self.bottom_layout = None
            self.screenshots_panel = None

        # right_margin = -10 - Skin.EXTRA_GROUP_MARGIN
        #     else:
        #         bottom_panel = None
        #     # FIXME:
        #     if bottom_panel is None:
        #         layout.add_spacer(0, Skin.get_bottom_panel_height())
        #     else:
        #         bottom_panel.set_min_height(Skin.get_bottom_panel_height())
        #         layout.add(bottom_panel, fill=True, margin_right=right_margin)
        # elif column == 1:
        #     group = LaunchGroup(self)
        #     layout.add(group, fill=True, margin=10, margin_top=0)
        #     layout.add_spacer(0, 10)

        self.realize_tabs()
        # self._menu = self.create_menu()
        if fsui.System.macosx and fsui.toolkit == 'wx':
            # import wx
            # self.tools_menu = self.create_menu()
            # menu_bar = wx.MenuBar()
            # menu_bar.Append(self.tools_menu._menu, _("Tools"))
            # self.SetMenuBar(menu_bar)
            pass

        self.status_bar = StatusBar(self)
        self.layout.add(self.status_bar, fill=True)

        was_maximized = LauncherSettings.get("maximized") == "1"

        if LauncherSettings.get(Option.LAUNCHER_CONFIG_FEATURE) == "1":
            if launcher.ui.get_screen_size()[0] > 1300:
                if launcher.ui.get_screen_size()[1] > 1000:
                    self.layout.min_width = 1280
                    self.layout.min_height = 720

        self.set_size(self.layout.get_min_size())

        self.center_on_screen()
        if was_maximized or maximize:
            self.maximize()

        LauncherSignal.add_listener("scan_done", self)
        LauncherSignal.add_listener("setting", self)

        self.update_title()
        self.check_for_update_once()
        self.implicit_config_handler = ImplicitConfigHandler(self)

    def on_destroy(self):
        # FIXME: Is this being run?
        print("LauncherWindow.on_destroy")
        LauncherSignal.remove_listener("scan_done", self)
        LauncherSignal.remove_listener("setting", self)

    checked_for_update = False

    @classmethod
    def check_for_update_once(cls):
        if cls.checked_for_update:
            return
        UpdateManager.run_update_check()
        cls.checked_for_update = True

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
            # this encoding / decoding is a bit ridiculous, but, this is
            # for Python 2.x..
            icon = check_icon(os.path.expanduser(
                "~/.local/share/fs-uae-launcher".encode(
                    sys.getfilesystemencoding())).decode(
                sys.getfilesystemencoding()))
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

    def update_title(self):
        if Skin.fws():
            # Just want to keep "FS-UAE Launcher" in the title
            return
        auth = LauncherSettings.get(Option.DATABASE_AUTH)
        if auth:
            username = LauncherSettings.get(Option.DATABASE_USERNAME)
            login_info = username
        else:
            login_info = gettext("Not logged in")
        title = "FS-UAE Launcher {0} ({1})".format(
            Application.instance().version, login_info)
        self.set_title(title)

    def on_setting(self, key, value):
        unused(value)
        if key == Option.DATABASE_AUTH:
            self.update_title()

    def on_resize(self):
        print("on_resize, size =", self.get_size())
        if self.is_maximized():
            LauncherSettings.set("maximized", "1")
        else:
            LauncherSettings.set("maximized", "0")
        if self.screenshots_panel is not None:
            window_width = self.get_size()[0]
            available = (window_width - 10 - 10 -
                         self.game_info_panel.get_min_width())
            num_screenshots = int((available - 22 + 22) /
                                  (Constants.SCREEN_SIZE[0] + 22))
            print(num_screenshots)
            screenshots_panel_width = \
                (Constants.SCREEN_SIZE[0] + 22) * num_screenshots - 22 + 22
            self.screenshots_panel.set_min_width(screenshots_panel_width)
        super().on_resize()

    def is_editor_enabled(self):
        return "--editor" in sys.argv

    def create_column(self, column, content=True, expand=False, min_width=0):
        layout = fsui.VerticalLayout()
        self.column_layout.add(layout, fill=True, expand=expand)
        if min_width:
            layout.add_spacer(min_width, 0)

        layout.add_spacer(0, 10 + Skin.EXTRA_GROUP_MARGIN)

        if content:
            book = Book(self)
            Skin.set_background_color(book)
            if column == 1:
                margin_right = Skin.EXTRA_GROUP_MARGIN
                # expand = False
                expand = True
            else:
                margin_right = 0
                expand = True
            hor_layout = fsui.HorizontalLayout()
            layout.add(
                hor_layout, fill=True, expand=expand, margin_right=margin_right)
            # hor_layout.add(
            #     book, fill=True, expand=expand, margin_right=margin_right)

            vert_layout = fsui.VerticalLayout()
            hor_layout.add(vert_layout, fill=True, expand=expand,
                           margin_right=margin_right)
            vert_layout.add(book, fill=True, expand=True)

#                        self.add_tab_panel(LaunchGroup, expand=False)

            if column == 2 and \
                    LauncherSettings.get(Option.LAUNCHER_CONFIG_FEATURE) == "1":
                if launcher.ui.get_screen_size()[0] >= 1280:
                    hor_layout.add_spacer(10)
                    # if not Skin.fws():
                    #     line_panel = fsui.Panel(self)
                    #     line_panel.set_background_color(
                    #         fsui.Color(*BORDER_COLOR))
                    #     line_panel.set_min_width(2)
                    #     hor_layout.add(line_panel, fill=True, margin_top=-10,
                    #                    margin_bottom=-10)
                    self.config_browser = ConfigBrowser(self)
                    self.config_browser.set_min_width(200)
                    # if Skin.fws():
                    hor_layout.add(self.config_browser, fill=True,
                                   expand=0.5, margin=-10, margin_left=0)
                    # else:
                    #     hor_layout.add(self.config_browser, fill=True,
                    #                    expand=0.5, margin=10)

            if column == 2:
                # if fs_uae_launcher.ui.get_screen_size()[1] >= 1024:
                #     vert_layout.add_spacer(100)

                hor2_layout = fsui.HorizontalLayout()
                vert_layout.add(hor2_layout, fill=True, margin=10)
                launch_group = LaunchGroup(self, self.gsc)
                # hor2_layout.add_spacer(0, expand=True)
                hor2_layout.add(launch_group, expand=True)

            self.books.append(book)
            self.add_column_content(column)
        else:
            layout.add_spacer(0, expand=True)
            self.books.append(None)

        # if column == 1 and Settings.get(Option.CONFIG_FEATURE) == "1":
        #     from fs_uae_launcher.ui.config.browser import ConfigBrowser
        #     config_browser = ConfigBrowser(self)
        #     config_browser.set_min_height(200)
        #     layout.add(config_browser, fill=True, expand=True, margin=10)

        layout.add_spacer(0, 10 + Skin.EXTRA_GROUP_MARGIN)
        # if fs_uae_launcher.ui.get_screen_size()[1] >= 768:
        #     right_margin = 0
        #     if column == 0:
        #         bottom_panel = BottomPanel(self)
        #     elif column == 2:
        #         bottom_panel = GameInfoPanel(self)
        #     elif column == 1:
        #         bottom_panel = ScreenshotsPanel(self)
        #         right_margin = -10 - Skin.EXTRA_GROUP_MARGIN
        #     else:
        #         bottom_panel = None
        #     # FIXME:
        #     if bottom_panel is None:
        #         layout.add_spacer(0, Skin.get_bottom_panel_height())
        #     else:
        #         bottom_panel.set_min_height(Skin.get_bottom_panel_height())
        #         layout.add(bottom_panel, fill=True, margin_right=right_margin)
        # elif column == 1:
        #     group = LaunchGroup(self)
        #     layout.add(group, fill=True, margin=10, margin_top=0)
        #     layout.add_spacer(0, 10)

    def add_column_content(self, column):
        default_page_index = 0
        default_tab_index_offset = 0
        if column == 1:
            if Skin.fws():
                self.add_tab_spacer(5)
                self.add_tab_spacer(64)
            else:
                # if USE_MAIN_MENU:
                icon = fsui.Image("launcher:res/main_menu.png")
                self.menu_button = self.add_tab_button(
                    None, icon, gettext("Main Menu"),
                    menu_function=self.open_main_menu, left_padding=5)
            # default_tab_index_offset = 1
            # self.add_tab_spacer(60)
            # else:
            #    self.add_tab_spacer(10)

            # page_index = 0
            self.add_page(column, ConfigurationsPanel, "",
                          gettext("Configurations"),
                          gettext("Configuration Browser"))

            self.add_tab_spacer(0, expand=True)

        elif column == 2:
            self.new_tab_group()

            self.add_tab_spacer(10)
            self.add_page(
                column, MainPanel,
                "32x32/go-home",
                gettext("Config"), gettext("Main Configuration Options"))
            self.add_page(
                column, FloppiesPanel,
                "32x32/media-floppy",
                gettext("Floppies"), gettext("Floppy Drives"))
            self.add_page(
                column, CDPanel,
                "32x32/media-optical",
                gettext("CD-ROMs"), gettext("CD-ROM Drives"))
            # noinspection SpellCheckingInspection
            self.add_page(
                column, HardDrivesPanel,
                "32x32/drive-harddisk",
                gettext("Hard Drives"))
            self.add_scroll_page(
                column, RomRamPanel,
                "32x32/application-x-firmware",
                gettext("Hardware"), gettext("ROM and RAM"))
            self.add_page(
                column, InputPanel,
                "32x32/applications-games",
                gettext("Input"), gettext("Input Options"))
            self.add_scroll_page(
                column, ExpansionsPanel,
                "32x32/audio-card",
                gettext("Expansions"), gettext("Expansions"))
            self.add_scroll_page(
                column, AdditionalConfigPanel,
                "32x32/system-shutdown",
                gettext("Additional Configuration"),
                gettext("Additional Configuration"))

            self.add_tab_spacer(0, expand=True)
            self.add_tab_spacer(10)
            self.add_tab_spacer(64)
            self.add_tab_spacer(5)

        # column - 1 is the group id of the tab group
            self.select_tab(
                default_page_index + default_tab_index_offset, column - 1)
        self.books[column].set_page(default_page_index)

    def create_menu(self):
        menu = fsui.PopupMenu()

        if LauncherSettings.get(Option.DATABASE_AUTH):
            menu.add_item(gettext("Update Game Database"),
                          self.on_update_game_database)
        menu.add_item(gettext("Update File Database"),
                      self.on_update_file_database)

        menu.add_separator()

        menu.add_item(gettext("ADF Creator"), self.on_adf_creator)
        menu.add_item(gettext("HDF Creator"), self.on_hdf_creator)
        if LauncherSettings.get(Option.NETPLAY_FEATURE) != "0":
            menu.add_item(gettext("Net Play"), self.on_net_play)

        menu.add_separator()
        menu.add_item(gettext("Import Kickstarts") + "...",
                      self.on_import_kickstarts)
        menu.add_item(gettext("Amiga Forever Import") + "...",
                      self.on_import_kickstarts)

        menu.add_separator()
        self.add_user_menu_content(menu)

        menu.add_separator()
        # menu.add_item(
        #         gettext("Kickstarts & ROMs"), self.on_import_kickstarts)
        menu.add_preferences_item(
            gettext("Settings"), self.on_settings_button)

        menu.add_separator()
        menu.add_item(gettext("About {name}").format(
            name="OAGD.net"), self.on_what_is_this)
        menu.add_about_item(gettext("About {name}").format(
            name="FS-UAE Launcher"), self.on_about)

        menu.add_separator()
        menu.add_about_item(gettext("Quit"), self.on_quit)
        return menu

    def _add_page(self, book, instance, icon_name, title, tooltip):
        book.add_page(instance)
        if icon_name:
            icon = fsui.Image("launcher:res/{0}.png".format(icon_name))
        else:
            icon = None

        def function():
            book.set_page(instance)

        if icon:
            self.add_tab(function, icon, title, tooltip)
        return instance

    def add_page(self, column, content_class, icon_name, title, tooltip=""):
        book = self.books[column]
        instance = content_class(book)
        if content_class == MainPanel:
            self.main_panel = instance
        return self._add_page(book, instance, icon_name, title, tooltip)

    def add_scroll_page(self, column, content_class, icon_name, title,
                        tooltip=""):
        book = self.books[column]
        instance = ConfigScrollArea(book)
        content_instance = content_class(instance)
        instance.set_widget(content_instance)
        if content_class == MainPanel:
            self.main_panel = instance
        return self._add_page(book, instance, icon_name, title, tooltip)

    def on_custom_button(self):
        from .config.ConfigDialog import ConfigDialog
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
                self._menu, (0, self.menu_button.size()[1] - 2))
        if fsui.System.windows:
            self.main_menu_close_time = time.time()
        return self._menu

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
            menu.add_item(gettext("Upload Files to OAGD.net Locker"),
                          self.on_upload_locker_files)
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
        fstd.desktop.open_url_in_browser("https://oagd.net/about")

    def on_scan_button(self):
        from .scan import ScanDialog
        ScanDialog(self.get_window()).show()

    def on_settings_button(self):
        from .settings.settings_dialog import SettingsDialog
        SettingsDialog.open(self)

    def on_about(self):
        dialog = AboutDialog(self.get_window())
        dialog.show()

    def on_quit(self):
        self.close()

    def on_import_kickstarts(self):
        SetupDialog(self.get_window()).show()

    def on_update_file_database(self):
        self.on_scan_button()

    def on_update_game_database(self):
        RefreshWindow.open(self)

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
