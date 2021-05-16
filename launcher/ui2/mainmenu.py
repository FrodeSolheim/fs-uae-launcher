import weakref

from fscore.developermode import DeveloperMode
from fsgamesys.product import Product
from fsui import PopupMenu
from fswidgets.widget import Widget
from launcher.context import useTranslation
from system.exceptionhandler import exceptionhandler
from system.prefs.controller import Controller
from system.utilities.updater import Updater
from system.wsopen import wsopen

# menu = fsui.PopupMenu()

#             menu.add_item(
#                 t("Update Game Database"), self.on_update_game_database
#             )

#             app_name = "FS-UAE Launcher"
#         menu.add_about_item(
#             t("About {name}").format(name=app_name), self.on_about
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
    def __init__(self, parent: Widget):
        # # FIXME: parent not needed?
        super().__init__()

        self._parent_ref = weakref.ref(parent)

        t = useTranslation()

        # self.add_item(
        #         t("Update Game Database"), self.on_update_game_database
        #     )
        # app_name = "{} Launcher".format(Product.base_name)

        if DeveloperMode.enabled:
            self.add_item(t("New window"), self.__on_new_window)
            self.add_separator()

        if Product.is_fs_uae():
            self.add_item(
                t("Execute command..."),
                self.__on_execute_command,
            )
            self.add_separator()

        self.add_item(
            t("Scan files..."),
            self.__on_file_scanner,
        )
        self.add_item(
            t("Sync game database..."),
            self.__on_database_updater,
        )

        self.add_separator()

        if DeveloperMode.enabled:
            self.add_item(
                t("Trigger exception..."),
                self.__on_cause_exception,
            )
            self.add_item(
                t("Trigger exception (chained)..."),
                self.__on_cause_chained_exception,
            )
            self.add_item(
                t("Trigger exception (double handlers)..."),
                self.__on_cause_exception_doubled_handled,
            )
            self.add_separator()

        # Utilities

        # if Product.is_fs_uae():
        #     self.add_item(t("Tools"), self.__on_tools)
        #     # self.add_item(t("Utilities"), self.__on_utilities)

        self.add_separator()
        self.add_item(t("Preferences"), self.__on_preferences)
        self.add_item(t("Controllers"), self.onGameControllers)
        self.add_separator()
        self.add_item(t("Utilities"), self.__on_utilities)
        self.add_item(t("Check for updates..."), self.onCheckForUpdates)

        # self.add_item(t("Check for updates..."), self.onCheckForUpdates)

        # self.add_item(t("Advanced"), self.__on_advanced_preferences)
        # self.add_item(t("Appearance"), self.__on_appearance_preferences)
        # self.add_item(t("WHDLoad"), self.__on_whdload_preferences)

        # self.add_separator()
        # self.add_about_item(
        #     # t("About {name}").format(name=app_name), self.__on_about
        #     t("About..."),
        #     self.__on_about,
        # )

    def getWindow(self):
        return self._parent_ref()

    def onCheckForUpdates(self):
        Updater.open(window=self.getWindow())

    def onGameControllers(self):
        Controller.open(window=self.getWindow())

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
        wsopen("SYS:Tools/DatabaseUpdater", window=self.getWindow())

    def __on_execute_command(self):
        wsopen("Special:Execute")

    def __on_file_scanner(self):
        wsopen("SYS:Tools/FileScanner", window=self.getWindow())

    def __on_new_window(self):
        wsopen("SYS:Launcher")

    def __on_preferences(self):
        wsopen("SYS:Prefs", window=self.getWindow())

    def __on_tools(self):
        wsopen("SYS:Tools", window=self.getWindow())

    def __on_utilities(self):
        wsopen("SYS:Utilities", window=self.getWindow())

    def __on_whdload_preferences(self):
        wsopen("SYS:Prefs/WHDLoad", window=self.getWindow())
