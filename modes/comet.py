"""Marquee Lighted Sign Project - comet"""

from collections.abc import Iterator
from dataclasses import dataclass
from itertools import cycle, repeat

from color import Color
from .performancemode import PerformanceMode
            

@dataclass(kw_only=True)
class Comet(PerformanceMode):
    """Rotating comet with tail."""
    length: int
    delay: float
    color: Color | None = None
    wheel_divisions: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        assert (self.color is None) ^ (self.wheel_divisions is None)
        self.head = -1
        if self.color is not None:
            self.colors = repeat(self.color)
        else:
            self.colors = self.wheel_colors()
        self.schedule(due=self.delay, repeat=True)

    def wheel_colors(self) -> Iterator[Color]:
        """"""
        assert self.wheel_divisions is not None
        colors = cycle(self.lights.colors.WHEEL)
        previous = next(colors)
        print(previous)
        yield previous
        for color in colors:
            for i in range(self.wheel_divisions):
                red = previous.red + (
                    (color.red - previous.red) // 
                    (self.wheel_divisions + 1) * (i + 1)
                )
                green = previous.green + (
                    (color.green - previous.green) // 
                    (self.wheel_divisions + 1) * (i + 1)
                )
                blue = previous.blue + (
                    (color.blue - previous.blue) // 
                    (self.wheel_divisions + 1) * (i + 1)
                )
                print(self.lights.colors.rgb(red, green, blue))
                yield self.lights.colors.rgb(red, green, blue)
            print(color)
            yield color
            previous = color

    def execute(self) -> None:
        """"""
        count = self.lights.count
        self.head = (self.head + 1) % count
        if self.head == 0:
            self.color = next(self.colors)
        for i in range(self.length):
            self.lights.set_channels(
                brightness=100 - (i + 2) * 25,
                transition=self.delay,
                color=self.color,
                on=True,
                channel_indexes={(self.head - i) % count},
            )
        # self.lights.set_channels(
        #     on=False,
        #     transition=self.delay,
        #     channel_indexes={(self.head - self.length) % count},
        # )

