"""Marquee Lighted Sign Project - modes"""

from dimmers import Dimmer, TRANSITION_MINIMUM
import random
from sequences import *
import time

from dimmers import RelayOverride
from players import Player
from signs import ALL_ON, ALL_OFF, LIGHT_COUNT

def register_modes(player: Player):
    """Register the operating modes."""
    player.add_mode(1, "all_on", seq_all_on, simple=True)
    player.add_mode(2, "even_on", seq_even_on, simple=True)
    player.add_mode(3, "even_off", seq_even_off, simple=True)
    player.add_mode(4, "all_off", seq_all_off, simple=True)
    player.add_mode(5, "blink_all", seq_blink_all, simple=True, pace=1)
    player.add_mode(6, "blink_alternate",
        seq_blink_alternate, simple=True, pace=1, 
    )
    player.add_mode(7, "rotate",
        lambda: seq_rotate("1100000000"), simple=True, pace=0.5
    )
    player.add_mode(8, "random_flip",
        lambda: seq_random_flip(player.sign.current_pattern),
        simple=True, pace=0.5
    )
    player.add_mode(9, "demo", lambda: mode_rhythmic_demo(player))
    player.add_mode(10, "blink_alternate_fade",
        seq_blink_alternate, simple=True, pace=4, 
        relay_override=RelayOverride(
            transition_on=1.0,
            transition_off=3.0,
        )
    )
    player.add_mode(11, "random_flip_fade",
        lambda: seq_random_flip(player.sign.current_pattern),
        simple=True, pace=2.0,
        relay_override=RelayOverride(),
    )
    player.add_mode(12, "blink_all_fade_seq", seq_blink_all, simple=True, pace=0.15,
        relay_override=RelayOverride(
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    player.add_mode(13, "blink_all_fade_con", seq_blink_all, simple=True, pace=1,
        relay_override=RelayOverride(
            concurrent=True,
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    player.add_mode(14, "blink_all_fade_fast", seq_blink_all, simple=True, pace=0.5,
        relay_override=RelayOverride(
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    player.add_mode(15, "blink_all_fade_slowwww", seq_blink_all, simple=True, pace=10,
        relay_override=RelayOverride(
            level_on=100,
            transition_on=10,
            level_off=10,
            transition_off=10,
        )
    )
    player.add_mode(16, "blink_all_fade_stealth", seq_blink_all, simple=True, pace=(1, 60),
        relay_override=RelayOverride(
            transition_on=2,
            transition_off=2,
        )
    )
    player.add_mode(17, "build_NEQ", function=lambda: build1(player, False))
    player.add_mode(18, "build_EQ", function=lambda: build1(player, True))
    player.add_mode(19, "random_fade", function=lambda: mode_random_fade(player))

def mode_random_fade(player: Player):

    def _new_transition() -> float:
        """"""
        return random.uniform(TRANSITION_MINIMUM, 5 * player.pace_factor)
    
    def _new_level(old) -> int:
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
                    level = _new_level(channel.brightness)
                )
                channel.next_update = now + tran
        player.pace_wait(0.1)

def build1(player: Player, equal: bool):
    player.sign.set_lights(ALL_ON)
    player.sign.set_lights(ALL_OFF, 
        relay_override=RelayOverride(concurrent=True))
    levels = [(i + 1) * 10 for i in range(10)]
    transitions = (
        [20] * 10 
            if equal else
        [(i + 1) * 2 for i in range(10)]
    )
    for dimmer, level, transition in zip(player.sign.dimmer_channels, levels, transitions):
        dimmer.set(level=level, transition=transition)
    player.pace_wait(40)

def mode_rhythmic_demo(player: Player):
    """Perform a rhythmic demonstration."""
    while True:
        # !!!!!!!!! BREAK THIS UP INTO SUB-FUNCTIONS

        Dimmer.set_brightness_all(level=30, wait=True)
        player.do_sequence(
            seq_center_alternate,
            count=2,
            pace=0.8,
        )
        Dimmer.set_brightness_all(offset=10)
        player.do_sequence(
            seq_blink_alternate,
            count=2,
            pace=0.8,
        )
        Dimmer.set_brightness_all(offset=10)
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
        Dimmer.set_brightness_all(offset=10)
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
        Dimmer.set_brightness_all(offset=10)
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
        Dimmer.set_brightness_all(offset=10)
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
        Dimmer.set_brightness_all(offset=10)
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
        Dimmer.set_brightness_all(level=100)
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

        Dimmer.set_brightness_all(level=0, transition=0.5, wait=True)
        Dimmer.set_brightness_all(level=100, transition=3.0)
        player.do_sequence(
            seq_rotate,
            count=8,
            pace=0.04,
        )
        player.do_sequence(seq_all_on, post_delay=6.4)
        player.do_sequence(seq_all_off, post_delay=900)

