from fsui.qt import QPixmap, QImage, QIcon
from fsbc.resources import Resources
from .Image import Image


class Icon(object):

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def stream_for_size(self, size):
        # package, file_ = name.split(":", 1)
        assert self.path.startswith("pkg:")
        package = self.path[4:]
        name = "res/{0}/{1}.png".format(size, self.name)
        stream = Resources(package).stream(name)
        return stream

    def qimage(self, size):
        stream = self.stream_for_size(size)
        qimage = QImage()
        qimage.loadFromData(stream.read())
        return qimage

    def image(self, size):
        return Image(object=self.qimage(size))

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
