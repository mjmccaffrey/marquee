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
                brightness=40,
                color=self.lights.colors.rgb(
                    int(r / 100 * 255),
                    int(g / 100 * 255),
                    int(b / 100 * 255),
                ),
                channel_indexes={i},
            )

        # Click intro
        for i in range(4):
            self.schedule(
                due=i / self.bps,
                action=partial(self.clicker.click),
            )
        delay = 4.0 / self.bps

        # Schedule to turn each on
        delays = (0.0,) + tuple(
            (n / self.bps) 
            for n in self.notes[:-1]
        )
        print(delays)
        for i, d in enumerate(delays):
            delay += d
            self.schedule(
                due=delay,
                action=partial(self.turn_on, index=i),
            )

        # Schedule repeat
        self.schedule(
            due=delay + 1 / self.bps,
            action=self.execute,
        )

        # Schedule full brightness
        self.schedule(
            due=delay,
            action=partial(
                self.lights.set_channels,
                brightness=100,
                transition=3.0,
            )
        )

    def turn_on(self, index: int):
        """"""
        self.lights.set_channels(
            on=True,
            transition=0.0,
            channel_indexes={index},
        )

