"""Marquee Lighted Sign Project - modes"""

from dimmers import Dimmer
from sequences import *

def mode_rhythmic_demo(player):
    """Perform a rhythmic demonstration."""
    while True:
        print("!!!!!")
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

# def dimmer_odd_even(player):
#     """ """
#     
#     up = range(0, 101, 5)
#     down = reversed(up)
#     pace = 0.5
#     player.do_sequence(seq_all_off)
#     while True:
#         
