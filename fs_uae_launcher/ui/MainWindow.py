import sys
import time
from fs_uae_launcher.ui.config.configscrollarea import ConfigScrollArea
import fstd.desktop
from fs_uae_launcher.ui.bottombar.GameInfoPanel import GameInfoPanel
from fs_uae_launcher.ui.bottombar.BottomPanel import BottomPanel
from fs_uae_launcher.ui.bottombar.ScreenshotsPanel import ScreenshotsPanel
from fs_uae_launcher.ui.bottombar.LaunchGroup import LaunchGroup
from fs_uae_workspace.shell import shell_open
import fsui as fsui
from fsbc.Application import Application
import fs_uae_launcher.ui
from ..Config import Config
from ..Signal import Signal
from fs_uae_launcher.Options import Option
from ..Settings import Settings
from ..I18N import gettext
from .AboutDialog import AboutDialog
from .Book import Book
from .CDPanel import CDPanel
from .ConfigurationsPanel import ConfigurationsPanel
from .Constants import Constants
from .config.additionalconfigpanel import AdditionalConfigPanel
from .config.expansionspanel import ExpansionsPanel
from .config.romrampanel import RomRamPanel
from .FloppiesPanel import FloppiesPanel
from .HardDrivesPanel import HardDrivesPanel
from .InputPanel import InputPanel
from .MainPanel import MainPanel
from .NetplayPanel import NetplayPanel
from .SetupDialog import SetupDialog
from .Skin import Skin
from .statusbar.StatusBar import StatusBar
from .WindowWithTabs import WindowWithTabs

USE_MAIN_MENU = 1


