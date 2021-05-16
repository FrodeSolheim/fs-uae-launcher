# pylint: disable=import-error,no-name-in-module
from PyQt5.QtWebKitWidgets import QWebView

from fsui.qt.qparent import QParent
from fsui.qt.qt import QUrl
from fswidgets.widget import Widget

# from PyQt5.QtWebEngineWidgets import QWebEngineView


class WebView(Widget):
    def __init__(self, parent):
        super().__init__(parent, QWebView(QParent(parent)))
        # self.widget().move(0, 2000)
        # if not border:
        #     self.setFrameStyle(fsui.qt.QFrame.NoFrame)
        # self.setReadOnly(read_only)
        # if font_family:
        #     print("FIXME: not respecting font_family yet")
        #     font = fsui.qt.QFont("Courier")
        #     # font.setStyleHint(QtGui.QFont.TypeWriter)
        #     self.setFont(font)
        # if text:
        #     self.append_text(text)
        # self.textChanged.connect(self.__text_changed)

    def load(self, url):
        print("load", url)
        self._qwidget.load(QUrl(url))
