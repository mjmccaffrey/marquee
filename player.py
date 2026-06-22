"""Marquee Lighted Sign Project - player"""

from dataclasses import dataclass, field
import logging
import signal
from typing import Any, cast, NoReturn
from typing_extensions import override

from devices.color import ColorSets
from devices.deviceset import DeviceSet
from devices.devices_misc import (
    ButtonAction, ButtonActionException, ButtonName,
)
from event import EventSystem
from modes.abstract.backgroundmode import BackgroundMode
from modes.abstract.foregroundmode import ForegroundMode
from modes import ChangeMode, ModeDefinition
from task import TaskSchedule

log = logging.getLogger('marquee.' + __name__)


@dataclass
class Player:
    """Executes one mode at a time. Contains the task queue."""
    modes: dict[int, ModeDefinition]
    mode_ids: dict[str, int]
    color_sets: ColorSets
    devices: DeviceSet
    speed_factor: float
    pace: float = field(init=False)
    bg_mode_instances: dict = field(init=False)
    events: EventSystem = field(init=False)
    tasks: TaskSchedule = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        log.info("Initializing player")
        self.active_mode: BackgroundMode | ForegroundMode | None = None
        self.live_bg_modes: dict[int, BackgroundMode] = {}
        signal.signal(signal.SIGTERM, self.sigterm_received)
        self.events = EventSystem()
        self.tasks = TaskSchedule()

    @override
    def __repr__(self) -> str:
        return f"<{self}>"
    
    @override
    def __str__(self) -> str:
        return "Player"

    def close(self) -> None:
        """Clean up."""
        log.info(f"Player {self} closed.")

    def sigterm_received(self, signal_number, stack_frame) -> None:
        """Callback for SIGTERM received."""
        log.info(f"SIGTERM received.")
        raise SigTerm

    def create_mode_instance(
        self, 
        mode_index: int | None = None,
        mode_definition: ModeDefinition | None = None,
        kwargs: dict[str, Any] = {},
        parent: BackgroundMode | ForegroundMode | None = None,
    ) -> BackgroundMode | ForegroundMode:
        """Return a new mode instance."""
        assert (mode_index is None) ^ (mode_definition is None)
        definition = mode_definition or self.modes[cast(int, mode_index)]
        _kwargs: dict[str, Any] = dict(
            index=definition.index,
            name=definition.name, 
            speed_factor=self.speed_factor,
            create_mode_instance=self.create_mode_instance,
            replace_kwarg_values=self.replace_kwarg_values,
            events=self.events,
            tasks=self.tasks,
            modes=self.modes,
            mode_ids=self.mode_ids,
            color_sets=self.color_sets,
            parent=parent,
        )
        _kwargs |= (
            self.replace_kwarg_values(definition.kwargs) | kwargs
        )
        if issubclass(definition.cls, ForegroundMode):
            _kwargs |= dict(
                devices=self.devices,
                speed_factor=self.speed_factor,
            )
        return definition.cls(**_kwargs)

    def effect_new_active_mode(
        self, 
        mode_index: int,
    ) -> BackgroundMode | ForegroundMode:
        """Create new mode instance, clean up old, etc."""

        # If there is an active mode and it is of type ForegroundMode, 
        # clean it up.
        # Note: After startup, there is always an active mode.
        if isinstance(self.active_mode, ForegroundMode):
            self.tasks.delete_owned_by(self.active_mode)

        # Create new mode instance
        new_mode = self.create_mode_instance(mode_index)
        assert isinstance(new_mode, BackgroundMode | ForegroundMode)

        # Note: A background mode will upon instantiation  
        #       be the active mode, for a very short time.
        if isinstance(new_mode, BackgroundMode):
            # If bg mode of same type already present, clean it up.
            if (conflict := self.live_bg_modes.pop(new_mode.index, None)):
                print(f'Deleting background mode {new_mode.name}')
                self.tasks.delete_owned_by(conflict)
            # Add new bg mode to bg mode list
            print(f'Adding background mode {new_mode.name}')
            self.live_bg_modes[new_mode.index] = new_mode

        # Return new mode instance
        return new_mode

    def execute(self, starting_mode_index: int) -> bool:
        """Play the specified starting mode and all subsequent modes.
           Return whether to shut down the system, or just exit."""
        new_mode_index: int | None = starting_mode_index
        while True:
            try:
                if new_mode_index is not None:
                    self.active_mode = self.effect_new_active_mode(new_mode_index)
                    new_mode_index = None
                    log.info(f"Executing mode {self.active_mode}")
                    self.active_mode.execute()
                self.wait()
            except ButtonActionException as press:
                if press.action == ButtonAction.HELD:
                    return True
                self.devices.buttons.reset()
                assert self.active_mode is not None
                print(f"Button {press.button} {press.action} in mode {self.active_mode}")
                log.debug(f"Button {press.button} {press.action} in mode {self.active_mode}")
                new_mode_index = self.notify_button_action(press.button)
            except ChangeMode as cm:
                log.debug("ChangeMode caught")
                new_mode_index, = cm.args
            except SigTerm:
                return False

    def notify_button_action(self, button: ButtonName) -> int | None:
        """Notify all background modes, and active mode, 
           of button action. Return active mode's response."""
        for mode in self.live_bg_modes.values():
            mode.button_action(button)
        return (
            self.active_mode.button_action(button)
            if isinstance(self.active_mode, ForegroundMode) else
            None
        )

    def replace_kwarg_values(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Replace variables with current runtime values."""
        vars: dict[str, Any] = {
            'LIGHT_PATTERN': self.devices.lights.relay_pattern,
        }
        if self.active_mode is not None:
            vars['PREVIOUS_MODE'] = self.active_mode.index
        return {
            k: vars[v] if isinstance(v, str) and v in vars else v
            for k, v in kwargs.items()
        }

    def wait(
        self, 
        seconds: float | None = None, 
    ) -> None | NoReturn:
        """Wait seconds, adjusted for speed_factor.
           If seconds is None, wait indefinitely (in this case,
           the current mode instance will never be returned to).
           While waiting, execute any tasks that come due; 
           any button press will terminate waiting."""

        if seconds is not None:
            seconds *= self.speed_factor
        self.tasks.wait(seconds, self.devices.buttons.wait)


class SigTerm(Exception):
    """Triggered to cleanly exit the application."""

