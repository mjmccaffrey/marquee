"""Marquee Lighted Sign Project - executor"""

from collections.abc import Callable
import signal
import time

from button import Button
from button_misc import ButtonSet
from instruments import BellSet, DrumSet
from lightset import LightSet
from lightset_misc import ALL_OFF, ALL_ON, EXTRA_COUNT
from modes.modeinterface import ModeInterface
from modes.mode_misc import ModeConstructor
from modes.playsequencemode import PlaySequenceMode
from playerinterface import PlayerInterface
from shelly import ShellyConsolidatedController
from specialparams import SpecialParams


class SigTerm(Exception):
    """Triggered to cleanly exit the application."""


class Executor:
    """Executes patterns and commands specified on the command line.
       If a mode is specified, creates and turns control over 
       to a Player object."""

    def __init__(
            self,
            create_player: Callable[..., PlayerInterface],
            setup_devices: Callable[
                [float], 
                tuple[BellSet, ButtonSet, DrumSet, LightSet]
            ],
        ) -> None:
        """Init the (single) executor."""
        self.create_player = create_player
        self.setup_devices = setup_devices
        self.mode_ids: dict[str, int] = {}
        self.mode_menu: list[tuple[int, str]] = []
        self.modes: dict[int, ModeConstructor] = {}
        self.commands: dict[str, Callable[[], None]] = {
            'calibrate': self.command_calibrate,
            'off': self.command_off,
        }

    def close(self) -> None:
        """Close dependencies."""
        self.player.close()
        print(f"Executor {self} closed. - !!! close devices")

    def add_mode(
            self, 
            name: str,
            cls: type[ModeInterface],
            index: int | None = None,
            hidden: bool = False,
            **kwargs,
    ) -> None:
        """Register the mode IDs and everything needed to create an instance."""
        assert name not in self.mode_ids, "Duplicate mode name"
        if index is None:
            index = max(self.modes) + 1 if self.modes else 0
        if not hidden:
            self.mode_menu.append((index, name))
            self.mode_ids[str(index)] = index
            self.mode_ids[name] = index
        self.modes[index] = ModeConstructor(index, name, cls, kwargs)

    def add_sequence_mode(
            self,
            name: str, 
            sequence: Callable,
            delay: tuple[float, ...] | float | None = None,
            special: SpecialParams | None = None,
            **kwargs,
        ) -> None:
        """Create a Mode object from a sequence and parameters, and register it."""
        self.add_mode(
            name, 
            PlaySequenceMode,
            sequence=sequence,
            delay=delay,
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
        ) -> None:
        """Effects the command-line specified command, mode or pattern(s)."""
        signal.signal(signal.SIGTERM, self.sigterm_received)
        self.bells, self.buttons, self.drums, self.lights = (
            self.setup_devices(brightness_factor)
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

    def execute_mode(self, mode_index: int, speed_factor: float) -> None:
        """Effects the command-line specified mode."""
        self.player: PlayerInterface = self.create_player(
            self.modes, 
            self.mode_ids,
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
    ) -> None:
        """Effects the command-line specified pattern(s)."""
        if brightness_pattern is not None:
            self.lights.set_channels(brightness_pattern)
            Button.wait(self.lights.controller.trans_def)
        if light_pattern is not None:
            self.lights.set_relays(light_pattern)

    def command_calibrate(self) -> None:
        """Execute calibration on each successive channel."""
        assert isinstance(self.lights.controller, ShellyConsolidatedController)
        print("Calibrating channels")
        # Set all light relays on
        self.lights.set_relays(ALL_ON)
        # Set all light channels to high
        self.lights.set_channels(
            brightness=100,
            force_update=True,
        )
        time.sleep(3)
        max_channel = max(
            d.channel_count for d in self.lights.controller.dimmers
        )
        for id in range(max_channel):
            print(f"Calibrating channel {id}")
            for dimmer in self.lights.controller.dimmers:
                if id < dimmer.channel_count:
                    dimmer.channels[id].calibrate()
            time.sleep(150)
        print("Calibration should be complete")

    def command_off(self) -> None:
        """Turn off all relays and potentially other devices."""
        self.lights.set_relays(ALL_OFF, '0' * EXTRA_COUNT)
        print("Marquee hardware is now partially shut down.")
        print()

    def sigterm_received(self, signal_number, stack_frame) -> None:
        """Callback for SIGTERM received."""
        print(f"SIGTERM received.")
        raise SigTerm

