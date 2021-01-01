from fsbc.settings import Settings
from fsgs.options.constants import (
    LAUNCHER_WINDOW_TITLE,
    WORKSPACE_WINDOW_TITLE,
)


def get_setting(name):
    return Settings.instance().get(name)


def get_launcher_window_title():
    value = get_setting(LAUNCHER_WINDOW_TITLE)
    if not value:
        value = "FS-UAE Launcher"
    return value


def get_workspace_window_title():
    value = get_setting(WORKSPACE_WINDOW_TITLE)
    if not value:
        value = "Launcher Workspace"
    return value
