from launcher.i18n import gettext
from launcher.settings.scan_settings_page import ScanSettingsPage
from system.classes.shellobject import shellObject
from system.classes.windowcache import WindowCache
from system.prefs.components.baseprefswindow import BasePrefsWindow

# from pyqtgraph.console import ConsoleWidget as QConsoleWidget

@shellObject
class Python:
    @staticmethod
    def open(**kwargs):
        WindowCache.open(FileDatabasePrefsWindow, **kwargs)


from fsui.context import get_theme
from fsui.qt.qparent import QParent
from fsui.qt.qt import QFontMetrics, QPushButton, QSignal
from fsui.qt.widget import Widget


class ConsoleWidget(Widget):
    activated = QSignal()

    def __init__(self, parent):
        qwidget = QConsoleWidget(QParent(parent))
        super().__init__(parent, qwidget)
        self.style = {
            "flexGrow": 1
        }
        # self._qwidget.clicked.connect(self.__on_clicked)
        # self._qwidget.resize(600, 600)


class FileDatabasePrefsWindow(BasePrefsWindow):
    def __init__(self, parent=None):
        super().__init__(parent, title=gettext("File database preferences"))
        self.panel = ConsoleWidget(self)
        # self.panel.setWidth(600)
        self.set_min_height(400)
        self.set_min_width(600)
        # self.layout.set_min_size((600, 400))
        self.layout.add(self.panel, fill=True, expand=True)
        self.set_size((600, 600))
