from fsui.qt.qparent import QParent
from fsui.qt.qt import QWidget
from fswidgets.widget import Widget


class Adapter(Widget):
    def __init__(self, parent: Widget, widget: QWidget):
        # self._widget = widget
        widget.setParent(QParent(parent))
        super().__init__(parent, widget)
        # self._widget.move(0, 2000)

        # def on_resize(self):
        #     self._widget.setGeometry(0, 0, self.width(), self.height())
