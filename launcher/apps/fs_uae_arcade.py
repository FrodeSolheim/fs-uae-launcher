import platform
import sys

from launcher.version import VERSION


def app_main():
    if "--help" in sys.argv:
        print(help_text)
        return
    print("FS-UAE Arcade {0}".format(VERSION))
    print(sys.argv)
    print(platform.uname())

    for i, arg in enumerate(sys.argv):
        if arg.startswith("--monitor="):
            sys.argv[i] = "--settings:monitor=" + arg[10:]
    try:
        import arcade.arcade_main

        arcade.arcade_main.main()
        print("main returned")

    finally:
        from fsbc.application import Application

        application = Application.instance()
        if application:
            print("calling Application stop")
            Application.get().stop()

        from fsbc.signal import Signal

        print("sending quit signal")
        Signal("quit").notify()


help_text = """\
FS-UAE Arcade {version}

Options:
  --fullscreen
  --window[=maximize]
  --monitor=left|right|middle-left|middle-right  (Requires fullscreen)
  --platform=<platform>                Open with chosen platform pre-selected
  --favorites                          Open with favorites pre-selected
  --disable-search                     Disable search function in Arcade UI

TODO: Add more documentation
""".format(version=VERSION)
