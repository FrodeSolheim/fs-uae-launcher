import fsui.qt
from .Widget import Widget
from urllib.parse import unquote_plus


class Label(fsui.qt.QLabel, Widget):

    def __init__(self, parent, label):
        fsui.qt.QLabel.__init__(self, label, parent.get_container())
        # self._widget = fsui.qt.QLabel(label, parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)

        # self._widget.setTextFormat(fsui.qt.Qt.RichText)
        # self._widget.setTextInteractionFlags(fsui.qt.Qt.TextBrowserInteraction)
        # self._widget.setOpenExternalLinks(True)
        self.setTextFormat(fsui.qt.Qt.RichText)
        self.setTextInteractionFlags(fsui.qt.Qt.TextBrowserInteraction)
        self.setOpenExternalLinks(True)

    def set_text(self, label):
        # self._widget.setText(label)
        self.setText(label)


class URLLabel(Label):

    def __init__(self, parent, label, url):
        self._label = label
        self._url = url
        Label.__init__(self, parent, self._fix_label())

    def set_text(self, label):
        self._label = label
        self._widget.setText(self._fix_label())

    def set_url(self, url):
        self._url = url
        self._widget.setText(self._fix_label())

    def _fix_label(self):
        url = unquote_plus(self._url)
        return "<a href=\"{0}\">{1}</a>".format(url, self._label)

    def get_min_height(self):
        # because the underline seems to be cut off otherwise...
        return Label.get_min_height(self) + 1


class MultiLineLabel(Widget):

    def __init__(self, parent, label, min_width=None):
        self._widget = fsui.qt.QLabel(label, parent.get_container())
        # Widget.__init__(self, parent)
        self.init_widget(parent)
        self._widget.setWordWrap(True)
        # self._widget.setFixedWidth(200)
        # self._widget.setFixedHeight(200)
        if min_width:
            self.set_min_width(min_width)

        self._widget.setTextFormat(fsui.qt.Qt.RichText)
        self._widget.setTextInteractionFlags(fsui.qt.Qt.TextBrowserInteraction)
        self._widget.setOpenExternalLinks(True)
        self._widget.setAlignment(fsui.qt.Qt.AlignLeft | fsui.qt.Qt.AlignTop)

    def set_text(self, label):
        self._widget.setText(label)

    # def set_fixed_width(self, width):

    # def set_min_width(self):
    #     pass

    def get_min_height(self):
        # + 1 because of url underlines
        if hasattr(self, "min_width"):
            if self.min_width:
                height = self._widget.heightForWidth(self.min_width) + 1
                if hasattr(self, "min_height"):
                    return max(self.min_height, height)
                return height
        return Widget.get_min_height(self) + 1
