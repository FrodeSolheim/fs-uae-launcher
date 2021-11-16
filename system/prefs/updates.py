from fswidgets.widget import Widget
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    VerticalFlexContainer,
)
from launcher.option import Option
from launcher.translation import t
from system.classes.shellobject import ShellObject, ShellOpenArgs, shellObject
from system.classes.windowcache import ShellWindowCache
from system.prefs.components.baseprefspanel import BasePrefsPanel
from system.prefs.components.baseprefswindow import BasePrefsWindow2
from system.prefs.components.defaultprefsbutton import DefaultPrefsButton
from system.prefs.components.prefscontrol import PrefsControl


@shellObject
class Updates(ShellObject):
    @staticmethod
    def shellOpen(args: ShellOpenArgs) -> None:
        ShellWindowCache.open(args, UpdatesPrefsWindow)


class UpdatesPrefsWindow(BasePrefsWindow2):
    def __init__(self):
        super().__init__(t("Preferences for updates"), UpdatesPrefsPanel)


class UpdatesPrefsPanel(BasePrefsPanel):
    def __init__(self, parent: Widget):
        super().__init__(parent)
        # FIXME: Use some kind of common min size via BasePrefsPanel?
        self.set_min_size((480, 0))
        # self.layout.set_padding(20, 20, 20, 20)
        # self.layout.set_padding(10, 10, 10, 10)

        with VerticalFlexContainer(self, style={"padding": 10}):
            AutomaticVersionCheckPrefsControl()
            with FlexContainer(style={"padding": 10}):
                DefaultPrefsButton()


class AutomaticVersionCheckPrefsControl(PrefsControl):
    def __init__(self):
        super().__init__(
            Option.CHECK_FOR_UPDATES,
            title=t("Automatic update check"),
            description=t(
                "When enabled, check for software updates on every startup."
            ),
        )
