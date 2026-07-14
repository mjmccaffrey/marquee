"""Marquee Lighted Sign Project - player"""

from contextlib import suppress
from dataclasses import dataclass, field
from itertools import count
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
from modes.abstract.mode import Mode
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
    events: EventSystem = field(init=False)
    tasks: TaskSchedule = field(init=False)

    def __post_init__(self) -> None:
        """Initialize."""
        log.info("Initializing player")
        self.mode_instances: dict[int, Mode] = {}  # Not children.
        self.mode_serial = count()
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
        log.info(f"Player closed.")

    def sigterm_received(self, signal_number, stack_frame) -> None:
        """Callback for SIGTERM received."""
        log.info(f"SIGTERM received.")
        raise SigTerm

    def foreground_mode_instance(self) -> Mode | None:
        """"""
        fg_iter = (m for m in self.mode_instances.values() if not m.background)
        return next(fg_iter, None)

    def create_mode_instance(
        self, 
        mode_index: int | None = None,
        mode_definition: ModeDefinition | None = None,
        kwargs: dict[str, Any] = {},
        parent: Mode | None = None,
    ) -> Mode:
        """Return a new mode instance."""
        assert (mode_index is None) ^ (mode_definition is None)
        definition = mode_definition or self.modes[cast(int, mode_index)]
        _kwargs: dict[str, Any] = dict(
            index=definition.index,
            name=definition.name, 
            serial=next(self.mode_serial),
            speed_factor=self.speed_factor,
            create_mode_instance=self.create_mode_instance,
            delete_mode_instance=self.delete_mode_instance,
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
        if issubclass(definition.cls, Mode):
            _kwargs |= dict(
                devices=self.devices,
                speed_factor=self.speed_factor,
            )
        return definition.cls(**_kwargs)

    def delete_mode_instance(self, mode_index: int) -> None:
        """"""
        mode = self.mode_instances[mode_index]
        print(f'Deleting mode {mode.name}')
        del self.mode_instances[mode_index]
        self.tasks.delete_owned_by(mode)

    def effect_new_mode(self, mode_index: int):
        """Create new mode instance, clean up old, etc."""
        # Create new mode instance
        new_mode = self.create_mode_instance(mode_index)
        if new_mode.background:
            # If bg mode of same type already present, delete it.
            if new_mode.index in self.mode_instances:
                self.delete_mode_instance(new_mode.index)
        else:
            # If any fg mode already present, delete it.
            fg_mode = self.foreground_mode_instance()
            if fg_mode is not None:
                self.delete_mode_instance(fg_mode.index)
        self.mode_instances[new_mode.index] = new_mode
        print(f'Effected new mode instance {new_mode.name}')
        if not new_mode.background:
            new_mode.execute()

    def execute(self, starting_mode_index: int) -> bool:
        """Play the specified starting mode and all subsequent modes.
           Return whether to shut down the system, or just exit."""
        new_mode_index: int | None = starting_mode_index
        while True:
            try:
                if new_mode_index is not None:
                    self.effect_new_mode(new_mode_index)
                    new_mode_index = None
                self.wait()
            except ButtonActionException as press:
                with suppress(ButtonActionException):
                    if press.action == ButtonAction.HELD:
                        return True
                    self.devices.buttons.reset()
                    log.info(f"Button {press.button} {press.action}")
                    new_mode_index = self.notify_button_action(press.button)
            except ChangeMode as cm:
                log.debug("ChangeMode caught")
                new_mode_index, = cm.args
            except SigTerm:
                return False

    def notify_button_action(self, button: ButtonName) -> int | None:
        """Notify all background modes, and active mode, 
           of button action. Return FG active mode's response."""
        for mode in self.mode_instances.values():
            if mode.background:
                mode.button_action(button)
        fg_mode = self.foreground_mode_instance()
        if fg_mode is not None:
            return mode.button_action(button)

    def replace_kwarg_values(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Replace variables with current runtime values."""
        vars: dict[str, Any] = {
            'LIGHT_PATTERN': self.devices.lights.relay_pattern,
        }
        fg_mode = self.foreground_mode_instance()
        if fg_mode is not None:
            vars['PREVIOUS_MODE'] = fg_mode.index
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

