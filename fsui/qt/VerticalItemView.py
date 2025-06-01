import weakref
from fsui.qt import Qt, QSize, QAbstractListModel, QListView, QBrush, Signal
from .widget_mixin import WidgetMixin


class Model(QAbstractListModel):
    def __init__(self, parent):
        QAbstractListModel.__init__(self, parent)
        self.parent = weakref.ref(parent)
        self.count = 0

    # def set_item_count(self, count):
    #     self.count = count

    def rowCount(self, parent):
        # print("returning count", self.count, "for parent", parent)
        # return self.count
        return self.parent().get_item_count()

    def data(self, index, role):
        row = index.row()
        # print("data for", index, "role", role)
        if role == Qt.ItemDataRole.SizeHintRole:
            height = self.parent()._row_height
            return QSize(height, height)
        elif role == Qt.ItemDataRole.DecorationRole:
            icon = self.parent().get_item_icon(row)
            if icon:
                return icon.qpixmap
        elif role == Qt.ItemDataRole.DisplayRole:
            return self.parent().get_item_text(row)
        elif role == Qt.ItemDataRole.ForegroundRole:
            color = self.parent().get_item_text_color(row)
            if color is not None:
                return QBrush(color)
        # return QVariant()


class VerticalItemView(QListView, WidgetMixin):

    item_selected = Signal(int)
    item_activated = Signal(int)

    def __init__(self, parent, border=True):
        QListView.__init__(self, parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        self.viewport().installEventFilter(self.get_window())
        self.verticalScrollBar().installEventFilter(self.get_window())
        if not border:
            self.setFrameStyle(0)

        # self.setSelectionModel()
        # self.model = QStandardItemModel(self)
        self.model = Model(self)
        self.setModel(self.model)
        # self.itemSelectionChanged.connect(self.__selection_changed)
        selection_model = self.selectionModel()
        print("VerticalItemView selectionModel = ", selection_model)
        selection_model.selectionChanged.connect(self.__selection_changed)
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
            QListView.keyPressEvent(self, event)

    def __double_clicked(self):
        index = self.get_index()
        if index is not None:
            self.on_activate_item(index)
            self.item_activated.emit(index)

    def __selection_changed(self):
        index = self.get_index()
        self.on_select_item(index)
        self.item_selected.emit(index)

    def on_activate_item(self, index):
        pass

    def get_item_icon(self, index):
        return None

    def get_item_text(self, index):
        return ""

    def get_item_text_color(self, index):
        return None

    # def set_item_count(self, count):
    #     #self.model.rowCoun
    #     self.model.set_item_count(count)
    #     #self.update()
    #     #self.invalidate()
    #     self.dataChanged(self.model.createIndex(0, 0),
    #             self.model.createIndex(count, 0))

    def set_default_icon(self, image):
        pass

    # def set_items(self, items):
    #    #print("set_items", items)
    #    self.model.clear()
    #    for label in items:
    #        item = QStandardItem(label)
    #        self.model.appendRow(item)

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
        idx = self.model.index(index, 0)
        self.scrollTo(idx)
        self.setCurrentIndex(idx)

    def select_item(self, index):
        self.set_index(index)

    def on_select_item(self, index):
        pass

    def update(self):
        # self.model.rowCoun
        count = self.get_item_count()
        # self.model.set_item_count(count)
        # self.update()
        # self.invalidate()
        self.dataChanged(
            self.model.createIndex(0, 0), self.model.createIndex(count, 0)
        )
