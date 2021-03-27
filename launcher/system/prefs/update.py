from launcher.i18n import gettext
from launcher.option import Option
from launcher.settings.option_ui import OptionUI
from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.common.baseprefspanel import BasePrefsPanel
from launcher.system.prefs.common.baseprefswindow import BasePrefsWindow2
from fsui import Window


def wsopen(window=None, **kwargs):
    return UpdatePrefs.open(openedFrom=window, **kwargs)


class UpdatePrefs:
    @staticmethod
    def open(*, openedFrom: Window = None, **kwargs):
        WindowCache.open(UpdatePrefsWindow, centerOnWindow=openedFrom)


class UpdatePrefsWindow(BasePrefsWindow2):
    def __init__(self):
        super().__init__("Update preferences", UpdatePrefsPanel)


class UpdatePrefsPanel(BasePrefsPanel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 20, 20, 20)
        # self.layout.set_padding(10, 10, 10, 10)
        import fsui

        self.layout.add(
            OptionUI.create_group(
                self,
                Option.CHECK_FOR_UPDATES,
                # gettext("Automatically check for new Launcher version"),
                gettext("Automatically check for updates on startup"),
            ),
            fill=True,
            # margin_top=20,
        )

        # self.layout.add(
        #     OptionUI.create_group(
        #         self,
        #         Option.CHECK_FOR_UPDATES,
        #         gettext("Automatically check for plugin updates"),
        #     ),
        #     fill=True,
        #     margin_top=20,
        # )
