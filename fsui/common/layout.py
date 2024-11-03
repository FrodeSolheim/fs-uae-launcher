from typing import Any, List, Optional, Tuple, Union, cast

from typing_extensions import Protocol

from fsui.common.spacer import Spacer
from fswidgets.types import Point, Size

DEBUG = 0


class LayoutItem(Protocol):
    def get_min_height(self, width: int) -> int:
        ...

    def get_min_width(self) -> int:
        ...


class LayoutItemInfo(object):
    def __init__(self) -> None:
        self.element: LayoutItem
        self.spacing = 0
        self.expand = False
        self.fill = False
        self.valign = 0.5
        self.margin_left = 0
        self.margin_right = 0
        self.margin_top = 0
        self.margin_bottom = 0
        self.size = 0


class Layout(object):
    def __init__(self, padding: int) -> None:
        # self.min_size = (0, 0)
        self.position = (0, 0)
        self.size = (0, 0)
        self.padding_left: int = padding
        self.padding_right: int = padding
        self.padding_top: int = padding
        self.padding_bottom: int = padding
        self._skip = 0
        # self.origin = (0, 0)
        self.children: List[Any] = []
        self.min_width = 0
        self.min_height = 0

    def visible(self) -> bool:
        return True

    def get_min_width(self) -> int:
        raise NotImplementedError()

    def get_min_height(self, width: int) -> int:
        raise NotImplementedError()

    def get_padding(self) -> Tuple[int, int, int, int]:
        return (
            self.padding_left,
            self.padding_top,
            self.padding_right,
            self.padding_bottom,
        )

    def set_padding(
        self, *amount: Union[int, Tuple[int, int, int, int]], css: bool = False
    ) -> None:
        print("set_padding", amount)
        try:
            amount = cast(Tuple[int, int, int, int], amount)
            if css:
                self.padding_top = amount[0]
                self.padding_right = amount[1]
                self.padding_bottom = amount[2]
                self.padding_left = amount[3]
            else:
                self.padding_left = amount[0]
                self.padding_top = amount[1]
                self.padding_right = amount[2]
                self.padding_bottom = amount[3]
        except IndexError:
            assert isinstance(amount[0], int)
            self.padding_left = amount[0]
            self.padding_right = amount[0]
            self.padding_top = amount[0]
            self.padding_bottom = amount[0]

    padding = property(get_padding, set_padding)

    def get_min_size(self) -> Size:
        min_width = self.get_min_width()
        min_height = self.get_min_height(min_width)
        return min_width, min_height

    def insert(
        self,
        index: int,
        element: LayoutItem,
        spacing: int = 0,
        expand: bool = False,
        fill: bool = False,
        valign: float = 0.5,
        margin: int = 0,
        margin_left: Optional[int] = None,
        margin_right: Optional[int] = None,
        margin_top: Optional[int] = None,
        margin_bottom: Optional[int] = None,
    ) -> None:
        self.add(
            element,
            spacing=spacing,
            expand=expand,
            fill=fill,
            valign=valign,
            margin=margin,
            margin_left=margin_left,
            margin_right=margin_right,
            margin_top=margin_top,
            margin_bottom=margin_bottom,
            index=index,
        )

    # FIXME: Rename margin -> margins (+ alias), margin_top -> top, etc
    def add(
        self,
        element: LayoutItem,
        spacing: int = 0,
        expand: bool = False,
        fill: bool = False,
        valign: float = 0.5,
        margin: int = 0,
        margin_left: Optional[int] = None,
        margin_right: Optional[int] = None,
        margin_top: Optional[int] = None,
        margin_bottom: Optional[int] = None,
        index: Optional[int] = None,
        left: Optional[int] = None,
        right: Optional[int] = None,
        top: Optional[int] = None,
        bottom: Optional[int] = None,
    ) -> None:
        """

        - By setting fill < 0, the height or width of the control will not
          be taken into account when calculating the layout height or width
          (depending on orientation). This makes it possible to center a
          larger control on a smaller layout

        - By setting expand < 0, the height or width of the control will not
          be taken into account as reserved space. It will still receive its
          share of expansion space, according to abs(expand) / sum(all expand).

        """
        if left is not None:
            margin_left = left
        if right is not None:
            margin_right = right
        if top is not None:
            margin_top = top
        if bottom is not None:
            margin_bottom = bottom
        child = LayoutItemInfo()
        child.element = element
        child.spacing = spacing
        child.expand = expand
        child.fill = fill
        child.valign = valign
        if margin_left is not None:
            child.margin_left = margin_left
        else:
            child.margin_left = margin
        if margin_right is not None:
            child.margin_right = margin_right
        else:
            child.margin_right = margin
        if margin_top is not None:
            child.margin_top = margin_top
        else:
            child.margin_top = margin
        if margin_bottom is not None:
            child.margin_bottom = margin_bottom
        else:
            child.margin_bottom = margin
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)

    def remove(self, element: LayoutItem) -> None:
        for i, child in enumerate(self.children):
            if child.element == element:
                del self.children[i]
                return

    def add_spacer(
        self,
        size: int,
        size2: Optional[int] = None,
        expand: bool = False,
        horizontal: bool = False,
    ) -> None:
        self.add(Spacer(size, size2, horizontal), expand=expand)

    def get_position(self) -> Point:
        return self.position

    def set_position(self, position: Point) -> None:
        self.position = position
        # self.origin = position
        # FIXME: avoid calling update after both set_position and set_size
        self.update()

    def set_size(self, size: Size) -> None:
        if DEBUG:
            print("Layout.set_size", size)
        self.size = size
        self.update()

    def set_position_and_size(self, position: Point, size: Size) -> None:
        self.position = position
        self.size = size
        self.update()

    def update(self) -> None:
        pass


