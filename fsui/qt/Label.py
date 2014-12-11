from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsui.qt import Qt, QLabel
from .Widget import Widget
from fsbc.http import unquote_plus


class Label(Widget):

    def __init__(self, parent, label):
        self._widget = QLabel(label, parent.get_container())
        #Widget.__init__(self, parent)
        self.init_widget(parent)

        self._widget.setTextFormat(Qt.RichText)
        self._widget.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self._widget.setOpenExternalLinks(True)

    def set_text(self, label):
        self._widget.setText(label)


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
