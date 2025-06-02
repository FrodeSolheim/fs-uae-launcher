from fsui.qt import Qt, QSize, Signal, QFont
from fsui.qt import QListView, QStandardItemModel, QStandardItem
from .widget_mixin import WidgetMixin


class ListView(QListView, WidgetMixin):

    item_selected = Signal(int)
    item_activated = Signal(int)

    def __init__(self, parent, border=True):
        # self = QListView(parent.get_container())
        QListView.__init__(self, parent.get_container())
        # Widget.__init__(self, parent)
        # self.setAutoFillBackground(True)
        self.init_widget(parent)
        self.viewport().installEventFilter(self.get_window())
        self.verticalScrollBar().installEventFilter(self.get_window())
        if not border:
            self.setFrameStyle(0)

        # self.setSelectionModel()
        self._model = QStandardItemModel(self)
        # self.setModel(self._model)
        self.setModel(self._model)
        # self.itemSelectionChanged.connect(self._on_selection_changed)
        selection_model = self.selectionModel()
        print("QListView selectionModel", selection_model)
        selection_model.selectionChanged.connect(self.__selection_changed)
        self.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.doubleClicked.connect(self.__double_clicked)
        # self.returnPressed.connect(self.__double_clicked)
        # self.activated.connect(self.__double_clicked)
        self._row_height = 26

    def set_row_height(self, height):
        self._row_height = height

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.__double_clicked()
        else:
            super().keyPressEvent(event)

    def __double_clicked(self):
        index = self.get_index()
        if index is not None:
            self.on_activate_item(index)
            self.item_activated.emit(index)

    def on_activate_item(self, index):
        pass

    def __selection_changed(self):
        index = self.get_index()
        self.on_select_item(index)
        self.item_selected.emit(index)

    def set_default_icon(self, image):
        pass

    def set_items(self, items):
        self._model.clear()
        for item in items:
            if isinstance(item, str):
                self.add_item(item)
            elif isinstance(item, dict):
                label = item["label"]
                icon = item.get("icon", None)
                bold = item.get("bold", False)
                self.add_item(label, icon, bold)
            else:
                label, icon = item
                self.add_item(label, icon)

    def clear(self):
        self._model.clear()

    def add_item(self, label, icon=None, bold=False):
        item = QStandardItem(label)
        if icon:
            try:
                item.setIcon(icon.qicon(16))
            except TypeError:
                item.setIcon(icon.qicon)
        item.setSizeHint(QSize(-1, self._row_height))
        if bold:
            font = self.font()
            font.setWeight(QFont.Weight.DemiBold)
            item.setFont(font)
        self._model.appendRow(item)

    def get_item(self, index):
        return self._model.item(index).text()

    def get_item_count(self):
        return self._model.rowCount()

    def get_index(self):
        indices = self.selectionModel().selectedIndexes()
        if len(indices) == 0:
            return None
        return indices[0].row()

    def set_index(self, index):
        if index is None:
            index = -1
        # print(self.rootIndex)
        # idx = QModelIndex.createIndex(index)
        idx = self._model.index(index, 0)
        self.scrollTo(idx)
        self.setCurrentIndex(idx)

    def select_item(self, index):
        self.set_index(index)

    def on_select_item(self, index):
        print("calling item_selected.emit")
        self.item_selected.emit(index)
