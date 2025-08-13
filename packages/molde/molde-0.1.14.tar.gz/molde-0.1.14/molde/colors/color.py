import typing
from qtpy.QtGui import QColor
import numpy as np
from dataclasses import dataclass


@dataclass(frozen=True, init=False)
class Color:
    r: int
    g: int
    b: int
    a: int

    @typing.overload
    def __new__(self, r: int, g: int, b: int, a: int = 255):
        """
        Initialize Colors with RGB or RGBA integer values ranging from 0 to 255.
        """

    @typing.overload
    def __new__(self, r: float, g: float, b: float, a: float = 1.0):
        """
        Initialize Colors with RGB or RGBA floating values ranging from 0.0 to 1.0.
        """

    @typing.overload
    def __new__(self, hexa: str):
        """
        Initialize colors from hex values.
        The valid formats incluce RGB (#FF0000 for example)
        and RGBA (#FF0000FF for example)
        """

    @typing.overload
    def __new__(self, qcolor: QColor):
        """
        Initialize the color class with an instance of QColor
        """

    @typing.overload
    def __new__(self, color: "Color"):
        """
        Initialize the color class with an instance it's own class
        """

    @typing.overload
    def __new__(self):
        """
        Initialize an empty black color
        """

    def __new__(cls, *args):
        """
        Calls the appropriate constructor for the class according to the
        number of arguments and their types.
        """

        all_int = all([isinstance(i, int) for i in args])
        all_float = all([isinstance(i, float) for i in args])

        if len(args) == 0:
            return cls.from_rgba(0, 0, 0, 255)

        elif len(args) == 1 and isinstance(args[0], str):
            return cls.from_hex(*args)

        elif len(args) == 1 and isinstance(args[0], QColor):
            return cls.from_qcolor(*args)

        elif len(args) == 1 and isinstance(args[0], Color):
            return cls.from_color(*args)

        elif len(args) in [3, 4] and all_int:
            return cls.from_rgba(*args)

        elif len(args) in [3, 4] and all_float:
            return cls.from_rgba_f(*args)

        else:
            raise ValueError("Invalid input values")

    @classmethod
    def from_rgba(cls, r: int, g: int, b: int, a: int = 255) -> "Color":
        """
        This is the default constructor for the class.
        All other constructors call this one.

        Since "Color" should be imutable, we use "object.__setattr__" to bypass
        the imutability just in the constructor.
        """

        obj = super().__new__(cls)
        object.__setattr__(obj, "r", round(np.clip(r, 0, 255)))
        object.__setattr__(obj, "g", round(np.clip(g, 0, 255)))
        object.__setattr__(obj, "b", round(np.clip(b, 0, 255)))
        object.__setattr__(obj, "a", round(np.clip(a, 0, 255)))
        return obj

    @classmethod
    def from_rgb(self, r: int, g: int, b: int) -> "Color":
        return self.from_rgba(r, g, b)

    @classmethod
    def from_rgb_f(self, r: float, g: float, b: float) -> "Color":
        return self.from_rgba_f(r, g, b)

    @classmethod
    def from_rgba_f(self, r: float, g: float, b: float, a: float = 1) -> "Color":
        return self.from_rgba(
            round(r * 255),
            round(g * 255),
            round(b * 255),
            round(a * 255),
        )

    @classmethod
    def from_hex(self, color: str) -> "Color":
        color = color.lstrip("#")
        if len(color) == 6:
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            return self.from_rgb(r, g, b)
        elif len(color) == 8:
            r, g, b, a = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16)
            return self.from_rgba(r, g, b, a)
        raise ValueError("Invalid hex color format")

    @classmethod
    def from_hsv(self, hue: float, saturation: float, value: float):
        v = value / 100
        s = saturation / 100

        c = v * s
        h = hue / 60
        x = c * (1 - abs(h % 2 - 1))

        if 0 <= h < 1:
            r, g, b = c, x, 0
        elif 1 <= h < 2:
            r, g, b = x, c, 0
        elif 2 <= h < 3:
            r, g, b = 0, c, x
        elif 3 <= h < 4:
            r, g, b = 0, x, c
        elif 4 <= h < 5:
            r, g, b = x, 0, c
        elif 5 <= h < 6:
            r, g, b = c, 0, x
        else:
            r, g, b = 0, 0, 0

        return self.from_rgb_f(
            (r + v - c),
            (g + v - c),
            (b + v - c),
        )

    @classmethod
    def from_qcolor(self, color: QColor) -> "Color":
        return self.from_rgba(color.red(), color.green(), color.blue(), color.alpha())

    @classmethod
    def from_color(self, color: "Color"):
        self.r = color.r
        self.g = color.g
        self.b = color.b
        self.a = color.a
        return self

    def to_rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_rgba(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

    def to_rgb_f(self) -> tuple[float, float, float]:
        return ((self.r / 255), (self.g / 255), (self.b / 255))

    def to_rgba_f(self) -> tuple[float, float, float, float]:
        return ((self.r / 255), (self.g / 255), (self.b / 255), (self.a / 255))

    def to_hex(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_hexa(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.a:02X}"

    def to_hsv(self) -> tuple[int, int, int]:
        r, g, b = self.to_rgb_f()
        min_, mid_, max_ = sorted((r, g, b))
        delta = max_ - min_

        if delta == 0:
            hue = 0
        elif max_ == r:
            hue = (g - b) / delta
        elif max_ == g:
            hue = (b - r) / delta + 2
        elif max_ == b:
            hue = (r - g) / delta + 4
        else:
            hue = 0

        hue = round(60 * hue)
        value = round(100 * max_)
        saturation = round(100 * delta / max_) if (max_ != 0) else 0

        return (
            np.clip(0, 360, hue),
            np.clip(0, 100, saturation),
            np.clip(0, 100, value),
        )

    def to_qt(self) -> QColor:
        return QColor(self.r, self.g, self.b, self.a)

    def copy(self) -> "Color":
        return Color(self.r, self.g, self.b, self.a)

    def apply_factor(self, factor: float | int) -> "Color":
        new_color = self.copy()
        new_color.r = round(np.clip(self.r * factor, 0, 255))
        new_color.g = round(np.clip(self.g * factor, 0, 255))
        new_color.b = round(np.clip(self.b * factor, 0, 255))

        return new_color

    def with_brightness(self, brightness: int) -> "Color":
        """
        Percentage of brightness of the new color.
        """
        h, s, _ = self.to_hsv()
        return self.from_hsv(h, s, brightness)

    def with_saturation(self, saturation: int) -> "Color":
        """
        Percentage of brightness of the new color.
        """
        h, _, v = self.to_hsv()
        return self.from_hsv(h, saturation, v)

    def with_rgba(
        self,
        r: int | None = None,
        g: int | None = None,
        b: int | None = None,
        a: int | None = None,
    ) -> "Color":
        return self.from_rgba(
            r if (r is not None) else self.r,
            g if (g is not None) else self.g,
            b if (b is not None) else self.b,
            a if (a is not None) else self.a,
        )

    def with_rgba_f(
        self,
        r: int | None = None,
        g: int | None = None,
        b: int | None = None,
        a: int | None = None,
    ) -> "Color":
        return self.from_rgba_f(
            r if (r is not None) else self.r,
            g if (g is not None) else self.g,
            b if (b is not None) else self.b,
            a if (a is not None) else self.a,
        )

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

    def __eq__(self, other: "Color"):
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a