class MainWindow(WindowWithTabs):

    instance = None

    def __init__(self, fsgs, icon):
        self.fsgs = fsgs
        border = True
        maximize = None
        if fs_uae_launcher.ui.get_screen_size()[1] <= 768:
            if fstd.desktop.is_running_gnome_3():
                border = False
                if "--window-border" in sys.argv:
                    border = True
            maximize = True
        if "--no-window-border" in sys.argv:
            border = False
        title = "FS-UAE Launcher {0}".format(Application.instance().version)

        WindowWithTabs.__init__(self, None, title, border=border)
        if icon:
            self.set_icon_from_path(icon)

        self.tab_panels = []
        self.books = []
        self.menu_button = None
        self.main_menu_close_time = 0
        self.user_menu_close_time = 0
        self.user_button = None
        self.main_panel = None

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
            if fs_uae_launcher.ui.get_screen_size()[0] >= need_width:
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

        if fs_uae_launcher.ui.get_screen_size()[1] >= 768:
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
        # self.menu = self.create_menu()
        if fsui.System.macosx and fsui.toolkit == 'wx':
            # import wx
            # self.tools_menu = self.create_menu()
            # menu_bar = wx.MenuBar()
            # menu_bar.Append(self.tools_menu._menu, _("Tools"))
            # self.SetMenuBar(menu_bar)
            pass

        self.status_bar = StatusBar(self)
        self.layout.add(self.status_bar, fill=True)

        was_maximized = Settings.get("maximized") == "1"

        if Settings.get(Option.CONFIG_FEATURE) == "1":
            if fs_uae_launcher.ui.get_screen_size()[0] > 1300:
                if fs_uae_launcher.ui.get_screen_size()[1] > 1000:
                    self.layout.min_width = 1280
                    self.layout.min_height = 720

        self.set_size(self.layout.get_min_size())

        self.center_on_screen()
        if was_maximized or maximize:
            self.maximize()

        Signal.add_listener("scan_done", self)
        Signal.add_listener("setting", self)

        self.update_title()

    def on_destroy(self):
        print("MainWindow.destroy")
        Signal.remove_listener("scan_done", self)
        Signal.remove_listener("setting", self)

    def on_scan_done_signal(self):
        print("MainWindow.on_scan_done_signal")
        Config.update_kickstart()

    def update_title(self):
        auth = Settings.get(Option.DATABASE_AUTH)
        if auth:
            username = Settings.get(Option.DATABASE_USERNAME)
            login_info = username
        else:
            login_info = gettext("Not logged in")
        title = "FS-UAE Launcher {0} ({1})".format(
            Application.instance().version, login_info)
        self.set_title(title)

    def on_setting(self, key, value):
        if key == Option.DATABASE_AUTH:
            self.update_title()

    def on_resize(self):
        print("on_resize, size =", self.get_size(), self.is_maximized())
        if self.is_maximized():
            Settings.set("maximized", "1")
        else:
            Settings.set("maximized", "0")

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

        fsui.Window.on_resize(self)

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

            if column == 2 and Settings.get(Option.CONFIG_FEATURE) == "1":
                if fs_uae_launcher.ui.get_screen_size()[0] >= 1280:
                    from fs_uae_launcher.ui.config.browser import ConfigBrowser
                    config_browser = ConfigBrowser(self)
                    config_browser.set_min_width(200)
                    hor_layout.add(config_browser, fill=True, expand=0.5,
                                   margin=10)

            if column == 2:
                # if fs_uae_launcher.ui.get_screen_size()[1] >= 1024:
                #     vert_layout.add_spacer(100)

                hor2_layout = fsui.HorizontalLayout()
                vert_layout.add(hor2_layout, fill=True, margin=10)
                launch_group = LaunchGroup(self)
                hor2_layout.add_spacer(0, expand=True)
                hor2_layout.add(launch_group)

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
            # if USE_MAIN_MENU:
            icon = fsui.Image("fs_uae_launcher:res/main_menu.png")
            self.menu_button = self.add_tab_button(
                None, icon, gettext("Main Menu"),
                menu_function=self.open_main_menu, left_padding=5)
            default_tab_index_offset = 1
            # self.add_tab_spacer(60)
            # else:
            #    self.add_tab_spacer(10)

            # page_index = 0
            self.add_page(column, ConfigurationsPanel, "",
                          gettext("Configurations"),
                          gettext("Configuration Browser"))

            # self.add_tab_spacer(194)

            # self.add_tab_spacer(10)
            # self.add_tab_spacer(10)

            # info_panel = self.add_tab_panel(InfoPanel, expand=False)
            # info_panel = \
            # self.add_tab_panel(InfoPanel, expand=True)
            # info_panel.set_min_width(316)
            # info_panel.set_min_width(326)
            # info_panel.set_min_width(272)

            self.add_tab_spacer(0, expand=True)

            # self.add_tab_spacer(10)
            # icon = fsui.Image("fs_uae_launcher:res/user_menu.png")
            # self.user_button = self.add_tab_button(
            #     None, icon, gettext("User Menu"),
            #     menu_function=self.open_user_menu,
            #     left_padding=5, right_padding=5)

            # self.add_tab_spacer(10)
            # if not USE_MAIN_MENU:
            #     icon = fsui.Image("fs_uae_launcher:res/tab_scan.png")
            #     self.add_tab_button(self.on_scan_button, icon,
            #                         gettext("Scan"),
            #                         gettext("Open Scan Dialog"))
            #     icon = fsui.Image("fs_uae_launcher:res/tab_settings.png")
            #     self.add_tab_button(self.on_settings_button, icon,
            #                         gettext("Settings"))

        elif column == 2:
            self.new_tab_group()

            self.add_tab_spacer(10)
            self.add_page(
                column, MainPanel,
                "crystal/32x32/apps/starthere",
                gettext("Config"), gettext("Main Configuration Options"))
            self.add_page(
                column, InputPanel,
                "tab_input_2",
                gettext("Input"), gettext("Input Options"))
            self.add_page(
                column, FloppiesPanel,
                "crystal/32x32/devices/3floppy_unmount_fs",
                gettext("Floppies"), gettext("Floppy Drives"))
            self.add_page(
                column, CDPanel,
                "crystal/32x32/devices/cdrom_unmount_fs",
                gettext("CD-ROMs"), gettext("CD-ROM Drives"))
            self.add_page(
                column, HardDrivesPanel,
                "crystal/32x32/apps/harddrive2",
                gettext("Hard Drives"))
            self.add_scroll_page(
                column, ExpansionsPanel,
                "crystal/32x32/apps/hardware_fs",
                gettext("Expansions"), gettext("Expansions"))
            self.add_scroll_page(
                column, RomRamPanel,
                "crystal/32x32/apps/kcmmemory",
                gettext("Hardware"), gettext("ROM and RAM"))
            self.add_scroll_page(
                column, AdditionalConfigPanel,
                "crystal/32x32/apps/kcontrol_fs",
                gettext("Additional Configuration"),
                gettext("Additional Configuration"))

            # self.add_tab_spacer(10)

            # if USE_MAIN_MENU:
            # self.add_tab_spacer(80)
            # else:
            #     icon = fsui.Image("fs_uae_launcher:res/tab_custom.png")
            #     self.add_tab_button(
            #         self.on_custom_button, icon, gettext("Custom"),
            #         gettext("Edit Custom Options"))
            #     self.add_tab_spacer(60)

            # self.add_tab_spacer(60)
            # self.add_tab_spacer(0, expand=True)
            # launch_group = LaunchGroup(self)
            # self.add_tab_panel(launch_group)
            # self.add_tab_panel(LaunchGroup)
            # self.add_tab_panel(LaunchGroup, expand=False)
            # self.add_tab_spacer(10)

            self.add_tab_spacer(0, expand=True)
            # FIXME: correct spacing so tabs are centered
            # self.add_tab_spacer(64)

            if Settings.get(Option.NETPLAY_FEATURE) == "1":
                # page_index += 1
                self.add_page(
                    column, NetplayPanel,
                    "crystal/32x32/apps/browser_fs",
                    gettext("Net Play"))
            self.add_tab_spacer(10)

        # column - 1 is the group id of the tab group
            self.select_tab(
                default_page_index + default_tab_index_offset, column - 1)
        self.books[column].set_page(default_page_index)

    def create_menu(self):
        menu = fsui.Menu()

        if Settings.get(Option.DATABASE_AUTH):
            menu.add_item(gettext("Update Game Database"),
                          self.on_update_game_database)
        menu.add_item(gettext("Update File Database"),
                      self.on_update_file_database)

        menu.add_separator()
        menu.add_item(gettext("ADF Creator") + "...", self.on_adf_creator)
        menu.add_item(gettext("HDF Creator") + "...", self.on_hdf_creator)

        menu.add_separator()
        menu.add_item(gettext("Import Kickstarts") + "...",
                      self.on_import_kickstarts)
        menu.add_item(gettext("Amiga Forever Import") + "...",
                      self.on_import_kickstarts)

        menu.add_separator()
        self.add_user_menu_content(menu)

        menu.add_separator()
        menu.add_preferences_item(
            gettext("Settings") + "...", self.on_settings_button)

        menu.add_separator()
        menu.add_item(gettext("About {name}").format(
            name="OAGD.net") + "...", self.on_what_is_this)
        menu.add_about_item(gettext("About {name}").format(
            name="FS-UAE Launcher") + "...", self.on_about)

        menu.add_separator()
        menu.add_about_item(gettext("Quit"), self.on_quit)
        return menu

    def _add_page(self, book, instance, icon_name, title, tooltip):
        book.add_page(instance)
        if icon_name:
            icon = fsui.Image("fs_uae_launcher:res/{0}.png".format(icon_name))
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

    def open_main_menu(self):
        if fsui.System.windows:
            if time.time() - getattr(self, "main_menu_close_time", 0) < 0.2:
                return
        self.menu = self.create_menu()
        if Skin.use_unified_toolbar():
            self.popup_menu(self.menu, (0, -2))
        else:
            self.menu_button.popup_menu(
                self.menu, (0, self.menu_button.size[1] - 2))
        if fsui.System.windows:
            self.main_menu_close_time = time.time()

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
        if Settings.get(Option.DATABASE_AUTH):
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
        shell_open("Workspace:Prefs/User/Login", parent=self)

    def on_log_out(self):
        print("on_log_out")
        shell_open("Workspace:Prefs/User/Logout", parent=self)

    def on_what_is_this(self):
        print("on_what_is_this")
        fstd.desktop.open_url_in_browser("http://oagd.net/about")

    def on_scan_button(self):
        from .ScanDialog import ScanDialog
        ScanDialog(self.get_window()).show()

    def on_settings_button(self):
        from .settings.SettingsDialog import SettingsDialog
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
        shell_open("Workspace:Tools/Refresh", parent=self)

    def on_upload_locker_files(self):
        print("on_upload_locker_files")
        shell_open("Workspace:Tools/LockerUploader", parent=self)

    def on_adf_creator(self):
        print("on_adf_creator")
        shell_open("Workspace:Tools/ADFCreator", parent=self)

    def on_hdf_creator(self):
        print("on_hdf_creator")
        shell_open("Workspace:Tools/HDFCreator", parent=self)
