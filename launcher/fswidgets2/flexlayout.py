from typing import Optional, Tuple

from typing_extensions import Literal

from fsui.common.layout import Layout
from fswidgets.widget import Widget

# from autologging import traced


TOP = 0
RIGHT = 1
BOTTOM = 2
LEFT = 3


# @traced
class FlexLayout(Layout):
    def __init__(self, parent=None):
        self.children = []
        # CSS-tyle: top, right, bottom, left
        # self.padding = [0, 0, 0, 0]
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        # self.horizontal = True
        self.flex_direction = 0  # type: Literal[0] | Literal[1]
        self.position = [0, 0]
        self.size = (0, 0)  # type: Tuple[int, int]
        self.align_items = "stretch"
        self.gap = 0

        self.insert_index = 0

        if parent:
            flex_direction = parent.style.get("flexDirection", "row")
            if flex_direction == "row":
                self.flex_direction = 0
            elif flex_direction == "column":
                self.flex_direction = 1
            else:
                raise Exception(f"Unsupported flexDirection {flex_direction}")
            self.align_items = parent.style.get("alignItems", "stretch")
            assert self.align_items in [
                "center",
                "flex-end",
                "flex-start",
                "stretch",
            ]
            self.gap = parent.style.get("gap", 0)

    def add(
        self,
        child: Widget,
        fill: Optional[bool] = None,
        expand: Optional[bool] = None,
    ):
        # Inserting at index instead of appending, since we can then use a
        # default insert index for new items, allowing widgets to support
        # adding widgets into the middle of default widgets.
        self.children.insert(self.insert_index, child)
        self.insert_index += 1

    def get_min_size(self):
        min_width = self.get_min_width()
        min_height = self.get_min_height(min_width)
        return (min_width, min_height)

    def get_min_width(self):
        # min_width = self.padding[RIGHT] + self.padding[LEFT]
        min_width = 0
        if self.flex_direction == 0:
            for i, child in enumerate(self.children):
                min_width += calculate_min_dimension(
                    child, 0, None, margins=True
                )
                if i > 0:
                    min_width += self.gap
        else:
            for child in self.children:
                min_width = max(
                    min_width,
                    calculate_min_dimension(child, 0, None, margins=True),
                )
        return min_width

    def get_min_height(self, width):
        min_height = 0
        if self.flex_direction == 0:
            for child in self.children:
                min_height = max(
                    min_height,
                    calculate_min_dimension(child, 1, width, margins=True),
                )
        else:
            for i, child in enumerate(self.children):
                min_height += calculate_min_dimension(
                    child, 1, width, margins=True
                )
                if i > 0:
                    min_height += self.gap
        return min_height

    def set_position(self, position: Tuple[int, int]):
        self.position = position

    def set_size(self, size: Tuple[int, int]):
        self.width = size[0]
        self.height = size[1]
        self.size = (size[0], size[1])

    def update(self):
        import traceback

        # traceback.print_stack()
        # print("FlexLayout.update width =", self.width, "height =", self.height)
        assert self.flex_direction in [0, 1]
        self.layout_children(self.flex_direction)
        # else:
        #     self.layout_children(1)

    def layout_children(self, flex_direction=0):
        d = flex_direction
        # x = self.x
        # y = self.y
        # width = self.width
        # height = self.height
        pos = self.position[d]
        size = self.size[d]
        # align = self.style["alignItems"]

        children = []

        flex_basis_total = 0
        flex_basis_total_inc_margins = 0
        flex_grow_total = 0
        for child_object in self.children:
            flex_basis = calculate_flex_basis(
                child_object, d, None if d == 0 else self.size[0]
            )
            flex_grow = 0
            align = self.align_items
            max_size = None
            cross_max_size = None
            cross_size = None
            margin_start = 0
            margin_end = 0
            cross_margin_start = 0
            cross_margin_end = 0

            if hasattr(child_object, "style"):
                style = child_object.style
                # FIXME: Min size? (included in ideal size so less important)
                cross_max_size = style.get(
                    "maxHeight" if d == 0 else "maxWidth"
                )
                cross_size = style.get("height" if d == 0 else "width")
                flex_grow = style.get("flexGrow", 0)
                align = style.get("alignSelf", align)
                max_size = style.get("maxWidth" if d == 0 else "maxHeight")

                margin_start = style.get(
                    "marginLeft" if d == 0 else "marginTop", 0
                )
                margin_end = style.get(
                    "marginRight" if d == 0 else "marginBottom", 0
                )
                cross_margin_start = style.get(
                    "marginLeft" if d == 1 else "marginTop", 0
                )
                cross_margin_end = style.get(
                    "marginRight" if d == 1 else "marginBottom", 0
                )

            flex_basis_total += flex_basis
            flex_basis_total_inc_margins += (
                flex_basis + margin_start + margin_end
            )
            # if i > 0:
            #     flex_basis_total_inc_margins

            flex_grow_total += flex_grow

            children.append(
                {
                    "align": align,
                    "cross_margins": cross_margin_start + cross_margin_end,
                    "cross_margin_start": cross_margin_start,
                    "cross_margin_end": cross_margin_end,
                    "cross_max_size": cross_max_size,
                    "cross_size": cross_size,
                    "flex_basis": flex_basis,
                    "flex_grow": flex_grow,
                    # "margins": margin_start + margin_end,
                    "margin_start": margin_start,
                    "margin_end": margin_end,
                    "object": child_object,
                    "size": flex_basis,
                    "size_max": max_size,
                }
            )

        if flex_grow_total == 0:
            pass
        else:
            restart = True
            available_size = size - self.gap * (len(self.children) - 1)
            while restart:
                restart = False
                # grow_rate = (size - flex_basis_total) / flex_grow_total
                grow_rate = (
                    available_size - flex_basis_total_inc_margins
                ) / flex_grow_total
                for child in children:
                    child["size"] += round(child["flex_grow"] * grow_rate)
                    if child["size_max"] and child["size"] > child["size_max"]:
                        # Set size to max size, prevent growth, and restart
                        child["size"] = child["size_max"]
                        flex_grow_total -= child["flex_grow"]
                        child["flex_grow"] = 0
                        restart = True
                        break

        for i, child in enumerate(children):
            child_position = [0, 0]
            if i > 0:
                pos += self.gap
            pos += child["margin_start"]
            child_position[d] = pos
            child_position[not d] = self.position[not d]

            child_size = [0, 0]
            child_size[d] = child["size"]
            cross_max_size = child["cross_max_size"]

            align = child["align"]
            parent_cross_size = self.size[not d]
            if align == "stretch":
                if child["cross_size"] is not None:
                    cross_size = child[
                        "cross_size"
                    ]  # + child["cross_margins"]
                else:
                    cross_size = parent_cross_size - child["cross_margins"]
                if cross_max_size is not None:
                    cross_size = min(cross_size, cross_max_size)
                child_position[not d] += child["cross_margin_start"]
            else:
                if child["cross_size"] is not None:
                    cross_size = child["cross_size"]
                else:
                    cross_size = (
                        child["object"].get_min_height(child["size"])
                        if d == 0
                        else child["object"].get_min_width()
                    )
                if cross_max_size is not None:
                    cross_size = min(cross_size, cross_max_size)
                cross_size_inc_margins = cross_size + child["cross_margins"]
                if align == "flex-start":
                    pass
                elif align == "center":
                    child_position[not d] += (
                        child["cross_margin_start"]
                        + (parent_cross_size - cross_size_inc_margins) // 2
                    )
                elif align == "flex-end":
                    child_position[not d] += (
                        child["cross_margin_start"]
                        + parent_cross_size
                        - cross_size_inc_margins
                    )

            child_size[not d] = cross_size

            # print(child_position, child_size)
            child["object"].set_position_and_size(child_position, child_size)
            pos += child["size"] + child["margin_end"]

    def layout_children_vertically(self):
        x = self.x
        y = self.y


