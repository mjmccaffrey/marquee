"""Marquee Lighted Sign Project - twelve"""

from dataclasses import dataclass
from functools import partial

from .performancemode import PerformanceMode

@dataclass(kw_only=True)
class Twelve(PerformanceMode):
    """"""
    colors = (
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
    notes = (
        0.5, 0.5, 0.5, 1, 1, 0.5,
        1, 0.5, 1, 1, 1.5, 1,
    )
    bpm = 160.0
    bps = bpm / 60

    def execute(self):
        """"""
        # Turn all off
        self.lights.set_channels(on=False)

        # Set each color
        for i, (r, g, b) in enumerate(self.colors):
            self.lights.set_channels(
                brightness=70,
                color=self.lights.colors.rgb(
                    int(r / 100 * 255),
                    int(g / 100 * 255),
                    int(b / 100 * 255),
                ),
                channel_indexes={i},
            )

        # Schedule to turn each on
        delays = (0.0,) + tuple(n / self.bps for n in self.notes[:-1])
        print(delays)
        delay = 0.0
        for i, d in enumerate(delays):
            delay += d
            self.schedule(
                due=delay,
                action=partial(self.turn_on, index=i),
            )

    def turn_on(self, index: int):
        """"""
        self.lights.set_channels(
            on=True,
            channel_indexes={index},
        )

