import fsui
import fsbc.system
from fsbc.util import memoize
from .Constants import Constants
from ..option import Option
from ..launcher_settings import LauncherSettings
import fsboot
try:
    import workspace
except ImportError:
    workspace = None

# LEVEL = 0xce
LEVEL = 0xeb
# LEVEL = 0xe4


class LauncherTheme(object):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        from fsui.qt import QPalette
        palette = QPalette()
        self.sidebar_list_background = fsui.Color(
            palette.color(QPalette.Base))
        self.sidebar_list_row_height = 28
        self.sidebar_list_row_text = fsui.Color(
            palette.color(QPalette.HighlightedText))
        self.sidebar_list_row_background = fsui.Color(
            palette.color(QPalette.Highlight))

        if Skin.fws():
            from workspace.ui.theme import WorkspaceTheme as WorkspaceTheme
            ws_theme = WorkspaceTheme.instance()
            self.sidebar_list_background = ws_theme.sidebar_background
            self.sidebar_list_row_text = fsui.Color(0xff, 0xff, 0xff)
            self.sidebar_list_row_background = ws_theme.selection_background
        elif Skin.windows_10():
            self.sidebar_list_background = fsui.Color(0xe2, 0xe2, 0xe2)

    @property
    def has_close_buttons(self):
        return LauncherSettings.get(Option.LAUNCHER_CLOSE_BUTTONS) == "1"


class Skin(object):

    EXTRA_GROUP_MARGIN = 0
    _fws = None

    @classmethod
    def use_unified_toolbar(cls):
        return False

    @classmethod
    def get_background_color(cls):
        c = cls._get_background_color()
        if c is None:
            return None
        return c.copy()

    @classmethod
    @memoize
    def _get_background_color(cls):
        # FIXME: Rename to launcher_bg/background_color and document.
        value = LauncherSettings.get("ui_background_color")
        if len(value) == 7 and value[0] == "#":
            def convert(s):
                return int(s, 16)
            r = convert(value[1:3])
            g = convert(value[3:5])
            b = convert(value[5:7])
            return fsui.Color(r, g, b)
        if cls.windows_10():
            return None
        elif cls.fws():
            return None
        elif fsbc.system.windows:
            # FIXME: Should really just check for Windows XP here, or maybe
            # just remove it altogether.
            return fsui.Color(LEVEL, LEVEL, LEVEL)
        elif fsbc.system.macosx:
            return fsui.Color(237, 237, 237)
        return None

    @classmethod
    def set_background_color(cls, widget):
        color = cls.get_background_color()
        if color is not None:
            widget.set_background_color(cls.get_background_color())

    @classmethod
    def get_window_padding_left(cls):
        return 10 + cls.EXTRA_GROUP_MARGIN

    @classmethod
    def get_window_padding_right(cls):
        return 10 + cls.EXTRA_GROUP_MARGIN

    @classmethod
    def get_window_padding_bottom(cls):
        return 10 + cls.EXTRA_GROUP_MARGIN

    @classmethod
    def get_bottom_margin(cls):
        return 10 + cls.get_window_padding_bottom()

    @classmethod
    def get_bottom_panel_height(cls):
        return (Constants.SCREEN_SIZE[1] + 20 + 2 + 1 + 1 +
                cls.get_bottom_margin())

    @classmethod
    def windows_10(cls):
        return fsui.theme == "fusion" and fsui.theme_variant == "windows10"

    @classmethod
    def fws(cls):
        if cls._fws is None:
            if fsboot.get("fws") == "1":
                cls._fws = True
            else:
                cls._fws = LauncherSettings.get(Option.LAUNCHER_THEME) == "fws"
            if workspace is None:
                cls._fws = None
        return cls._fws
