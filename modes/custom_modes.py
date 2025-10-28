"""Marquee Lighted Sign Project - custom_modes"""

from collections.abc import Iterator
from dataclasses import dataclass
import itertools
import random
import time

from dimmers import TRANSITION_MINIMUM
from lightset_misc import (
    ALL_HIGH, ALL_LOW, ALL_ON, 
    LIGHT_COUNT, LIGHTS_BY_ROW,
)
from music.music_notation import Bell
from .playmode import PlayMode
from .playmusicmode import PlayMusicMode
from sequences import lights_in_groups, opposite, rotate
from specialparams import DimmerParams


@dataclass(kw_only=True)
class BellTest(PlayMusicMode):
    """Test all bells."""

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices()

    def execute(self) -> None:
        """Perform bell test."""
        start = time.time()
        for pitch in range(self.bells.pitch_levels):
            due = start + 0.5 * pitch
            self.schedule(
                action = lambda: self.bells.play({pitch}),
                due = due,
            )
            self.schedule(
                action = lambda: self.bells.release({pitch}),
                due = due + self.bells.release_time,
            )
            

@dataclass(kw_only=True)
class RotateReversible(PlayMode):
    """Rotate a pattern, reversing direction in response to a button press."""
    delay: float
    pattern: str

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(dimmers=True)

    def execute(self) -> None:
        """Display pattern, set next pattern, and exit.
           Called repeatedly until the mode is changed."""
        self.schedule(
            lambda: self.lights.set_relays(self.pattern),
            time.time() + self.delay
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
    special: DimmerParams | None = None

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(
            dimmers=(self.special is None),
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
        start = time.time()
        for index, (pattern, pace) in enumerate(itertools.cycle(values)):
            self.schedule(
                lambda: self.lights.set_relays(
                    pattern, 
                    special=self.special,
                ),
                start + index * pace
            )


@dataclass(kw_only=True)
class RandomFade(PlayMode):
    """Change brightness of random bulb to a random level,
       with either a random or specified transition time."""
    transition: float = -1

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(relays=True)

    def _new_transition(self) -> float:
        if self.transition == -1:
            return random.uniform(TRANSITION_MINIMUM, 5.0 * self.player.speed_factor)
        else:
            return self.transition

    def _new_brightness(self, old) -> int:
        new = old
        while abs(new - old) < 20:
            new = random.randrange(101)
        return new
    
    def execute(self) -> None:
        """Perform RandomFade indefinitely."""
        for channel in self.lights.dimmer_channels:
            channel.next_update = 0
        due = time.time()
        while True:
            for channel in self.lights.dimmer_channels:
                now = time.time()
                if channel.next_update < now:
                    transition = self._new_transition()
                    self.schedule(
                        lambda: channel.set(
                            transition = transition,
                            brightness = self._new_brightness(channel.brightness),
                        ),
                        due,
                    )
                    due += 0.1
                    channel.next_update = now + transition


@dataclass(kw_only=True)
class EvenOddFade(PlayMode):
    """Fade every-other bulb."""
    delay: float

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(relays=True)

    def execute(self) -> None:
        """Perform EvenOddFade indefinitely."""
        self.lights.set_dimmers(ALL_LOW) 
        delay = 0.5
        odd_on = ''.join('1' if i % 2 else '0' for i in range(LIGHT_COUNT))
        even_on = opposite(odd_on)
        due = time.time()
        for pattern in itertools.cycle((even_on, odd_on)):
            start = time.time()
            self.schedule(
                lambda: self.lights.set_relays(
                    pattern, 
                    special=DimmerParams(
                        concurrent=True,
                        brightness_on = 90,
                        brightness_off = 10,
                        transition_on=delay,
                        transition_off=delay,
                    )
                ),
                due,
            )
            due += delay


@dataclass(kw_only=True)
class RapidFade(PlayMode):
    """Test of achieving a very fast fade by giving the channel
       2 different set commands in rapid succession."""

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(relays=True)
 
    def execute(self) -> None:
        """Perform RapidFade indefinitely."""
        self.lights.set_relays(ALL_ON)
        due = time.time()
        while True:
            self.lights.set_dimmers(ALL_HIGH, force_update=True)
            previous = None
            for channel in self.lights.dimmer_channels:
                self.schedule(
                    lambda: channel.set(brightness=0, transition=TRANSITION_MINIMUM),
                    due,
                )
                if previous:
                    self.schedule(
                        lambda: previous.set(  # type: ignore
                            brightness=40, 
                            transition=TRANSITION_MINIMUM,
                        ),
                        due,
                    ),
                previous = channel
                due += 0.25
            assert previous is not None
            self.schedule(
                lambda: previous.set(  # type: ignore
                    brightness=40, 
                    transition=TRANSITION_MINIMUM,
                ),
                due,
            )


@dataclass(kw_only=True)
class SilentFadeBuild(PlayMode):
    """Alternately build rows / columns from top / bottom / left / right."""

    def __post_init__(self) -> None:
        """Initialize."""
        self.preset_devices(relays=True)
 
    def execute(self) -> None:
        """Perform SilentFadeBuild indefinitely."""
        self.lights.set_relays(ALL_ON)
        due = time.time()
        while True:
            for rows in (False, True):
                for from_top_left, brightness in (
                    (True, 100), (False, 0),
                    (False, 100), (True, 0),
                ):
                    for lights in lights_in_groups(rows, from_top_left):
                        self.schedule(
                            lambda: self.lights.set_dimmer_subset(
                                lights, brightness, 1.0
                            ),
                            due,
                        )
                        due += 0.5
                    due += 1.0
                due += 1.0


@dataclass(kw_only=True)
class FillBulbs(PlayMode):
    """Gag to fill sign with electricity."""

    def __post_init__(self) -> None:
        """Initialize."""
        self.lights.set_dimmers(ALL_LOW)
        self.player.wait(0.5)
        self.preset_devices(relays=True)
 
    def execute(self) -> None:
        """Bulb juice flows down from the top center."""
        for lights in LIGHTS_BY_ROW:
            self.lights.set_dimmer_subset(lights, 30, 2.0)
            self.player.wait(1.0)
        self.player.wait(1.0)
        for lights in reversed(LIGHTS_BY_ROW):
            self.lights.set_dimmer_subset(lights, 100, 1.5)
            self.player.wait(1.5)
            self.bells.play({7})
        self.player.wait(None)


@dataclass(kw_only=True)
class HourlyChime(PlayMode):
    """Chime and light the hour."""
    def __post_init__(self) -> None:
        """Initialize."""
        self.lights.set_dimmers(ALL_HIGH)
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

