import fsui


class Column(fsui.VerticalLayout):

    def __init__(self, parent=None, padding=0):
        super().__init__(padding)
        if parent is not None:
            if hasattr(parent, "set_layout"):
                parent.set_layout(self)
            else:
                parent.layout = self

    def add(self, element, spacing=0, expand=False, fill=True, valign=0.5,
            margin=0, left=None, right=None,
            top=None, bottom=None):
        super().add(element, spacing=spacing, expand=expand, fill=fill,
                    valign=valign, margin=margin, margin_left=left,
                    margin_right=right, margin_top=top, margin_bottom=bottom)

    def expand(self):
        return self.spacer(0, expand=True)

    def row(self, **kwargs):
        row = Row()
        self.add(row, **kwargs)
        return row

    def set_min_size(self, size):
        self.min_width = size[0]
        self.min_height = size[1]

    def spacer(self, size, expand=False):
        self.add_spacer(1, size, expand=expand)


class Row(fsui.HorizontalLayout):

    def __init__(self, parent=None, padding=0):
        super().__init__(padding)
        if parent is not None:
            if hasattr(parent, "set_layout"):
                parent.set_layout(self)
            else:
                parent.layout = self

    def add(self, element, spacing=0, expand=False, fill=True, valign=0.5,
            margin=0, left=None, right=None,
            top=None, bottom=None):
        super().add(element, spacing=spacing, expand=expand, fill=fill,
                    valign=valign, margin=0, margin_left=left,
                    margin_right=right, margin_top=top, margin_bottom=bottom)

    def column(self, **kwargs):
        column = Column()
        self.add(column, **kwargs)
        return column

    def expand(self):
        return self.spacer(0, expand=True)

    def set_min_size(self, size):
        self.min_width = size[0]
        self.min_height = size[1]

    def spacer(self, size, expand=False):
        self.add_spacer(size, 1, expand=expand)
