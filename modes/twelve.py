"""Marquee Lighted Sign Project - twelve"""

from collections.abc import Iterator
from dataclasses import dataclass
from functools import partial

from .musicmode import MusicMode
from music import act_part, section, set_mode

@dataclass(kw_only=True)
class Twelve(MusicMode):
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
    bpm = 160

    def execute(self):
        """"""
        # Turn all off
        self.lights.set_channels(on=False)

        # Set each color
        for i, (r, g, b) in enumerate(self.colors):
            self.lights.set_channels(
                brightness=28,
                color=self.lights.colors.rgb(
                    int(r / 100 * 255),
                    int(g / 100 * 255),
                    int(b / 100 * 255),
                ),
                channel_indexes={i},
            )

        # next = self.play_basic()
        next = self.play_music()

        # # Schedule repeat
        # self.schedule(
        #     due=next,
        #     action=self.execute,
        # )

    def play_basic(self) -> float:
        """"""
        notes = (
            0.5, 0.5, 0.5, 1, 1, 0.5,
            1, 0.5, 1, 1, 1.5, 1,
        )
        bps = self.bpm / 60

        # Click intro
        for i in range(4):
            self.schedule(
                due=i / bps,
                action=partial(self.clicker.click),
            )
        delay = 4 / bps

        # Schedule to turn each on
        delays = (0.0,) + tuple(
            (n / bps) 
            for n in notes[:-1]
        )
        for i, d in enumerate(delays):
            delay += d
            self.schedule(
                due=delay,
                action=partial(
                    self.lights.set_channels,
                    on=True,
                    transition=0.0,
                    channel_indexes={i},
                )
            )

        # Return when to repeat
        return delay + 1 / bps

    def play_music(self) -> float:
        """"""
        set_mode(self)
        indices = iter(range(self.lights.count))

        def turn_on():
            """"""
            index = next(indices)
            print("TURN ON", index)
            self.lights.set_channels(
                on=True,
                transition=0.0,
                channel_indexes={index},
            )

        song = section(
            # 𝅝 𝅗𝅥 ♩ ♪ 𝅘𝅥𝅯 𝅘𝅥𝅰 𝄻 𝄼 𝄽 𝄾 𝄿 𝅀
            act_part(
                '  ♪ ♪ ♪ ♩ ♩ ♪  |  ♩ ♪ ♩ ♩ ♪  |  𝄽 ♩ ',
                turn_on,
            )
        )
        song.play(tempo=self.bpm)
        return 0.0
    

