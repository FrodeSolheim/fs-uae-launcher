from fsui.context import get_theme
from fsui.decorators import deprecated
from fsui.qt import QComboBox, QFontMetrics
from fsui.qt.qparent import QParent
from fsui.qt.widget import Widget


class ComboBox(Widget):
    def __init__(self, parent, items=[], read_only=False):
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
        self._qwidget.setEditable(True)

        # FIXME: Why?? Disabling until checked, remember to comment
        # self._qwidget.lineEdit().installEventFilter(self.get_window())

        self.set_items(items)

        if len(items) > 0:
            self.set_index(0)
        self._qwidget.currentIndexChanged.connect(self.__current_index_changed)

        # self.dumpObjectTree()
        # print("(dumped)")
        self.update_style()

    def clear(self):
        self._qwidget.clear()

    def __current_index_changed(self):
        self.on_changed()

    def get_min_width(self):
        # We don't want min width to be decided by the contents of the line
        # edit control.
        return 50

    @deprecated
    def get_text(self):
        self.text()

    def index(self):
        return self._qwidget.currentIndex()

    def on_changed(self):
        pass

    def set_index(self, index):
        self._qwidget.setCurrentIndex(index)

    def set_items(self, items):
        self._qwidget.clear()
        for i, item in enumerate(items):
            self._qwidget.insertItem(i, item)

    def set_item_text(self, item, text):
        self._qwidget.setItemText(item, text)

    def set_text(self, text):
        self._qwidget.lineEdit().setText(text)

    def text(self):
        return self._qwidget.lineEdit().text()

    def update_style(self):
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
        fontmetrics = QFontMetrics(self._qwidget.font())
        fontheight = fontmetrics.height()
        # print(fontheight)
        # FIXME: Assumed
        border = 4
        min_height = fontheight + padding.top + padding.bottom + border
        self.set_min_height(min_height)

        padding = theme.textfield_padding()
        # Padding top/bottom does not work before it does not influence the
        # parent (ComboBox) height.
        self._qwidget.lineEdit().setStyleSheet(
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
        self._qwidget.setStyleSheet(
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
