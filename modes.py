"""Marquee Lighted Sign Project - modes"""

import itertools
import random
from sequences import *
import time

from dimmers import RelayOverride, TRANSITION_MINIMUM
from executors import Executor
from players import Player
from signs import ALL_LOW, ALL_ON, ALL_OFF, LIGHT_COUNT

def register_mode_ids(exec: Executor):
    exec.add_mode_ids(1, "all_on")
    exec.add_mode_ids(2, "all_off")
    exec.add_mode_ids(3, "even_on")
    exec.add_mode_ids(4, "even_off")
    exec.add_mode_ids(5, "blink_all")
    exec.add_mode_ids(6, "blink_alternate")
    exec.add_mode_ids(7, "rotate")
    exec.add_mode_ids(8, "random_flip")
    exec.add_mode_ids(9, "demo")
    exec.add_mode_ids(10, "blink_alternate_fade")
    exec.add_mode_ids(11, "random_flip_fade")
    exec.add_mode_ids(12, "blink_all_fade_seq")
    exec.add_mode_ids(13, "blink_all_fade_con")
    exec.add_mode_ids(14, "blink_all_fade_fast")
    exec.add_mode_ids(15, "blink_all_fade_slowwww")
    exec.add_mode_ids(16, "blink_all_fade_stealth")
    exec.add_mode_ids(17, "build_NEQ")
    exec.add_mode_ids(18, "build_EQ")
    exec.add_mode_ids(19, "random_fade")
    exec.add_mode_ids(20, "random_fade_steady")
    exec.add_mode_ids(21, "even_odd_fade")
    exec.add_mode_ids(22, "corner_rotate_fade")
    exec.add_mode_ids(23, "rotate_slight_fade")

def register_mode_functions(exec: Executor):
    """Register the operating modes."""
    player = exec.player
    sign = exec.player.sign
    exec.add_sequence_mode_func(1, "all_on", seq_all_on)
    exec.add_sequence_mode_func(2, "all_off", seq_all_off)
    exec.add_sequence_mode_func(3, "even_on", seq_even_on)
    exec.add_sequence_mode_func(4, "even_off", seq_even_off)
    exec.add_sequence_mode_func(5, "blink_all", 
        seq_blink_all, pace=1,
    )
    exec.add_sequence_mode_func(6, "blink_alternate", 
        seq_blink_alternate, pace=1, 
    )
    exec.add_sequence_mode_func(7, "rotate",
        lambda: seq_rotate("1100000000"), pace=0.5,
    )
    exec.add_sequence_mode_func(8, "random_flip",
        lambda: seq_random_flip(sign.light_pattern), pace=0.5,
    )
    exec.add_sequence_mode_func(9, "demo",
        lambda: seq_random_flip(sign.light_pattern), pace=0.5,
    )
    exec.add_sequence_mode_func(10, "blink_alternate_fade",
        seq_blink_alternate, pace=4, 
        override=RelayOverride(
            transition_on=1.0,
            transition_off=3.0,
        )
    )
    exec.add_sequence_mode_func(11, "random_flip_fade",
        lambda: seq_random_flip(sign.light_pattern), pace=2.0,
        override=RelayOverride(),
    )
    exec.add_sequence_mode_func(12, "blink_all_fade_seq",
        seq_blink_all, pace=1,
        override=RelayOverride(
            concurrent=False,
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    exec.add_sequence_mode_func(13, "blink_all_fade_con", 
        seq_blink_all, pace=1,
        override=RelayOverride(
            concurrent=True,
            transition_on=0.5,
            transition_off=0.5,
        )
    )
    exec.add_sequence_mode_func(14, "blink_all_fade_fast", 
        seq_blink_all, pace=0.5,
        override=RelayOverride()
    )
    exec.add_sequence_mode_func(15, "blink_all_fade_slowwww", 
        seq_blink_all, pace=10,
        override=RelayOverride(
            brightness_on=100,
            brightness_off=10,
        )
    )
    exec.add_sequence_mode_func(16, "blink_all_fade_stealth", 
        seq_blink_all, pace=(1, 60),
        override=RelayOverride(
            transition_on=2,
            transition_off=2,
        )
    )
    exec.add_mode_func(17, "build_NEQ", lambda: build1(player, False))
    exec.add_mode_func(18, "build_EQ", lambda: build1(player, True))
    exec.add_mode_func(19, "random_fade", lambda: mode_random_fade(player))
    exec.add_mode_func(20, "random_fade_steady", lambda: mode_random_fade(player, 2.0))
    exec.add_mode_func(21, "even_odd_fade", lambda: mode_even_odd_fade(player))
    exec.add_sequence_mode_func(22, "corner_rotate_fade", 
        seq_opposite_corner_pairs, pace=5,
        override=RelayOverride(
            concurrent=True,
            brightness_on = 90,
            brightness_off = 10,
        )
    )
    exec.add_sequence_mode_func(23, "rotate_slight_fade",
        seq_rotate, pace=0.5,
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
        