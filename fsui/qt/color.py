from typing import Tuple, Union

from fsui.qt import QColor


class Color(QColor):
    # FIXME: Replace/augment constructor with static factory methods
    def __init__(
        self,
        *args: Union[
            QColor, int, Tuple[int, int, int], Tuple[int, int, int, int]
        ],
    ):
        QColor.__init__(self)
        if len(args) == 1:
            c = args[0]
            if isinstance(c, QColor):
                self.setRgb(c.red(), c.green(), c.blue(), c.alpha())
            elif isinstance(c, int):
                r = (c & 0xFF0000) >> 16
                g = (c & 0x00FF00) >> 8
                b = c & 0x0000FF
                self.setRgb(r, g, b)
            else:
                if len(c) == 3:
                    r, g, b = c  # type: ignore
                    self.setRgb(r, g, b)
                else:
                    r, g, b, a = c  # type: ignore
                    self.setRgba(r, g, b, a)  # type: ignore
        elif len(args) == 3:
            self.setRgb(*args)  # type: ignore
        elif len(args) == 4:
            self.setRgb(args[0], args[1], args[2])  # type: ignore
            self.setAlpha(args[3])  # type: ignore
        else:
            raise TypeError("Color object is not initialized")

    @staticmethod
    def fromHex(string: str) -> "Color":
        if not string.startswith("#"):
            return Color(0, 0, 0, 0)
        string = string[1:]
        if len(string) == 6:
            try:
                c = int(string, 16)
            except ValueError:
                return Color(0, 0, 0, 0)
            r = (c & 0xFF0000) >> 16
            g = (c & 0x00FF00) >> 8
            b = c & 0x0000FF
            return Color(r, g, b)
        elif len(string) == 8:
            try:
                c = int(string, 16)
            except ValueError:
                return Color(0, 0, 0, 0)
            r = (c & 0xFF000000) >> 24
            g = (c & 0x00FF0000) >> 16
            b = (c & 0x0000FF00) >> 8
            a = c & 0x000000FF
            return Color(r, g, b, a)
        return Color(0, 0, 0, 0)

    @classmethod
    def from_hex(cls, string: str) -> "Color":
        return cls.fromHex(string)

    def mix(self, color: "Color", opacity: float = 0.5) -> "Color":
        # print("mix", color)
        """Mixes this color with another color and returns the result.

        Arguments:
        color -- The overlay color to mix in (Color or wx.Colour)
        opacity -- The opacity of the overlay color in the range [0.0, 1.0]

        Returns a reference to self.
        """
        assert 0.0 <= opacity <= 1.0, "Invalid opacity"
        iopacity = 1 - opacity
        # return wx.Colour(
        self.set_components(
            int(self[0] * iopacity + color[0] * opacity),
            int(self[1] * iopacity + color[1] * opacity),
            int(self[2] * iopacity + color[2] * opacity),
        )
        return self

    @staticmethod
    def mix_colors(
        basecolor: "Color", overlaycolor: "Color", opacity: float = 0.5
    ) -> "Color":
        c = Color(basecolor)
        return c.mix(overlaycolor, opacity)

    def transparent(self) -> bool:
        return self.alpha() == 0

    def set_components(
        self, red: int, green: int, blue: int, alpha: int = 255
    ) -> None:
        self.setRgb(red, green, blue)
        self.setAlpha(alpha)

    def to_hex(self) -> str:
        if self.alpha() != 255:
            return "#{:02x}{:02x}{:02x}{:02x}".format(
                self.red(), self.green(), self.blue(), self.alpha()
            )
        return "#{:02x}{:02x}{:02x}".format(
            self.red(), self.green(), self.blue()
        )

    def lighten(self, amount: float = 0.05) -> "Color":
        c = HSLColor.fromColor(self).lighten(amount).to_rgb()
        self.set_components(c.red(), c.green(), c.blue())
        return self

    def darken(self, amount: float = 0.05) -> "Color":
        c = HSLColor.fromColor(self).darken(amount).to_rgb()
        self.set_components(c.red(), c.green(), c.blue())
        return self

    # def mix(self, color, opacity=0.5):
    #     """Mixes this color with another color and returns the result.
    #
    #     Arguments:
    #     color -- The overlay color to mix in (Color or wx.Colour)
    #     opacity -- The opacity of the overlay color in the range [0.0, 1.0]
    #
    #     Returns a reference to self.
    #     """
    #     assert opacity >= 0.0 and opacity <= 1.0, "Invalid opacity"
    #     iopacity = 1 - opacity
    #     #return wx.Colour(
    #     self.Set(
    #             int(self.Red() * iopacity + color.Red() * opacity),
    #             int(self.Green() * iopacity + color.Green() * opacity),
    #             int(self.Blue() * iopacity + color.Blue() * opacity))
    #     return self

    def invert(self) -> "Color":
        self.set_components(
            255 - self.red(), 255 - self.green(), 255 - self.blue()
        )
        return self

    def inverted(self) -> "Color":
        return self.copy().invert()

    def copy(self) -> "Color":
        return Color(self.red(), self.blue(), self.green(), self.alpha())

    def complement(self) -> "Color":
        r, g, b = self.red(), self.green(), self.blue()
        baseval = max(r, max(g, b)) + min(r, min(g, b))
        self.set_components(
            baseval - self.red(), baseval - self.green(), baseval - self.blue()
        )
        return self

    def complemented(self) -> "Color":
        return self.copy().complement()

    @property
    def intensity(self) -> int:
        return (self.red() + self.blue() + self.green()) // 3

    def __getitem__(self, index: int) -> int:
        if index == 0:
            return self.red()
        if index == 1:
            return self.green()
        if index == 2:
            return self.blue()
        raise IndexError("Invalid color component")

    def __str__(self) -> str:
        return f"<Color('#{self.red():02x}{self.green():02x}{self.blue():02x}{self.alpha():02x}')'>"

    def __ne__(self, other: object) -> bool:
        """
        >>> Color(1, 2, 3) == Color(0x010203)
        True
        >>> Color(1, 2, 3) == Color(0x010204)
        False
        >>> Color(1, 2, 3) == Color.from_hex("#010203")
        True
        >>> Color(1, 2, 3, 254) == Color.from_hex("#010203")
        False
        >>> Color(1, 2, 3, 255) == Color.from_hex("#010203")
        True
        >>> Color(1, 2, 3, 254) == Color.from_hex("#010203FE")
        True
        >>> Color(1, 2, 3, 254) == None
        False
        >>> Color(1, 2, 3, 254) != None
        True
        >>> Color(1, 2, 3, 254) == "Hello"
        False
        >>> Color(1, 2, 3, 254) != "Hello"
        True
        >>> Color(14, 72, 83, 254) != Color(99, 7, 76, 2)
        True
        >>> Color(14, 72, 83, 254) == Color(99, 7, 76, 2)
        False
        >>> Color(4, 4, 4, 4) == Color(4, 4, 4, 4)
        True
        >>> Color(4, 4, 4, 4) != Color(4, 4, 4, 4)
        False
        """
        if isinstance(other, Color):
            return (
                self.red() != other.red()
                or self.green() != other.green()
                or self.blue() != other.blue()
                or self.alpha() != other.alpha()
            )
        return True


