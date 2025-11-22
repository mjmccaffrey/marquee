"""Marquee Lighted Sign Project - custom_modes"""

from collections.abc import Iterator
from dataclasses import dataclass
from functools import partial
import itertools
import random
import time

from lightset_misc import (
    ALL_HIGH, ALL_LOW, ALL_ON, LIGHT_COUNT,
)
from music.music_notation import Bell
from .playmode import PlayMode
from .playmusicmode import PlayMusicMode
from sequences import lights_in_groups, opposite, rotate
from specialparams import ChannelParams


@dataclass(kw_only=True)
class BellTest(PlayMusicMode):
    """Test all bells."""

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices()

    def execute(self) -> None:
        """Perform bell test."""
        for pitch in range(self.bells.pitch_levels):
            due = 0.5 * pitch
            self.schedule(
                action = partial(self.bells.play, {pitch}),
                due = due,
                name = f"BellTest play {pitch}",
            )
            self.schedule(
                action = partial(self.bells.release, {pitch}),
                due = due + self.bells.release_time,
                name = f"BellTest release {pitch}",
            )
            

@dataclass(kw_only=True)
class RotateReversible(PlayMode):
    """Rotate a pattern, reversing direction in response to a button press."""
    delay: float
    pattern: str

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(channels=True)

    def execute(self) -> None:
        """Display pattern, set next pattern, and exit.
           Called repeatedly until the mode is changed."""
        self.schedule(
            partial(self.lights.set_relays, self.pattern),
            self.delay,
            name=f"RotateReversible set_relays {self.pattern}",

        )
        self.pattern = (
            self.pattern[self.direction:] + self.pattern[:self.direction]
        )


@dataclass(kw_only=True)
class RotateRewind(PlayMode):
    """Rotate a pattern at a decreasing speed, and then rewind."""
    pattern: str = "1" + "0" * (LIGHT_COUNT - 1)
    clockwise: bool = True
    start_pace: float = 0.1
    special: ChannelParams | None = None

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(
            channels=(self.special is None),
            relays=(self.special is not None),
        )

    @staticmethod
    def _spin_pace(start: float) -> Iterator[float]:
        """Return a series of spin pace values."""
        pace = start
        while pace < 1.75:
            yield pace
            pace *= 1.1

    def execute(self) -> None:
        """Perform RotateRewind indefinitely."""
        values = [
            (pattern, pace)
            for pattern, pace  in zip(
                itertools.cycle(rotate(self.pattern, self.clockwise)),
                self._spin_pace(self.start_pace),
            )
        ]
        values.extend(reversed(values[1:-1]))
        for index, (pattern, pace) in enumerate(itertools.cycle(values)):
            self.schedule(
                partial(self.lights.set_relays, pattern, special=self.special),
                index * pace,
                name=f"RotateRewind set_relays {pattern}",
            )


@dataclass(kw_only=True)
class RandomFade(PlayMode):
    """Change brightness of random bulb to a random level,
       with either a random or specified trans time."""
    trans: float = -1

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(relays=True)

    def _new_trans(self) -> float:
        if self.trans == -1:
            return random.uniform(
                self.player.lights.trans_min, 
                5.0 * self.player.speed_factor
            )
        else:
            return self.trans

    def _new_brightness(self, old) -> int:
        new = old
        while abs(new - old) < 20:
            new = random.randrange(101)
        return new
    
    def execute(self) -> None:
        """Perform RandomFade indefinitely."""
        next_update = {
            light: 0.0
            for light in range(self.lights.light_count)
        }
        due = 0.0
        while True:
            for light in range(self.lights.light_count):
                now = time.time()
                if next_update[light] < now:
                    brightnesses = self.lights.brightnesses()
                    trans = self._new_trans()
                    self.schedule(
                        partial(
                            self.lights.set_channels,
                            transition=trans,
                            brightness=self._new_brightness(brightnesses[light]),
                            channel_indexes = [light],
                        ),
                        due,
                        name=f"RandomFade set channel {light}",
                    )
                    due += 0.1


@dataclass(kw_only=True)
class EvenOddFade(PlayMode):
    """Fade every-other bulb."""
    delay: float

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(relays=True)

    def execute(self) -> None:
        """Perform EvenOddFade indefinitely."""
        self.lights.set_channels(brightness=0) 
        delay = 0.5
        odd_on = ''.join('1' if i % 2 else '0' for i in range(LIGHT_COUNT))
        even_on = opposite(odd_on)
        due = 0.0
        for pattern in itertools.cycle((even_on, odd_on)):
            self.schedule(
                partial(
                    self.lights.set_relays,
                    pattern, 
                    special=ChannelParams(
                        concurrent=True,
                        brightness_on = 90,
                        brightness_off = 10,
                        trans_on=delay,
                        trans_off=delay,
                    )
                ),
                due,
            )
            due += delay


@dataclass(kw_only=True)
class SilentFadeBuild(PlayMode):
    """Alternately build rows / columns from top / bottom / left / right."""

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(relays=True)
 
    def execute(self) -> None:
        """Perform SilentFadeBuild indefinitely."""
        self.lights.set_relays(ALL_ON)
        due = 0.0
        while True:
            for rows in (False, True):
                for from_top_left, brightness in (
                    (True, 100), (False, 0),
                    (False, 100), (True, 0),
                ):
                    for lights in lights_in_groups(rows, from_top_left):
                        self.schedule(
                            partial(
                                self.lights.set_channels,
                                brightness=brightness,
                                transition=1.0,
                                channel_indexes=lights,
                            ),
                            due,
                        )
                        due += 0.5
                    due += 1.0
                due += 1.0


@dataclass(kw_only=True)
class HourlyChime(PlayMode):
    """Chime and light the hour."""
    def __post_init__(self) -> None:
        """Initialize."""
        self.lights.set_channels(brightness=100)
        self.player.wait(0.5)
        self.preset_devices(relays=True)
 
    def execute(self) -> None:
        """Chime and light the hour."""
        self.player.wait(1.0)
        for hour in range(time.gmtime().tm_hour):
            self.lights.set_relays(
                str('1' if i <= hour else '0' for i in range(LIGHT_COUNT))
            )
            self.bells.play({Bell.e})
            self.player.wait(1.5)
        self.player.wait(5.0)

