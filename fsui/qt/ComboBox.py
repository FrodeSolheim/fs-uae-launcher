from fsui.qt import QComboBox
from .widget_mixin import WidgetMixin


class ComboBox(QComboBox, WidgetMixin):
    def __init__(self, parent, items=[], read_only=False):
        QComboBox.__init__(self, parent.get_container())
        # self = QComboBox(parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        # self.setEditable(not read_only)
        print(
            "FIXME: ComboBox not respecting read_only"
            "(because of missing lineEdit then"
        )
        self.setEditable(True)
        self.lineEdit().installEventFilter(self.get_window())

        self.set_items(items)

        if len(items) > 0:
            self.set_index(0)
        self.currentIndexChanged.connect(self.__current_index_changed)

    def __current_index_changed(self):
        self.on_changed()

    def get_min_width(self):
        # We don't want min width to be decided by the contents of the
        # line edit
        return 50

    def set_items(self, items):
        self.clear()
        for i, item in enumerate(items):
            self.insertItem(i, item)

    def set_item_text(self, item, text):
        self.setItemText(item, text)

    def get_index(self):
        # return self.GetSelection()
        return self.currentIndex()

    def set_index(self, index):
        self.setCurrentIndex(index)

    def get_text(self):
        return self.lineEdit().text()

    def set_text(self, text):
        self.lineEdit().setText(text)

    def on_changed(self):
        pass
