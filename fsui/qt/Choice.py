from fsui.qt import QComboBox, Qt
from fsui.qt.signal import Signal, SignalWrapper
from .widget_mixin import WidgetMixin


class Choice(QComboBox, WidgetMixin):

    changed_signal = Signal()
    item_selected = Signal(int)
    ITEM_SEPARATOR = "---"

    def __init__(self, parent, items=None, cursor_keys=True):
        if items is None:
            items = []
        QComboBox.__init__(self, parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        self.inhibit_change_event = False
        self.cursor_keys = cursor_keys

        for i, item in enumerate(items):
            self.insertItem(i, item)

        if len(items) > 0:
            self.set_index(0)
        self.currentIndexChanged.connect(self.__current_index_changed)

        self.changed = SignalWrapper(self, "changed")
        # self.changed.inhibit = self.inhibit_signal

    def keyPressEvent(self, event):
        if not self.cursor_keys:
            print("cursor keys is false", event.key(), Qt.Key.Key_Up)
            if event.key() == Qt.Key_Up or event.key() == Qt.Key.Key_Down:
                print("ignoring")
                return
        super().keyPressEvent(event)

    # @contextmanager
    # def inhibit_signal(self, name):
    #     attr = "_inhibit_" + name
    #     old = getattr(self, attr, False)
    #     print("setattr", self, attr, True)
    #     setattr(self, attr, True)
    #     yield
    #     print("setattr", self, attr, old)
    #     setattr(self, attr, old)

    def add_item(self, label, icon=None):
        # item = QStandardItem(label)
        # if icon:
        #     item.setIcon(icon.qicon)
        # item.setSizeHint(QSize(-1, 24))
        if label == self.ITEM_SEPARATOR:
            self.insertSeparator(self.count())
        elif icon is not None:
            self.addItem(icon.qicon, label)
        else:
            self.addItem(label)
        return self.count() - 1

    def remove_item(self, index):
        self.removeItem(index)

    def __current_index_changed(self):
        # print("__current_index_changed", self.currentIndex(),
        #       "inhibit", self.inhibit_change_event)
        if not self.inhibit_change_event:
            # print("Choice.__current_index_changed")
            # if not getattr(self, "_inhibit_changed", False):
            if not self.changed.inhibit:
                if not getattr(self, "_inhibit_item_selected", False):
                    index = self.currentIndex()
                    self.item_selected.emit(index)
                self.changed.emit()
                self.on_changed()

    def get_index(self):
        return self.currentIndex()

    def set_index(self, index, signal=True):
        try:
            if not signal:
                self.inhibit_change_event = True
            self.setCurrentIndex(-1 if index is None else index)
        finally:
            if not signal:
                self.inhibit_change_event = False

    def set_item_text(self, index, text):
        self.setItemText(index, text)

    def on_changed(self):
        pass

    def __len__(self):
        return self.count()


class ItemChoice(Choice):
    def __init__(self, parent):
        Choice.__init__(self, parent)

    def update(self):
        # for i, item in enumerate(self.items):
        #     self.add_item(item["name"], icon=self.get_item_icon(i))
        old = self.inhibit_change_event
        old_index = self.get_index()
        self.inhibit_change_event = True
        self.clear()
        for i in range(self.get_item_count()):
            text = self.get_item_text(i)
            icon = self.get_item_icon(i)
            self.add_item(text, icon)
        if old_index < self.get_item_count():
            self.set_index(old_index)
        self.inhibit_change_event = old

    def select_item(self, index, signal=True):
        print("select_item", index)
        if index is None:
            self.set_index(-1, signal=signal)
        else:
            self.set_index(index, signal=signal)

    def on_changed(self):
        self.on_select_item(self.get_index())

    def on_select_item(self, index):
        pass
