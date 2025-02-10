"""Marquee Lighted Sign Project - main"""

import argparse
import contextlib
import os
import sys
import time

from modes import *
from players import Player

class ArgumentParserBugFix(argparse.ArgumentParser):
    """"""
    def error(self, message):
        print(f'????? {message}')
        raise ValueError("Generic argparse error")

    def exit(self, status=0, message=None):
        print(f'!!!!! {status}:{message}')
        exit(status)

def display_help(player):
    """"Display the command-line syntax."""
    print()
    print("Usage:")
    print("\tmarquee.py mode <mode_index | mode_name>")
    print("\tmarquee.py pattern <-dimmer [pattern]> <-relay [pattern]> <-do_not_derive_missing>")
    print("\tmarquee.py command [command_name]")
    print("Modes:")
    for index, entry in player.modes.items():
        if index != 0:
            print(f'{index}\t{entry.name}')
    print("Patterns: !!!!!!!!")
    print("Commands:")
    for command in player.commands:
        print(f'\t{command}')
    print()

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

def parse_runtime_arguments(player):
    parser = ArgumentParserBugFix(exit_on_error=False)
    subparsers = parser.add_subparsers(dest='operation', required=True)
    command_parser = subparsers.add_parser('command')
    command_parser.add_argument('command_name', choices=player.commands.keys())
    mode_parser = subparsers.add_parser('mode')
    mode_parser.add_argument(
        'mode_id', 
        choices=player.mode_id_to_index.keys() - {'0', 'selection'} # !!!
    )
    pattern_parser = subparsers.add_parser('pattern')
    pattern_parser.add_argument('-relay', type=validate_light_pattern)
    pattern_parser.add_argument('-dimmer', type=validate_brightness_pattern)
    pattern_parser.add_argument('-do_not_derive_missing', dest='derive_missing', action='store_false')
    try:
        return parser.parse_args()
    except (argparse.ArgumentError, argparse.ArgumentTypeError, ValueError) as e:
        print(f"ERROR:{e}")
        return False

def process_runtime_arguments(player):
    """Validate and interpret the runtime arguments.
       Return dict of parameters if the arguments are valid, 
       otherwise False."""
    parsed = parse_runtime_arguments(player)
    print(f'parsed:{parsed}')
    if not parsed:
        return False
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
    print(f'args:{args}')
    return args

def main():
    """Execute Marquee application."""
    try:
        player = Player()
        register_modes(player)
        if arg := process_runtime_arguments(player):
            player.execute(**arg)
        else:
            display_help(player)
    finally:
        player.close()  # !!! ignore errors

if __name__ == "__main__":
    main()
