from typing import Optional, Tuple, Union

from fsui.common.element import LightElement
from fswidgets.types import Size


class Spacer(LightElement):
    def __init__(
        self,
        size: int = 0,
        size2: Optional[int] = None,
        horizontal: bool = False,
    ):
        LightElement.__init__(self, None)
        self.width: int
        self.height: int
        if size2 is None:
            if horizontal:
                self.width = size
                self.height = 0
            else:
                self.height = size
                self.width = 0
        else:
            self.width = size
            self.height = size2

    def get_min_size(self) -> Tuple[int, int]:
        return self.width, self.height

    def get_min_width(self) -> int:
        return self.width

    def get_min_height(self, width: int) -> int:
        return self.height
