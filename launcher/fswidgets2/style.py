from typing import Dict, Union


class Style:
    def __init__(
        self,
        initial: Dict[str, Union[str, int]] = None,
        addStyle: Dict[str, Union[str, int]] = None,
    ):
        super().__init__()
        self._explicit = initial.copy() if initial else {}
        # else:
        #     self._explicit = {}  # type: Dict[str, Union[str, int]]
        if addStyle is not None:
            self._explicit.update(addStyle)

        self._implicit = {}  # type: Dict[str, Union[str, int]]
        # self.padding_top = 0
        # self.padding_right = 0
        # self.padding_bottom = 0
        # self.padding_left = 0
        self._update()

    def update(self, *args, **kwargs):
        # super().update(*args, **kwargs)
        self._explicit.update(*args, **kwargs)
        self._update()

    def get(self, key, default=None):
        return self._implicit.get(key, default)

    def _update(self):
        style = self._explicit.copy()

        padding = style.get("padding")
        if isinstance(padding, int):
            if style.get("paddingTop") is None:
                style["paddingTop"] = padding
            if style.get("paddingRight") is None:
                style["paddingRight"] = padding
            if style.get("paddingBottom") is None:
                style["paddingBottom"] = padding
            if style.get("paddingLeft") is None:
                style["paddingLeft"] = padding
        if style.get("paddingTop") is None:
            style["paddingTop"] = 0
        if style.get("paddingRight") is None:
            style["paddingRight"] = 0
        if style.get("paddingBottom") is None:
            style["paddingBottom"] = 0
        if style.get("paddingLeft") is None:
            style["paddingLeft"] = 0

        margin = style.get("margin")
        if isinstance(margin, int):
            if style.get("marginTop") is None:
                style["marginTop"] = margin
            if style.get("marginRight") is None:
                style["marginRight"] = margin
            if style.get("marginBottom") is None:
                style["marginBottom"] = margin
            if style.get("marginLeft") is None:
                style["marginLeft"] = margin
        if style.get("marginTop") is None:
            style["marginTop"] = 0
        if style.get("marginRight") is None:
            style["marginRight"] = 0
        if style.get("marginBottom") is None:
            style["marginBottom"] = 0
        if style.get("marginLeft") is None:
            style["marginLeft"] = 0

        self._implicit = style
        # padding = self.get("padding")
        # if isinstance(padding, int):
        #     self.padding_top = padding
        #     self.padding_right = padding
        #     self.padding_bottom = padding
        #     self.padding_left = padding
        # self.padding_top = self.get("paddingTop", self.padding_top)
        # self.padding_right = self.get("paddingRight", self.padding_right)
        # self.padding_bottom = self.get("paddingBottom", self.padding_bottom)
        # self.padding_left = self.get("paddingLeft", self.padding_left)

        # margin = self.get("margin")
        # if self.get("marginTop") is None:
        #     self["marginTop"] = margin
        # if not self.get("marginLeft"):
        #     self["marginLeft"] = margin

    @property
    def padding_top(self):
        return self.get("paddingTop")

    @property
    def padding_right(self):
        return self.get("paddingRight")

    @property
    def padding_bottom(self):
        return self.get("paddingBottom")

    @property
    def padding_left(self):
        return self.get("paddingLeft")
