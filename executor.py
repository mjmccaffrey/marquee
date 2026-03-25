"""Marquee Lighted Sign Project - executor"""

from collections.abc import Callable
import logging
import signal
import time
from typing import Any, Protocol

from color import ColorSets
from devices.buttonset import ButtonSet
from event import Shutdown, SigTerm
from instruments import BellSet, DrumSet
from lightset import ClickSet, LightSet
from modes.basemode import BaseMode
from modes.modes_misc import ModeDefinition
from modes.sequencemode import SequenceMode
from player import Player
from specialparams import SpecialParams

log = logging.getLogger('marquee.' + __name__)


class Executor:
    """Executes patterns and commands specified on the command line.
       If a mode is specified, creates and turns control over 
       to a Player object."""

    def __init__(
            self,
            create_player: Callable[..., Player],
            setup_devices: 'SetupDevices',
        ) -> None:
        """Init the (single) executor."""
        self.create_player = create_player
        self.setup_devices = setup_devices
        self.mode_ids: dict[str, int] = {}
        self.mode_menu: list[tuple[int, str]] = []
        self.modes: dict[int, ModeDefinition] = {}
        self.color_sets = ColorSets('color_sets.json')
        self.commands: dict[str, Callable[[], None]] = {
            'calibrate': self.command_calibrate,
            'off': self.command_off,
        }

    def close(self) -> None:
        """Close dependencies."""
        self.player.close()
        log.info(f"Executor {self} closed. - !!! close devices")

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
        ) -> bool:
        """Effect the command-line specified command, mode or pattern(s).
           Return True if system shutdown requested, else False."""
        shutdown = False
        signal.signal(signal.SIGTERM, self.sigterm_received)
        devices = self.setup_devices(brightness_factor, speed_factor)
        (self.bells, self.buttons, self.drums, 
         self.lights, self.top, self.clicker) = devices
        if command is not None:
            self.execute_command(command)
        elif mode_index is not None:
            try:
                self.execute_mode(mode_index, speed_factor)
            except Shutdown:
                shutdown = True
            except SigTerm:
                pass
        else:
            self.execute_pattern(light_pattern, brightness_pattern)
        return shutdown

    def execute_command(self, command: str):
        """Effects the command-line specified command."""
        self.commands[command]()

    def execute_mode(self, mode_index: int, speed_factor: float) -> None:
        """Effects the command-line specified mode."""
        self.player: Player = self.create_player(
            self.modes, 
            self.mode_ids,
            self.color_sets,
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
            time.sleep(self.lights.trans_min)
        if light_pattern is not None:
            self.lights.set_relays(light_pattern)

    def command_calibrate(self) -> None:
        """Calibrate all light sets supporting it."""
        for lightset in [self.lights, self.top]:
            try:
                lightset.calibrate()
            except NotImplementedError:
                pass

    def command_off(self) -> None:
        """Turn off all relays and potentially other devices."""
        for d in (self.bells, self.drums, self.lights):
            d.relays.set_state_of_devices('0' * d.relays.count)
        log.info("Marquee hardware is now partially shut down.")
        log.info('')

    def sigterm_received(self, signal_number, stack_frame) -> None:
        """Callback for SIGTERM received."""
        log.info(f"SIGTERM received.")
        raise SigTerm


class SetupDevices(Protocol):
    """"""
    def __call__(
        self,
        brightness_factor: float,
        speed_factor: float,
     ) -> tuple[BellSet, ButtonSet, DrumSet, LightSet, LightSet, ClickSet]:
        ...

