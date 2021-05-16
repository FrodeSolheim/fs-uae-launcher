from dataclasses import dataclass
from typing import Tuple

Point = Tuple[int, int]
Position = Tuple[int, int]
Size = Tuple[int, int]


@dataclass
class WindowState:
    x: int
    y: int
    width: int
    height: int
    maximized: bool


# Import Widget last to resolve any import cycles
# from fsui import Widget
