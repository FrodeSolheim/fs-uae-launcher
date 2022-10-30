import weakref
from typing import Any, Optional, cast

from typing_extensions import Protocol

from fsui.qt.color import Color
from fsui.qt.core import QModelIndex, QObject
from fsui.qt.icon import Icon
from fsui.qt.image import Image
from fsui.qt.qparent import QParent
from fsui.qt.qt import QAbstractListModel, QBrush, QListView, QSize, Qt
from fsui.qt.signal import Signal
from fswidgets.widget import Widget


class HasItemCount(Protocol):
    def get_item_count(self) -> int:
        ...


class Model(QAbstractListModel):
    def __init__(self, parent: QObject, parent2: HasItemCount) -> None:
        QAbstractListModel.__init__(self, parent)
        self.parent2 = weakref.ref(parent2)
        self.count = 0

    # def set_item_count(self, count):
    #     self.count = count

    # PyQt6-stubs uses parent = ... ?
    def rowCount(self, parent: QModelIndex) -> int:  # type: ignore
        # print("returning count", self.count, "for parent", parent)
        # return self.count
        p = self.parent2()
        assert p is not None
        return p.get_item_count()

    # PyQt6-stubs uses parent = ... ?
    def data(self, index: QModelIndex, role: int) -> Any:  # type: ignore
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


class VerticalItemView(Widget):
    item_selected = Signal(int)
    item_activated = Signal(int)

    def __init__(self, parent: Widget, border: bool = True) -> None:
        super().__init__(parent, QListView(QParent(parent)))
        # FIXME: Why?
        # self._qwidget.viewport().installEventFilter(self.get_window())
        # self._qwidget.verticalScrollBar().installEventFilter(self.get_window())
        if not border:
            self.qListView.setFrameStyle(0)

        # self.setSelectionModel()
        # self.model = QStandardItemModel(self)
        self.model = Model(self, self)
        self.qListView.setModel(self.model)
        # self.itemSelectionChanged.connect(self.__selection_changed)
        selection_model = self.qListView.selectionModel()
        print("VerticalItemView selectionModel = ", selection_model)
        selection_model.selectionChanged.connect(self.__selection_changed)
        self.qListView.doubleClicked.connect(self.__double_clicked)
        # self.returnPressed.connect(self.__double_clicked)
        # self.activated.connect(self.__double_clicked)
        self._row_height = 26

    def set_row_height(self, height: int) -> None:
        self._row_height = height

    # FIXME
    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key.Key_Return:
    #         self.__double_clicked()
    #     else:
    #         QListView.keyPressEvent(self, event)

    def __double_clicked(self) -> None:
        index = self.index()
        if index is not None:
            self.on_activate_item(index)
            self.item_activated.emit(index)

    def __selection_changed(self) -> None:
        index = self.index()
        if index is not None:
            self.on_select_item(index)
            self.item_selected.emit(index)

    def on_activate_item(self, index: int) -> None:
        pass

    def get_item_count(self) -> int:
        raise NotImplementedError()

    def get_item_icon(self, index: int) -> Optional[Image]:
        return None

    def get_item_text(self, index: int) -> str:
        return ""

    def get_item_text_color(self, index: int) -> Optional[Color]:
        return None

    # def set_item_count(self, count):
    #     #self.model.rowCoun
    #     self.model.set_item_count(count)
    #     #self.update()
    #     #self.invalidate()
    #     self.dataChanged(self.model.createIndex(0, 0),
    #             self.model.createIndex(count, 0))

    def set_default_icon(self, image: Image) -> None:  # FIXME: Or Icon?
        pass

    # def set_items(self, items):
    #    #print("set_items", items)
    #    self.model.clear()
    #    for label in items:
    #        item = QStandardItem(label)
    #        self.model.appendRow(item)

    def index(self) -> Optional[int]:
        indices = self.qListView.selectionModel().selectedIndexes()
        if len(indices) == 0:
            return None
        return indices[0].row()

    @property
    def qListView(self) -> QListView:
        return cast(QListView, self.qWidget)

    def set_index(self, index: Optional[int]) -> None:
        if index is None:
            index = -1
        # print(self.rootIndex)
        # idx = QModelIndex.createIndex(index)
        idx = self.model.index(index, 0)
        self.qListView.scrollTo(idx)
        self.qListView.setCurrentIndex(idx)

    def select_item(self, index: Optional[int]) -> None:
        self.set_index(index)

    def on_select_item(self, index: int) -> None:
        pass

    def update(self) -> None:
        # self.model.rowCoun
        count = self.get_item_count()
        # self.model.set_item_count(count)
        # self.update()
        # self.invalidate()
        self.qListView.dataChanged(
            self.model.createIndex(0, 0), self.model.createIndex(count, 0)
        )
