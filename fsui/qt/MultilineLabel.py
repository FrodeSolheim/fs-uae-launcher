from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsui.qt import QLabel, Qt
from .Widget import Widget


class MultilineLabel(Widget):

    def __init__(self, parent, label, min_width=None):
        self._widget = QLabel(label, parent.get_container())
        #Widget.__init__(self, parent)
        self.init_widget(parent)
        self._widget.setWordWrap(True)
        # self._widget.setFixedWidth(200)
        # self._widget.setFixedHeight(200)
        if min_width:
            self.set_min_width(min_width)

        self._widget.setTextFormat(Qt.RichText)
        self._widget.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self._widget.setOpenExternalLinks(True)
        self._widget.setAlignment(Qt.AlignLeft | Qt.AlignTop)

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
