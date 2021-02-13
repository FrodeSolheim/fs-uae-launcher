from fsbc.settings import Settings
from fsgamesys.options.constants import (
    LAUNCHER_WINDOW_TITLE,
    WORKSPACE_WINDOW_TITLE,
)
from fsgamesys.product import Product


def get_setting(name):
    return Settings.instance().get(name)


def get_launcher_window_title():
    value = get_setting(LAUNCHER_WINDOW_TITLE)
    if not value:
        if Product.is_fs_uae() or Product.is_openretro():
            value = "{} Launcher".format(Product.base_name)
        else:
            # Experimental styling of name, similar to styling of FSEMU
            # emulators done by GameDriver.
            value = "{}  ·  Launcher".format(Product.base_name)
    return value


def get_workspace_window_title():
    value = get_setting(WORKSPACE_WINDOW_TITLE)
    if not value:
        value = "{} Workspace".format(Product.base_name)
    return value
