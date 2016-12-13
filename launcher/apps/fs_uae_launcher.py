import sys
from launcher.version import VERSION


def app_main():
    if "--help" in sys.argv:
        print(help_text)
        return
    print("FS-UAE Launcher {0}".format(VERSION))

    from launcher.fs_uae_launcher import FSUAELauncher
    application = FSUAELauncher()

    application.start()
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
