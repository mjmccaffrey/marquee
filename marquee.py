"""Marquee Lighted Sign Project - main"""

import sys
import time

from dimmers import RelayOverride
from modes import *
import players
from sequences import *

def display_help(player):
    """"Display the command-line syntax."""
    print()
    print("Usage: marquee.py {mode_index | mode_name | light_pattern}\n")
    print("Valid modes:")
    for index, entry in player.modes.items():
        if index != 0:
            print(f'{index}\t{entry.name}')
    print()

def register_modes(player: players.Player):
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
        lambda: seq_random_flip(player._sign.current_pattern),
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
        lambda: seq_random_flip(player._sign.current_pattern),
        simple=True, pace=2.0,
        relay_override=RelayOverride(
            # transition_on=1.0,
            # transition_off=3.0,
            level_on=80,
            level_off=10,
        )
    )
    player.add_mode(12, "blink_all_fade_seq", seq_blink_all, simple=True, pace=1,
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
            level_on=90,
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
    player.add_mode(17, "build_1", function=lambda: build1(player))

    ## Rather than a fixed transition rate, calculate so that effective rate is 10%-20% per second
    # Bulbs fade and build at long random rates.  At start, each builds from 0% to a random %
    # Rows of bulbs progressively fade, and then build back from the bottom
    # Snake growing counter/clockwise
    # 2 snakes of length 3 bouncing off each other
    # Sides fade and build, and then top & bottom do the same
    # Spin, or other action, as all bulbs slowly build
    # Rotate 50% to 100% every 0.5 seconds
    # Build and fade random corner

    def build1(player):
        player.do_sequence(seq_all_on)
        player.do_sequence(seq_all_off, relay_override=RelayOverride(concurrent=True))
        for i, dimmer in enumerate(player._sign._dimmers):
            print(i)
            dimmer.set(level=(i+1)*10, transition=10)
        time.sleep(30)

def is_valid_light_pattern(arg):
    """ Return True if arg is a valid light pattern, 
        otherwise False. """
    return (
        len(arg) == LIGHT_COUNT and 
        all(e in {"0", "1"} for e in arg)
    )

def is_valid_brightness_pattern(arg):
    """ Return True if arg is a valid brightness pattern, 
        otherwise False. """
    return (
        len(arg) == LIGHT_COUNT and 
        all(e.upper() in "0123456789A" for e in arg)
    )

def process_runtime_argument(player):
    """Validate and interpret the runtime arguments.
       Return dict of parameters if the arguments are valid, 
       otherwise False."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        return False
    arg1 = sys.argv[1]
    if is_valid_light_pattern(arg1):
        player_args = {"light_pattern": arg1}
        if len(sys.argv) == 3:
            arg2 = sys.argv[2]
            if is_valid_brightness_pattern(arg1):
                player_args |=  {"brightness_pattern": arg2}
            else:
                return False
        else:
            player_args |= {"brightness_pattern": "AAAAAAAAAA"}
    elif arg1 in player.mode_id_to_index:
        player_args = {"mode_index": player.mode_id_to_index[arg1]}
    else:
        return False
    return player_args

def main():
    """Execute Marquee application."""
    try:
        player = players.Player()
        register_modes(player)
        arg = process_runtime_argument(player)
        if arg:
            player.execute(**arg)
        else:
            display_help(player)
    finally:
        player.close()

if __name__ == "__main__":
    main()
