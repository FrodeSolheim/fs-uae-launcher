from fsgamesys.options.option import Option
from fsui import Window
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    VerticalFlexContainer,
)
from launcher.fswidgets2.panel import Panel
from launcher.system.classes.shellobject import shellObject
from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.components.baseprefspanel import BasePrefsPanel
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow2
from launcher.system.prefs.components.defaultprefsbutton import (
    DefaultPrefsButton,
)
from launcher.system.prefs.components.prefscontrol import PrefsControl
from launcher.system.prefs.components.prefsdivider import PrefsDivider
from launcher.system.prefs.update import AutomaticVersionCheck
from launcher.translation import t


@shellObject
class UpdatePrefs:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(PrivacyPrefsWindow, **kwargs)


class PrivacyPrefsWindow(BasePrefsWindow2):
    def __init__(self):
        super().__init__(t("Privacy preferences"), PrivacyPrefsPanel)


class PrivacyPrefsPanel(BasePrefsPanel):
    WIDTH = 500

    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 0))
        with VerticalFlexContainer(self, style={"padding": 10}):
            PrefsControl(
                # FIXME: Option.NETWORK_ACCCESS?
                Option.OFFLINE_MODE,
                title=t("Allow network access"),
                description=t(
                    "When disabled, do not try to do anything over network "
                    "including version checks, automatic downloads, etc. "
                    "FIXME: Not implemented everywhere in the app yet!"
                ),
            ).disable()
            PrefsDivider()
            AutomaticVersionCheck()
            PrefsDivider()
            PrefsControl(
                Option.AUTOMATIC_ERROR_REPORTING,
                title=t("Automatic error reporting"),
                description=t(
                    "When enabled, automatically send error reports to the "
                    "developer when exceptions occur. It is off by default "
                    "to respect your privacy, but please consider enabling it "
                    "to help the developer detect and fix bugs."
                ),
            )
            PrefsDivider()
            PrefsControl(
                Option.AUTOMATIC_ERROR_REPORTING_INCLUDE_USER_ID,
                title=t("Include user ID in error reports"),
                description=t(
                    "When enabled, include your OpenRetro.org user ID (when "
                    "logged in) in error reports to help group together "
                    "related errors from you."
                ),
            )
            with FlexContainer(style={"padding": 10}):
                DefaultPrefsButton()
