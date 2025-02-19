"""Marquee Lighted Sign Project - modes"""

from dimmers import Dimmer, TRANSITION_MINIMUM
import itertools
import random
from sequences import *
import time

from dimmers import RelayOverride
from players import Player
from signs import ALL_ON, ALL_OFF, LIGHT_COUNT

def register_modes(player: Player):
    """Register the operating modes."""
    player.add_mode(1, "all_on", sequence=seq_all_on)
    player.add_mode(2, "even_on", sequence=seq_even_on)
    player.add_mode(3, "even_off", sequence=seq_even_off)
    player.add_mode(4, "all_off", sequence=seq_all_off)
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
        sequence=lambda: seq_random_flip(player.sign.current_pattern), pace=0.5,
    )
    player.add_mode(9, "demo", mode=lambda: mode_rhythmic_demo(player))
    player.add_mode(10, "blink_alternate_fade",
        sequence=seq_blink_alternate, pace=4, 
        relay_override=RelayOverride(
            transition_on=1.0,
            transition_off=3.0,
        )
    )
    player.add_mode(11, "random_flip_fade",
        sequence=seq_random_flip(player.sign.current_pattern), pace=2.0,
        relay_override=RelayOverride(),
    )
    player.add_mode(12, "blink_all_fade_seq", 
        sequence=seq_blink_all, pace=0.15,
        relay_override=RelayOverride(
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    player.add_mode(13, "blink_all_fade_con", 
        sequence=seq_blink_all, pace=1,
        relay_override=RelayOverride(
            concurrent=True,
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    player.add_mode(14, "blink_all_fade_fast", 
        sequence=seq_blink_all, pace=0.5,
        relay_override=RelayOverride(
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    player.add_mode(15, "blink_all_fade_slowwww", 
        sequence=seq_blink_all, pace=10,
        relay_override=RelayOverride(
            brightness_on=100,
            transition_on=10,
            brightness_off=10,
            transition_off=10,
        )
    )
    player.add_mode(16, "blink_all_fade_stealth", 
        sequence=seq_blink_all, pace=(1, 60),
        relay_override=RelayOverride(
            transition_on=2,
            transition_off=2,
        )
    )
    player.add_mode(17, "build_NEQ", mode=lambda: build1(player, False))
    player.add_mode(18, "build_EQ", mode=lambda: build1(player, True))
    player.add_mode(19, "random_fade", mode=lambda: mode_random_fade(player))
    player.add_mode(20, "even_odd_fade", mode=lambda: mode_even_odd_fade(player))
    player.add_mode(21, "corner_rotate_fade", 
        sequence=seq_opposite_corner_pairs, pace=5,
        relay_override=RelayOverride(
            concurrent=True,
            brightness_on = 90,
            brightness_off = 10,
            transition_on=5,
            transition_off=5,
        )
    )

def mode_random_fade(player: Player):
    """"""
    def _new_transition() -> float:
        """"""
        return random.uniform(TRANSITION_MINIMUM, 5.0 * player.pace_factor)
    
    def _new_brightness(old) -> int:
        """"""
        new = old
        while abs(new - old) < 10:
            new = random.randrange(101)
        return new

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
    player.sign.set_lights(ALL_ON)
    player.sign.set_lights(ALL_OFF, 
        relay_override=RelayOverride(concurrent=True))
    brightnesss = [(i + 1) * 10 for i in range(10)]
    transitions = (
        [20] * 10 
            if equal else
        [(i + 1) * 2 for i in range(10)]
    )
    for dimmer, brightness, transition in zip(player.sign.dimmer_channels, brightnesss, transitions):
        dimmer.set(brightness=brightness, transition=transition)
    player.wait(40)

def mode_even_odd_fade(player: Player):
    """"""
    player.sign.set_lights(
        ALL_OFF, relay_override=RelayOverride(concurrent=True),
    )
    player.sign.set_lights(ALL_ON)
    delay = 5.0
    odd_on = ''.join('1' if i % 2 else '0' for i in range(LIGHT_COUNT))
    even_on = opposite_pattern(odd_on)
    for pattern in itertools.cycle((even_on, odd_on)):
        player.sign.set_lights(
            pattern, 
            relay_override=RelayOverride(
                concurrent=True,
                brightness_on = 90,
                brightness_off = 10,
                transition_on=delay,
                transition_off=delay,
            )
        )
        player.wait(delay)

def mode_rhythmic_demo(player: Player):
    """Perform a rhythmic demonstration."""
        # !!!!!!!!! BREAK THIS UP INTO SUB-FUNCTIONS

    while True:
        player.do_sequence(
            seq_center_alternate,
            count=2,
            pace=0.8,
        )
        player.do_sequence(
            seq_blink_alternate,
            count=2,
            pace=0.8,
        )
        player.do_sequence(
            lambda: seq_move_halves(from_left=True),
            count=1,
            pace=0.4,
            stop=4,
        )
        player.do_sequence(
            lambda: seq_move_halves(from_left=False),
            count=1,
            pace=0.4,
            stop=4,
        )
        player.do_sequence(
            lambda: seq_build_halves(from_left=True),
            count=1,
            pace=0.4,
            stop=4,
        )
        player.do_sequence(
            lambda: seq_build_halves(from_left=False),
            count=1,
            pace=0.4,
            stop=4,
        )
        player.do_sequence(
           lambda: seq_build_rows_4("1", from_top=True),
           count=4,
           pace=0.2,
        )
        player.do_sequence(
           lambda: seq_build_rows_4("1", from_top=False),
           count=4,
           pace=0.2,
        )
        player.do_sequence(
            lambda: seq_rotate('1000000000', clockwise=True),
            count=1,
            pace=0.2,
            stop=8,
        )
        player.do_sequence(
            lambda: seq_rotate('0000000010', clockwise=False),
            count=1,
            pace=0.2,
            stop=8,
        )
        player.do_sequence(
            lambda: seq_rotate('0111111111', clockwise=True),
            count=2,
            pace=0.2,
            stop=4,
        )
        player.do_sequence(
            lambda: seq_rotate('1111111110', clockwise=False),
            count=2,
            pace=0.2,
            stop=4,
        )
        player.do_sequence(
            lambda: seq_rotate('1100000000', clockwise=True),
            count=4,
            pace=0.1,
            stop=8,
        )
        player.do_sequence(
            lambda: seq_rotate('1111111100', clockwise=False),
            count=4,
            pace=0.1,
            stop=8,
        )

        player.do_sequence(
            seq_rotate,
            count=8,
            pace=0.04,
        )
        player.do_sequence(seq_all_on, post_delay=6.4)
        player.do_sequence(seq_all_off, post_delay=900)
