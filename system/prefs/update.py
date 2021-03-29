from fsui import Window
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    VerticalFlexContainer,
)
from launcher.option import Option
from launcher.settings.option_ui import OptionUI
from launcher.translation import t
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefspanel import BasePrefsPanel
from system.prefs.components.baseprefswindow import BasePrefsWindow2
from system.prefs.components.defaultprefsbutton import DefaultPrefsButton
from system.prefs.components.prefscontrol import PrefsControl


@shellObject
class Update:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(UpdatePrefsWindow, **kwargs)


class UpdatePrefsWindow(BasePrefsWindow2):
    def __init__(self):
        super().__init__(t("Update preferences"), UpdatePrefsPanel)


class UpdatePrefsPanel(BasePrefsPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((480, 0))
        # self.layout.set_padding(20, 20, 20, 20)
        # self.layout.set_padding(10, 10, 10, 10)

        with VerticalFlexContainer(self, style={"padding": 10}):
            AutomaticVersionCheck()

            with FlexContainer(style={"padding": 10}):
                DefaultPrefsButton()

        # self.layout.add(
        #     OptionUI.create_group(
        #         self,
        #         Option.CHECK_FOR_UPDATES,
        #         # gettext("Automatically check for new Launcher version"),
        #         t("Automatically check for updates on startup"),
        #     ),
        #     fill=True,
        #     # margin_top=20,
        # )

        # self.layout.add(
        #     OptionUI.create_group(
        #         self,
        #         Option.CHECK_FOR_UPDATES,
        #         gettext("Automatically check for plugin updates"),
        #     ),
        #     fill=True,
        #     margin_top=20,
        # )


class AutomaticVersionCheck(PrefsControl):
    def __init__(self):
        super().__init__(
            Option.CHECK_FOR_UPDATES,
            title=t("Automatic update check"),
            description=t(
                "When enabled, check for software updates on every startup."
            ),
        )
