"""Marquee Lighted Sign Project - executor"""

from collections.abc import Callable
import signal
import time
from typing import Any

from devices.button import Button
from devices.devices_misc import SetupDevices
from lightset_misc import ALL_ON
from modes.basemode import BaseMode
from modes.mode_misc import ModeDefinition
from modes.sequencemode import SequenceMode
from player import Player
from devices.shelly import ShellyConsolidatedController
from specialparams import SpecialParams


class SigTerm(Exception):
    """Triggered to cleanly exit the application."""


class Executor:
    """Executes patterns and commands specified on the command line.
       If a mode is specified, creates and turns control over 
       to a Player object."""

    def __init__(
            self,
            create_player: Callable[..., Player],
            setup_devices: SetupDevices,
        ) -> None:
        """Init the (single) executor."""
        self.create_player = create_player
        self.setup_devices = setup_devices
        self.mode_ids: dict[str, int] = {}
        self.mode_menu: list[tuple[int, str]] = []
        self.modes: dict[int, ModeDefinition] = {}
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
            cls: type[BaseMode],
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
        self.modes[index] = ModeDefinition(index, name, cls, kwargs)

    def add_sequence_mode(
            self,
            name: str, 
            sequence: Callable,
            sequence_kwargs: dict[str, Any] = {},
            delay: tuple[float, ...] | float | None = None,
            index: int | None = None,
            hidden: bool = False,
            special: SpecialParams | None = None,
            **kwargs,
        ) -> None:
        """Create a Mode object from a sequence and parameters, and register it."""
        self.add_mode(
            name=name, 
            cls=SequenceMode,
            index=index,
            hidden=hidden,
            sequence=sequence,
            sequence_kwargs=sequence_kwargs,
            delay=delay,
            special=special,
            **kwargs,
        )

    def execute(
            self, 
            brightness_factor: float = 1.0,  # Must default; only
            speed_factor: float = 1.0,       # provided with mode.
            command: str | None = None, 
            mode_index: int | None = None, 
            light_pattern: str | None = None, 
            brightness_pattern: str | None = None,
        ) -> None:
        """Effects the command-line specified command, mode or pattern(s)."""
        signal.signal(signal.SIGTERM, self.sigterm_received)
        devices = self.setup_devices(brightness_factor, speed_factor)
        (self.bells, self.buttons, self.drums, 
         self.lights, self.top, self.clicker) = devices
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
        self.player: Player = self.create_player(
            self.modes, 
            self.mode_ids,
            self.bells,
            self.buttons,
            self.drums,
            self.lights,
            self.top,
            self.clicker,
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
            self.lights.set_channels(
                brightness=brightness_pattern,
                transition=self.lights.trans_min,
            )
            Button.wait(self.lights.trans_min)
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
            force=True,
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
        for d in (self.bells, self.drums, self.lights):
            d.relays.set_state_of_devices('0' * d.relays.count)
        print("Marquee hardware is now partially shut down.")
        print()

    def sigterm_received(self, signal_number, stack_frame) -> None:
        """Callback for SIGTERM received."""
        print(f"SIGTERM received.")
        raise SigTerm

