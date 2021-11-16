import fsui
from fsgamesys.options.option import Option
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.settings.settings_page import SettingsPage
from system.prefs.components.notworking import PrefsNotWorkingWarningPanel


class LoggingSettingsPage(SettingsPage):
    def __init__(self, parent: Widget) -> None:
        super().__init__(parent)

        PrefsNotWorkingWarningPanel(parent=self)
        self.layout.add_spacer(20)

        icon = fsui.Icon("settings", "pkg:workspace")
        title = gettext("Logging")
        subtitle = ""
        self.add_header(icon, title, subtitle)

        label = fsui.MultiLineLabel(
            self,
            gettext(
                "The following options may affect performance, "
                "so only enable them when needed for testing or "
                "debugging purposes."
            ),
            640,
        )
        self.layout.add(label, fill=True, margin_top=20)

        self.add_option(Option.LOG_AUTOSCALE)
        self.add_option(Option.LOG_INPUT)
