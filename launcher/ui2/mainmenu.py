import weakref

from fscore.developermode import DeveloperMode
from fsgamesys.product import Product
from fsui import PopupMenu
from launcher.i18n import gettext
from launcher.system.exceptionhandler import exceptionhandler
from launcher.system.wsopen import wsopen

# menu = fsui.PopupMenu()

#             menu.add_item(
#                 gettext("Update Game Database"), self.on_update_game_database
#             )

#             app_name = "FS-UAE Launcher"
#         menu.add_about_item(
#             gettext("About {name}").format(name=app_name), self.on_about
#         )

# # FIXME: WORKAROUND FOR SOMETHING?
# def open_main_menu(self):
#     if fsui.System.windows:
#         if time.time() - getattr(self, "main_menu_close_time", 0) < 0.2:
#             return
#     self._menu = self.create_menu()
#     if Skin.use_unified_toolbar():
#         self.popup_menu(self._menu, (0, -2))
#     else:
#         self.menu_button.popup_menu(
#             self._menu, (0, self.menu_button.size()[1] - 2)
#         )
#     if fsui.System.windows:
#         self.main_menu_close_time = time.time()
#     return self._menu


class MainMenu(PopupMenu):
    def __init__(self, parent):
        # # FIXME: parent not needed?
        super().__init__()

        self._parent_ref = weakref.ref(parent)

        # self.add_item(
        #         gettext("Update Game Database"), self.on_update_game_database
        #     )
        # app_name = "{} Launcher".format(Product.base_name)

        if DeveloperMode.enabled:
            self.add_item(gettext("New window"), self.__on_new_window)
            self.add_separator()

        if Product.is_fs_uae():
            self.add_item(
                gettext("Execute command..."),
                self.__on_execute_command,
            )
            self.add_separator()

        self.add_item(
            gettext("Scan files..."),
            self.__on_file_scanner,
        )
        self.add_item(
            gettext("Update game database..."),
            self.__on_database_updater,
        )

        self.add_separator()

        if DeveloperMode.enabled:
            self.add_item(
                gettext("Trigger exception..."),
                self.__on_cause_exception,
            )
            self.add_item(
                gettext("Trigger exception (chained)..."),
                self.__on_cause_chained_exception,
            )
            self.add_item(
                gettext("Trigger exception (double handlers)..."),
                self.__on_cause_exception_doubled_handled,
            )
            self.add_separator()

        self.add_item(gettext("Preferences"), self.__on_preferences)
        if Product.is_fs_uae():
            self.add_item(gettext("Tools"), self.__on_tools)
            self.add_item(gettext("Utilities"), self.__on_utilities)

        # self.add_item(gettext("Advanced"), self.__on_advanced_preferences)
        # self.add_item(gettext("Appearance"), self.__on_appearance_preferences)
        # self.add_item(gettext("WHDLoad"), self.__on_whdload_preferences)

        # self.add_separator()
        # self.add_about_item(
        #     # gettext("About {name}").format(name=app_name), self.__on_about
        #     gettext("About..."),
        #     self.__on_about,
        # )

    def __on_about(self):
        print("on_about")

    # def __on_advanced_preferences(self):
    #     wsopen("SYS:Prefs/Advanced")

    # def __on_appearance_preferences(self):
    #     wsopen("SYS:Prefs/Appearance")

    @exceptionhandler
    def __on_cause_chained_exception(self):
        try:
            print(1 / 0)
        except Exception:
            try:
                print(2 + "string")  # type: ignore
            except Exception:
                print(1 / 0)

    @exceptionhandler
    def __on_cause_exception(self):
        print(1 / 0)

    @exceptionhandler
    def __on_cause_exception_doubled_handled(self):
        # This will call a method which is protected by an exception handler,
        # while also having an exception handler itself.
        self.__on_cause_exception_doubled_handled_2()

    @exceptionhandler
    def __on_cause_exception_doubled_handled_2(self):
        print(1 / 0)

    def __on_database_updater(self):
        wsopen("SYS:Tools/DatabaseUpdater", window=self._parent_ref())

    def __on_execute_command(self):
        wsopen("Special:Execute")

    def __on_file_scanner(self):
        wsopen("SYS:Tools/FileScanner", window=self._parent_ref())

    def __on_new_window(self):
        wsopen("SYS:Launcher")

    def __on_preferences(self):
        wsopen("SYS:Prefs", window=self._parent_ref())

    def __on_tools(self):
        wsopen("SYS:Tools", window=self._parent_ref())

    def __on_utilities(self):
        wsopen("SYS:Utilities", window=self._parent_ref())

    def __on_whdload_preferences(self):
        wsopen("SYS:Prefs/WHDLoad", window=self._parent_ref())
