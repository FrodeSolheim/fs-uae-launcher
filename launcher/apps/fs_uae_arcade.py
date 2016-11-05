import sys


def app_main():
    if "--help" in sys.argv:
        print(help_text)
        return
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
FS-UAE Arcade Help"

Options:
  --fullscreen
  --window
  --monitor=left|right|middle-left|middle-right  (Requires fullscreen)
  --platform=<platform>
"""
