from .spacer import Spacer


DEBUG = 0


class LayoutChild(object):
    def __init__(self):
        self.element = None
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
    def __init__(self, padding):
        # self.min_size = (0, 0)
        self.position = (0, 0)
        self.size = (0, 0)
        self.padding_left = padding
        self.padding_right = padding
        self.padding_top = padding
        self.padding_bottom = padding
        self._skip = 0
        # self.origin = (0, 0)
        self.children = []
        self.min_width = 0
        self.min_height = 0

    def is_visible(self):
        return True

    def get_padding(self):
        return (
            self.padding_left,
            self.padding_top,
            self.padding_right,
            self.padding_bottom,
        )

    def set_padding(self, *amount):
        print("set_padding", amount)
        try:
            self.padding_left = amount[0]
            self.padding_top = amount[1]
            self.padding_right = amount[2]
            self.padding_bottom = amount[3]
        except IndexError:
            self.padding_left = amount[0]
            self.padding_right = amount[0]
            self.padding_top = amount[0]
            self.padding_bottom = amount[0]

    padding = property(get_padding, set_padding)

    def get_min_size(self):
        return self.get_min_width(), self.get_min_height()

    def insert(
        self,
        index,
        element,
        spacing=0,
        expand=False,
        fill=False,
        valign=0.5,
        margin=0,
        margin_left=None,
        margin_right=None,
        margin_top=None,
        margin_bottom=None,
    ):
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
        element,
        spacing=0,
        expand=False,
        fill=False,
        valign=0.5,
        margin=0,
        margin_left=None,
        margin_right=None,
        margin_top=None,
        margin_bottom=None,
        index=None,
        left=None,
        right=None,
        top=None,
        bottom=None,
    ):
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
        child = LayoutChild()
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

    def remove(self, element):
        for i, child in enumerate(self.children):
            if child.element == element:
                del self.children[i]
                return

    def add_spacer(self, size=0, size2=None, expand=False):
        self.add(Spacer(size, size2), expand=expand)

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position
        # self.origin = position
        # FIXME: avoid calling update after both set_position and set_size
        self.update()

    def set_size(self, size):
        if DEBUG:
            print("Layout.set_size", size)
        self.size = size
        self.update()

    def set_position_and_size(self, position, size):
        self.position = position
        self.size = size
        self.update()

    def update(self):
        pass


class LinearLayout(Layout):
    def __init__(self, vertical, padding=0):
        Layout.__init__(self, padding)
        self.vertical = vertical

    def update(self):
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
            if not child.element.is_visible():
                continue

            child.min_size = [
                child.element.get_min_width(),
                child.element.get_min_height(),
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
            if not child.element.is_visible():
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
                    position[1] += round((
                        fill_size[1]
                        - child.margin_top
                        - child.margin_bottom
                        - size[1]
                    ) * child.valign)

            child.element.set_position_and_size(position, size)

            if self.vertical:
                y += size[1] + child._skip
            else:
                x += size[0] + child._skip


class HorizontalLayout(LinearLayout):
    def __init__(self, padding=0):
        LinearLayout.__init__(self, False, padding=padding)

    def get_min_width(self):
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

    def get_min_height(self):
        min_height = 0
        for child in self.children:
            h = child.element.get_min_height()
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
    def __init__(self, padding=0):
        LinearLayout.__init__(self, True, padding=padding)

    def get_min_width(self):
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

    def get_min_height(self):
        min_height = 0
        last_margin = 0
        for child in self.children:
            if hasattr(child.element, "explicitly_hidden"):
                if child.element.explicitly_hidden():
                    continue
            min_height += child.element.get_min_height()
            min_height += max(last_margin, child.margin_top)
            last_margin = child.margin_bottom
        min_height += last_margin
        min_height += self.padding_top + self.padding_bottom
        if min_height < self.min_height:
            return self.min_height
        return min_height
