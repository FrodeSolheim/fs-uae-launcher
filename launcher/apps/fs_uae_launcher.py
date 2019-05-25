import platform
import sys
import traceback

from launcher.version import VERSION


def app_main():
    if "--help" in sys.argv:
        print(help_text)
        return
    print("FS-UAE Launcher {0}".format(VERSION))
    print(sys.argv)
    print(platform.uname())

    for i, arg in enumerate(sys.argv[:]):
        if arg == "--fullscreen" or arg == "--fullscreen=1":
            sys.argv[i] = "--settings:fullscreen=1"
        elif arg == "--no-fullscreen" or arg == "--fullscreen=0":
            sys.argv[i] = "--settings:fullscreen=0"

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
                "An error occurred starting FS-UAE Launcher:\n\n"
                + repr(e)
                + "\n\nFS-UAE Launcher cannot start "
                "because of this.",
                "FS-UAE Launcher",
            )
            fsui.show_error(traceback.format_exc())
    else:
        app.run()
        app.save_settings()

    # from fs_uae_launcher.netplay.IRC import IRC
    # IRC.stop()

    from fsbc.signal import Signal

    Signal("quit").notify()
    print("app_main done")


help_text = """\
FS-UAE Launcher {version}

Options:
  --new-config[=<platform>]

Options for directly launching games:
  --fullscreen
  --no-fullscreen
  --no-gui                             Do not show launch progress dialog
  --no-auto-detect-game                Do not auto-detect game from archive

TODO: Add more documentation

Or you can execute fs-uae-launcher <command> - where command is one of:
  * arcade                             Launch FS-UAE Arcade
  * fs-uae-netplay-server              Run netplay server
  * list-dirs                          List directories used by the Launcher
  * list-plugins                       List installed plugins
""".format(
    version=VERSION
)
