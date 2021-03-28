from typing import Dict

from fsui import Window
from launcher.system.c.whdload import WHDLoad
from launcher.system.classes.executedialog import ExecuteDialog
from launcher.system.exceptionhandler import exceptionhandler
from launcher.system.prefs.advancedprefswindow import AdvancedPrefsWindow

# from launcher.system.prefs.appearanceprefswindow import AppearancePrefsWindow
from launcher.system.prefs.arcadeprefswindow import ArcadePrefsWindow
from launcher.system.prefs.controllerprefswindow import ControllerPrefsWindow
from launcher.system.prefs.directoryprefswindow import DirectoryPrefsWindow
from launcher.system.prefs.filedatabaseprefswindow import (
    FileDatabasePrefsWindow,
)
from launcher.system.prefs.gamedatabaseprefswindow import (
    GameDatabasePrefsWindow,
)
from launcher.system.prefs.keyboardprefswindow import KeyboardPrefsWindow
from launcher.system.prefs.localeprefswindow import LocalePrefsWindow
from launcher.system.prefs.loggingprefswindow import LoggingPrefsWindow
from launcher.system.prefs.midiprefswindow import MidiPrefsWindow
from launcher.system.prefs.mouseprefswindow import MousePrefsWindow
from launcher.system.prefs.netplayprefswindow import NetPlayPrefsWindow
from launcher.system.prefs.openglprefswindow import OpenGLPrefsWindow

# from launcher.system.prefs.openretro.openretroprefswindow import (
#     OpenRetroPrefsWindow,
# )
from launcher.system.prefs.overscanprefswindow import OverscanPrefsWindow
from launcher.system.prefs.pluginprefswindow import PluginPrefsWindow
from launcher.system.prefs.powerprefswindow import PowerPrefsWindow
from launcher.system.prefs.screenmodeprefswindow import ScreenModePrefsWindow
from launcher.system.prefs.soundprefswindow import SoundPrefsWindow
from launcher.system.prefs.videoprefswindow import VideoPrefsWindow
from launcher.system.prefs.whdloadprefswindow import WHDLoadPrefsWindow
from launcher.system.prefs.workspaceprefswindow import WorkspacePrefsWindow
from launcher.system.tools.calculator import CalculatorWindow
from launcher.system.tools.databaseupdater import DatabaseUpdaterWindow
from launcher.system.tools.filescanner import FileScannerWindow
from launcher.system.utilities.checksum import ChecksumWindow
from launcher.system.utilities.clock import ClockWindow
from launcher.system.utilities.multiview import MultiView, MultiViewWindow
from launcher.ws.shell import (
    shell_icon,
    shell_isdir,
    shell_realcase,
    shell_window_geometry,
)
from launcher.ws.shellwindow import ShellWindow

SYSTEM_C_LOADWB = "system:c/loadwb"
# SYSTEM_C_GURU = "system:C/guru"
SYSTEM_LAUNCHER = "system:launcher"
SYSTEM_PREFS = "system:prefs"
SYSTEM_PREFS_ADVANCED = "system:prefs/advanced"
SYSTEM_PREFS_APPEARANCE = "system:prefs/appearance"
SYSTEM_PREFS_ARCADE = "system:prefs/arcade"
SYSTEM_PREFS_CONTROLLER = "system:prefs/controller"
# SYSTEM_PREFS_DIRECTORY = "system:prefs/directory"
SYSTEM_PREFS_FILEDATABASE = "system:prefs/filedatabase"
SYSTEM_PREFS_GAMEDATABASE = "system:prefs/gamedatabase"
SYSTEM_PREFS_KEYBOARD = "system:prefs/keyboard"
SYSTEM_PREFS_LOCALE = "system:prefs/locale"
SYSTEM_PREFS_LOGGING = "system:prefs/logging"
SYSTEM_PREFS_MIDI = "system:prefs/midi"
SYSTEM_PREFS_MOUSE = "system:prefs/mouse"
SYSTEM_PREFS_NETPLAY = "system:prefs/netplay"
SYSTEM_PREFS_OPENGL = "system:prefs/opengl"
SYSTEM_PREFS_OPENRETRO = "system:prefs/openretro"
SYSTEM_PREFS_OVERSCAN = "system:prefs/overscan"
SYSTEM_PREFS_PLUGIN = "system:prefs/plugin"
SYSTEM_PREFS_POWER = "system:prefs/power"
# SYSTEM_PREFS_PRIVACY = "system:prefs/privacy"
SYSTEM_PREFS_SCREENMODE = "system:prefs/screenmode"
SYSTEM_PREFS_SOUND = "system:prefs/sound"
SYSTEM_PREFS_STORAGE = "system:prefs/storage"
SYSTEM_PREFS_VIDEO = "system:prefs/video"
SYSTEM_PREFS_WHDLOAD = "system:prefs/whdload"
SYSTEM_PREFS_WORKSPACE = "system:prefs/workspace"

# TODO: Add some code (somewhere) to remember window position and sizes, and
# restore correctly, but take into account new window dimension constraints
# and monitors being removed (etc)

