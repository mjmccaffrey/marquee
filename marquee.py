"""Marquee Lighted Sign Project - main"""

import argparse
import sys
import time

from dimmers import RelayOverride
from modes import *
import players
from sequences import *

def display_help(player):
    """"Display the command-line syntax."""
    print()
    print("Usage: marquee.py {mode_index | mode_name | light_pattern | command}\n")
    print("Commands:")
    for command in player.commands:
        print(command)
    print("Modes:")
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
            # level_on=80,
            # level_off=10,
        )
    )
    player.add_mode(12, "blink_all_fade_seq", seq_blink_all, simple=True, pace=0.15,  # ,
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
    player.add_mode(17, "build_NEQ", function=lambda: build1(player, False))
    player.add_mode(18, "build_EQ", function=lambda: build1(player, True))

    ## Rather than a fixed transition rate, calculate so that effective rate is 10%-20% per second
    # Bulbs fade and build at long random rates.  At start, each builds from 0% to a random %
    # Rows of bulbs progressively fade, and then build back from the bottom
    # Sides fade and build, and then top & bottom do the same
    # Spin, or other action, as all bulbs slowly build
    # Rotate 50% to 100% every 0.5 seconds
    # Build and fade random corner pair
    # blink_all_fade_seq with rotating order - build+0, fade+1, build+2, fade+3, etc.

def build1(player, equal):
    player.do_sequence(seq_all_on, pace=0)
    player.do_sequence(seq_all_off, pace=0, relay_override=RelayOverride(concurrent=True))
    levels = [(i + 1) * 10 for i in range(10)]
    transitions = (
        [20] * 10 
            if equal else
        [(i + 1) * 2 for i in range(10)]
    )
    for dimmer, level, transition in zip(player._sign._dimmers, levels, transitions):
        dimmer.set(level=level, transition=transition)
    time.sleep(40)

def validate_light_pattern(arg):
    """ Return arg if it is a valid light pattern, 
        otherwise raise exception. """
    if not (
        len(arg) == LIGHT_COUNT and 
        all(e in {"0", "1"} for e in arg)
    ): raise ValueError("Invalid light pattern")
    return arg

def validate_brightness_pattern(arg):
    """ Return normalized arg if it is a valid brightness pattern, 
        otherwise raise exception. """
    arg = arg.upper()
    if not (
        len(arg) == LIGHT_COUNT and 
        all(e in "0123456789A" for e in arg)
    ): raise ValueError("Invalid brightness pattern")
    return arg

def process_runtime_arguments(player):
    """Validate and interpret the runtime arguments.
       Return dict of parameters if the arguments are valid, 
       otherwise False."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='operation')
    command_parser = subparsers.add_parser('command')
    command_parser.add_argument('command_name', choices=['calibrate_all_dimmers'])
    mode_parser = subparsers.add_parser('mode')
    mode_parser.add_argument('mode_id', choices=['1', '2', 'ab', 'cd'])
    pattern_parser = subparsers.add_parser('pattern')
    pattern_parser.add_argument('-relay', type=validate_light_pattern)
    pattern_parser.add_argument('-dimmer', type=validate_brightness_pattern)
    pattern_parser.add_argument('-do_not_derive_missing', dest='derive_missing', action='store_false')
    parsed = parser.parse_args()
    print(parsed)
    # sys.exit()
    if parsed.operation == 'command':
        args = {"command": parsed.command_name}
    elif parsed.operation == 'mode':
        args = {"mode_index": player.mode_id_to_index[parsed.mode_id]}
    elif parsed.operation == 'pattern':
        args = {}
        if p:= parsed.relay:
            args |= {"light_pattern": p}
        if p := parsed.dimmer:
            args |= {"brightness_pattern": p}
        if parsed.relay:
            if not parsed.dimmer and parsed.derive_missing:
                pattern = ['A' if e == '1' else '0' for e in parsed.relay]
                args |= {"brightness_pattern": pattern}
        elif parsed.dimmer:
            if parsed.derive_missing:
                pattern = ['0' if e == '0' else "1" for e in parsed.dimmer]
                args |= {"light_pattern": pattern}
        else:
             return False
    else:
        raise Exception("Command line parsing error")
    print(args)
    return args

def main():
    """Execute Marquee application."""
    try:
        player = players.Player()
        register_modes(player)
        arg = process_runtime_arguments(player)
        if arg:
            player.execute(**arg)
        else:
            display_help(player)
    finally:
        player.close()

if __name__ == "__main__":
    main()
