from urllib.parse import unquote_plus

from fsui.qt.qparent import QParent
from fsui.qt.qt import QLabel, Qt
from fsui.qt.widget import Widget


class PlainLabel(Widget):
    def __init__(self, parent, label):
        super().__init__(parent, QLabel(label, QParent(parent)))

    def set_text(self, label):
        self._qwidget.setText(label)


class Label(PlainLabel):
    TEXT_ALIGNMENT_CENTER = 1

    def __init__(self, parent, label="", selectable=True):
        super().__init__(parent, label)

        self._qwidget.setTextFormat(Qt.RichText)
        # self.setTextInteractionFlags(fsui.qt.Qt.TextBrowserInteraction)
        if selectable:
            self._qwidget.setTextInteractionFlags(
                Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
            )
        self._qwidget.setOpenExternalLinks(True)
        # self.setFocusPolicy(Qt.NoFocus)

        # FIXME: focusPolicy()
        # FIXME: make Label more plain, and rather make a InteractiveLabel
        # descendant or something like that

    def set_text_alignment(self, alignment):
        if alignment == 1:
            self._qwidget.setAlignment(Qt.AlignHCenter)

    def set_text_color(self, color):
        palette = self._qwidget.palette()
        palette.setColor(self._qwidget.foregroundRole(), color)
        self._qwidget.setPalette(palette)


class URLLabel(Label):
    def __init__(self, parent, label, url):
        self._label = label
        self._url = url
        Label.__init__(self, parent, self._fix_label())
        # self.setFocusPolicy(Qt.StrongFocus)

    def set_text(self, label):
        self._label = label
        # super().set_text(self._fix_label())
        self.update_text()

    def set_url(self, url):
        self._url = url
        # self.set_text(self._fix_label())
        self.update_text()

    def update_text(self):
        super().set_text(self._fix_label())

    def _fix_label(self):
        url = unquote_plus(self._url)
        fixed = '<a href="{0}">{1}</a>'.format(url, self._label)
        print(fixed)
        return fixed

    def get_min_height(self, width):
        # because the underline seems to be cut off otherwise...
        return super().get_min_height(width) + 1


class MultiLineLabel(Widget):
    def __init__(self, parent, label, min_width=None):
        super().__init__(parent, QLabel(label, QParent(parent)))
        self._qwidget.setWordWrap(True)
        # self._widget.setFixedWidth(200)
        # self._widget.setFixedHeight(200)
        if min_width:
            self.set_min_width(min_width)

        self._qwidget.setTextFormat(Qt.RichText)
        self._qwidget.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self._qwidget.setOpenExternalLinks(True)
        self._qwidget.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def set_text(self, label):
        self._qwidget.setText(label)

    def get_min_height(self, width):
        # + 1 because of url underlines
        if hasattr(self, "min_width"):
            if self.min_width:
                # FIXME: Use width...!
                height = self._qwidget.heightForWidth(self.min_width) + 1
                if hasattr(self, "min_height"):
                    return max(self.min_height, height)
                return height
        return super().get_min_height(width) + 1
