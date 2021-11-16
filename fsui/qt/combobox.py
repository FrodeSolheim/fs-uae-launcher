from typing import List, cast

from fscore.deprecated import deprecated
from fsui.context import get_theme
from fsui.qt import QComboBox, QFontMetrics
from fsui.qt.qparent import QParent
from fsui.theme import Padding
from fswidgets.widget import Widget


class ComboBox(Widget):
    def __init__(
        self, parent: Widget, items: List[str] = [], read_only: bool = False
    ) -> None:
        super().__init__(parent, QComboBox(QParent(parent)))
        # QComboBox.__init__(self, parent.get_container())
        # self = QComboBox(parent.get_container())
        # Widget.__init__(self, parent)
        # self.init_widget(parent)
        # self.setEditable(not read_only)
        print(
            "FIXME: ComboBox not respecting read_only"
            "(because of missing lineEdit then"
        )
        self.qComboBox.setEditable(True)

        # FIXME: Why?? Disabling until checked, remember to comment
        # self.qComboBoc.lineEdit().installEventFilter(self.get_window())

        self.setItems(items)

        if len(items) > 0:
            self.set_index(0)
        self.qComboBox.currentIndexChanged.connect(
            self.__current_index_changed
        )

        # self.dumpObjectTree()
        # print("(dumped)")
        self.update_style()

    def clear(self) -> None:
        self.qComboBox.clear()

    @property
    def qComboBox(self) -> QComboBox:
        return cast(QComboBox, self.qWidget)

    def setIndex(self, index: int) -> None:
        self.qComboBox.setCurrentIndex(index)

    def setItems(self, items: List[str]) -> None:
        self.qComboBox.clear()
        for i, item in enumerate(items):
            self.qComboBox.insertItem(i, item)

    def setText(self, text: str) -> None:
        self.qComboBox.lineEdit().setText(text)

    # -------------------------------------------------------------------------

    def __current_index_changed(self) -> None:
        self.on_changed()

    def get_min_width(self) -> int:
        # We don't want min width to be decided by the contents of the line
        # edit control.
        return 50

    @deprecated
    def get_text(self) -> str:
        return self.text()

    def index(self) -> int:
        return self.qComboBox.currentIndex()

    def on_changed(self) -> None:
        pass

    @deprecated
    def set_index(self, index: int) -> None:
        self.setIndex(index)

    @deprecated
    def set_items(self, items: List[str]) -> None:
        self.setItems(items)

    def set_item_text(self, item: int, text: str) -> None:
        self.qComboBox.setItemText(item, text)

    @deprecated
    def set_text(self, text: str) -> None:
        self.setText(text)

    def text(self) -> str:
        return self.qComboBox.lineEdit().text()

    def update_style(self) -> None:
        # There seems to be an issue with specifying padding-top and
        # padding-bottom for a QComboBox. The internal pop menu also gets
        # padding added, resulting in ugly white borders at the top/bottom of
        # the popup, and there seems to be no way to remove this. So instead,
        # we calculate minimum height based on font height manually.
        theme = get_theme(self)
        padding = theme.choice_padding()
        if not padding:
            # Indicates that we do not want custom styling
            return
        fontmetrics = QFontMetrics(self.qComboBox.font())
        fontheight = fontmetrics.height()
        # print(fontheight)
        # FIXME: Assumed
        border = 4
        min_height = fontheight + padding.top + padding.bottom + border
        self.set_min_height(min_height)

        padding = theme.textfield_padding()
        if padding is None:
            padding = Padding(0, 0, 0, 0)
        # Padding top/bottom does not work before it does not influence the
        # parent (ComboBox) height.
        self.qComboBox.lineEdit().setStyleSheet(
            f"""
            QLineEdit {{
                /*
                background: #ffff00;
                border: 2px solid #00ff00;
                color: red;

                background: #ffff00;
                color: red;
                */
                /* padding-top: {padding.top}px; */
                padding-right: {padding.right}px;
                padding-left: {padding.left}px;
                /* padding-bottom: {padding.bottom}px; */
            }}
        """
        )
        self.qComboBox.setStyleSheet(
            f"""
            QComboBox {{
                /*
                border: 2px solid #ffff00;
                */
            }}
            /*
            QComboBox QAbstractItemView {{
                border: 2px solid darkgray;
                selection-background-color: lightgray;
                padding-top: 10px;
                height: 40px;
            }}
            QComboBox QAbstractItemView::item {{
                border: 2px solid darkgray;
                selection-background-color: lightgray;
                padding-top: 10px;
                height: 40px;
            }}
            QComboBox QListView::item {{
                border: 2px solid darkgray;
                selection-background-color: lightgray;
                padding-top: 10px;
                height: 40px;
            }}
            */
        """
        )
