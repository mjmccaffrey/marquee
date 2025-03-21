"""Marquee Lighted Sign Project - mode definitions"""

import itertools
import random
from sequence_defs import *
import time

from dimmers import RelayOverride, TRANSITION_MINIMUM
from signs import ALL_LOW, ALL_ON, LIGHT_COUNT

def mode_random_fade(player, transition=None):
    """Change brightness of random bulb to a random level,
       with either a random or specified transition time."""
    def _new_transition() -> float:
        if transition is None:
            return random.uniform(TRANSITION_MINIMUM, 5.0 * player.speed_factor)
        else:
            return transition
    def _new_brightness(old) -> int:
        new = old
        while abs(new - old) < 20:
            new = random.randrange(101)
        return new
    player.sign.set_lights(ALL_ON)
    for channel in player.sign.dimmer_channels:
        channel.next_update = 0
    while True:
        for channel in player.sign.dimmer_channels:
            if channel.next_update < (now := time.time()):
                channel.set(
                    transition = (tran := _new_transition()),
                    brightness = _new_brightness(channel.brightness)
                )
                channel.next_update = now + tran
        player.wait(0.1)

def mode_even_odd_fade(player):
    """Fade every-other bulb."""
    player.sign.set_dimmers(ALL_LOW) 
    player.sign.set_lights(ALL_ON)
    delay = 5.0
    odd_on = ''.join('1' if i % 2 else '0' for i in range(LIGHT_COUNT))
    even_on = opposite_pattern(odd_on)
    for pattern in itertools.cycle((even_on, odd_on)):
        player.sign.set_lights(
            pattern, 
            override=RelayOverride(
                concurrent=True,
                brightness_on = 90,
                brightness_off = 10,
                transition_on=delay,
                transition_off=delay,
            )
        )
        player.wait(delay)

def build_brightness(player, equal_trans: bool):
    """Brightness change rate test."""
    player.sign.set_lights(ALL_ON)
    player.sign.set_dimmers(ALL_LOW)
    brightnesss = [(i + 1) * 10 for i in range(LIGHT_COUNT)]
    transitions = (
        [20] * LIGHT_COUNT
            if equal_trans else
        [(i + 1) * 2 for i in range(LIGHT_COUNT)]
    )
    for dimmer, brightness, transition in zip(player.sign.dimmer_channels, brightnesss, transitions):
        dimmer.set(brightness=brightness, transition=transition)
    player.wait(40)
