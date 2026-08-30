"""Marquee Lighted Sign Project - player"""

from contextlib import suppress
from dataclasses import dataclass, field
from itertools import count
import logging
import signal
from typing import Any, cast, NoReturn
from typing_extensions import override

from devices.color import ColorSets
from devices.device_schemas import (
    ControlAction, ControlActionException, ControlName,
    DeviceName, DeviceSet,
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
        self.mode_instances: dict[int, Mode] = {}
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
        """Return a new mode instance.
           Does not update self.mode_instances."""
        assert (mode_index is None) ^ (mode_definition is None)
        definition = mode_definition or self.modes[cast(int, mode_index)]
        _kwargs: dict[str, Any] = dict(
            index=definition.index,
            name=definition.name, 
            serial=next(self.mode_serial),
            speed_factor=self.speed_factor,
            create_mode_instance=self.create_mode_instance,
            delete_mode_instance=self.delete_mode_instance,
            events=self.events,
            tasks=self.tasks,
            modes=self.modes,
            mode_ids=self.mode_ids,
            color_sets=self.color_sets,
            parent=parent,
        )
        if issubclass(definition.cls, Mode):
            _kwargs |= dict(
                devices=self.devices,
                speed_factor=self.speed_factor,
            )
        return definition.cls(**_kwargs)

    def delete_mode_instance(self, mode_index: int) -> None:
        """Delete the instance of mode_index, along
           with any mode instances with instance as parent."""
        mode = self.mode_instances[mode_index]
        # Delete children of specified.
        for instance in self.mode_instances.values():
            if instance.parent == mode:
                self.delete_mode_instance(instance.index)
        # Delete specified.
        print(f'Deleting mode {mode.name} with parent {mode.parent}')
        mode.close()
        del self.mode_instances[mode_index]
        self.tasks.delete_owned_by(mode)

    def effect_new_mode(self, mode_index: int):
        """Create new mode instance, clean up old, etc."""
        print("EFFECTING", mode_index)
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
        print(f'Effected new mode instance {new_mode.name.upper()}')
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
            except ControlActionException as act:
                with suppress(ControlActionException):
                    if act.action == ControlAction.BUTTON_HELD:
                        return True
                    self.devices[DeviceName.CONTROLS].reset()
                    log.info(f"Button {act.control} {act.action}")
                    new_mode_index = self.notify_control_action(act.control)
            except ChangeMode as cm:
                log.debug("ChangeMode caught")
                new_mode_index, = cm.args
            except SigTerm:
                return False

    def notify_control_action(self, control: ControlName) -> int | None:
        """Notify all background modes, and active mode, 
           of control action. Return FG active mode's response."""
        for mode in self.mode_instances.values():
            if mode.background:
                mode.control_action(control)
        fg_mode = self.foreground_mode_instance()
        if fg_mode is not None:
            return mode.control_action(control)

    def wait(
        self, 
        seconds: float | None = None, 
    ) -> None | NoReturn:
        """Wait seconds, adjusted for speed_factor.
           If seconds is None, wait indefinitely (in this case,
           the current mode instance will never be returned to).
           While waiting, execute any tasks that come due; 
           any control activity will terminate waiting."""

        if seconds is not None:
            seconds *= self.speed_factor
        self.tasks.wait(seconds, self.devices[DeviceName.CONTROLS].wait)


class SigTerm(Exception):
    """Triggered to cleanly exit the application."""

