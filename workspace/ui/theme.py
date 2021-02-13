import fsui
from fsgamesys.options.option import Option
from fsui.theme import Theme
from launcher.launcher_settings import LauncherSettings


class WorkspaceTheme(Theme):

    __instance = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        super().__init__()
        self.title_font = fsui.Font("Noto Sans", 15)
        # self.title_color = fsui.Color(0x80, 0x80, 0x80)
        self.title_color = fsui.Color(0x44, 0x44, 0x44)
        self.title_background = fsui.Color(0xFF, 0xFF, 0xFF)
        # self.title_separator_color = fsui.Color(0xe5, 0xe5, 0xe5)
        self.title_separator_color = fsui.Color(0xCC, 0xCC, 0xCC)
        self.window_background = fsui.Color(0xF2, 0xF2, 0xF2)
        # self.sidebar_background = fsui.Color(0xeb, 0xeb, 0xeb)
        self.sidebar_background = fsui.Color(0xE2, 0xE2, 0xE2)
        self.selection_background = fsui.Color(0x40, 0x80, 0xFF)

        self.title_glow_color = None
        # self.title_glow_color = fsui.Color(0xff, 0xcc, 0xff, 0x80)

    @property
    def has_close_buttons(self):
        return LauncherSettings.get(Option.LAUNCHER_CLOSE_BUTTONS) == "1"
