from typing import Optional

from fscore.deprecated import deprecated
from fswidgets.types import Point, Size
from fswidgets.widget import Widget


class Element:
    def __init__(
        self, parent: Optional[Widget], delay_create: bool = False
    ) -> None:
        self.parent = parent
        from fsui.common.layout import Layout

        self.layout: Optional[Layout] = None
        self.position: Point = (0, 0)
        self.size: Size = (0, 0)

    def create(self) -> "Element":
        self.on_create()
        return self

    def get_min_size(self) -> Size:
        return 0, 0

    def get_position(self) -> Point:
        return self.position

    def get_position_base(self) -> Point:
        base = self.get_position_base()
        pos = self.get_position()
        return base[0] + pos[0], base[1] + pos[1]

    def get_size(self) -> Size:
        return self.size

    @deprecated
    def is_visible(self) -> bool:
        return self.visible()

    def on_create(self) -> None:
        pass

    def on_resize(self) -> None:
        if self.layout:
            self.layout.set_size(self.get_size())
            self.layout.update()

    def set_position(self, position: Point) -> None:
        self.position = position

    def set_position_and_size(self, position: Point, size: Size) -> None:
        self.set_position(position)
        self.set_size(size)

    def set_size(self, size: Size) -> None:
        self.size = size
        if self.layout:
            self.layout.set_size(size)
        self.on_resize()

    def visible(self) -> bool:
        return True


class LightElement(Element):
    def __init__(self, parent: Optional[Widget]) -> None:
        Element.__init__(self, parent)
