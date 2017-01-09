import sys
from launcher.version import VERSION


def app_main():
    if "--help" in sys.argv:
        print(help_text)
        return
    print("FS-UAE Launcher {0}".format(VERSION))

    from launcher.fs_uae_launcher import FSUAELauncher
    application = FSUAELauncher()
    try:
        application.start()
    except Exception as e:
        import fsui
        fsui.show_error("An error occurred starting FS-UAE Launcher:\n\n" +
                        repr(e) + "\n\nFS-UAE Launcher cannot start "
                        "because of this.", "FS-UAE Launcher")
    else:
        application.run()
        application.save_settings()

    # from fs_uae_launcher.netplay.IRC import IRC
    # IRC.stop()

    from fsbc.signal import Signal
    Signal("quit").notify()
    print("app_main done")


help_text = """\
FS-UAE Launcher Help"

Options:
  --no-gui                             Do not show launch progress dialog

TODO: Add more documentation
"""
