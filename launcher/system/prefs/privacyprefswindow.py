from fsgs.options.option import Option
from fsui import (
    Panel,
    MultiLineLabel,
)
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
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 0, 20, 20)

        # label = Label(self, "Titlebar font:")
        # self.layout.add(label, fill=True)

        label = MultiLineLabel(
            self,
            gettext(
                "The Launcher checks for new version on every startup by "
                "default, but you can disable this."
            ),
            500,
        )
        self.layout.add(label, fill=True, margin_top=20)
        self.layout.add(
            OptionUI.create_group(
                self,
                Option.CHECK_FOR_UPDATES,
                gettext("Automatic version check"),
            ),
            fill=True,
            margin_top=10,
        )

        label = MultiLineLabel(
            self,
            gettext(
                "The Launcher can automatically send error reports to the "
                "developer when an exception occurs. It is recommended to "
                "keep this option enabled to help fix bugs."
            ),
            500,
        )
        self.layout.add(label, fill=True, margin_top=24)
        self.layout.add(
            OptionUI.create_group(
                self,
                Option.AUTOMATIC_ERROR_REPORTING,
                gettext("Automatic error reporting"),
            ),
            fill=True,
            margin_top=10,
        )

        label = MultiLineLabel(
            self,
            gettext(
                "You can also choose to include additional data to help group "
                "together multiple error reports from you."
            ),
            500,
        )
        self.layout.add(label, fill=True, margin_top=20)
        self.layout.add(
            OptionUI.create_group(
                self,
                Option.AUTOMATIC_ERROR_REPORTING_INCLUDE_USER_ID,
                gettext("Include user ID in error reports (when logged in)"),
            ),
            fill=True,
            margin_top=10,
        )

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
