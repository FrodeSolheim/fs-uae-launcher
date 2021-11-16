from fsui import PopupMenu
from fsui.qt.toplevelwidget import internalWindowsSet
from launcher.i18n import gettext
from system.exceptionhandler import exceptionhandler
from system.wsopen import wsopen


class WorkspaceMenu(PopupMenu):
    def __init__(self, parent):
        # # FIXME: parent not needed?
        super().__init__()

        self.add_item(
            gettext("Execute command..."),
            self.__on_execute_command,
        )
        self.add_separator()
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

        self.add_item(gettext("New Launcher window"), self.__on_new_window)
        self.add_item(gettext("Preferences"), self.__on_preferences)
        self.add_item(gettext("Tools"), self.__on_tools)
        self.add_item(gettext("Utilities"), self.__on_utilities)

        self.add_separator()
        self.add_about_item(gettext("About..."), self.__on_about)
        self.add_item(gettext("Quit..."), self.__on_quit)

    def __on_about(self):
        # FIXME
        print("on_about")

    @exceptionhandler
    def __on_cause_chained_exception(self):
        try:
            print(1 / 0)
        except Exception:
            try:
                print(2 + "string")
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

    def __on_execute_command(self):
        wsopen("Special:Execute")

    def __on_new_window(self):
        wsopen("SYS:Launcher")

    def __on_preferences(self):
        wsopen("SYS:Prefs")

    def __on_quit(self):
        print("FIXME: Close all windows")

        for window in list(internalWindowsSet):
            window.close()

    def __on_tools(self):
        wsopen("SYS:Tools")

    def __on_utilities(self):
        wsopen("SYS:Utilities")
