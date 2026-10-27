"""Marquee Lighted Sign Project - argument"""

from argparse import (
    Action, ArgumentParser, ArgumentError, ArgumentTypeError, 
    Namespace, _SubParsersAction
)
from collections.abc import Callable
from itertools import groupby
from functools import partial
from typing import Any, NoReturn
from typing_extensions import override

from schemas import LightConfig
from systems import SystemName


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

    @override
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
    
    @override
    def error(self, message) -> NoReturn:
        """ Do not exit when certain errors occur. """
        raise ValueError(f"Argparse error:{message}")

    @override
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


def str_to_system_name(arg: str) -> SystemName:
    """Validates and converts a system name."""
    try:
        return SystemName(arg.lower())
    except ValueError:
        raise ValueError()


def display_help(
    mode_menu: list[tuple[int, str]], 
    color_menu: list[tuple[str, int, str]],
    commands: dict[str, Callable],
) -> None:
    """"Display the command-line syntax."""
    print("")
    print("Usage:")
    print("   marquee.py ")
    print("      [--system={system_name}]")
    print("      [--testing={true | false}]")
    print("      mode {mode_index} | {mode_name}")
    print("          [--brightness_factor={[0 - 1.0]}]")
    print("          [--speed_factor={(0 - 5.0]}]")
    print("      pattern --dimmer={pattern} &| --relay={pattern}")
    print("          [--derive_missing={true | false}]")
    print("      color {set_index} | {set_name}")
    print("      command {command_name}")
    print("")
    # print("System: Defaults to marquee. Determines which {system}_devices file is used.")
    print("Systems:")
    for system_name in SystemName:
        print(f'   {system_name.value}')
    # print("Testing: Defaults to false. Determines whether mocks are used in {system}_devices.")
    # print("")
    print("")
    print("Modes:")
    for index, name in mode_menu:
        print(f'   {index:>2}   {name}')
    print("")
    print("Patterns: Specify --dimmer, --relay, or both.")
    print(f"   dimmer: <light_count> hex values, each 0..A (0%..100%)")
    print(f"   relay: <light_count> binary values")
    print("   derive_missing:")
    print("      If true (default) and only one pattern is specified,")
    print("      the missing pattern will be assumed.")
    print("      If false, the state of the device set without a pattern")
    print("      will not be initialized at startup.")
    print("")
    print("Colors:")
    for group_name, sets in groupby(color_menu, lambda e: e[0]):
        print(f'   {group_name}')
        for _, index, set_name in sets:
            print(f'     {index:>3}   {set_name}')
    print("")
    print("Commands:")
    for command in commands:
        print(f'   {command}')
    print("")


def validate_brightness_factor(arg: str) -> float:
    """ Return arg as float if it is a valid brightness factor,
        otherwise raise exception. """
    try:
        value = float(arg)
        if not 0.0 <= value <= 1.0:
            raise ValueError
    except ValueError:
        raise ValueError(f"Invalid brightness factor: {arg}")
    else:
        return value


def validate_speed_factor(arg: str) -> float:
    """ Return arg as float if it is a valid speed factor,
        otherwise raise exception. """
    try:
        value = float(arg)
        if not 0.0 < value <= 5.0:
            raise ValueError
    except ValueError:
        raise ValueError(f"Invalid speed factor: {arg}")
    else:
        return value
    

def validate_light_pattern(arg: str) -> str:
    """ Return arg if it is a valid light pattern, 
        otherwise raise exception. """
    if not (
        # len(arg) == light_config.count and 
        all(e in {"0", "1"} for e in arg)
    ): 
        raise ValueError(f"Invalid light pattern: {arg}")
    return arg


def validate_brightness_pattern(arg: str) -> str:
    """ Return normalized arg if it is a valid brightness pattern, 
        otherwise raise exception. """
    arg_normalized = arg.upper()
    if not (
        # len(arg_normalized) == light_config.count and 
        all(e in "0123456789AF" for e in arg_normalized)
    ): 
        raise ValueError(f"Invalid brightness pattern: {arg}")
    return arg_normalized


