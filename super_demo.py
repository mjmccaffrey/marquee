""""""

from sequence_defs import *

from dimmers import RelayOverride, TRANSITION_MINIMUM
from players import Player
from signs import ALL_ON, ALL_OFF, LIGHT_COUNT

def mode_super_demo(player: Player):
    """Perform a rhythmic demonstration."""
        # !!!!!!!!! BREAK THIS UP INTO SUB-FUNCTIONS

    while True:
        discover_relays()
        discover_dimmers() - QUICK build & fade, twice
        mid_game()
        end_game()
        post_game()
            FADE DURING THIS
            player.play_sequence(seq_all_on, post_delay=6.4)
            player.play_sequence(seq_all_off, post_delay=900)

        player.play_sequence(
            seq_center_alternate,
            count=2,
            pace=0.8,
        )
        player.play_sequence(
            seq_blink_alternate,
            count=2,
            pace=0.8,
        )

        player.play_sequence(
            lambda: seq_move_halves(from_left=True),
            count=1,
            pace=0.4,
            stop=4,
        )
        player.play_sequence(
            lambda: seq_move_halves(from_left=False),
            count=1,
            pace=0.4,
            stop=4,
        )
        player.play_sequence(
            lambda: seq_build_halves(from_left=True),
            count=1,
            pace=0.4,
            stop=4,
        )
        player.play_sequence(
            lambda: seq_build_halves(from_left=False),
            count=1,
            pace=0.4,
            stop=4,
        )

        (just under) 4 COUNT PAUSE
        -- or --


        GRACE NOTES
        player.play_sequence(
           lambda: seq_build_rows_4("1", from_top=True),
           count=4,
           pace=0.2,
        )
        player.play_sequence(
           lambda: seq_build_rows_4("1", from_top=False),
           count=4,
           pace=0.2,
        )


        player.play_sequence(
            lambda: seq_rotate('1000000000', clockwise=True),
            count=1,
            pace=0.2,
            stop=8,
        )
        player.play_sequence(
            lambda: seq_rotate('0000000010', clockwise=False),
            count=1,
            pace=0.2,
            stop=8,
        )

        THIS PART IS LAME
        player.play_sequence(
            lambda: seq_rotate('0111111111', clockwise=True),
            count=2,
            pace=0.2,
            stop=4,
        )
        player.play_sequence(
            lambda: seq_rotate('1111111110', clockwise=False),
            count=2,
            pace=0.2,
            stop=4,
        )
        player.play_sequence(
            lambda: seq_rotate('1100000000', clockwise=True),
            count=4,
            pace=0.1,
            stop=8,
        )
        player.play_sequence(
            lambda: seq_rotate('1111111100', clockwise=False),
            count=4,
            pace=0.1,
            stop=8,
        )

        build from 10% to 100%
        player.play_sequence(
            seq_rotate,
            count=8,
            pace=0.04,
        )