window_registry = {}  # type: Dict[str, Window]


def simple_window_cache(window_class, window_key, window=None, parent=None):
    try:
        win = window_registry[window_key]
    except LookupError:
        pass
    else:
        win.raise_and_activate()
        return
    win = window_class(None)

    def remove_window():
        del window_registry[window_key]

    window_registry[window_key] = win
    win.closed.connect(remove_window)
    win.show()
    # if parent is not None:
    #     print("\n\nCENTER ON PARENT\n\n")
    #     window.center_on_parent()
    if window is not None:
        print("\n\nCENTER ON WINDOW\n\n")
        win.center_on_window(window)


def wsopen_workspace(*, parent=None):
    from launcher.ws.workspacewindow import WorkspaceWindow

    simple_window_cache(WorkspaceWindow, SYSTEM_C_LOADWB)


def wsopen_guru(*, parent=None):
    @exceptionhandler
    def cause_exception():
        print(1 / 0)
        # try:
        #     print(1 / 0)
        # except Exception:
        #     try:
        #         print(2 + "string")
        #     except Exception:
        #         print(1 / 0)

    cause_exception()
    # import sys
    # sys.exit(1)


def wsopen_guru2(*, parent=None):
    print(1 / 0)


def wsopen_launcher(*, parent=None, **kwargs):
    from launcher.ui2.launcher2window import Launcher2Window

    window = Launcher2Window(parent=parent)
    window.show()


def wsopen_shell(path, args=None, window=None, parent=None, **kwargs):
    print(f"wsopen_shell {path} window={window} parent={parent}")

    def ShellWindowWrapper(parent):
        position, size = shell_window_geometry(path)
        win = ShellWindow(parent, path)
        if position is None and size is None:
            pass
        elif position is None:
            win.set_size(size)
        else:
            win.set_position_and_size(position, size)
        return win

    simple_window_cache(ShellWindowWrapper, path, window=window, parent=parent)


def wsopen_prefs_window(name, *, window=None, parent=None):
    print("wsopen_prefs_window", name)

    window_class = {
        SYSTEM_PREFS_ADVANCED: AdvancedPrefsWindow,
        # SYSTEM_PREFS_APPEARANCE: AppearancePrefsWindow,
        SYSTEM_PREFS_ARCADE: ArcadePrefsWindow,
        SYSTEM_PREFS_CONTROLLER: ControllerPrefsWindow,
        # SYSTEM_PREFS_DIRECTORY: DirectoryPrefsWindow,
        SYSTEM_PREFS_FILEDATABASE: FileDatabasePrefsWindow,
        SYSTEM_PREFS_GAMEDATABASE: GameDatabasePrefsWindow,
        SYSTEM_PREFS_KEYBOARD: KeyboardPrefsWindow,
        SYSTEM_PREFS_LOCALE: LocalePrefsWindow,
        SYSTEM_PREFS_LOGGING: LoggingPrefsWindow,
        SYSTEM_PREFS_MIDI: MidiPrefsWindow,
        SYSTEM_PREFS_MOUSE: MousePrefsWindow,
        SYSTEM_PREFS_NETPLAY: NetPlayPrefsWindow,
        SYSTEM_PREFS_OPENGL: OpenGLPrefsWindow,
        # SYSTEM_PREFS_OPENRETRO: OpenRetroPrefsWindow,
        SYSTEM_PREFS_OVERSCAN: OverscanPrefsWindow,
        SYSTEM_PREFS_PLUGIN: PluginPrefsWindow,
        SYSTEM_PREFS_POWER: PowerPrefsWindow,
        # SYSTEM_PREFS_PRIVACY: PrivacyPrefsWindow,
        SYSTEM_PREFS_SCREENMODE: ScreenModePrefsWindow,
        SYSTEM_PREFS_SOUND: SoundPrefsWindow,
        SYSTEM_PREFS_STORAGE: DirectoryPrefsWindow,
        SYSTEM_PREFS_VIDEO: VideoPrefsWindow,
        SYSTEM_PREFS_WHDLOAD: WHDLoadPrefsWindow,
        SYSTEM_PREFS_WORKSPACE: WorkspacePrefsWindow,
    }[name]
    simple_window_cache(window_class, name, window=window, parent=parent)


# def run_execute_dialog():
#     # dialog = ExecuteDialog(None)
#     # dialog.show()
#     # if dialog.show_modal():
#     #     command = dialog.command()
#     #     print("COMMAND:", command)
#     #     if ":" not in command:
#     #         print("FIXME: Hack, prefixing command with C: for now")
#     #         command = "C:" + command
#     #     wsopen(command)


