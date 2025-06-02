from typing import Tuple
from fsui.qt import Qt, QPoint, QRect, QPen, QBrush, QLinearGradient, QColor
from fsui.qt import QFont
from .Color import Color


class Font(object):
    def __init__(self, name=None, size=None, font=None):
        if font is not None:
            self.font = font
        else:
            assert name
            self.font = QFont(name)
            if size:
                self.font.setPixelSize(size)

    def qfont(self):
        return self.font

    def set_bold(self, bold=True):
        self.font.setWeight(QFont.Weight.DemiBold if bold else QFont.Weight.Normal)

    def adjust_size(self, increment=1):
        size = self.font.pointSize()
        print("pontSize is", size)
        self.font.setPointSize(size + increment)

    def increase_size(self, increment=1):
        size = self.font.pointSize()
        print("pontSize is", size)
        self.font.setPointSize(size + increment)


class DrawingContext(object):
    def __init__(self, painter):
        self.qpainter = painter
        self.text_color = Color(0, 0, 0)

    def clear(self, color=None):
        # assuming here that the operations are clipped anyway, so just
        # using an larger-than-expected size
        rect = QRect(0, 0, 3000, 2000)
        if color is not None:
            self.qpainter.fillRect(rect, QBrush(color))
        else:
            self.qpainter.eraseRect(rect)

    def get_font(self):
        return Font(self.qpainter.font())

    def set_font(self, font):
        self.qpainter.setFont(font.font)

    def draw_text(self, text: str, x: int, y: int) -> None:
        # self.qpainter.drawText(QPoint(x, y), text)
        self.qpainter.setPen(QPen(self.text_color))
        self.qpainter.drawText(
            x, y, 10000, 1000, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, text
        )

    def measure_text(self, text: str) -> Tuple[int, int]:
        # return self.dc.GetTextExtent(text)
        # return (10, 10)
        rect = self.qpainter.boundingRect(
            0, 0, 10000, 1000, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, text
        )
        return rect.width(), rect.height()

    # def set_color(self, color):
    #     self.dc.SetPen(wx.Pen(color))
    #     #self.gc.SetPen(self.gc.CreatePen(wx.Pen(color)))

    def get_text_color(self):
        # return Color(self.dc.GetTextForeground())
        # pass
        # return Color(self.qpainter.pen().color())
        return self.text_color

    def set_text_color(self, color):
        # self.dc.SetTextForeground(color)
        # self.qpainter.setPen(QPen(color))
        self.text_color = Color(color)

    def draw_line(self, x1, y1, x2, y2, c):
        if x1 == x2:  # Line is vertical
            if y1 > y2:
                y1, y2 = y2, y1
            x2 += 1
        elif y1 == y2:  # Line is horizontal
            if x1 > x2:
                x1, x2 = x2, x1
            y2 += 1
        else:
            # Line is neither horizontal nor vertical, not supported right now
            return
        self.draw_rectangle(x1, y1, x2 - x1, y2 - y1, c)

    def draw_image(self, image, x, y):
        # self.dc.DrawBitmap(image.bitmap, x, y, True)
        self.qpainter.drawImage(QPoint(x, y), image.qimage)

    def draw_vertical_gradient(self, x, y, w, h, c1, c2):
        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0.0, c1)
        gradient.setColorAt(1.0, c2)
        self.qpainter.setPen(QPen(QColor(0, 0, 0, 0)))
        self.qpainter.setBrush(QBrush(gradient))
        self.qpainter.drawRect(x, y, w, h)

    def draw_rectangle(self, x, y, w, h, c):
        self.qpainter.setPen(QPen(QColor(0, 0, 0, 0)))
        self.qpainter.setBrush(QBrush(c))
        self.qpainter.drawRect(x, y, w, h)

    def rounded_rectangle(
        self, x, y, w, h, c, radius, border_color=None, border_width=1.0
    ):
        if border_color is not None:
            self.qpainter.setPen(QPen(border_color, border_width))
        else:
            self.qpainter.setPen(QPen(QColor(0, 0, 0, 0)))
        self.qpainter.setBrush(QBrush(c))
        self.qpainter.drawRoundedRect(x, y, w, h, radius, radius)
