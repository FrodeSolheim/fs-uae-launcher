from fsui import Panel
from launcher.i18n import gettext
from launcher.system.classes.shellobject import shellObject
from launcher.system.classes.windowcache import WindowCache
from launcher.system.prefs.components.baseprefswindow import BasePrefsWindow


@shellObject
class MIDI:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(MidiPrefsWindow, **kwargs)


class MidiPrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("MIDI preferences"))
        self.panel = MidiPrefsPanel(self)
        self.layout.add(self.panel, fill=True, expand=True)


class MidiPrefsPanel(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        # FIXME
        self.set_min_size((540, 100))
        self.layout.set_padding(20, 0, 20, 20)
