"""Custom operating modes."""

from sequences import *

def seq_center_alternate():
    """Alternate the top and bottom center lights."""
    yield "0100000000"
    yield "0000001000"

def mode_rhythmic_demo(do_sequence):
    """Perform a rhythmic demonstration."""
    while True:
        do_sequence(
            seq_center_alternate,
            count=2,
            pace=0.8,
        )
        do_sequence(
            seq_blink_alternate,
            count=2,
            pace=0.8,
        )
        do_sequence(
            lambda: seq_move_halves(from_left=True),
            count=1,
            pace=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_move_halves(from_left=False),
            count=1,
            pace=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_build_halves(from_left=True),
            count=1,
            pace=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_build_halves(from_left=False),
            count=1,
            pace=0.4,
            stop=4,
        )

        do_sequence(
           lambda: seq_build_rows_4("1", from_top=True),
           count=4,
           pace=0.2,
        )
        do_sequence(
           lambda: seq_build_rows_4("1", from_top=False),
           count=4,
           pace=0.2,
        )
        do_sequence(
            lambda: seq_rotate('1000000000', clockwise=True),
            count=1,
            pace=0.2,
            stop=8,
        )
        do_sequence(
            lambda: seq_rotate('0000000010', clockwise=False),
            count=1,
            pace=0.2,
            stop=8,
        )
        do_sequence(
            lambda: seq_rotate('0111111111', clockwise=True),
            count=2,
            pace=0.2,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('1111111110', clockwise=False),
            count=2,
            pace=0.2,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('1100000000', clockwise=True),
            count=4,
            pace=0.1,
            stop=8,
        )
        do_sequence(
            lambda: seq_rotate('1111111100', clockwise=False),
            count=4,
            pace=0.1,
            stop=8,
        )
        do_sequence(
            seq_rotate,
            count=8,
            pace=0.04,
        )
        do_sequence(seq_all_on, post_delay=6.4)
        do_sequence(seq_all_off, post_delay=900)
