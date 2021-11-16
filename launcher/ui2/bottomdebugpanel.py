from fsui import Button, Color, HorizontalLayout, Panel
from fsui.context import get_window
from fswidgets.widget import Widget
from launcher.context import get_wsopen
from launcher.settings.settings_dialog import SettingsDialog
from system.exceptionhandler import exceptionhandler
from system.wsopen import (
    SYSTEM_C_LOADWB,
    SYSTEM_LAUNCHER,
    SYSTEM_PREFS,
    SYSTEM_PREFS_ADVANCED,
    SYSTEM_PREFS_APPEARANCE,
    SYSTEM_PREFS_WHDLOAD,
)


class BottomDebugPanel(Panel):
    def __init__(
        self, parent: Widget, *, close: bool = False, quit: bool = False
    ) -> None:
        super().__init__(parent)

        panel = Panel(self)
        panel.set_min_height(1)
        panel.set_background_color(Color(0x888888))
        self.layout.add(panel, fill=True)

        horilayout = HorizontalLayout()
        self.layout.add(
            horilayout,
            fill=True,
            expand=True,
            margin_top=10,
            margin_right=10,
            margin_bottom=10,
        )

        if close:
            button = Button(self, label="Close")
            button.activated.connect(self.__on_close)
            horilayout.add(button, margin_left=10)
        if quit:
            button = Button(self, label="Quit")
            button.activated.connect(self.__on_quit)
            horilayout.add(button, margin_left=10)

        button = Button(self, label="Settings")
        button.activated.connect(self.__on_settings)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="Launcher")
        button.activated.connect(self.__on_launcher)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="Prefs")
        button.activated.connect(self.__on_prefs)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="Advanced")
        button.activated.connect(self.__on_advanced_prefs)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="Appearance")
        button.activated.connect(self.__on_appearance_prefs)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="WHDLoad")
        button.activated.connect(self.__on_whdload_prefs)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="LoadWB")
        button.activated.connect(self.__on_loadwb)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="UH")
        button.activated.connect(self.__on_unhandled_exception)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="UH2")
        button.activated.connect(self.__on_unhandled_exception_2)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="UH3")
        button.activated.connect(self.__on_unhandled_exception_3)
        horilayout.add(button, margin_left=10)

        button = Button(self, label="GC")
        button.activated.connect(self.__on_garbage_collector)
        horilayout.add(button, margin_left=10)

    @exceptionhandler
    def __on_quit(self) -> None:
        # get_window(self).close()
        print("FIXME: Close all windows")
        from fsui.qt.toplevelwidget import internalWindowsSet

        for window in list(internalWindowsSet):
            window.close()

    @exceptionhandler
    def __on_advanced_prefs(self) -> None:
        get_wsopen(self)(SYSTEM_PREFS_ADVANCED)

    @exceptionhandler
    def __on_appearance_prefs(self) -> None:
        get_wsopen(self)(SYSTEM_PREFS_APPEARANCE)

    @exceptionhandler
    def __on_close(self) -> None:
        get_window(self).close()

    @exceptionhandler
    def __on_garbage_collector(self) -> None:
        print("-" * 79)
        print("Running garbage collector...")
        import gc

        gc.collect()
        print("Garbage collector done\n")

    @exceptionhandler
    def __on_launcher(self) -> None:
        get_wsopen(self)(SYSTEM_LAUNCHER)

    @exceptionhandler
    def __on_loadwb(self) -> None:
        get_wsopen(self)(SYSTEM_C_LOADWB)

    @exceptionhandler
    def __on_prefs(self) -> None:
        get_wsopen(self)(SYSTEM_PREFS)

    @exceptionhandler
    def __on_settings(self) -> None:
        SettingsDialog.open(self.getWindow())

    @exceptionhandler
    def __on_unhandled_exception(self) -> None:
        1 / 0

    # Without @exceptionhandler on purpose, for testing
    def __on_unhandled_exception_2(self) -> None:
        import sys

        print(sys.excepthook)
        1 / 0

    # Without @exceptionhandler on purpose, for testing
    def __on_unhandled_exception_3(self) -> None:
        import sys

        sys.excepthook = sys.__excepthook__
        print(sys.excepthook)
        1 / 0

    @exceptionhandler
    def __on_whdload_prefs(self) -> None:
        get_wsopen(self)(SYSTEM_PREFS_WHDLOAD)