def add_color_operation(sub_p: _SubParsersAction, choices: list[str]):
    """Define color operation."""
    color_p = sub_p.add_parser('color')
    color_p.add_argument('color_id', choices=choices)
    color_p.add_argument(
        'brightness', 
        optional=True, 
        type=int,
        choices=range(0, 101),
        default=100,
    )


def add_command_operation(sub_p: _SubParsersAction, choices: list[str]):
    """Define command operation."""
    command_p = sub_p.add_parser('command')
    command_p.add_argument('command_name', choices=choices)


def add_mode_operation(sub_p: _SubParsersAction, choices: list[str]):
    """Define mode operation."""
    mode_p = sub_p.add_parser('mode')
    mode_p.add_argument('mode_id', choices=choices)
    mode_p.add_argument(
        'brightness_factor', 
        optional=True, 
        type=validate_brightness_factor,
        default=1.0,
    )
    mode_p.add_argument(
        'speed_factor', 
        optional=True, 
        type=validate_speed_factor, 
        default=1.0,
    )


def add_pattern_operation(sub_p: _SubParsersAction):
    """Define pattern operation."""
    pattern_p = sub_p.add_parser('pattern')
    pattern_p.add_argument(
        'relay', 
        optional=True, 
        type=validate_light_pattern,
    )
    pattern_p.add_argument(
        'dimmer', 
        optional=True, 
        type=validate_brightness_pattern,
    )
    pattern_p.add_argument(
        'derive_missing', 
        optional=True, 
        # dest='derive_missing', 
        type=str_to_bool, 
        default=True,
    )


def parse_arguments(
    mode_ids: dict[str, int], 
    color_ids: dict[str, str],
    commands: dict[str, Callable],
) -> Namespace:
    """ Parse the command-line arguments. """
    top_p = ArgumentParserImproved(exit_on_error=False)
    top_p.add_argument(
        'system',
        optional=True,
        dest='system_name',
        type=str_to_system_name,
        default=SystemName.MARQUEE,
    )
    top_p.add_argument(
        'testing', 
        optional=True, 
        type=str_to_bool, 
        default=False,
    )
    #
    sub_p = top_p.add_subparsers(dest='operation', required=True)
    add_color_operation(sub_p, list(color_ids.keys()))
    add_command_operation(sub_p, list(commands.keys()))
    add_mode_operation(sub_p, list(mode_ids.keys()))
    add_pattern_operation(sub_p)
    #
    try:
        return top_p.parse_args()
    except (ArgumentError, ArgumentTypeError, ValueError) as err:
        raise ValueError()


def process_arguments(
    mode_ids: dict[str, int], 
    color_ids: dict[str, str],
    commands: dict[str, Callable],
) -> dict[str, Any]:
    """Validate and interpret the runtime arguments.
       Return dict of parameters if the arguments are valid, 
       otherwise raise an error."""
    try:
        parsed = parse_arguments(mode_ids, color_ids, commands)
    except ValueError as err:
        raise
    args = {
        "system_name": parsed.system_name,
        "testing": parsed.testing,
    }
    match parsed.operation:
        case 'color':
            args |= {
                "color": color_ids[parsed.color_id],
                "brightness": parsed.brightness,
            }
        case 'command':
            args |= {"command": parsed.command_name}
        case 'mode':
            args |= {
                "mode_index": mode_ids[parsed.mode_id],
                "brightness_factor": parsed.brightness_factor,
                "speed_factor": parsed.speed_factor,
            }
        case 'pattern':
            args |= {}
            if parsed.relay:
                args |= {"light_pattern": parsed.relay}
            if parsed.dimmer:
                args |= {"brightness_pattern": parsed.dimmer}
            if parsed.relay:
                if not parsed.dimmer and parsed.derive_missing:
                    pattern = ''.join(
                        'A' if e == '1' else '0' 
                        for e in parsed.relay
                    )
                    args |= {"brightness_pattern": pattern}
            elif parsed.dimmer:
                if parsed.derive_missing:
                    pattern = ''.join(
                        '0' if e == '0' else "1"
                        for e in parsed.dimmer
                    )
                    args |= {"light_pattern": pattern}
            else:
                raise ValueError()
        case _:
            raise Exception("Unexpected error processing command line")
    return args