class HSLColor:
    def __init__(self) -> None:
        self.h: float = 0.0
        self.s: float = 0.0
        self.l: float = 0.0

    @classmethod
    def fromColor(cls, color: Color) -> "HSLColor":
        return cls.from_rgb(color.red(), color.green(), color.blue())

    @staticmethod
    def from_rgb(red: int, green: int, blue: int) -> "HSLColor":
        r = red / 255
        g = green / 255
        b = blue / 255
        c = HSLColor()
        ma = max(r, max(g, b))
        mi = min(r, min(g, b))
        if ma == mi:
            c.h = 0
        elif ma == r:
            c.h = (60 * (g - b) / (ma - mi)) % 360
        elif ma == g:
            c.h = (60 * (b - r) / (ma - mi)) + 120
        else:
            c.h = (60 * (r - g) / (ma - mi)) + 240
        c.l = (ma + mi) / 2
        if ma == mi:
            c.s = 0
        elif c.l <= 0.5:
            c.s = (ma - mi) / (2 * c.l)
        else:  # c.l > 0.5
            c.s = (ma - mi) / (2 - 2 * c.l)
        return c

    def darken(self, amount: float = 0.05) -> "HSLColor":
        self.l = max(0.0, self.l - amount)
        return self

    def lighten(self, amount: float = 0.05) -> "HSLColor":
        self.l = min(1.0, self.l + amount)
        return self

    def to_rgb(self) -> Color:
        if self.l < 0.5:
            q = self.l * (1 + self.s)
        else:  # c.l >= 0.5
            q = self.l + self.s - (self.l * self.s)
        p = 2 * self.l - q
        hk = self.h / 360
        # t = [tr, tg, tb]
        t = [hk + 1 / 3, hk, hk - 1 / 3]
        for i in range(3):
            if t[i] < 0.0:
                t[i] += 1.0
            elif t[1] > 1.0:
                t[i] -= 1.0
        rgb = [0, 0, 0]
        for i in range(3):
            if t[i] < 1 / 6:
                rgb[i] = int(round(255 * (p + ((q - p) * 6 * t[i]))))
            elif 1 / 6 <= t[i] < 1 / 2:
                rgb[i] = int(round(255 * q))
            elif 1 / 2 <= t[i] < 2 / 3:
                rgb[i] = int(round(255 * (p + ((q - p) * 6 * (2 / 3 - t[i])))))
            else:
                rgb[i] = int(round(255 * p))
        return Color(rgb[0], rgb[1], rgb[2])

    def __getitem__(self, index: int) -> int:
        if index == 0:
            return int(round(self.h))
        if index == 1:
            return int(round(self.s * 100))
        if index == 2:
            return int(round(self.l * 100))
        raise IndexError("Invalid color component")

    # FIXME: getitem / set_components does not use the same scale
    def set_components(self, h: float, s: float, l: float) -> None:
        self.h = h
        self.s = s
        self.l = l


if __name__ == "__main__":
    import doctest

    doctest.testmod()
