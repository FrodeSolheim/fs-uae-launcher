def app_main():
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
