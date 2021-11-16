import fsui
from fsui.qt.imageview import ImageView
from fswidgets.widget import Widget
from launcher.context import get_settings


class WarningBase(ImageView):
    def __init__(self, parent: Widget) -> None:
        self.warning_icon = fsui.Image("launcher:/data/16x16/warning_2.png")
        self.no_warning_icon = fsui.Image.create_blank(16, 16)
        super().__init__(parent, self.no_warning_icon)
        self._warning_state = None
        self.set_warning_state(False)

    def set_warning_state(self, warning_state: bool):
        if warning_state != self._warning_state:
            self._warning_state = warning_state
            self.set_image(
                self.warning_icon if warning_state else self.no_warning_icon
            )
            # if self.set_visible(warning_state):
            #     # FIXME: Maybe better if the warning occupied space always and
            #     # just had blank icon
            #     print("OverrideWarning: visible changed, updating parent layout")
            #     get_parent(self).layout.update()


class OverrideWarning(WarningBase):
    def __init__(self, parent: Widget, name: str) -> None:
        super().__init__(parent)

        # FIXME: Disabled because there is not a single config in the Launcher
        # anymore. Warnings, if any, must be moved to the launcher window
        # with indications that config overrides settings. This cannot happen
        # in the settings dialog any more...

        # setattr(self, "on_{0}_config".format(name), self.on_config)
        # ConfigBehavior(self, [name])
        # text = gettext(
        #     "Option {name} is overridden by current configuration".format(
        #         name=name
        #     )
        # )
        # self.set_tooltip(text)

    def on_config(self, value: str):
        self.set_warning_state(bool(value))


class OptionWarning(WarningBase):
    def __init__(self, parent: Widget, warning) -> None:
        super().__init__(parent)
        self.warning_function = warning[0]
        self.options = {
            option: get_settings(self).get(option) for option in warning[1]
        }
        # self._last_options = None

        # text = gettext(
        #     "Option {name} is overridden by current configuration".format(
        #         name=name
        #     )
        # )
        get_settings(self).add_listener(self)
        # self.set_tooltip(text)
        # self.set_background_color(fsui.Color(0xff0000))
        # print("WARNING", self)
        self.update_warning()

    def update_warning(self) -> None:
        # if self._last_options == self.options:
        #     # No need to update
        #     return
        warning = self.warning_function(self, self.options)
        # print(self.options, "=>", warning)
        # self._last_options = self.options.copy()
        self.set_warning_state(bool(warning))
        if warning:
            self.set_tooltip(warning)

    def on_setting(self, option: str, value: str) -> None:
        # print("OptionWarning.on_setting", option, value)
        if option in self.options:
            self.options[option] = value
            self.update_warning()
