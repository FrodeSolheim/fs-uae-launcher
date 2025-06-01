from fsbc.resources import Resources
from fsui.qt import Qt, QImage, QIcon, QPixmap


class Image(object):

    NEAREST = 0

    def __init__(self, name="", object=None):
        if object:
            self.qimage = object
        else:
            self.qimage = QImage()

            if hasattr(name, "read"):
                self.qimage.loadFromData(name.read())
            elif name.startswith("pkg://"):
                parts = name.split("/", 3)
                stream = Resources(parts[2]).stream(parts[3])
                self.qimage.loadFromData(stream.read())
            else:
                index = name.find(":")
                if index > 1:
                    package, file_ = name.split(":", 1)
                    stream = Resources(package).stream(file_)
                    self.qimage.loadFromData(stream.read())
                else:
                    print("loading image from", name)
                    self.qimage.load(name)
            # self._bitmap = None

    @property
    def size(self):
        return self.qimage.width(), self.qimage.height()

    def width(self):
        return self.qimage.width()

    def height(self):
        return self.qimage.height()

    @property
    def qpixmap(self):
        return QPixmap(self.qimage)

    @property
    def qicon(self):
        return QIcon(QPixmap(self.qimage))

    # @property
    # def bitmap(self):
    #     if self._bitmap is None:
    #         self._bitmap = wx.BitmapFromImage(self.qimage)
    #     return self._bitmap

    def grey_scale(self):
        # return Image(object=self.qimage.convertToFormat(
        #     QImage.Format_ARGB32, Qt.AutoOnly))
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
        return Image(object=copy)

    def resize(self, size, filter=1):
        if size == self.size:
            return
        if filter:
            q = Qt.TransformationMode.SmoothTransformation
        else:
            q = Qt.TransformationMode.FastTransformation
        self.qimage = self.qimage.scaled(
            size[0], size[1], Qt.AspectRatioMode.IgnoreAspectRatio, q
        )
        # self._bitmap = None
