"""Marquee Lighted Sign Project - mode_defs"""

from collections.abc import Iterator
from dataclasses import dataclass
import itertools
import random
from sequences import lights_in_groups, opposite, rotate
import time

from configuration import ALL_HIGH, ALL_LOW, ALL_ON, LIGHT_COUNT
from dimmers import TRANSITION_MINIMUM
from modes import PlayMusicMode, PlayMode
from definitions import DimmerParams

@dataclass
class BellTest(PlayMusicMode):
    """Test all bells."""

    def __post_init__(self):
        """Initialize."""
        self.preset_devices()

    def execute(self):
        """Perform bell test."""
        for pitch in range(8):
            self.player.bells.play({pitch})
            self.player.wait(0.5)
        
@dataclass
class RotateReversible(PlayMode):
    """Rotate a pattern, reversing direction in response to a button press."""
    pace: float
    pattern: str

    def __post_init__(self):
        """Initialize."""
        self.preset_devices(dimmers=True)

    def execute(self):
        """Display a single pattern.
           Called repeatedly until the mode is changed."""
        self.player.lights.set_relays(self.pattern)
        self.player.wait(self.pace)
        self.pattern = (
            self.pattern[self.direction:] + self.pattern[:self.direction]
        )

@dataclass
class RotateRewind(PlayMode):
    """Rotate a pattern at a decreasing speed, and then rewind."""
    pattern: str = "1" + "0" * (LIGHT_COUNT - 1)
    clockwise: bool = True
    start_pace: float = 0.1
    special: DimmerParams | None = None

    def __post_init__(self):
        """Initialize."""
        self.preset_devices(
            dimmers=(self.special is None),
            relays=(self.special is not None),
        )
        self.paces = [v for v in self._spin_pace(self.start_pace)]

    @staticmethod
    def _spin_pace(start: float) -> Iterator[float]:
        """Return a series of spin pace values."""
        pace = start
        while pace < 2.0:
            yield pace
            pace *= 1.2

    def execute(self):
        """"""
        values = [
            (pattern, pace)
            for pattern, pace  in zip(
                rotate(self.pattern, self.clockwise),
                self._spin_pace(self.start_pace),
            )
        ]
        values.extend(reversed(values))
        for pattern, pace in itertools.cycle(values):
            self.player.lights.set_relays(
                pattern, 
                special=self.special,
            )
            self.player.wait(pace)

@dataclass
class RandomFade(PlayMode):
    """Change brightness of random bulb to a random level,
       with either a random or specified transition time."""
    transition: float = -1

    def __post_init__(self):
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
    
    def execute(self):
        """"""
        for channel in self.player.lights.dimmer_channels:
            channel.next_update = 0
        while True:
            for channel in self.player.lights.dimmer_channels:
                if channel.next_update < (now := time.time()):
                    channel.set(
                        transition = (tran := self._new_transition()),
                        brightness = self._new_brightness(channel.brightness)
                    )
                    channel.next_update = now + tran
            self.player.wait(0.1)

@dataclass
class EvenOddFade(PlayMode):
    """Fade every-other bulb."""
    pace: float

    def __post_init__(self):
        """Initialize."""
        self.preset_devices(relays=True)

    def execute(self):
        """"""
        self.player.lights.set_dimmers(ALL_LOW) 
        delay = 0.5
        odd_on = ''.join('1' if i % 2 else '0' for i in range(LIGHT_COUNT))
        even_on = opposite(odd_on)
        for pattern in itertools.cycle((even_on, odd_on)):
            start = time.time()
            self.player.lights.set_relays(
                pattern, 
                special=DimmerParams(
                    concurrent=True,
                    brightness_on = 90,
                    brightness_off = 10,
                    transition_on=delay,
                    transition_off=delay,
                )
            )
            self.player.wait(delay, time.time() - start)

@dataclass
class RapidFade(PlayMode):
    """"""

    def __post_init__(self):
        """Initialize."""
        self.preset_devices(relays=True)
 
    def execute(self):
        """"""
        self.player.lights.set_relays(ALL_ON)
        while True:
            self.player.lights.set_dimmers(ALL_HIGH, force_update=True)
            previous = None
            for channel in self.player.lights.dimmer_channels:
                start = time.time()
                channel.set(brightness=0, transition=TRANSITION_MINIMUM)
                if previous:
                    previous.set(brightness=40, transition=TRANSITION_MINIMUM)
                previous = channel
                self.player.wait(0.25, elapsed = time.time() - start)
            assert previous is not None
            previous.set(brightness=40, transition=TRANSITION_MINIMUM)
            # self.player.wait(10)

@dataclass
class BuildBrightness(PlayMode):
    """Brightness change rate test."""
    equal_trans: bool

    def __post_init__(self):
        """Initialize."""
        self.preset_devices(relays=True)

    def execute(self):
        self.player.lights.set_dimmers(ALL_LOW)
        brightnesss = [(i + 1) * 10 for i in range(LIGHT_COUNT)]
        transitions = (
            [0.5] * LIGHT_COUNT
                if self.equal_trans else
            [(i + 1) * 2 for i in range(LIGHT_COUNT)]
        )
        for dimmer, brightness, transition in zip(self.player.lights.dimmer_channels, brightnesss, transitions):
            dimmer.set(brightness=brightness, transition=transition)
        self.player.wait(4)

@dataclass
class SilentFadeBuild(PlayMode):
    """"""

    def __post_init__(self):
        """Initialize."""
        self.preset_devices(relays=True)
 
    def execute(self):
        """"""
        self.player.lights.set_relays(ALL_ON)
        while True:
            for rows in (False, True):
                for from_top_left, brightness in (
                    (True, 100), (False, 0),
                    (False, 100), (True, 0),
                ):
                    for lights in lights_in_groups(rows, from_top_left):
                        self.player.lights.set_dimmer_subset(
                            lights, brightness, 1.0
                        )
                        self.player.wait(0.5)
                    self.player.wait(1.0)
                self.player.wait(1.0)
