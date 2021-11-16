from typing import cast

from fsui.qt.image import Image
from fsui.qt.qparent import QParent
from fsui.qt.qt import QLabel
from fswidgets.widget import Widget


class ImageView(Widget):
    def __init__(
        self, parent: Widget, image: Image, stretch: bool = False
    ) -> None:
        super().__init__(parent, QLabel(QParent(parent)))
        self.qLabel.setPixmap(image.qpixmap)
        if stretch:
            self.qLabel.setScaledContents(True)

    @property
    def qLabel(self) -> QLabel:
        return cast(QLabel, self.qWidget)

    def set_image(self, image: Image) -> None:
        self.qLabel.setPixmap(image.qpixmap)
