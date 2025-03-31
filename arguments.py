"""Marquee Lighted Sign Project - arguments"""

from collections.abc import Callable
from typing import Any, NoReturn

from argparse import Action, ArgumentParser, ArgumentError, ArgumentTypeError, Namespace
from signs import LIGHT_COUNT

class ArgumentParserImproved(ArgumentParser):
    """
    Causes parse_args to not exit, regardless of the error.
    References:
        https://bugs.python.org/issue41255
        https://github.com/python/cpython/issues/103498
        https://stackoverflow.com/questions/67890157/python-3-9-1-argparse-exit-on-error-not-working-in-certain-situations
        https://stackoverflow.com/questions/69108632/unable-to-catch-exception-error-for-argparse
    Also some small enhancements.
    """ 

    def add_argument(self, *args, **kwargs) -> Action:
        """If new kwarg optional==True, the option is added
           prefixed by both - and --."""
        if kwargs.pop('optional', False):
            new_args = [
                ('-' + arg, '--' + arg)
                for arg in args
            ]
            args = tuple(a for t in new_args for a in t)
        return super().add_argument(*args, **kwargs)
    
    def error(self, message) -> NoReturn:
        """ Do not exit when certain errors occur. """
        raise ValueError(f"Argparse error:{message}")

    def exit(self, status=0, message=None) -> NoReturn:
        """ Do not exit when certain other errors occur. """
        raise ValueError(f"Argparse error:{status}:{message}")

def str_to_bool(arg: str) -> bool:
    """ Map English words to booleans. """
    values = {
        'true': True, 'yes': True, 'on': True,
        'false': False, 'no': False, 'off': False,
    }
    try:
        return values[arg.lower()]
    except KeyError:
        raise ValueError()

def display_help(
    mode_menu: list[tuple[int, str]], 
    commands: dict[str, Callable],
):
    """"Display the command-line syntax."""
    print()
    print("Usage:")
    print("  marquee.py mode [mode_index | mode_name]")
    print("                  [--brightness_factor=[0 - 1.0]]")
    print("                  [--speed_factor=[0 - 1.0]]")
    print("  marquee.py pattern [--dimmer=[pattern] &| --relay=[pattern]]")
    print("                     [--derive_missing=[true|false]]")
    print("  marquee.py command [command_name]")
    print()
    print("Modes:")
    for index, name in mode_menu:
        print(f'   {index}   {name}')
    print()
    print("Patterns: Specify --dimmer, --relay, or both.")
    print(f"  dimmer: {LIGHT_COUNT} hex values, each 0..A (0%..100%)")
    print(f"  relay: {LIGHT_COUNT} binary values")
    print("  derive_missing:")
    print("      If true (default) and only one pattern is specified,")
    print("      the missing pattern will be assumed.")
    print("      If false, the state of the device set without a pattern")
    print("      will not be initialized at startup.")
    print()
    print("Commands:")
    for command in commands:
        print(f'  {command}')
    print()

def validate_light_pattern(arg: str) -> str:
    """ Return arg if it is a valid light pattern, 
        otherwise raise exception. """
    if not (
        len(arg) == LIGHT_COUNT and 
        all(e in {"0", "1"} for e in arg)
    ): 
        print(f"Invalid light pattern:{arg}")
        raise ValueError()
    return arg

def validate_brightness_pattern(arg: str) -> str:
    """ Return normalized arg if it is a valid brightness pattern, 
        otherwise raise exception. """
    arg_normalized = arg.upper()
    if not (
        len(arg_normalized) == LIGHT_COUNT and 
        all(e in "0123456789AF" for e in arg_normalized)
    ): 
        print(f"Invalid brightness pattern:{arg}")
        raise ValueError()
    return arg_normalized

def parse_arguments(
    mode_ids: dict[str, int], 
    commands: dict[str, Callable],
) -> Namespace:
    """ Parse the command-line arguments. """
    top_p = ArgumentParserImproved(exit_on_error=False)
    sub_p = top_p.add_subparsers(dest='operation', required=True)
    command_p = sub_p.add_parser('command')
    command_p.add_argument('command_name', choices=commands.keys())
    mode_p = sub_p.add_parser('mode')
    mode_choices = mode_ids.keys()
    mode_p.add_argument('mode_id', choices=mode_choices)
    mode_p.add_argument('brightness_factor', 
        optional=True, 
        type=float, default=1.0)
    mode_p.add_argument('speed_factor', 
        optional=True, 
        type=float, default=1.0)
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
        print(1, err)
        raise ValueError()

def process_arguments(
    mode_ids: dict[str, int], 
    commands: dict[str, Callable],
) -> dict[str, Any]:
    """Validate and interpret the runtime arguments.
       Return dict of parameters if the arguments are valid, 
       otherwise raise an error."""
    try:
        parsed = parse_arguments(mode_ids, commands)
    except ValueError as err:
        print(2, err)
        raise
    print("Args: " + ''.join('{k}: {v}, ' for k, v in vars(parsed).items()))
    if parsed.operation == 'command':
        args = {"command": parsed.command_name}
    elif parsed.operation == 'mode':
        args = {
            "mode_index": mode_ids[parsed.mode_id],
            "brightness_factor": parsed.brightness_factor,
            "speed_factor": parsed.speed_factor,
        }
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
            raise ValueError()
    else:
        raise Exception("Unexpected error processing command line")
    return args
