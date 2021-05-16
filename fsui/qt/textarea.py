from typing import Any, List, Optional, cast

from fscore.deprecated import deprecated
from fsui.qt.color import Color
from fsui.qt.qparent import QParent
from fsui.qt.qt import QColor, QFont, QFrame, QTextCursor, QTextEdit
from fsui.qt.signal import Signal
from fswidgets.widget import Widget


class TextArea(Widget):
    changed: Any = Signal()

    def __init__(
        self,
        parent: Widget,
        text: str = "",
        read_only: bool = False,
        font_family: Optional[str] = None,
        border: bool = True,
        line_wrap: bool = True,
        text_color: Optional[Color] = None,
        background_color: Optional[Color] = None,
        padding: Optional[int] = None,
    ):
        super().__init__(parent, QTextEdit("", QParent(parent)))
        if not border:
            self.qwidget.setFrameStyle(QFrame.NoFrame)
        self.qwidget.setReadOnly(read_only)
        if font_family:
            print("FIXME: not respecting font_family yet")
            font = QFont("Courier")
            # font.setStyleHint(QtGui.QFont.TypeWriter)
            self.qwidget.setFont(font)
        if line_wrap == False:
            self.qwidget.setLineWrapMode(QTextEdit.NoWrap)
        if text:
            self.appendText(text)

        stylesheet: List[str] = []
        if text_color:
            stylesheet.append(f"color: {text_color.to_hex()};")
        if background_color:
            stylesheet.append(
                f"background-color: {background_color.to_hex()};"
            )
        if padding:
            stylesheet.append(f"padding: {padding};")
        if stylesheet:
            nl = "\n"
            stylesheet_str = f"QTextEdit {{\n{nl.join(stylesheet)}\n}}\n"
            # print(stylesheet_str)
            self.qwidget.setStyleSheet(stylesheet_str)

        self.qwidget.textChanged.connect(self.onInput)  # type: ignore
        self.qwidget.textChanged.connect(self.__text_changed)  # type: ignore

    def appendText(self, text: str):
        self.qwidget.append(text)
        self.qwidget.moveCursor(QTextCursor.End)

    def appendTextWithColor(self, text: str, color):
        # text = text.replace("\n", "\r\n")
        # print("Appending text:", repr(text))
        # self.moveCursor(QTextCursor.End)
        # self.insertPlainText(text.strip())
        if color is not None:
            self.qwidget.setTextColor(QColor(*color))
        # self.appendPlainText(text.strip())
        self.qwidget.append(text)
        self.qwidget.moveCursor(QTextCursor.End)

    def getText(self) -> str:
        return self.qwidget.toPlainText()

    def onInput(self):
        pass

    @property
    def qwidget(self):
        return cast(QTextEdit, self.getQWidget())

    def scrollToStart(self):
        """
        # FIXME: The name is a bit misleading because it also moves the
        # text cursor to the start...
        """
        self.qwidget.moveCursor(QTextCursor.Start)

    def setText(self, text: str):
        self.qwidget.setPlainText(text.replace("\n", "\r\n"))

    # -------------------------------------------------------------------------

    def __text_changed(self):
        self.changed.emit()

    # -------------------------------------------------------------------------

    @deprecated
    def get_text(self):
        return self.getText()

    @deprecated
    def set_text(self, text: str):
        return self.setText(text)

    @deprecated
    def append_text(self, text: str, color=None):
        self.appendTextWithColor(text, color)

    @deprecated
    def scroll_to_start(self):
        self.scrollToStart()
