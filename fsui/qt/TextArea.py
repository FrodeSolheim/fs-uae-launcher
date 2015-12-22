import fsui.qt
from .widget_mixin import WidgetMixin


class TextArea(fsui.qt.QTextEdit, WidgetMixin):

    changed = fsui.qt.Signal()

    def __init__(
            self, parent, text="", read_only=False, font_family=None,
            border=True):
        fsui.qt.QTextEdit.__init__(self, "", parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        if not border:
            self.setFrameStyle(fsui.qt.QFrame.NoFrame)
        self.setReadOnly(read_only)
        if font_family:
            print("FIXME: not respecting font_family yet")
            font = fsui.qt.QFont("Courier")
            # font.setStyleHint(QtGui.QFont.TypeWriter)
            self.setFont(font)
        if text:
            self.append_text(text)
        self.textChanged.connect(self.__text_changed)

    def get_text(self):
        return self.toPlainText()

    def set_text(self, text):
        self.setPlainText(text.replace("\n", "\r\n"))

    def append_text(self, text, color=None):
        # text = text.replace("\n", "\r\n")
        # print("Appending text:", repr(text))
        # self.moveCursor(QTextCursor.End)
        # self.insertPlainText(text.strip())
        if color is not None:
            self.setTextColor(fsui.qt.QColor(*color))
        # self.appendPlainText(text.strip())
        self.append(text.strip())
        self.moveCursor(fsui.qt.QTextCursor.End)

    def scroll_to_start(self):
        self.moveCursor(fsui.qt.QTextCursor.Start)

    def __text_changed(self):
        self.changed.emit()
