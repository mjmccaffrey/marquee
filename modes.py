"""Custom operating modes."""

from sequences import *

def mode_rhythmic_demo(do_sequence):
    """Perform a rhythmic demonstration."""
    while True:

        do_sequence(seq_all_on)



        do_sequence(
            lambda: seq_build_rows(pattern="1", from_top=True),
            count=4,
            pace=1,
        )
        do_sequence(
            lambda: seq_build_rows(pattern="1", from_top=False),
            count=4,
            pace=1,
        )
        do_sequence(
            lambda: seq_build_rows(pattern="0", from_top=True),
            count=4,
            pace=1,
        )
        do_sequence(
            lambda: seq_build_rows(pattern="0", from_top=False),
            count=4,
            pace=1,
        )

        do_sequence(
            seq_blink_alternate,
            count=2,
            pace=0.8,
        )
        do_sequence(
            seq_blink_all,
            count=2,
            pace=0.8,
        )

        do_sequence(
            lambda: seq_move_halves(from_left=True),
            count=2,
            pace=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_move_halves(from_left=False),
            count=2,
            pace=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_build_halves(from_left=True),
            count=2,
            pace=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_build_halves(from_left=False),
            count=2,
            pace=0.4,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('1000000000', clockwise=True),
            count=2,
            pace=0.2,
            stop=4,
        )
        do_sequence(
            lambda: seq_rotate('0000000001', clockwise=False),
            count=2,
            pace=0.2,
            stop=4,
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
            count=2,
            pace=0.1,
            stop=8,
        )
        do_sequence(
            lambda: seq_rotate('1111111100', clockwise=False),
            count=2,
            pace=0.1,
            stop=8,
        )

        #
        do_sequence(
            seq_rotate,
            count=8,
            pace=0.04,
        )

        # !!!! OR, just rotate 8 lights per beat, rather than 10

        # !!!! do_sequence(seq_rotate, 7, 0.04, stop=9)

        do_sequence(seq_all_on, post_delay=6.4)
        do_sequence(seq_all_off, post_delay=900)