def calculate_flex_basis(child, direction, width):
    return calculate_min_dimension(child, direction, width)


def calculate_min_dimension(child, direction, width, margins=False):
    d = direction
    # min_size = 0
    # padding_left = 0
    # padding_right = 0
    # padding = 0

    style = getattr(child, "style", {})

    # if width is None:
    #     padding_start = int(style.get("paddingLeft", 0))
    #     padding_end = int(style.get("paddingRight", 0))
    # else:
    #     padding_start = int(style.get("paddingTop", 0))
    #     padding_end = int(style.get("paddingBottom", 0))
    # padding = padding_start + padding_end

    # width_or_height = ("width", "height")
    size = style.get("width" if d == 0 else "height", None)

    # if size is not None:
    #     return size

    # if hasattr(child, "layout"):
    #     layout = child.layout
    #     if width is None:
    #         min_size = padding + layout.get_min_width()
    #     else:
    #         min_size = padding + layout.get_min_height(width=width)
    #     return min_size

    # FIXME: Qt-specific
    # min_size = 10
    # if width is None:
    #     min_size = child.minimumSizeHint()[0]
    # else:
    #     min_size = child.minimumSizeHint()[1]
    if size is None:
        size = child.get_min_width() if d == 0 else child.get_min_height(width)

    max_size = style.get("maxWidth" if d == 0 else "maxHeight", size)
    size = min(size, max_size)

    if margins:
        margin_start = style.get("marginLeft" if d == 0 else "marginTop", 0)
        margin_end = style.get("marginRight" if d == 0 else "marginBottom", 0)
        size += margin_start + margin_end

    return size
