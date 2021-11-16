from typing import cast

from fscore.deprecated import deprecated
from fsui.context import get_theme
from fsui.qt.gui import QFontMetrics
from fsui.qt.qparent import QParent
from fsui.qt.signal import Signal, SignalWrapper
from fsui.qt.widgets import QLineEdit
from fswidgets.widget import Widget


class TextField(Widget):
    changed_signal = Signal()
    activated_signal = Signal()

    # FIXME: Insert * after parent
    def __init__(
        self,
        parent: Widget,
        text: str = "",
        read_only: bool = False,
        placeholder: str = "",
        clearbutton: bool = False,
        passwordMode: bool = False,
    ) -> None:
        super().__init__(parent, QLineEdit(text, QParent(parent)))
        # Widget.__init__(self, parent)
        # self.init_widget(parent)
        self.qLineEdit.setReadOnly(read_only)

        self._has_text = text != ""
        self.update_color()

        # noinspection PyUnresolvedReferences
        self.qLineEdit.textChanged.connect(self.__on_text_changed)
        # noinspection PyUnresolvedReferences
        self.qLineEdit.returnPressed.connect(self.__on_return_pressed)

        self.changed = SignalWrapper(self, "changed")
        self.activated = SignalWrapper(self, "activated")

        if passwordMode:
            self.qLineEdit.setEchoMode(QLineEdit.Password)
        if placeholder:
            self.qLineEdit.setPlaceholderText(placeholder)
        if clearbutton:
            self.qLineEdit.setClearButtonEnabled(True)
        self.update_style()

    def update_style(self) -> None:
        # There seems to be an issue with specifying padding-top and
        # padding-bottom for a QSpinBox.
        theme = get_theme(self)
        padding = theme.textfield_padding()
        if not padding:
            # Indicates that we do not want custom styling
            return
        fontmetrics = QFontMetrics(self.qLineEdit.font())
        fontheight = fontmetrics.height()
        print(fontheight)
        border = 4
        min_height = fontheight + padding.top + padding.bottom + border
        self.set_min_height(min_height)
        print("MINHEIGHT (TEXTFIELD)", min_height)
        has_text = self.text() != ""
        self.qLineEdit.setStyleSheet(
            f"""
            QLineEdit {{
                color: {"#000000" if has_text else "#666666"};
                padding-right: {padding.right}px;
                padding-left: {padding.left}px;
            }}
            """
        )

    def update_color(self) -> None:
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
    def value(self) -> str:
        return self.text()

    @deprecated
    def get_text(self) -> str:
        return self.text()

    def on_changed(self) -> None:
        pass

    def __on_return_pressed(self) -> None:
        self.activated.emit()

    def __on_text_changed(self, _: str) -> None:
        self.update_color()
        self.changed.emit()
        self.on_changed()

    @property
    def qLineEdit(self) -> QLineEdit:
        return cast(QLineEdit, self.getQWidget())

    def select_all(self) -> None:
        self.qLineEdit.selectAll()

    def set_cursor_position(self, position: int) -> None:
        self.qLineEdit.setCursorPosition(position)

    def set_text(self, text: str) -> None:
        self.qLineEdit.setText(text)

    def text(self) -> str:
        return self.qLineEdit.text()


class PasswordField(TextField):
    def __init__(self, parent: Widget, text: str = ""):
        super().__init__(parent, text)
        self.qLineEdit.setEchoMode(QLineEdit.Password)
