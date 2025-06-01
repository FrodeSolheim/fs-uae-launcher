from typing import List, Optional, cast

from fsui.context import get_theme
from fsui.qt.image import Image
from fsui.qt.qparent import QParent
from fsui.qt.qt import QComboBox, QFontMetrics
from fsui.qt.signal import Signal, SignalWrapper
from fswidgets.widget import Widget


class Choice(Widget):
    changed_signal = Signal()
    item_selected = Signal(int)
    ITEM_SEPARATOR = "---"

    def __init__(
        self,
        parent: Widget,
        items: Optional[List[str]] = None,
        cursor_keys: bool = True,
    ):
        if items is None:
            items = []
        super().__init__(parent, QComboBox(QParent(parent)))
        self.inhibit_change_event = False
        self.cursor_keys = cursor_keys

        for i, item in enumerate(items):
            self.qComboBox.insertItem(i, item)
        if len(items) > 0:
            self.set_index(0)
        self.qComboBox.currentIndexChanged.connect(
            self.__on_current_index_changed
        )
        self.changed = SignalWrapper(self, "changed")
        self.update_style()

    def getIndex(self) -> int:
        return self.index()

    @property
    def qComboBox(self) -> QComboBox:
        return cast(QComboBox, self.qWidget)

    def setIndex(self, index: int) -> None:
        self.set_index(index)

    # -------------------------------------------------------------------------

    # FIXME: This needs to be fixed
    # keyPressEvent isn't intercepted anymore
    # def keyPressEvent(self, a0: QKeyEvent) -> None:
    #     if not self.cursor_keys:
    #         print("cursor keys is false", a0.key(), Qt.Key.Key_Up)
    #         if a0.key() == Qt.Key.Key_Up or a0.key() == Qt.Key.Key_Down:
    #             print("ignoring")
    #             return
    #     super().keyPressEvent(a0)

    # @contextmanager
    # def inhibit_signal(self, name):
    #     attr = "_inhibit_" + name
    #     old = getattr(self, attr, False)
    #     print("setattr", self, attr, True)
    #     setattr(self, attr, True)
    #     yield
    #     print("setattr", self, attr, old)
    #     setattr(self, attr, old)

    # FIXME: Allow adding Icon?
    def add_item(self, label: str, icon: Optional[Image] = None) -> int:
        # item = QStandardItem(label)
        # if icon:
        #     item.setIcon(icon.qicon)
        # item.setSizeHint(QSize(-1, 24))
        if label == self.ITEM_SEPARATOR:
            self.qComboBox.insertSeparator(self.count())
        elif icon is not None:
            self.qComboBox.addItem(icon.qicon, label)
        else:
            self.qComboBox.addItem(label)
        return self.count() - 1

    def clear(self) -> None:
        return self.qComboBox.clear()

    def count(self) -> int:
        return self.qComboBox.count()

    def index(self) -> int:
        return self.qComboBox.currentIndex()

    def on_changed(self) -> None:
        pass

    def __on_current_index_changed(self) -> None:
        # print("__current_index_changed", self.currentIndex(),
        #       "inhibit", self.inhibit_change_event)
        if not self.inhibit_change_event:
            # print("Choice.__current_index_changed")
            # if not getattr(self, "_inhibit_changed", False):
            if not self.changed.inhibit:
                if not getattr(self, "_inhibit_item_selected", False):
                    index = self.qComboBox.currentIndex()
                    self.item_selected.emit(index)
                self.changed.emit()
                self.on_changed()

    def remove_item(self, index: int) -> None:
        self.qComboBox.removeItem(index)

    def set_index(self, index: int, signal: bool = True) -> None:
        try:
            if not signal:
                self.inhibit_change_event = True
            self.qComboBox.setCurrentIndex(-1 if index is None else index)
        finally:
            if not signal:
                self.inhibit_change_event = False

    def set_item_text(self, index: int, text: str) -> None:
        self.qComboBox.setItemText(index, text)

    def update_style(self) -> None:
        # There seems to be an issue with specifying padding-top and
        # padding-bottom for a QComboBox. The internal pop menu also gets
        # padding added, resulting in ugly white borders at the top/bottom of
        # the popup, and there seems to be no way to remove this. So instead,
        # we calculate minimum height based on font height manually.
        theme = get_theme(self)
        padding = theme.choice_padding()
        if padding:
            fontmetrics = QFontMetrics(self.qComboBox.font())
            fontheight = fontmetrics.height()
            print(fontheight)
            # FIXME: Assumed
            border = 4
            min_height = fontheight + padding.top + padding.bottom + border
            self.set_min_height(min_height)
        self.qComboBox.setStyleSheet(
            f"""
            QComboBox {{
                padding-right: 8px;
                padding-left: 8px;
            }}
        """
        )

    # def __len__(self):
    #     return self.count()


class ItemChoice(Choice):
    def __init__(self, parent: Widget):
        super().__init__(parent)

    def on_changed(self) -> None:
        self.on_select_item(self.index())

    def on_select_item(self, index: int) -> None:
        pass

    def select_item(self, index: Optional[int], signal: bool = True) -> None:
        print("select_item", index)
        if index is None:
            self.set_index(-1, signal=signal)
        else:
            self.set_index(index, signal=signal)

    def update(self) -> None:
        # for i, item in enumerate(self.items):
        #     self.add_item(item["name"], icon=self.get_item_icon(i))
        old = self.inhibit_change_event
        old_index = self.index()
        self.inhibit_change_event = True
        self.clear()
        for i in range(self.get_item_count()):
            text = self.get_item_text(i)
            icon = self.get_item_icon(i)
            self.add_item(text, icon)
        if old_index < self.get_item_count():
            self.set_index(old_index)
        self.inhibit_change_event = old
