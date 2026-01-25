"""Marquee Lighted Sign Project - colorwheel"""

from .performancemode import PerformanceMode


class ColorWheel(PerformanceMode):
    """"""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.rotation = 1
    
    def execute(self):
        """"""
        values = (
            (100, 0, 0),
            (100, 50, 0),
            (100, 100, 0),
            (50, 80, 0),
            (0, 100, 0),
            (0, 100, 50),
            (0, 100, 100),
            (0, 60, 100),
            (0, 0, 100),
            (50, 0, 100),
            (100, 0, 100),
            (100, 0, 50),
        )
        for i, (r, g, b) in enumerate(values):
            self.lights.set_channels(
                brightness=int(100 / 12 * ((i + self.rotation + 1) % 12)),
                color=self.lights.colors.rgb(
                    int(r / 100 * 255),
                    int(g / 100 * 255),
                    int(b / 100 * 255),
                ),
                transition=1.0,
                channel_indexes={(i + self.rotation) % 12},
            )
        self.rotation = (self.rotation + 1) % 12
        self.schedule(
            self.execute, due=1.5,
        )

