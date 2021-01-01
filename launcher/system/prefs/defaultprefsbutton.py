from fsui import Button
from launcher.context import get_settings
from launcher.i18n import gettext


class DefaultPrefsButton(Button):
    def __init__(self, parent, *, options):
        super().__init__(parent, gettext("Reset to defaults"))
        self.activated.connect(self.__on_reset_to_defaults)
        settings = get_settings(self)
        self.options = {option: settings.get(option) for option in options}
        self.update_enabled_state()

        self.remove_listener = settings.add_listener(self)
        # FIXME: Implement
        # self.destroy.connect(settings.add_listener(self))

    def on_destroy(self):
        # self.remove_listener()
        get_settings(self).remove_listener(self)
        super().on_destroy()

    # def __destroyed(self):
    #     get_settings(self).remove_listener(self)

    def update_enabled_state(self):
        self.set_enabled(any(self.options.values()))

    def on_setting(self, option, value):
        print("DefaultPrefsButton.on_setting", option, value)
        if option in self.options:
            self.options[option] = value
        self.update_enabled_state()

    # def update(self, observable, news):
    #     pass

    def __on_reset_to_defaults(self):
        settings = get_settings(self)
        for option in self.options:
            settings.set(option, "")
