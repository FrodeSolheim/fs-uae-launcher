from fsui.context import get_theme
from fsui.decorators import deprecated
from fsui.qt.qparent import QParent
from fsui.qt.qt import QFontMetrics, QLineEdit
from fsui.qt.signal import Signal, SignalWrapper
from fswidgets.widget import Widget


class TextField(Widget):
    changed_signal = Signal()
    activated_signal = Signal()

    # FIXME: Insert * after parent
    def __init__(
        self,
        parent,
        text="",
        read_only=False,
        placeholder="",
        clearbutton=False,
        passwordMode=False,
    ):
        super().__init__(parent, QLineEdit(text, QParent(parent)))
        # Widget.__init__(self, parent)
        # self.init_widget(parent)
        self._qwidget.setReadOnly(read_only)

        self._has_text = text != ""
        self.update_color()

        # noinspection PyUnresolvedReferences
        self._qwidget.textChanged.connect(self.__on_text_changed)
        # noinspection PyUnresolvedReferences
        self._qwidget.returnPressed.connect(self.__on_return_pressed)

        self.changed = SignalWrapper(self, "changed")
        self.activated = SignalWrapper(self, "activated")

        if passwordMode:
            self._qwidget.setEchoMode(QLineEdit.Password)
        if placeholder:
            self._qwidget.setPlaceholderText(placeholder)
        if clearbutton:
            self._qwidget.setClearButtonEnabled(True)
        self.update_style()

    def update_style(self):
        # There seems to be an issue with specifying padding-top and
        # padding-bottom for a QSpinBox.
        theme = get_theme(self)
        padding = theme.textfield_padding()
        if not padding:
            # Indicates that we do not want custom styling
            return
        fontmetrics = QFontMetrics(self._qwidget.font())
        fontheight = fontmetrics.height()
        print(fontheight)
        border = 4
        min_height = fontheight + padding.top + padding.bottom + border
        self.set_min_height(min_height)
        print("MINHEIGHT (TEXTFIELD)", min_height)
        has_text = self.text() != ""
        self._qwidget.setStyleSheet(
            f"""
            QLineEdit {{
                color: {"#000000" if has_text else "#666666"};
                padding-right: {padding.right}px;
                padding-left: {padding.left}px;
            }}
            """
        )

    def update_color(self):
        has_text = self.text() != ""
        if has_text != self._has_text:
            self._has_text = has_text
            self.update_style()
        # self.setStyleSheet(f"""
        #     QLineEdit[text=""] {{
        #         color: {"#000000" if has_text else "#666666"};
        #     }}
        #     """
        # )

    @deprecated
    def value(self):
        return self.text()

    @deprecated
    def get_text(self):
        return self.text()

    def on_changed(self):
        pass

    def __on_return_pressed(self):
        self.activated.emit()

    def __on_text_changed(self, _):
        self.update_color()
        self.changed.emit()
        self.on_changed()

    def select_all(self):
        self._qwidget.selectAll()

    def set_cursor_position(self, position):
        self._qwidget.setCursorPosition(position)

    def set_text(self, text):
        self._qwidget.setText(text)

    def text(self):
        return self._qwidget.text()


class PasswordField(TextField):
    def __init__(self, parent, text=""):
        super().__init__(parent, text)
        self._qwidget.setEchoMode(QLineEdit.Password)
