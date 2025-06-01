from typing import IO, Optional, Union

from fscore.resources import Resources
from fsui.qt.qt import QColor, QIcon, QImage, QPixmap, QSize, Qt
from fswidgets.types import Size


class Image:
    NEAREST = 0

    @classmethod
    def create_blank(cls, width: int, height: int) -> "Image":
        # qimage = QPixmap(16, 16).toImage()
        qimage = QImage(QSize(16, 16), QImage.Format.Format_ARGB32)
        qimage.fill(QColor(0, 0, 0, 0))

        return Image(qimage=qimage)

    def __init__(
        self, name: Union[str, IO[bytes]] = "", qimage: Optional[QImage] = None
    ) -> None:
        if qimage:
            self.qimage = qimage
        else:
            self.qimage = QImage()
            if isinstance(name, str):
                if name.startswith("/"):
                    with open(name, "rb") as f:
                        self.qimage.loadFromData(f.read())
                elif name.startswith("pkg://"):
                    parts = name.split("/", 3)
                    stream = Resources(parts[2]).stream(parts[3])
                    self.qimage.loadFromData(stream.read())
                else:
                    index = name.find(":")
                    if index > 1:
                        package, file_ = name.split(":", 1)
                        stream = Resources(package, "").stream(file_)
                        self.qimage.loadFromData(stream.read())
                    else:
                        print("loading image from", name)
                        self.qimage.load(name)
            else:
                self.qimage.loadFromData(name.read())

    @property
    def size(self) -> Size:
        return self.qimage.width(), self.qimage.height()

    def copy(self) -> "Image":
        return Image(qimage=self.qimage.copy())

    def invert(self) -> None:
        self.qimage.invertPixels()

    def width(self) -> int:
        return self.qimage.width()

    def height(self) -> int:
        return self.qimage.height()

    @property
    def qpixmap(self) -> QPixmap:
        return QPixmap(self.qimage)

    @property
    def qicon(self) -> QIcon:
        return QIcon(QPixmap(self.qimage))

    # @property
    # def bitmap(self):
    #     if self._bitmap is None:
    #         self._bitmap = wx.BitmapFromImage(self.qimage)
    #     return self._bitmap

    def grey_scale(self) -> "Image":
        # return Image(qimage=self.qimage.convertToFormat(
        #     QImage.Format.Format_ARGB32, Qt.AutoOnly))
        copy = self.qimage.convertToFormat(QImage.Format.Format_ARGB32, Qt.ImageConversionFlag.AutoColor)
        # copy = self.qimage.copy(0, 0, *self.size)

        # WARNING: this is presumably a bit slow...
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                p = copy.pixel(x, y)

                # RGBA
                # r = (p & 0xff000000) >> 24
                # g = (p & 0x00ff0000) >> 16
                # b = (p & 0x0000ff00) >> 8
                # a = p & 0x000000ff
                # # v = (r + g + b) // 3
                # v = int(r * 0.299 + g * 0.587 + b * 0.114)
                # p = v << 24 | v << 16 | v << 8 | a

                # ARGB
                a = (p & 0xFF000000) >> 24
                r = (p & 0x00FF0000) >> 16
                g = (p & 0x0000FF00) >> 8
                b = p & 0x000000FF
                # v = (r + g + b) // 3
                v = int(r * 0.299 + g * 0.587 + b * 0.114)
                p = a << 24 | v << 16 | v << 8 | v

                copy.setPixel(x, y, p)
        return Image(qimage=copy)

    def resize(self, size: Size, filter_: bool = True) -> None:
        if size == self.size:
            return
        if filter_:
            q = Qt.TransformationMode.SmoothTransformation
        else:
            q = Qt.TransformationMode.SmoothTransformation
        self.qimage = self.qimage.scaled(
            size[0], size[1], Qt.AspectRatioMode.IgnoreAspectRatio, q
        )
        # self._bitmap = None

    def save(self, path: str) -> None:
        self.qimage.save(path)
