from typing import Optional

from fscore.deprecated import deprecated
from fsui.qt.qt import QFont
from fswidgets.qt.gui import QFontMetrics

# FIXME: Add more
weight_map = {
    "normal": 400,
    "medium": 500,
    "semi-bold": 600,
    "bold": 700,
}


class Font:
    @staticmethod
    def from_description(description):
        return Font(**Font.parse(description))

    @staticmethod
    def parse(description):
        parts = description.split(" ")
        size = 16
        weight = "normal"
        if len(parts) > 1 and parts[-1].isdecimal():
            size = int(parts.pop())
        if len(parts) > 1 and parts[-1].lower() in weight_map:
            weight = parts.pop()
        name = " ".join(parts).strip()
        print(name, "weight =", weight, "size =", size)
        # return (name, weight, size)
        return {"name": name, "weight": weight, "size": size}

    def __init__(
        self, name=None, size=None, font: Optional[QFont] = None, weight=None
    ):
        if font is not None:
            self.font: QFont = font
        else:
            assert name
            self.font = QFont(name)
            if size:
                self.font.setPixelSize(size)
        if weight:
            self.set_weight(weight)

    def describe(self):
        return {
            "name": self.font.family(),
            "size": self.font.pixelSize(),
            "weight": self.font.weight(),
        }

    def measureText(self, text: str):
        metrics = QFontMetrics(self.qfont)
        return metrics.width(text), metrics.height()

    @property
    def qfont(self) -> QFont:
        return self.font

    def setBold(self, bold: bool = True) -> "Font":
        self.qfont.setBold(bold)
        # Allow chaining operations
        return self

    @deprecated
    def set_bold(self, bold: bool = True):
        return self.setBold(bold)

    # def size(self):
    #     return self.font.pixelSize()
    #
    # def set_size(self, size):
    #     self.font.setPixelSize(size)

    def set_weight(self, weight):
        # print("\n\n\nset weight weight", weight)
        # qt_weight = QFont.Normal
        if isinstance(weight, str):
            iweight = weight_map.get(weight.lower(), 400)
        else:
            iweight = weight
        # FIXME: Create proper table and add more
        if iweight == 400:
            qt_weight = QFont.Normal
        elif iweight == 500:
            qt_weight = QFont.Medium
        elif iweight == 600:
            qt_weight = QFont.DemiBold
        elif iweight == 700:
            qt_weight = QFont.Bold
        else:
            print(f"WARNING: Font.set_weight: Unknown font weight {weight}")
            qt_weight = QFont.Normal
        # print(qt_weight)
        self.font.setWeight(qt_weight)
        # Allow chaining operations
        return self

    def adjust_size(self, increment=1):
        size = self.font.pointSize()
        print("pontSize is", size)
        self.font.setPointSize(size + increment)

    def increase_size(self, increment=1):
        size = self.font.pointSize()
        print("pontSize is", size)
        self.font.setPointSize(size + increment)

    def set_point_size(self, point_size):
        self.font.setPointSize(point_size)
        # Allow chaining operations
        return self

    def set_size(self, size):
        self.font.setPixelSize(size)
        # Allow chaining operations
        return self
