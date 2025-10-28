"""Marquee Lighted Sign Project - executor"""
"""Executes patterns and commands specified on the command line.
    If a mode is specified, creates and turns control over 
    to a Player object."""

from collections.abc import Callable
import signal
import time

from button import Button
from button_misc import ButtonSet
from dimmers import TRANSITION_DEFAULT
from instruments import BellSet, DrumSet
from lightset import LightSet
from lightset_misc import ALL_OFF, ALL_ON, EXTRA_COUNT
from modes.modeinterface import ModeInterface
from modes.mode_misc import ModeConstructor
from modes.playsequencemode import PlaySequenceMode
from playerinterface import PlayerInterface
from specialparams import SpecialParams


class SigTerm(Exception):
    """Triggered to cleanly exit the application."""


create_player: Callable[..., PlayerInterface]
setup_devices: Callable[
    [float], 
    tuple[BellSet, ButtonSet, DrumSet, LightSet]
]
mode_ids: dict[str, int] = {}
mode_menu: list[tuple[int, str]] = []
modes: dict[int, ModeConstructor] = {}
commands: dict[str, Callable[[], None]] = {}

def close() -> None:
    """Close dependencies."""
    print(f"!!!!!! need to close devices")


def add_mode(
    name: str,
    mode_class: type[ModeInterface],
    index: int | None = None,
    hidden: bool = False,
    **kwargs,
) -> None:
    """Register the mode IDs and everything needed to create a mode instance."""
    assert name not in mode_ids, "Duplicate mode name"
    if index is None:
        index = max(modes) + 1 if modes else 0
    if not hidden:
        mode_menu.append((index, name))
        mode_ids[str(index)] = index
        mode_ids[name] = index
    modes[index] = ModeConstructor(name, mode_class, kwargs)


def add_sequence_mode(
        name: str, 
        sequence: Callable,
        delay: tuple[float, ...] | float | None = None,
        special: SpecialParams | None = None,
        **kwargs,
    ) -> None:
    """Create a Mode object from a sequence and parameters, and register it."""
    add_mode(
        name, 
        PlaySequenceMode,
        sequence=sequence,
        delay=delay,
        special=special,
        **kwargs,
    )


def execute_command(command: str):
    """Effects the command-line specified command."""
    commands[command]()


def execute_mode(mode_index: int, speed_factor: float) -> None:
    """Effects the command-line specified mode."""
    player: PlayerInterface = create_player(
        modes, 
        mode_ids,
        bells,
        buttons,
        drums,
        lights,
        speed_factor,
    )
    player.execute(mode_index)


def execute_pattern(
    light_pattern: str | None, 
    brightness_pattern: str | None,
) -> None:
    """Effects the command-line specified pattern(s)."""
    if brightness_pattern is not None:
        lights.set_dimmers(brightness_pattern)
        Button.wait(TRANSITION_DEFAULT)
    if light_pattern is not None:
        lights.set_relays(light_pattern)


def command_calibrate_dimmers() -> None:
    """Execute calibration on all dimmers on each successive channel."""
    print("Calibrating dimmers")
    # Set all light relays on
    lights.set_relays(ALL_ON)
    # Set all light dimmers to high
    for dimmer in lights.dimmers:
        for channel in dimmer.channels:
            channel.set(brightness=100)
    time.sleep(3)
    max_channel = max(d.channel_count for d in lights.dimmers)
    for id in range(max_channel):
        print(f"Calibrating channel {id}")
        for dimmer in lights.dimmers:
            if id < dimmer.channel_count:
                dimmer.channels[id].calibrate()
        time.sleep(150)
    print("Calibration should be complete")


def command_off() -> None:
    """Turn off all relays and potentially other devices."""
    lights.set_relays(ALL_OFF, '0' * EXTRA_COUNT)
    print("Marquee hardware is now partially shut down.")
    print()


def sigterm_received(signal_number, stack_frame) -> None:
    """Callback for SIGTERM received."""
    print(f"SIGTERM received.")
    raise SigTerm


def execute(
        command: str | None = None, 
        mode_index: int | None = None, 
        brightness_factor: float = 1.0,
        speed_factor: float = 1.0,
        light_pattern: str | None = None, 
        brightness_pattern: str | None = None,
    ) -> None:
    """Effects the command-line specified command, mode or pattern(s)."""
    signal.signal(signal.SIGTERM, sigterm_received)
    bells, buttons, drums, lights = (
        setup_devices(brightness_factor)
    )
    if command is not None:
        execute_command(command)
    elif mode_index is not None:
        execute_mode(mode_index, speed_factor)
    else:
        execute_pattern(light_pattern, brightness_pattern)

def init(
    create_player: Callable[..., PlayerInterface],
    setup_devices: Callable[
        [float], 
        tuple[BellSet, ButtonSet, DrumSet, LightSet]
    ],
) -> None:
    """Init the executor."""
    global _create_player, _setup_devices, commands
    _create_player = create_player
    _setup_devices = setup_devices
    commands: dict[str, Callable[[], None]] = {
        'calibrate_dimmers': command_calibrate_dimmers,
        'off': command_off,
    }


