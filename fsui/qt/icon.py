from fsbc.resources import Resources
from fsui.qt.image import Image
from fsui.qt.qt import QPixmap, QImage, QIcon


class Icon:
    """
    FIXME: Add support for icon search path, so, during startup, a list
    of package data directories to check can be added to this class, and
    icons can be looked up just by name.
    """

    def __init__(self, name, path=""):
        self.name = name
        self.path = path

    def stream_for_size(self, size):
        # package, file_ = name.split(":", 1)
        # if self.name.startswith("/"):
        #     return open(self.name, "rb")
        # else:
        assert self.path.startswith("pkg:")
        package = self.path[4:]
        try:
            name = "res/{0}x{0}/{1}.png".format(size, self.name)
            stream = Resources(package).stream(name)
        except LookupError:
            name = "res/{0}/{1}.png".format(size, self.name)
            stream = Resources(package).stream(name)
        return stream

    def qimage(self, size):
        stream = self.stream_for_size(size)
        qimage = QImage()
        qimage.loadFromData(stream.read())
        return qimage

    def image(self, size):
        return Image(qimage=self.qimage(size))

    def qpixmap(self, size):
        return QPixmap(self.qimage(size))

    def qicon(self, size=None):
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
