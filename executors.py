"""Marquee Lighted Sign Project - executors"""

from collections.abc import Callable
from signal import SIGUSR1  # type: ignore

from gpiozero import Button as _Button  # type: ignore

from basemode import BaseMode
from buttons import Button
from buttonsets import ButtonSet
from configuration import (
    ALL_RELAYS, ALL_OFF, DIMMER_ADDRESSES, EXTRA_COUNT,
)
from definitions import SpecialParams, ModeConstructor
from dimmers import ShellyDimmer, ShellyProDimmer2PM, TRANSITION_DEFAULT
from instruments import BellSet, DrumSet
from lightsets import LightSet
from modes import PlaySequenceMode
from relays import NumatoRL160001, NumatoSSR80001

def setup_devices(brightness_factor: float):
    """Create and return device objects."""
    bells = BellSet(
        relays = NumatoSSR80001("/dev/ttyACM1")
    )
    drums = DrumSet(
        relays = NumatoRL160001("/dev/ttyACM0")
    )
    lights = LightSet(
        relays = NumatoRL160001("/dev/ttyACM2", ALL_RELAYS),
        dimmers = [
            ShellyProDimmer2PM(i, ip)
            for i, ip in enumerate(DIMMER_ADDRESSES)
        ],
        brightness_factor=brightness_factor,
    )
    buttons = ButtonSet(
        body_back = Button(
            _Button(pin=26, bounce_time=0.10, hold_time=10), 
            support_hold=True,
            signal_number=SIGUSR1,
        ),
        remote_a = Button(_Button(pin=5, pull_up=False, bounce_time=0.10)),
        remote_b = Button(_Button(pin=6, pull_up=False, bounce_time=0.10)),
        remote_c = Button(_Button(pin=13, pull_up=False, bounce_time=0.10)),
        remote_d = Button(_Button(pin=19, pull_up=False, bounce_time=0.10)),
    )
    return bells, buttons, drums, lights

class Executor():
    """Executes patterns and commands specified on the command line.
       If a mode is specified, creates and turns control over 
       to a Player object."""

    def __init__(
            self,
            create_player: Callable,
            setup_devices: Callable,
        ):
        """"""
        self.create_player = create_player
        self.setup_devices = setup_devices
        self.mode_ids: dict[str, int] = {}
        self.mode_menu: list[tuple[int, str]] = []
        self.modes: dict[int, ModeConstructor] = {}
        self.commands: dict[str, Callable] = {
            'calibrate_dimmers': self.command_calibrate_dimmers,
            'off': self.command_off,
        }

    def close(self):
        """Close dependencies."""
        self.player.close()
        # !!! close devices

    def command_calibrate_dimmers(self):
        """Calibrate dimmers."""
        ShellyDimmer.calibrate_all()

    def command_off(self):
        """Turn off all relays and potentially other devices."""
        self.lights.set_relays(ALL_OFF, '0' * EXTRA_COUNT)
        print("Marquee hardware is now partially shut down.")
        print()

    def add_mode(
            self, 
            name: str,
            mode_class: type[BaseMode],
            hidden: bool = False,
            **kwargs,
    ):
        """Register the mode IDs and everything needed to create an instance."""
        assert name not in self.mode_ids, "Duplicate mode name"
        index = len(self.modes)
        if not hidden:
            self.mode_menu.append((index, name))
            self.mode_ids[str(index)] = index
            self.mode_ids[name] = index
        self.modes[index] = ModeConstructor(name, mode_class, kwargs)

    def add_sequence_mode(
            self,
            name: str, 
            sequence: Callable,
            pace: tuple[float, ...] | float | None = None,
            special: SpecialParams | None = None,
            **kwargs,
        ):
        """Create a Mode object from a sequence and parameters, and register it."""
        self.add_mode(
            name, 
            PlaySequenceMode,
            sequence=sequence,
            pace=pace,
            special=special,
            **kwargs,
        )

    def execute(
            self, 
            command: str | None = None, 
            mode_index: int | None = None, 
            brightness_factor: float = 1.0,
            speed_factor: float = 1.0,
            light_pattern: str | None = None, 
            brightness_pattern: str | None = None,
        ):
        """Effects the command-line specified command, mode or pattern(s)."""
        self.bells, self.buttons, self.drums, self.lights = (
            setup_devices(brightness_factor)
        )
        if command is not None:
            self.execute_command(command)
        elif mode_index is not None:
            self.execute_mode(mode_index, speed_factor)
        else:
            self.execute_pattern(light_pattern, brightness_pattern)

    def execute_command(self, command: str):
        """Effects the command-line specified command."""
        self.commands[command]()

    def execute_mode(self, mode_index: int, speed_factor: float):
        """Effects the command-line specified mode."""
        self.player = self.create_player(
            self.modes, 
            self.bells,
            self.buttons,
            self.drums,
            self.lights,
            speed_factor,
        )
        self.player.execute(mode_index)

    def execute_pattern(
        self, 
        light_pattern: str | None, 
        brightness_pattern: str | None,
    ):
        """Effects the command-line specified pattern(s)."""
        if brightness_pattern is not None:
            self.lights.set_dimmers(brightness_pattern)
            Button.wait(TRANSITION_DEFAULT)
        if light_pattern is not None:
            self.lights.set_relays(light_pattern)
