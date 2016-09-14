from launcher.version import VERSION


def app_main():
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
