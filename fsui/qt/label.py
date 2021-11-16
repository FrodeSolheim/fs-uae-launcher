from typing import Optional, cast
from urllib.parse import unquote_plus

from fsui.qt.color import Color
from fsui.qt.qparent import QParent
from fsui.qt.qt import QLabel, Qt
from fswidgets.widget import Widget


class PlainLabel(Widget):
    def __init__(self, parent: Widget, label: str):
        super().__init__(parent, QLabel(label, QParent(parent)))

    @property
    def qLabel(self) -> QLabel:
        return cast(QLabel, self.qWidget)

    def set_text(self, label: str) -> None:
        self.qLabel.setText(label)


class Label(PlainLabel):
    TEXT_ALIGNMENT_CENTER = 1

    def __init__(
        self, parent: Widget, label: str = "", selectable: bool = True
    ) -> None:
        super().__init__(parent, label)

        self.qLabel.setTextFormat(Qt.RichText)
        # self.setTextInteractionFlags(fsui.qt.Qt.TextBrowserInteraction)
        if selectable:
            self.qLabel.setTextInteractionFlags(
                cast(
                    Qt.TextInteractionFlags,
                    Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse,
                )
            )
        self.qLabel.setOpenExternalLinks(True)
        # self.setFocusPolicy(Qt.NoFocus)

        # FIXME: focusPolicy()
        # FIXME: make Label more plain, and rather make a InteractiveLabel
        # descendant or something like that

    def set_text_alignment(self, alignment: int) -> None:
        if alignment == 1:
            self.qLabel.setAlignment(Qt.AlignHCenter)

    def set_text_color(self, color: Color) -> None:
        palette = self.qLabel.palette()
        palette.setColor(self.qLabel.foregroundRole(), color)
        self.qLabel.setPalette(palette)


class URLLabel(Label):
    def __init__(self, parent: Widget, label: str, url: str) -> None:
        self._label = label
        self._url = url
        Label.__init__(self, parent, self._fix_label())
        # self.setFocusPolicy(Qt.StrongFocus)

    def set_text(self, label: str) -> None:
        self._label = label
        # super().set_text(self._fix_label())
        self.update_text()

    def set_url(self, url: str) -> None:
        self._url = url
        # self.set_text(self._fix_label())
        self.update_text()

    def update_text(self) -> None:
        super().set_text(self._fix_label())

    def _fix_label(self) -> str:
        url = unquote_plus(self._url)
        fixed = '<a href="{0}">{1}</a>'.format(url, self._label)
        print(fixed)
        return fixed

    def get_min_height(self, width: int) -> int:
        # because the underline seems to be cut off otherwise...
        return super().get_min_height(width) + 1


class MultiLineLabel(Widget):
    def __init__(
        self, parent: Widget, label: str, min_width: Optional[int] = None
    ) -> None:
        super().__init__(parent, QLabel(label, QParent(parent)))
        self.qLabel.setWordWrap(True)
        # self._widget.setFixedWidth(200)
        # self._widget.setFixedHeight(200)
        if min_width:
            self.set_min_width(min_width)

        self.qLabel.setTextFormat(Qt.RichText)
        self.qLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.qLabel.setOpenExternalLinks(True)
        # FIXME: How to correctly fix multiple flags w.r.t typing?
        self.qLabel.setAlignment(
            cast(Qt.AlignmentFlag, Qt.AlignLeft | Qt.AlignTop)
        )

    def get_min_height(self, width: int) -> int:
        # + 1 because of url underlines
        if hasattr(self, "min_width"):
            if self.min_width:
                # FIXME: Use width...!
                height = self.qLabel.heightForWidth(self.min_width) + 1
                if hasattr(self, "min_height"):
                    return max(self.min_height, height)
                return height
        return super().get_min_height(width) + 1

    @property
    def qLabel(self) -> QLabel:
        return cast(QLabel, self.qWidget)

    def set_text(self, label: str) -> None:
        self.qLabel.setText(label)
