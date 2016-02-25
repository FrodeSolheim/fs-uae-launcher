from fsui.qt.helpers import QParent
from fsui.qt.widget import Widget


class Adapter(Widget):

    def __init__(self, parent, widget):
        super().__init__()
        self._widget = widget
        self._widget.setParent(QParent(parent))
        # self._widget.move(0, 2000)

    # def on_resize(self):
    #     self._widget.setGeometry(0, 0, self.width(), self.height())