def wsopen(name, args=None, *, window=None, parent=None):
    # FIXME: Case insensitive
    print(f"WSOpen name={name} window={window} parent={parent}")
    kwargs = {"parent": parent, "window": window}

    name_lower = name.lower()
    if name_lower.startswith("c:"):
        name_lower = name_lower.replace("c:", "system:c/")
    elif name_lower.startswith("sys:"):
        name_lower = name_lower.replace("sys:", "system:")

    if name_lower == SYSTEM_C_LOADWB:
        return wsopen_workspace(**kwargs)

    elif name_lower == "system:c/guru":
        return wsopen_guru(**kwargs)

    elif name_lower == "system:c/guru2":
        return wsopen_guru2(**kwargs)

    elif name_lower == SYSTEM_LAUNCHER:
        return wsopen_launcher(**kwargs)

    # elif name == SYSTEM_PREFS:
    #     return wsopen_prefs(**kwargs)
    # elif name == SYSTEM_PREFS_ADVANCED:
    #     return wsopen_prefs_window(name, parent=parent)
    # elif name == SYSTEM_PREFS_APPEARANCE:
    #     return wsopen_prefs_window(name, parent=parent)
    # elif name == SYSTEM_PREFS_PRIVACY:
    #     return wsopen_prefs_window(name, parent=parent)
    # elif name == SYSTEM_PREFS_WHDLOAD:
    #     return wsopen_prefs_window(name, parent=parent)

    elif name_lower == "system:prefs/platforms":
        return wsopen_shell(name_lower, window=window, **kwargs)

    elif name_lower.startswith("system:prefs/platforms"):
        return wsopen_prefs_window(name_lower, window=window)

    elif name_lower == "system:tools/calculator":
        simple_window_cache(CalculatorWindow, name_lower, window=window)
        return

    elif name_lower == "system:tools/filescanner":
        simple_window_cache(FileScannerWindow, name_lower, window=window)
        return

    elif name_lower == "system:tools/databaseupdater":
        simple_window_cache(DatabaseUpdaterWindow, name_lower, window=window)
        return

    elif name_lower == "system:utilities/checksum":
        # simple_window_cache(ClockWindow, name_lower)
        ChecksumWindow(None, None).show()
        return

    elif name_lower == "system:utilities/clock":
        simple_window_cache(ClockWindow, name_lower, window=window)
        return

    elif name_lower == "system:utilities/multiview":
        simple_window_cache(MultiViewWindow, name_lower, window=window)
        return

    elif name_lower == "special:execute":
        # run_execute_dialog()
        simple_window_cache(ExecuteDialog, name_lower, window=window)
        return

    elif name_lower == "test:flexbox":
        from launcher.fswidgets2.flexboxtestwindow import FlexboxTestWindow

        simple_window_cache(FlexboxTestWindow, name_lower, window=window)
        return

    elif shell_isdir(name_lower):
        return wsopen_shell(name_lower, **kwargs)

    elif name_lower.endswith(".info"):
        # real_path = shell_realcase(name)
        # icon = ShellIcon()
        icon = shell_icon(name_lower)
        print("-------------------------------")
        print(icon)
        tool = icon.defaulttool()
        if tool:
            print("Tool:", tool)
            return wsopen_tool(tool, tooltypes=icon.tooltypes(), iconpath=name)
        else:
            if shell_isdir(name_lower[:-5]):
                return wsopen_shell(name_lower[:-5], **kwargs)

    elif name_lower.startswith("system:"):
        try:
            module_name = "launcher." + name_lower.replace(":", ".").replace(
                "/", "."
            )
            print("Try importing", module_name)
            import importlib

            module = importlib.import_module(module_name)
        except ImportError:
            pass
        else:
            print(module)
            WorkspaceObject = getattr(module, "WorkspaceObject", None)
            if WorkspaceObject is not None:
                WorkspaceObject.open(window=window)
                return
            wsopen_function = getattr(module, "wsopen", None)
            if callable(wsopen_function):
                wsopen_function(window=window)
                return

    if name_lower.startswith("system:prefs/"):
        return wsopen_prefs_window(name_lower, window=window)

    raise Exception("Could not open '{}' (Unrecognized)".format(name))


def wsopen_tool(tool, *, tooltypes=None, iconpath=None):
    if tooltypes is None:
        tooltypes = []
    tool_lower = tool.lower()
    iconpath_lower = iconpath.lower()

    # FIXME: Should be able to cache window based on tool and iconpath...
    # probably. But possibly let tool choose to do this

    tool_lower = tool_lower.replace("sys:", "system:")

    if tool_lower == "multiview":
        tool_lower = "system:utilities/multiview"
    # elif tool_lower == "sys:utilities/multiview":
    #     tool_lower = "system:utilities/multiview"
    elif tool_lower == "whdload":
        tool_lower = "system:c/whdload"
    elif tool_lower == "c:whdload":
        tool_lower = "system:c/whdload"

    if tool_lower == "system:c/whdload":
        tool_class = WHDLoad
    elif tool_lower == "system:utilities/multiview":
        tool_class = MultiView
    else:
        tool_class = None

    iconpath_realcase = shell_realcase(iconpath)
    path = iconpath[:-5]
    # try:
    #     path_realcase = shell_realcase(path)
    #     # FIXME: Check correct exception here, LookupError? IOError?
    # except Exception:
    #     path_realcase = None

    if tool_class is not None:
        tool_class.wsopen(
            iconpath=iconpath_realcase, path=path, tooltypes=tooltypes
        )
    else:
        raise Exception(f"Cannot run tool {tool}")
