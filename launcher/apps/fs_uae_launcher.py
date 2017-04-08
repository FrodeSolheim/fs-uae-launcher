import sys
import traceback

from launcher.version import VERSION


def app_main():
    if "--help" in sys.argv:
        print(help_text)
        return
    print("FS-UAE Launcher {0}".format(VERSION))

    from launcher.launcherapp import LauncherApp
    app = LauncherApp()
    if "--no-auto-detect-game" in sys.argv:
        sys.argv.remove("--no-auto-detect-game")
        LauncherApp.auto_detect_game = False
    try:
        app.start()
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        import fsui
        if "--no-gui" in sys.argv:
            pass
        else:
            fsui.show_error(
                "An error occurred starting FS-UAE Launcher:\n\n" +
                repr(e) + "\n\nFS-UAE Launcher cannot start "
                "because of this.", "FS-UAE Launcher")
    else:
        app.run()
        app.save_settings()

    # from fs_uae_launcher.netplay.IRC import IRC
    # IRC.stop()

    from fsbc.signal import Signal
    Signal("quit").notify()
    print("app_main done")


help_text = """\
FS-UAE Launcher Help"

Options:
  --no-gui                             Do not show launch progress dialog
  --no-auto-detect-game                Do not try to auto-detect game from archive

  --new-config[=<platform>]

TODO: Add more documentation
"""
