from typing import List, Optional, Tuple, Union, cast

from typing_extensions import TypedDict

from fsui.qt.icon import Icon
from fsui.qt.image import Image
from fsui.qt.qparent import QParent
from fsui.qt.qt import (
    QFont,
    QListView,
    QSize,
    QStandardItem,
    QStandardItemModel,
)
from fsui.qt.signal import Signal
from fswidgets.widget import Widget


class Item(TypedDict):
    label: str
    icon: Optional[Icon]
    bold: bool


class ListView(Widget):
    item_selected = Signal(int)
    item_activated = Signal(int)

    def __init__(self, parent: Widget, border: bool = True):
        # self = QListView(parent.get_container())
        super().__init__(parent, QListView(QParent(parent)))
        # Widget.__init__(self, parent)
        # self.init_widget(parent)

        # FIXME: Hmmm...?
        # self._qwidget.viewport().installEventFilter(self.get_window())
        # self._qwidget.verticalScrollBar().installEventFilter(self.get_window())

        if not border:
            self.qListView.setFrameStyle(0)

        # self.setSelectionModel()
        self._model = QStandardItemModel(self)
        # self.setModel(self._model)
        self.qListView.setModel(self._model)
        # self.itemSelectionChanged.connect(self._on_selection_changed)
        selection_model = self.qListView.selectionModel()
        print("QListView selectionModel", selection_model)
        selection_model.selectionChanged.connect(self.__on_selection_changed)
        self.qListView.setEditTriggers(QListView.NoEditTriggers)
        self.qListView.doubleClicked.connect(self.__on_double_clicked)
        # self.returnPressed.connect(self.__double_clicked)
        # self.activated.connect(self.__double_clicked)
        self._row_height = 26

    def add_item(
        self,
        label: str,
        icon: Optional[Union[Icon, Image]] = None,
        bold: bool = False,
    ) -> None:
        item = QStandardItem(label)
        if icon is not None:
            if isinstance(icon, Icon):
                item.setIcon(icon.qicon(16))
            else:
                item.setIcon(icon.qicon)
        item.setSizeHint(QSize(-1, self._row_height))
        if bold:
            font = self.qListView.font()
            font.setWeight(QFont.Bold)
            item.setFont(font)
        self._model.appendRow(item)

    def clear(self) -> None:
        self._model.clear()

    def get_item(self, index: int) -> str:
        return self._model.item(index).text()

    def get_item_count(self) -> int:
        return self._model.rowCount()

    # FIXME:
    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Return:
    #         self.__double_clicked()
    #     else:
    #         super().keyPressEvent(event)

    def on_activate_item(self, index: int) -> None:
        pass

    def __on_double_clicked(self) -> None:
        index = self.index()
        if index is not None:
            self.on_activate_item(index)
            self.item_activated.emit(index)

    def __on_selection_changed(self) -> None:
        index = self.index()
        if index is not None:
            self.on_select_item(index)
            self.item_selected.emit(index)

    def set_default_icon(self, image: Icon) -> None:
        pass

    def set_items(
        self, items: List[Union[str, Item, Tuple[str, Icon]]]
    ) -> None:
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

    def index(self) -> Optional[int]:
        indices = self.qListView.selectionModel().selectedIndexes()
        if len(indices) == 0:
            return None
        return indices[0].row()

    def on_select_item(self, index: int) -> None:
        print("calling item_selected.emit")
        self.item_selected.emit(index)

    @property
    def qListView(self) -> QListView:
        return cast(QListView, self.qWidget)

    def select_item(self, index: int) -> None:
        self.set_index(index)

    def set_index(self, index: int) -> None:
        if index is None:
            index = -1
        idx = self._model.index(index, 0)
        self.qListView.scrollTo(idx)
        self.qListView.setCurrentIndex(idx)

    def set_row_height(self, height: int) -> None:
        self._row_height = height
