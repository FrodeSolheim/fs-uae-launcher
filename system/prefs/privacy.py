from fsgamesys.options.option import Option
from fsui import Window
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    VerticalFlexContainer,
)
from launcher.fswidgets2.panel import Panel
from launcher.fswidgets2.text import Text
from launcher.translation import t
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefspanel import BasePrefsPanel
from system.prefs.components.baseprefswindow import BasePrefsWindow2
from system.prefs.components.defaultprefsbutton import DefaultPrefsButton
from system.prefs.components.prefscontrol import PrefsControl
from system.prefs.components.prefsdivider import PrefsDivider
from system.prefs.updates import AutomaticVersionCheckPrefsControl


@shellObject
class Privacy:
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
                ),
            ).disable()
            Text(
                "FIXME: Off-line mode is not fully implemented yet!",
                style={"margin": 10},
            )
            PrefsDivider()
            AutomaticVersionCheckPrefsControl()
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
