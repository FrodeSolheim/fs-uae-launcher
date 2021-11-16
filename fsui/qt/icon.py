from typing import IO, Optional

from fscore.resources import Resources
from fsui.qt.image import Image
from fsui.qt.qt import QIcon, QImage, QPixmap


class Icon:
    """
    FIXME: Add support for icon search path, so, during startup, a list
    of package data directories to check can be added to this class, and
    icons can be looked up just by name.
    """

    def __init__(self, name: str, path: str = "") -> None:
        self.name = name
        self.path = path

    def stream_for_size(self, size: int) -> IO[bytes]:
        # package, file_ = name.split(":", 1)
        # if self.name.startswith("/"):
        #     return open(self.name, "rb")
        # else:
        assert self.path.startswith("pkg:")
        package = self.path[4:]
        try:
            name = "{0}x{0}/{1}.png".format(size, self.name)
            stream = Resources(package).stream(name)
        except LookupError:
            name = "{0}/{1}.png".format(size, self.name)
            stream = Resources(package).stream(name)
        return stream

    def qimage(self, size: int) -> QImage:
        stream = self.stream_for_size(size)
        qimage = QImage()
        qimage.loadFromData(stream.read())
        return qimage

    def image(self, size: int) -> Image:
        return Image(qimage=self.qimage(size))

    def qpixmap(self, size: int) -> QPixmap:
        return QPixmap(self.qimage(size))

    def qicon(self, size: Optional[int] = None) -> QIcon:
        icon = QIcon()
        if size is not None:
            sizes = [size]
        else:
            sizes = [16, 22, 24, 32, 40, 48, 64, 128, 256]
        for size in sizes:
            try:
                pixmap = self.qpixmap(size)
            except Exception:
                pass
            else:
                icon.addPixmap(pixmap)
        return icon
