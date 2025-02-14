"""Marquee Lighted Sign Project - arguments"""

from argparse import ArgumentParser, ArgumentError, ArgumentTypeError
from players import Player
from signs import LIGHT_COUNT

class ArgumentParserImproved(ArgumentParser):
    """
    !!!!
    https://bugs.python.org/issue41255
    https://github.com/python/cpython/issues/103498
    https://stackoverflow.com/questions/67890157/python-3-9-1-argparse-exit-on-error-not-working-in-certain-situations
    https://stackoverflow.com/questions/69108632/unable-to-catch-exception-error-for-argparse
    """ 

    def add_argument(self, *args, **kwargs):
        if kwargs.pop('optional', False):
            new_args = [
                ('-' + arg, '--' + arg)
                for arg in args
            ]
            args = tuple(a for t in new_args for a in t)
        return super().add_argument(*args, **kwargs)
    
    def error(self, message):
        raise ValueError(f"Argparse error:{message}")

    def exit(self, status=0, message=None):
        raise ValueError(f"Argparse error:{status}:{message}")

def str_to_bool(arg):
    values = {
        'true': True, 'yes': True, 'on': True,
        'false': False, 'no': False, 'off': False,
    }
    try:
        return values[arg.lower()]
    except KeyError:
        raise ValueError

def display_help(player: Player):
    """"Display the command-line syntax."""
    print()
    print("Usage:")
    print("  marquee.py mode [mode_index | mode_name]")
    print("  marquee.py pattern [--dimmer=[pattern] &| --relay=[pattern]]")
    print("                     [--derive_missing=[true|false]]")
    print("  marquee.py command [command_name]")
    print()
    print("Modes:")
    for index, entry in player.modes.items():
        if index != 0:
            print(f'   {index}   {entry.name}')
    print()
    print("Patterns: Specify --dimmer, --relay, or both.")
    print("  dimmer: 10 hex values, each 0..A (0%..100%)")
    print("  relay: 10 binary values")
    print("  derive_missing:")
    print("      If true (default) and only one pattern is specified,")
    print("      the missing pattern will be assumed.")
    print("      If false, the state of the device set without a pattern")
    print("      will not be initialized at startup.")
    print()
    print("Commands:")
    for command in player.commands:
        print(f'  {command}')
    print()

def validate_light_pattern(arg: str):
    """ Return arg if it is a valid light pattern, 
        otherwise raise exception. """
    if not (
        len(arg) == LIGHT_COUNT and 
        all(e in {"0", "1"} for e in arg)
    ): raise ValueError("Invalid light pattern")
    return arg

def validate_brightness_pattern(arg: str):
    """ Return normalized arg if it is a valid brightness pattern, 
        otherwise raise exception. """
    arg = arg.upper()
    if not (
        len(arg) == LIGHT_COUNT and 
        all(e in "0123456789A" for e in arg)
    ): raise ValueError("Invalid brightness pattern")
    return arg

def parse_arguments(player: Player):
    top_p = ArgumentParserImproved(exit_on_error=False)
    sub_p = top_p.add_subparsers(dest='operation', required=True)
    command_p = sub_p.add_parser('command')
    command_p.add_argument('command_name', choices=player.commands.keys())
    mode_p = sub_p.add_parser('mode')
    mode_p.add_argument('mode_id', choices=player.mode_id_to_index.keys())
    mode_p.add_argument('pace_factor', 
        optional=True, type=float, default=1.0)
    pattern_p = sub_p.add_parser('pattern')
    pattern_p.add_argument('relay', 
        optional=True, type=validate_light_pattern)
    pattern_p.add_argument('dimmer', 
        optional=True, type=validate_brightness_pattern)
    pattern_p.add_argument('derive_missing', 
        optional=True, dest='derive_missing', type=str_to_bool, default=True)
    try:
        return top_p.parse_args()
    except (ArgumentError, ArgumentTypeError, ValueError) as err:
        print(f"ERROR:{err}")
        return False

def process_arguments(player: Player):
    """Validate and interpret the runtime arguments.
       Return dict of parameters if the arguments are valid, 
       otherwise False."""
    parsed = parse_arguments(player)
    ##print(f'parsed:{parsed}')
    if not parsed:
        return False
    if parsed.operation == 'command':
        args = {"command": parsed.command_name}
    elif parsed.operation == 'mode':
        args = {"mode_index": player.mode_id_to_index[parsed.mode_id]}
        player.pace_factor = parsed.pace_factor
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
