import launcher.version
from arcade.Application import Application
from arcade.glui.imageloader import ImageLoader
from arcade.ui.arcade_window import (ArcadeWindow, check_argument, fullscreen,
                                     maximized)
from fsbc.init import initialize_application
from fsbc.settings import Settings
from fsbc.system import macosx

from .gnome3 import handle_gnome_extensions, running_in_gnome_3

K_UI_MODE_ALL_HIDDEN = 3
K_UI_OPTION_AUTO_SHOW_MENU_BAR = 1 << 0


def os_x_set_system_ui_mode(mode, option):
    # noinspection PyUnresolvedReferences
    import objc
    # noinspection PyUnresolvedReferences
    from Foundation import NSBundle

    bundle = NSBundle.bundleWithPath_(
        "/System/Library/Frameworks/Carbon.framework"
    )
    objc.loadBundleFunctions(
        bundle, globals(), (("SetSystemUIMode", b"III", ""),)
    )
    # noinspection PyUnresolvedReferences
    SetSystemUIMode(mode, option)


def main():
    application = Application()
    initialize_application("fs-uae-arcade", version=launcher.version.VERSION)

    # fs_width, fs_height = fsui.get_screen_size()
    # cursor_position = None

    # use_window = False
    # use_window_decorations = True
    # use_fullscreen = True
    # use_fullscreen_window = False
    # use_top_clock = check_argument("top_clock") != "0"
    # use_top_logo = check_argument("top_logo") != "0"

    if macosx:
        if fullscreen() or maximized():
            if check_argument("system_autohide") == "1":
                os_x_set_system_ui_mode(
                    K_UI_MODE_ALL_HIDDEN, K_UI_OPTION_AUTO_SHOW_MENU_BAR
                )
    elif running_in_gnome_3():
        if fullscreen() or maximized():
            # use_fullscreen = False
            # use_window_decorations = False
            # use_window = "maximized"
            if check_argument("system_autohide") == "1":
                handle_gnome_extensions()
                # cursor_position = fs_width - 1, fs_height - 1
                # use_top_clock = False
                # use_top_logo = False
                # app.settings["fs-uae:fullscreen-mode::default"] = "window"
        else:
            # We want a normal window.
            pass

    Settings.instance().set("__arcade", "1")

    # if windows:
    #     pass
    # elif macosx:
    #     # use_fullscreen_window = True
    #     # Settings.instance().set("__fullscreen_mode", "window")
    #     pass
    # else:
    #     # app.settings["fs-uae:fullscreen-mode::default"] = "window"
    #     pass

    # if check_argument("fullscreen"):
    #     use_fullscreen = check_argument("fullscreen") == "1"
    #
    # if "--fullscreen-mode=fullscreen" in sys.argv:
    #     use_fullscreen_window = False
    # elif "--fullscreen-mode=window" in sys.argv:
    #     use_fullscreen_window = True
    #
    # if "--maximize" in sys.argv:
    #     use_window = "maximized"
    #     use_fullscreen = False
    #
    # if "--no-window-decorations" in sys.argv:
    #     use_window_decorations = False

    # app.settings["game-center:fullscreen"] = \
    #     "1" if use_fullscreen else "0"
    # if use_fullscreen_window:
    #     app.settings["game-center:fullscreen-mode"] = "window"
    # else:
    #     app.settings["game-center:fullscreen-mode"] = ""
    # app.settings["game-center:window-decorations"] = \
    #     "1" if use_window_decorations else "0"
    # app.settings["game-center:maximize"] = \
    #     "1" if use_window == "maximized" else "0"
    # app.settings["game-center:top-clock"] = "1" if use_top_clock else "0"
    # app.settings["game-center:top-logo"] = "1" if use_top_logo else "0"

    ArcadeWindow().show_auto()

    # if cursor_position is not None:
    #     os.environ["FSGS_RETURN_CURSOR_TO"] = "{0},{1}".format(
    #         cursor_position[0], cursor_position[1])

    application.run()
    print("application.run returned")

    application.stop()
    ImageLoader.get().stop()

    application.wait()

    print(" --- arcade.arcade_main.main is done ---")
    return
