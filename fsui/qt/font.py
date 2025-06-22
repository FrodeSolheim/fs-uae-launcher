from typing import Optional, Union

from typing_extensions import TypedDict

from fscore.deprecated import deprecated
from fsui.qt.qt import QFont
from fswidgets.qt.gui import QFontMetrics
from fswidgets.types import Size

# FIXME: Add more
weight_map = {
    "normal": 400,
    "medium": 500,
    "semi-bold": 600,
    "bold": 700,
}


class FontDescription(TypedDict):
    name: str
    weight: Union[str, int]
    size: int


class Font:
    @staticmethod
    def from_description(description: str) -> "Font":
        return Font(**Font.parse(description))

    @staticmethod
    def parse(description: str) -> FontDescription:
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
        self,
        name: Optional[str] = None,
        size: Optional[int] = None,
        font: Optional[QFont] = None,  # legacy option
        qFont: Optional[QFont] = None,
        weight: Optional[Union[int, str]] = None,
    ) -> None:
        self.font: QFont
        if qFont is not None:
            self.font = qFont
        elif font is not None:
            self.font = font
        else:
            assert name
            self.font = QFont(name)
            if size:
                self.font.setPixelSize(size)
        if weight:
            self.set_weight(weight)

    def describe(self) -> FontDescription:
        return {
            "name": self.font.family(),
            "size": self.font.pixelSize(),
            "weight": self.font.weight(),
        }

    def measureText(self, text: str) -> Size:
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
    def set_bold(self, bold: bool = True) -> "Font":
        return self.setBold(bold)

    # def size(self):
    #     return self.font.pixelSize()
    #
    # def set_size(self, size):
    #     self.font.setPixelSize(size)

    def set_weight(self, weight: Union[int, str]) -> "Font":
        # print("\n\n\nset weight weight", weight)
        # qt_weight = QFont.Normal
        if isinstance(weight, str):
            iweight = weight_map.get(weight.lower(), 400)
        else:
            iweight = weight
        # FIXME: Create proper table and add more
        if iweight == 400:
            qt_weight = QFont.Weight.Normal
        elif iweight == 500:
            qt_weight = QFont.Weight.Medium
        elif iweight == 600:
            qt_weight = QFont.Weight.DemiBold
        elif iweight == 700:
            qt_weight = QFont.Weight.Bold
        else:
            print(f"WARNING: Font.set_weight: Unknown font weight {weight}")
            qt_weight = QFont.Weight.Normal
        # print(qt_weight)
        self.font.setWeight(qt_weight)
        # Allow chaining operations
        return self

    def adjust_size(self, increment: int = 1) -> None:
        size = self.font.pointSize()
        print("pontSize is", size)
        self.font.setPointSize(size + increment)

    def increase_size(self, increment: int = 1) -> None:
        size = self.font.pointSize()
        print("pontSize is", size)
        self.font.setPointSize(size + increment)

    def set_point_size(self, point_size: int) -> "Font":
        self.font.setPointSize(point_size)
        # Allow chaining operations
        return self

    def set_size(self, size: int) -> "Font":
        self.font.setPixelSize(size)
        # Allow chaining operations
        return self