class LinearLayout(Layout):
    def __init__(self, vertical: bool, padding: int = 0):
        super().__init__(padding)
        self.vertical = vertical

    def update(self) -> None:
        available = self.size[self.vertical]
        if self.vertical:
            available = available - self.padding_top - self.padding_bottom
        else:
            available = available - self.padding_left - self.padding_right
        if DEBUG:
            print("update, available =", available)
        expanding = 0

        last_margin = 0

        for child in self.children:
            if not child.element.visible():
                continue

            child_min_width = child.element.get_min_width()
            child_min_height = child.element.get_min_height(child_min_width)
            child.min_size = [
                child_min_width,
                child_min_height,
            ]

            if child.expand < 0:
                child.size = 0
            else:
                child.size = child.min_size[self.vertical]

            # if child.fill < 0:
            #     child.min_size[not self.vertical] = 0

            available -= child.size
            expanding += abs(child.expand)

            if self.vertical:
                child._skip = max(last_margin, child.margin_top)
                available -= child._skip
                last_margin = child.margin_bottom
                # available = available - child.margin_top - child.margin_bottom
                # available = available - last_margin + max()
                # last_margin = child.margin_bottom
            else:
                child._skip = max(last_margin, child.margin_left)
                available -= child._skip
                last_margin = child.margin_right
        available -= last_margin

        if DEBUG:
            print("available", available, "expanding", expanding)
        if available > 0 and expanding > 0:
            if DEBUG:
                print("distributing extra pixels:", available)
            available2 = available
            for child in self.children:
                extra = int(available2 * (abs(child.expand) / expanding))
                if DEBUG:
                    print(child.expand, expanding, extra)
                child.size += extra
                available -= extra
            # some more pixels could be available due to rounding
            if available > 0:
                # print("distributing extra pixels:", available)
                for child in self.children:
                    if abs(child.expand):
                        child.size += 1
                        available -= 1
                        if available == 0:
                            break
        x = self.padding_left
        y = self.padding_top
        # self_height = self.size[1] - self.padding_top - self.padding_bottom
        fill_size = (
            self.size[0] - self.padding_left - self.padding_right,
            self.size[1] - self.padding_top - self.padding_bottom,
        )

        for child in self.children:
            if not child.element.visible():
                continue

            size = [child.min_size[0], child.min_size[1]]

            size[self.vertical] = child.size
            if child.fill > 0:
                size[not self.vertical] = fill_size[not self.vertical]
                if self.vertical:
                    size[0] -= child.margin_left + child.margin_right
                else:
                    size[1] -= child.margin_top + child.margin_bottom

            if DEBUG:
                print(child.element, size)

            self_pos = self.get_position()
            position = [self_pos[0] + x, self_pos[1] + y]

            position[self.vertical] += child._skip
            if self.vertical:
                position[0] += child.margin_left
            else:
                position[1] += child.margin_top

            if child.fill <= 0:
                # center child
                if self.vertical:
                    # position[0] += (self.size[0] - size[0]) // 2
                    pass
                else:
                    position[1] += int((
                        fill_size[1]
                        - child.margin_top
                        - child.margin_bottom
                        - size[1]
                    ) * child.valign) # because valign is a float

            child.element.set_position_and_size(position, size)

            if self.vertical:
                y += size[1] + child._skip
            else:
                x += size[0] + child._skip


class HorizontalLayout(LinearLayout):
    def __init__(self, padding: int = 0) -> None:
        LinearLayout.__init__(self, False, padding=padding)

    def add_spacer(
        self,
        size: int,
        size2: Optional[int] = None,
        expand: bool = False,
        horizontal: bool = True,  # FIXME: Not nice to include this arg here
        # but typing / mypy complains otherwise
    ) -> None:
        assert horizontal == True
        super().add_spacer(size, size2, expand, horizontal=True)

    def get_min_width(self) -> int:
        min_width = 0
        last_margin = 0
        for child in self.children:
            min_width += child.element.get_min_width()
            min_width += max(last_margin, child.margin_left)
            last_margin = child.margin_right
        min_width += last_margin
        min_width += self.padding_left + self.padding_right
        if min_width < self.min_width:
            return self.min_width
        return min_width

    def get_min_height(self, width: int) -> int:
        min_height = 0
        for child in self.children:
            h = child.element.get_min_height(width)
            if child.fill == -1:
                h = 0
            h += child.margin_top + child.margin_bottom
            if h > min_height:
                min_height = h
        min_height += self.padding_top + self.padding_bottom
        if min_height < self.min_height:
            return self.min_height
        return min_height


class VerticalLayout(LinearLayout):
    def __init__(self, padding: int = 0) -> None:
        super().__init__(True, padding=padding)

    def get_min_width(self) -> int:
        min_width = 0
        for child in self.children:
            if hasattr(child.element, "explicitly_hidden"):
                if child.element.explicitly_hidden():
                    continue
            w = child.element.get_min_width()
            w += child.margin_left + child.margin_right
            if w > min_width:
                min_width = w
        min_width += self.padding_left + self.padding_right
        if min_width < self.min_width:
            return self.min_width
        return min_width

    def get_min_height(self, width: int) -> int:
        min_height = 0
        last_margin = 0
        for child in self.children:
            if hasattr(child.element, "explicitly_hidden"):
                if child.element.explicitly_hidden():
                    continue
            min_height += child.element.get_min_height(width)
            min_height += max(last_margin, child.margin_top)
            last_margin = child.margin_bottom
        min_height += last_margin
        min_height += self.padding_top + self.padding_bottom
        if min_height < self.min_height:
            return self.min_height
        return min_height
