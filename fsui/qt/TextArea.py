from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsui.qt import QPlainTextEdit, QFrame, QFont, QTextCursor, Signal, QColor
from fsui.qt import QTextEdit, QFrame, QFont, QTextCursor, Signal, QColor
from .Widget import Widget

QPlainTextEdit = QTextEdit


class TextArea(QPlainTextEdit, Widget):

    changed = Signal()

    def __init__(
            self, parent, text="", read_only=False, font_family=None,
            border=True):
        QPlainTextEdit.__init__(self, "", parent.get_container())
        #Widget.__init__(self, parent)
        self.init_widget(parent)
        if not border:
            self.setFrameStyle(QFrame.NoFrame);
        self.setReadOnly(read_only)
        if font_family:
            print("FIXME: not respecting font_family yet")
            font = QFont("Courier")
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
        #text = text.replace("\n", "\r\n")
        #print("Appending text:", repr(text))
        #self.moveCursor(QTextCursor.End)
        #self.insertPlainText(text.strip())
        if color is not None:
            self.setTextColor(QColor(*color))
        #self.appendPlainText(text.strip())
        self.append(text.strip())
        self.moveCursor(QTextCursor.End)

    def scroll_to_start(self):
        self.moveCursor(QTextCursor.Start)

    def __text_changed(self):
        self.changed.emit()
