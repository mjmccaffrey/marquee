"""Marquee Lighted Sign Project - colorwheel"""

from color import RGB
from .performancemode import PerformanceMode

class ColorWheel(PerformanceMode):
    """"""

    def execute(self):
        """"""
        values = (
            (100, 0, 0),
            (100, 50, 0),
            (100, 100, 0),
            (50, 100, 0),
            (0, 100, 0),
            (0, 100, 50),
            (0, 100, 100),
            (0, 50, 100),
            (0, 0, 100),
            (50, 0, 100),
            (100, 0, 100),
            (100, 0, 50),
        )
        for i, (r, g, b) in enumerate(values):
            self.lights.set_channels(
                brightness=100,
                color=RGB(
                    int(r / 100 * 255),
                    int(g / 100 * 255),
                    int(b / 100 * 255),
                    self.lights.gamut,
                ),
                transition=0,
                channel_indexes=[i],
            )
