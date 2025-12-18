"""Marquee Lighted Sign Project - color"""

from abc import ABC

import rgbxy


class Color(ABC):
    """Base for colors."""
    x: float
    y: float


class XY(Color):
    """XY color."""

    def __init__(self, x: float, y: float) -> None:
        """Initialize."""
        self.x, self.y = x, y


class RGB(Color):
    """RGB color."""
    
    incomplete_instances: list['RGB'] = []

    @staticmethod
    def _adjust_incomplete_color(rgb: 'RGB', gamut: rgbxy.Gamut) -> None:
        """Calculate closest XY value for color gamut."""
        converter = rgbxy.Converter(gamut)
        rgb.x, rgb.y = converter.rgb_to_xy(rgb.red, rgb.green, rgb.blue)

    @classmethod
    def adjust_incomplete_colors(cls, gamut: rgbxy.Gamut) -> None:
        """Calculate closest XY value for color gamut."""
        converter = rgbxy.Converter(gamut)
        for rgb in cls.incomplete_instances:
            rgb.x, rgb.y = converter.rgb_to_xy(rgb.red, rgb.green, rgb.blue)
        cls.incomplete_instances = []

    def __init__(
        self, 
        red: int, 
        green: int, 
        blue: int,
        gamut: rgbxy.Gamut | None = None,
    ) -> None:
        """Initialize."""
        self.red, self.green, self.blue = red, green, blue
        if gamut is None:
            self.incomplete_instances.append(self)
        else:
            self._adjust_incomplete_color(rgb=self, gamut=gamut)


class Colors:
    """Create an instance for gamut-adjusted constants.
       Class constants are not adjusted to a gamut."""
    BLUE = RGB(0, 0, 255)
    CYAN = RGB(0, 255, 255)
    GREEN = RGB(0, 255, 0)
    MAGENTA = RGB(255, 0, 255)
    RED = RGB(255, 0, 0)
    WHITE = RGB(255, 255, 255)
    YELLOW = RGB(255, 255, 0)

    def __init__(self, gamut: rgbxy.Gamut) -> None:
        """Initialize."""
        self.BLUE = RGB(0, 0, 255, gamut)
        self.CYAN = RGB(0, 255, 255, gamut)
        self.GREEN = RGB(0, 255, 0, gamut)
        self.MAGENTA = RGB(255, 0, 255, gamut)
        self.RED = RGB(255, 0, 0, gamut)
        self.WHITE = RGB(255, 255, 255, gamut)
        self.YELLOW = RGB(255, 255, 0, gamut)


class Random:
    """Generate random values within color gamut."""
    
    def __init__(self, gamut: rgbxy.Gamut) -> None:
        """Initialize."""
        self.converter = rgbxy.Converter(gamut)

    def random(self):
        """Return random color within gamut."""
        return XY(*self.converter.get_random_xy_color())

