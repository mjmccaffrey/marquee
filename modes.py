"""Marquee Lighted Sign Project - modes"""

import itertools
import random
from sequences import *
import time

from dimmers import RelayOverride, TRANSITION_MINIMUM
from players import Player
from signs import ALL_LOW, ALL_ON, ALL_OFF, LIGHT_COUNT

def register_modes(player: Player):
    """Register the operating modes."""
    player.add_mode(1, "all_on", sequence=seq_all_on)
    player.add_mode(2, "all_off", sequence=seq_all_off)
    player.add_mode(3, "even_on", sequence=seq_even_on)
    player.add_mode(4, "even_off", sequence=seq_even_off)
    player.add_mode(5, "blink_all", 
        sequence=seq_blink_all, pace=1,
    )
    player.add_mode(6, "blink_alternate", 
        sequence=seq_blink_alternate, pace=1, 
    )
    player.add_mode(7, "rotate",
        sequence=lambda: seq_rotate("1100000000"), pace=0.5,
    )
    player.add_mode(8, "random_flip",
        sequence=lambda: seq_random_flip(player.sign.light_pattern), pace=0.5,
    )
    player.add_mode(9, "demo",
        sequence=lambda: seq_random_flip(player.sign.light_pattern), pace=0.5,
    )
    player.add_mode(10, "blink_alternate_fade",
        sequence=seq_blink_alternate, pace=4, 
        override=RelayOverride(
            transition_on=1.0,
            transition_off=3.0,
        )
    )
    player.add_mode(11, "random_flip_fade",
        sequence=lambda: seq_random_flip(player.sign.light_pattern), pace=2.0,
        override=RelayOverride(),
    )
    player.add_mode(12, "blink_all_fade_seq",
        sequence=seq_blink_all, pace=1,
        override=RelayOverride(
            concurrent=False,
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    player.add_mode(13, "blink_all_fade_con", 
        sequence=seq_blink_all, pace=1,
        override=RelayOverride(
            concurrent=True,
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    player.add_mode(14, "blink_all_fade_fast", 
        sequence=seq_blink_all, pace=0.5,
        override=RelayOverride()
    )
    player.add_mode(15, "blink_all_fade_slowwww", 
        sequence=seq_blink_all, pace=10,
        override=RelayOverride(
            brightness_on=100,
            brightness_off=10,
        )
    )
    player.add_mode(16, "blink_all_fade_stealth", 
        sequence=seq_blink_all, pace=(1, 60),
        override=RelayOverride(
            transition_on=2,
            transition_off=2,
        )
    )
    player.add_mode(17, "build_NEQ", mode=lambda: build1(player, False))
    player.add_mode(18, "build_EQ", mode=lambda: build1(player, True))
    player.add_mode(19, "random_fade", mode=lambda: mode_random_fade(player))
    player.add_mode(20, "random_fade_steady", mode=lambda: mode_random_fade(player, 2.0))
    player.add_mode(21, "even_odd_fade", mode=lambda: mode_even_odd_fade(player))
    player.add_mode(22, "corner_rotate_fade", 
        sequence=seq_opposite_corner_pairs, pace=5,
        override=RelayOverride(
            concurrent=True,
            brightness_on = 90,
            brightness_off = 10,
        )
    )
    player.add_mode(23, "rotate_slight_fade",
        sequence=lambda: seq_rotate(), pace=0.5,
        override=RelayOverride(
            concurrent=False,
            brightness_on = 100,
            brightness_off = 30,
        )
    )

def mode_random_fade(player: Player, transition=None):
    """"""
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

def build1(player: Player, equal: bool):
    """"""
    player.sign.set_lights(ALL_ON)
    player.sign.set_dimmers(ALL_LOW)
    brightnesss = [(i + 1) * 10 for i in range(LIGHT_COUNT)]
    transitions = (
        [20] * LIGHT_COUNT
            if equal else
        [(i + 1) * 2 for i in range(LIGHT_COUNT)]
    )
    for dimmer, brightness, transition in zip(player.sign.dimmer_channels, brightnesss, transitions):
        dimmer.set(brightness=brightness, transition=transition)
    player.wait(40)

def mode_even_odd_fade(player: Player):
    """"""
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
        