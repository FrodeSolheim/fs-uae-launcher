from typing import Any, Dict, Optional, Union


class Style:
    def __init__(
        self,
        initial: Optional[Dict[str, Union[str, int]]] = None,
        addStyle: Optional[Dict[str, Union[str, int]]] = None,
        *,
        backgroundColor: Optional[str] = None,
        marginBottom: Optional[int] = None,
        marginLeft: Optional[int] = None,
        marginRight: Optional[int] = None,
        marginTop: Optional[int] = None,
        padding: Optional[int] = None,
    ):
        super().__init__()
        self._explicit = initial.copy() if initial else {}
        # else:
        #     self._explicit = {}  # type: Dict[str, Union[str, int]]
        if addStyle is not None:
            self._explicit.update(addStyle)

        def setValue(name: str, value: Any):
            if value is not None:
                self._explicit[name] = value

        setValue(
            "backgroundColor",
            backgroundColor,
        )
        setValue("marginBottom", marginBottom)
        setValue("marginLeft", marginLeft)
        setValue("marginRight", marginRight)
        setValue("marginTop", marginTop)
        setValue("padding", padding)

        # if backgroundColor is not None:
        #     self._explicit["backgroundColor"] = backgroundColor
        # if marginBottom is not None:
        #     self._explicit["marginBottom"] = marginBottom
        # if marginLeft is not None:
        #     self._explicit["marginLeft"] = marginLeft

        self._implicit = {}  # type: Dict[str, Union[str, int]]
        # self.padding_top = 0
        # self.padding_right = 0
        # self.padding_bottom = 0
        # self.padding_left = 0
        self._update()

    def update(self, *args, **kwargs):
        # super().update(*args, **kwargs)
        if len(args) == 1 and isinstance(args[0], Style):
            self._explicit.update(args[0]._explicit)
        else:
            self._explicit.update(*args, **kwargs)
        self._update()

    def get(self, key: str, default=None):
        return self._implicit.get(key, default)

    def getBackgroundColor(self) -> str:
        return self.get("backgroundColor")

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
    def padding_top(self) -> int:
        return self.get("paddingTop")

    @property
    def padding_right(self) -> int:
        return self.get("paddingRight")

    @property
    def padding_bottom(self) -> int:
        return self.get("paddingBottom")

    @property
    def padding_left(self) -> int:
        return self.get("paddingLeft")


# FIXME: Any
StyleParam = Union[Style, Dict[Any, Any]]
