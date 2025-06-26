"""Marquee Lighted Sign Project - mode definitions"""

import itertools
import random
from sequences import *
import time

from definitions import DimmerParams, ALL_HIGH, ALL_LOW, ALL_ON, LIGHT_COUNT
from dimmers import TRANSITION_MINIMUM
from modes import PlayMode
from players import Player

class RotateReversible(PlayMode):
    """Rotate a pattern, reversing direction in response to a button press."""
    def __init__(
        self,
        player: Player, 
        name: str,
        #
        pace: float,
        pattern: str,
    ):
        super().__init__(
            player=player, 
            name=name, 
            preset_dimmers=True, 
        )
        self.pattern = pattern
        self.pace = pace

    def execute(self):
        """Display a single pattern.
           Called repeatedly until the mode is changed."""
        self.player.set_relays(self.pattern)
        self.player.wait(self.pace)
        self.pattern = (
            self.pattern[self.direction:] + self.pattern[:self.direction]
        )

class RandomFade(PlayMode):
    """Change brightness of random bulb to a random level,
       with either a random or specified transition time."""

    def __init__(
        self,
        player: Player, 
        name: str,
        #
        transition: float = -1,
    ):
        super().__init__(
            player=player, 
            name=name, 
            preset_relays=True, 
        )
        self.transition = transition

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
        for channel in self.player.dimmer_channels:
            channel.next_update = 0
        while True:
            for channel in self.player.dimmer_channels:
                if channel.next_update < (now := time.time()):
                    channel.set(
                        transition = (tran := self._new_transition()),
                        brightness = self._new_brightness(channel.brightness)
                    )
                    channel.next_update = now + tran
            self.player.wait(0.1)

class EvenOddFade(PlayMode):
    """Fade every-other bulb."""

    def __init__(
        self,
        player: Player, 
        name: str,
        #
        pace: float,
    ):
        super().__init__(
            player=player, 
            name=name, 
            preset_relays=True, 
        )
        self.pace = pace

    def execute(self):
        """"""
        self.player.lights.set_dimmers(ALL_LOW) 
        delay = 5.0
        odd_on = ''.join('1' if i % 2 else '0' for i in range(LIGHT_COUNT))
        even_on = opposite(odd_on)
        for pattern in itertools.cycle((even_on, odd_on)):
            print(pattern)
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
            self.player.wait(delay)

class RapidFade(PlayMode):
    """"""
    def __init__(
        self,
        player: Player, 
        name: str,
        #
    ):
        super().__init__(
            player=player, 
            name=name, 
            preset_relays=True, 
        )
 
    def execute(self):
        """"""
        self.player.set_relays(ALL_ON)
        while True:
            self.player.set_dimmers(ALL_HIGH, force_update=True)
            previous = None
            for channel in self.player.dimmer_channels:
                start = time.time()
                channel.set(brightness=0, transition=TRANSITION_MINIMUM)
                if previous:
                    previous.set(brightness=40, transition=TRANSITION_MINIMUM)
                previous = channel
                self.player.wait(0.25, elapsed = time.time() - start)
            assert previous is not None
            previous.set(brightness=40, transition=TRANSITION_MINIMUM)
            # self.player.wait(10)

class BuildBrightness(PlayMode):
    """Brightness change rate test."""

    def __init__(
        self,
        player: Player, 
        name: str,
        #
        equal_trans: bool,
    ):
        super().__init__(
            player=player, 
            name=name, 
            preset_relays=True, 
        )
        self.equal_trans = equal_trans

    def execute(self):
        self.player.set_dimmers(ALL_LOW)
        brightnesss = [(i + 1) * 10 for i in range(LIGHT_COUNT)]
        transitions = (
            [0.5] * LIGHT_COUNT
                if self.equal_trans else
            [(i + 1) * 2 for i in range(LIGHT_COUNT)]
        )
        for dimmer, brightness, transition in zip(self.player.dimmer_channels, brightnesss, transitions):
            dimmer.set(brightness=brightness, transition=transition)
        self.player.wait(4)
