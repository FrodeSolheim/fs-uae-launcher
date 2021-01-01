from fsui.qt.qparent import QParent
from fsui.qt.qt import QColor, QFont, QFrame, QTextCursor, QTextEdit
from fsui.qt.signal import Signal
from fsui.qt.widget import Widget


class TextArea(Widget):
    changed = Signal()

    def __init__(
        self,
        parent,
        text="",
        read_only=False,
        font_family=None,
        border=True,
        line_wrap=True,
        text_color=None,
        background_color=None,
        padding=None,
    ):
        super().__init__(parent, QTextEdit("", QParent(parent)))
        if not border:
            self._qwidget.setFrameStyle(QFrame.NoFrame)
        self._qwidget.setReadOnly(read_only)
        if font_family:
            print("FIXME: not respecting font_family yet")
            font = QFont("Courier")
            # font.setStyleHint(QtGui.QFont.TypeWriter)
            self._qwidget.setFont(font)
        if line_wrap == False:
            self._qwidget.setLineWrapMode(QTextEdit.NoWrap)
        if text:
            self.append_text(text)

        stylesheet = []
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
            self._qwidget.setStyleSheet(stylesheet_str)

        self._qwidget.textChanged.connect(self.__text_changed)

    def get_text(self):
        return self._qwidget.toPlainText()

    def set_text(self, text):
        self._qwidget.setPlainText(text.replace("\n", "\r\n"))

    def append_text(self, text, color=None):
        # text = text.replace("\n", "\r\n")
        # print("Appending text:", repr(text))
        # self.moveCursor(QTextCursor.End)
        # self.insertPlainText(text.strip())
        if color is not None:
            self._qwidget.setTextColor(QColor(*color))
        # self.appendPlainText(text.strip())
        self._qwidget.append(text)
        self._qwidget.moveCursor(QTextCursor.End)

    def scroll_to_start(self):
        self._qwidget.moveCursor(QTextCursor.Start)

    def __text_changed(self):
        self.changed.emit()
