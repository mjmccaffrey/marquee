"""Marquee Lighted Sign Project - color"""

class Color:
    """Base for colors."""
    x: float
    y: float
    brightness: float

class XY(Color):
    """XY color."""

    def __init__(self, x: float, y: float, brightness: float) -> None:
        """Initialize."""
        self.x = x
        self.y = y
        self.brightness = brightness


class RGB(Color):
    """RGB color."""
    red: int
    green: int
    blue: int

    def __init__(self, red: int, green: int, blue: int) -> None:
        """Initialize."""
        self.red = red
        self.green = green
        self.blue = blue
        self.x, self.y, self.brightness = self.convert_rgb_to_xy()

    def convert_rgb_to_xy(self) -> tuple[float, float, float]:
        """Convert RGB to XY."""
        # https://developers.meethue.com/develop/application-design-guidance/
        # color-conversion-formulas-rgb-to-xy-and-back/

        red, green, blue = self.red, self.green, self.blue
        red = (
            pow((red + 0.055) / 1.055, 2.4) 
            if red > 0.04045 else 
            red / 12.92
        )
        green = (
            pow((green + 0.055) / 1.055, 2.4)
            if green > 0.04045 else
            green / 12.92
        )
        blue = (
            pow((blue + 0.055) / 1.055, 2.4)
            if blue > 0.04045 else
            blue / 12.92
        )
        _x = red * 0.4124 + green * 0.3576 + blue * 0.1805
        _y = red * 0.2126 + green * 0.7152 + blue * 0.0722
        _z = red * 0.0193 + green * 0.1192 + blue * 0.9505
        x = _x / (_x + _y + _z)
        y = _y / (_x + _y + _z)
        brightness = _y
        return x, y, brightness


RED = RGB(255, 0, 0)
GREEN = RGB(0, 255, 0)
BLUE = RGB(0, 0, 255)

