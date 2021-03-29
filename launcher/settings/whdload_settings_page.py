import fsui
from fsgamesys.options.option import Option
from launcher.context import get_settings
from launcher.i18n import gettext
from launcher.settings.settings_page import SettingsPage
from system.classes.filepickerfield import FilePickerField
from system.classes.optionhelpbutton import OptionHelpButton
from system.prefs.components.defaultprefsbutton import DefaultPrefsButton

# TODO: Show warning symbol when whdload_path is not found
# TODO: Show warning symbol when whdload_key_path is not found
# TODO: Show warning symbol on version when whdload_path is set

# TODO: FIXME: Slightly bigger and clearer warning symbol


class WHDLoadSettingsPage(SettingsPage):
    WIDTH = 500

    def __init__(self, parent):
        super().__init__(parent)

        # label = fsui.MultiLineLabel(
        #     self,
        #     gettext(
        #         "These options only apply when you use the automatic WHDLoad "
        #         "support in FS-UAE Launcher & Arcade. (*)"
        #     ),
        #     self.WIDTH,
        # )
        # self.layout.add(label, fill=True, margin_top=0, margin_bottom=20)

        self.add_option(
            Option.WHDLOAD_VERSION,
            margin_top=0,
            warnings=[(key_path_override_warning, [Option.WHDLOAD_PATH])],
        )
        self.add_divider()
        # FIXME: Show units with grayed out text after the main label?
        # "Splash delay: [unit text in gray]"
        self.add_option(
            Option.WHDLOAD_SPLASH_DELAY,
            # gettext("Splash delay (1/50ths seconds)"),
            gettext("Splash delay"),
            # margin_top=20,
        )
        self.add_divider()
        self.add_option(
            Option.WHDLOAD_PRELOAD,
            gettext("Preload game into RAM"),
            # margin_top=20,
        )
        self.add_divider()
        self.add_option(
            Option.WHDLOAD_QUIT_KEY,
            gettext("Quit key"),
            # margin_top=20
        )
        self.add_divider()

        # FIXME: Label should have a flag to enable HTML-like markup.
        # markup=True. Should default to false and "escape" special chars.
        # label = fsui.Label(
        #     self,
        #     gettext("WHDLoad.key file (For WHDLoad < 18.3):").replace(
        #         "<", "&lt;"
        #     ),
        # )

        label = self.create_option_label(
            self,
            gettext("WHDLoad.key file"),
        )
        self.layout.add(label, margin_top=10)

        horilayout = fsui.HorizontalLayout()
        self.layout.add(horilayout, fill=True, margin_top=6)
        self.whdload_key_path_picker = FilePickerField(
            self,
            path=get_settings(self).get(Option.WHDLOAD_KEY_PATH),
            placeholder=gettext("Registration key For WHDLoad < 18.3"),
        )
        self.whdload_key_path_picker.changed.connect(
            self.__on_whdload_key_path_changed
        )
        horilayout.add(self.whdload_key_path_picker, expand=True)
        helpbutton = OptionHelpButton(self, Option.WHDLOAD_KEY_PATH)
        horilayout.add(helpbutton, fill=True, margin_left=10)

        self.add_divider()

        label = self.create_option_label(
            self,
            gettext("Custom WHDLoad executable"),
        )
        self.layout.add(label, margin_top=10)

        horilayout = fsui.HorizontalLayout()
        self.layout.add(horilayout, fill=True, margin_top=6)
        self.whdload_path_picker = FilePickerField(
            self,
            path=get_settings(self).get(Option.WHDLOAD_PATH),
            placeholder=gettext("Overrides WHDLoad version"),
        )
        self.whdload_path_picker.changed.connect(
            self.__on_whdload_path_changed
        )
        horilayout.add(self.whdload_path_picker, expand=True)
        helpbutton = OptionHelpButton(self, Option.WHDLOAD_PATH)
        horilayout.add(helpbutton, fill=True, margin_left=10)

        # self.add_divider()

        label = fsui.MultiLineLabel(
            self,
            gettext(
                "These options only apply when you use the automatic WHDLoad "
                "support in FS-UAE Launcher & Arcade, for example when "
                "running WHDLoad variants from the online game database."
            ),
            self.WIDTH,
        )
        self.layout.add(label, fill=True, margin_top=20)

        self.layout.add(
            DefaultPrefsButton(
                self,
                options=[
                    Option.WHDLOAD_KEY_PATH,
                    Option.WHDLOAD_PATH,
                    Option.WHDLOAD_PRELOAD,
                    Option.WHDLOAD_QUIT_KEY,
                    Option.WHDLOAD_SPLASH_DELAY,
                    Option.WHDLOAD_VERSION,
                ],
            ),
            margin_top=20,
        )

    def __on_whdload_path_changed(self):
        get_settings(self).set(
            Option.WHDLOAD_PATH, self.whdload_path_picker.path()
        )

    def __on_whdload_key_path_changed(self):
        get_settings(self).set(
            Option.WHDLOAD_KEY_PATH, self.whdload_key_path_picker.path()
        )


def key_path_override_warning(self, options):
    # FIXME: Only considering settings now, maybe warning should apply
    # also when config overrides this...?
    # Maybe options should contain merged settings/config ?
    # Actually, this is problematic then multiple gscontext is is use,
    # maybe config override warnings might have to go away...
    if options.get(Option.WHDLOAD_PATH):
        return gettext(
            "Custom WHDLoad executable overrides the selected version"
        )
    return None
