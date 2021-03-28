from fsui import Button
from launcher.context import get_settings
from launcher.fswidgets2.parentstack import ParentStack
from launcher.i18n import gettext


class DefaultPrefsButton(Button):
    def __init__(self, parent=None, *, options=None):
        autoParent = False
        if parent is None:
            parent = ParentStack.top()
            autoParent = True

        super().__init__(parent, gettext("Reset to defaults"))
        self.activated.connect(self.__on_reset_to_defaults)
        settings = get_settings(self)

        self.remove_listener = settings.add_listener(self)
        # FIXME: Implement
        # self.destroy.connect(settings.add_listener(self))
        if autoParent:
            parent.layout.add(self)

        # Add automatically discovered settings
        optionsOnPanel = None
        while parent and optionsOnPanel is None:
            parent = parent.getParent()
            optionsOnPanel = getattr(parent, "optionsOnPanel", None)
        options = options or []
        if optionsOnPanel is not None:
            options.extend(optionsOnPanel)
            # for optionName in optionsOnPanel:
            #     self.options[optionName] = settings.get(optionName)

        self.options = {option: settings.get(option) for option in options}
        self.update_enabled_state()

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
