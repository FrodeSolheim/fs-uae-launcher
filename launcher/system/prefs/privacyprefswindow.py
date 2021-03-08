from fsui.context import get_theme
from fsgamesys.options.option import Option
from fsui import MultiLineLabel, Panel
from launcher.i18n import gettext
from launcher.settings.option_ui import OptionUI
from launcher.system.prefs.baseprefswindow import BasePrefsWindow
from launcher.system.prefs.defaultprefsbutton import DefaultPrefsButton


class PrivacyPrefsWindow(BasePrefsWindow):
    def __init__(self, parent):
        super().__init__(parent, title=gettext("Privacy preferences"))
        self.panel = PrivacyPrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class PrivacyPrefsPanel(Panel):
    WIDTH = 500

    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        # self.set_min_size((540, 100))
        self.layout.set_padding(20, 20, 20, 20)
        theme = get_theme(self)

        # label = Label(self, "Titlebar font:")
        # self.layout.add(label, fill=True)

        self.layout.add(
            OptionUI.create_group(
                self,
                Option.CHECK_FOR_UPDATES,
                gettext("Automatic version check"),
            ),
            fill=True,
            # margin_top=20,
        )
        self.layout.add(
            MultiLineLabel(
                self,
                gettext(
                    "When enabled, check for new version on every startup."
                ),
                self.WIDTH,
            ),
            fill=True,
            margin_top=10,
            bottom=10 + theme.label_vertical_padding(),
        )

        OptionUI.add_divider(self, self.layout)

        self.layout.add(
            OptionUI.create_group(
                self,
                Option.AUTOMATIC_ERROR_REPORTING,
                gettext("Automatic error reporting"),
            ),
            fill=True,
            # margin_top=10,
        )
        self.layout.add(
            MultiLineLabel(
                self,
                gettext(
                    "When enabled, automatically send error reports to the "
                    "developer when an exception occurs. It is off by default "
                    "to respect your privacy, but please consider enabling it "
                    "to help the developer detect and fix bugs."
                ),
                self.WIDTH,
            ),
            fill=True,
            margin_top=10,
            bottom=10 + theme.label_vertical_padding(),
        )

        OptionUI.add_divider(self, self.layout)

        self.layout.add(
            OptionUI.create_group(
                self,
                Option.AUTOMATIC_ERROR_REPORTING_INCLUDE_USER_ID,
                gettext("Include user ID in error reports"),
            ),
            fill=True,
            margin_top=10,
        )
        self.layout.add(
            MultiLineLabel(
                self,
                gettext(
                    "When enabled, include your OpenRetro.org user ID (when "
                    "logged in) in error reports to help group together "
                    "related errors from you."
                ),
                self.WIDTH,
            ),
            fill=True,
            margin_top=10,
            bottom=theme.label_vertical_padding(),
        )

        # OptionUI.add_divider(self, self.layout)

        self.layout.add(
            DefaultPrefsButton(
                self,
                options=[
                    Option.AUTOMATIC_ERROR_REPORTING,
                    Option.AUTOMATIC_ERROR_REPORTING_INCLUDE_USER_ID,
                    Option.CHECK_FOR_UPDATES,
                ],
            ),
            margin_top=20,
        )
