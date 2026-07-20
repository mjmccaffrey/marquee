"""Marquee Lighted Sign Project - color"""

from abc import ABC
from collections.abc import Iterator
import json
import logging
from pathlib import Path
import random
from typing import TypedDict
from typing_extensions import override

from devices import rgbxy

log = logging.getLogger('marquee.' + __name__)


def balanced_distribution(values: tuple, desired_length: int) -> tuple:
    """Return tuple of randomly distributed values in which 
       each value is present no more than one more time 
       than any other value."""
    full, remainder = divmod(desired_length, len(values))
    result = list(values) * full
    result.extend(random.sample(values, remainder))
    random.shuffle(result)
    return tuple(result)


class Color(ABC):
    """Base for colors."""
    x: float
    y: float


class XY(Color):
    """XY color."""

    def __init__(self, x: float, y: float) -> None:
        """Initialize."""
        self.x, self.y = x, y


class XYB(Color):
    """XYB color (not really)."""

    def __init__(self, x: float, y: float, b: float) -> None:
        """Initialize."""
        self.x, self.y, self.b = x, y, b


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

    @override
    def __repr__(self):
        """"""
        return f"RGB({self.red}, {self.green}, {self.blue})"


class Colors:
    """Contains named colors. Instantiate for gamut-adjusted colors."""
    RED = RGB(255, 0, 0)
    ORANGE = RGB(255, 128, 0)
    YELLOW = RGB(255, 255, 0)
    LIME = RGB(128, 200, 0)
    GREEN = RGB(0, 255, 0)
    SPRING = RGB(0, 255, 128)
    CYAN = RGB(0, 255, 255)
    TEAL = RGB(0, 155, 255)
    BLUE = RGB(0, 0, 255)
    VIOLET = RGB(128, 0, 255)
    MAGENTA = RGB(255, 0, 255)
    ROSE = RGB(255, 0, 128)
    WHITE = RGB(255, 255, 255)
    WHEEL = (
        RED, ORANGE, YELLOW, LIME, GREEN, SPRING,
        CYAN, TEAL, BLUE, VIOLET, MAGENTA, ROSE,
    )
    INDIGO = RGB(75, 0, 130)
    DEEP_GOLD = XY(0.495, 0.468)
    BRIGHT_GOLD = XY(0.481, 0.449)

    def __init__(self, gamut: rgbxy.Gamut) -> None:
        """Create an instance for gamut-adjusted constants.
           Class constants are not adjusted to a gamut."""
        self.gamut = gamut
        self.converter = rgbxy.Converter(gamut)
        self.RED = RGB(255, 0, 0, self.gamut)
        self.ORANGE = RGB(255, 128, 0, self.gamut)
        self.YELLOW = RGB(255, 255, 0, self.gamut)
        self.LIME = RGB(128, 255, 0, self.gamut)
        self.GREEN = RGB(0, 255, 0, self.gamut)
        self.SPRING = RGB(0, 255, 128, self.gamut)
        self.CYAN = RGB(0, 255, 255, self.gamut)
        self.TEAL = RGB(0, 128, 255, self.gamut)
        self.BLUE = RGB(0, 0, 255, self.gamut)
        self.VIOLET = RGB(128, 0, 255, self.gamut)
        self.MAGENTA = RGB(255, 0, 255, self.gamut)
        self.ROSE = RGB(255, 0, 128, self.gamut)
        self.WHITE = RGB(255, 255, 255, self.gamut)

    def random(self) -> XY:
        """Return random color within gamut."""
        return XY(*self.converter.get_random_xy_color())

    def rgb(self, r: int, g: int, b: int) -> RGB:
        """Return RGB instance adjusted for gamut."""
        return RGB(r, g, b, self.gamut)

    def wheel_colors(self, divisions: int) -> Iterator[Color]:
        """Yield wheel colors, along with divisions in-between colors."""
        colors = iter(self.WHEEL)
        previous = next(colors)
        yield previous
        for color in colors:
            for i in range(divisions):
                red = previous.red + (
                    (color.red - previous.red) // 
                    (divisions + 1) * (i + 1)
                )
                green = previous.green + (
                    (color.green - previous.green) // 
                    (divisions + 1) * (i + 1)
                )
                blue = previous.blue + (
                    (color.blue - previous.blue) // 
                    (divisions + 1) * (i + 1)
                )
                yield self.rgb(red, green, blue)
            previous = color


class ColorSet:
    """Color theme."""

    class SetChannelsKwargs(TypedDict):
        color: tuple[Color, ...]
        brightness: tuple[int, ...]

    def __init__(
        self, 
        name: str, 
        group: str, 
        colors: tuple[RGB, ...] | tuple[XYB, ...],
    ) -> None:
        """"""
        self.name, self.group, self.colors = name, group, colors

    def set_channels_kwargs(self, light_count: int) -> SetChannelsKwargs:
        """"""
        colors = balanced_distribution(self.colors, light_count)
        if isinstance(colors[0], RGB):
            return self.SetChannelsKwargs(
                color=colors,
                brightness=tuple(100 for c in colors),  # !!!
            )
        elif isinstance(colors[0], XYB):
            return self.SetChannelsKwargs(
                color=tuple(XY(c.x, c.y) for c in colors),
                brightness=tuple(round(c.b) for c in colors),  # !!!
            )
        else:
            raise RuntimeError


class ColorSets:
    """All color themes, available by name and group name."""
    BySetName = dict[str, ColorSet]
    ByGroupName = dict[str, list[ColorSet]]
    by_set_name: BySetName
    by_group_name: ByGroupName

    def __init__(self, source: str) -> None:
        """"""
        unordered = (
            self._basic_colors() |
            self._load_color_sets(Path(source))
        )
        self.by_group_name = self._create_color_groups(unordered)
        self.by_set_name = {
            s.name: s
            for _, sets in self.by_group_name.items()
            for s in sets
        }
    
    def each_set_name(self) -> Iterator[tuple[str, str]]:
        """"""
        for gn, sets in self.by_group_name.items():
            for s in sets:
                yield (gn, s.name)

    def lookup(self, name: str) -> ColorSet:
        """Return color set with name."""
        if name not in self.by_set_name:
            raise ValueError(f"Color set {name} not defined.")
        return self.by_set_name[name]

    @staticmethod
    def _basic_colors() -> BySetName:
        """Construct color set for each basic color."""
        return {
            key.lower(): ColorSet(key.lower(), 'basic', (value,))
            for key, value in vars(Colors).items()
            if isinstance(value, RGB)
        } | {
            'wheel': ColorSet('wheel', 'basic', Colors.WHEEL)
        }

    @staticmethod
    def _load_color_sets(source: Path) -> BySetName:
        """Load color sets from file."""
        with open(source) as f:
            data = json.load(f)
        return {
            name: ColorSet(
                name, 
                group, 
                tuple(XYB(*c) for c in set(tuple(l) for l in colors)),
            )
            for name, group, colors in data
        }
            

    @staticmethod
    def _create_color_groups(sets: BySetName) -> ByGroupName:
        """Return color sets organized by group name."""
        group_names = sorted(set(s.group for s in sets.values()))
        set_names = sorted(s.name for s in sets.values())
        return {
            group: [
                sets[n] for n in set_names 
                if sets[n].group == group
            ]
            for group in group_names
        }

