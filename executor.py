"""Marquee Lighted Sign Project - executor"""

from collections.abc import Callable
import logging
import time
from typing import Any, cast, Protocol

from devices.color import ColorSets
from devices.device_schemas import DeviceName, DeviceSet
from devices.specialparams import SpecialParams
from instruments import LightSet, RelayInstrument
from modes import BaseMode, ModeDefinition, SequenceMode
from player import Player

log = logging.getLogger('marquee.' + __name__)


class Executor:
    """Executes patterns, colors and commands specified on the command line.
       If a mode is specified, creates and turns control over 
       to a Player object."""

    def __init__(
        self,
        create_player: Callable[..., Player],
        define_devices: 'SetupDevices',
    ) -> None:
        """Init the (single) executor."""
        self.create_player = create_player
        self.define_devices = define_devices
        #
        self.mode_ids: dict[str, int] = {}
        self.mode_menu: list[tuple[int, str]] = []
        self.modes: dict[int, ModeDefinition] = {}
        #
        self._load_color_set_names()
        self.commands: dict[str, Callable[[], None]] = {
            'calibrate': self.command_calibrate,
            'off': self.command_off,
        }

    def _load_color_set_names(self) -> None:
        """Load color set identifiers.
           Discard the actual colors. Kludge."""
        color_sets = ColorSets()
        self.color_ids: dict[str, str] = {
            e: sn
            for i, (gn, sn) in enumerate(color_sets.each_set_name())
            for e in (str(i), sn)
        }
        self.color_menu: list[tuple[str, int, str]] = [
            (gn, i, sn)
            for i, (gn, sn) in enumerate(color_sets.each_set_name())
        ]

    def close(self) -> None:
        """Close dependencies."""
        self.player.close()
        log.info(f"Executor closed.")

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
        self.modes[index] = ModeDefinition(
            index=index, name=name, cls=cls, kwargs=kwargs,
        )

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
        color: str | None = None, 
        brightness: int | None = None,
        command: str | None = None, 
        mode_index: int | None = None, 
        light_pattern: str | None = None, 
        brightness_pattern: str | None = None,
    ) -> bool:
        """Effect the command-line specified command, mode or pattern(s).
           Return True if system shutdown requested, else False."""
        shutdown = False
        self.devices = self.define_devices(brightness_factor, speed_factor)
        self.lights = cast(LightSet, self.devices[DeviceName.LIGHTS])
        if color is not None:
            assert brightness is not None
            self.execute_color(color, brightness)
        if command is not None:
            self.execute_command(command)
        elif mode_index is not None:
            shutdown = self.execute_mode(mode_index, speed_factor)
        else:
            self.execute_pattern(light_pattern, brightness_pattern)
        return shutdown

    def execute_color(self, color: str, brightness: int) -> None:
        """Executes color operation."""
        cs = cast(
            LightSet, self.devices[DeviceName.LIGHTS]
        ).color_sets.by_set_name[color]
        kwargs = cs.set_channels_kwargs(self.lights.count)
        kwargs |= dict(
            on=True,
            brightness=brightness,
        )
        self.devices.lights.set_channels(**kwargs)  # type: ignore

    def execute_command(self, command: str) -> None:
        """Executes command operation."""
        self.commands[command]()

    def execute_mode(self, mode_index: int, speed_factor: float) -> bool:
        """Launches Player with the command-line specified mode.
           Returns the Player's exit / shutdown return value."""
        self.player: Player = self.create_player(
            devices=self.devices,
            mode_ids=self.mode_ids,
            modes=self.modes, 
            speed_factor=speed_factor,
        )
        return self.player.execute(mode_index)

    def execute_pattern(
        self, 
        light_pattern: str | None, 
        brightness_pattern: str | None,
    ) -> None:
        """Executes the pattern operation."""
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
        for lightset in [self.lights]:
            if lightset is not None:
                try:
                    lightset.calibrate()
                except NotImplementedError:
                    pass
    def command_off(self) -> None:
        """Turn off all relays and potentially other devices."""
        for dn in (
            DeviceName.BELLS, DeviceName.DRUMS, DeviceName.LIGHTS,
        ):
            device = cast(RelayInstrument | None, self.devices.get(dn))
            if device is not None and device.relays is not None:
                device.relays.set_state_of_devices('0' * device.relays.count)
        log.info("Marquee hardware is now partially powered off.")
        log.info('')


class SetupDevices(Protocol):
    """Call signature to return the device set."""
    def __call__(
        self,
        brightness_factor: float,
        speed_factor: float,
    ) -> DeviceSet:
        ...

