"""Marquee Lighted Sign Project - basemode"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import logging
import sys
import time
from typing import Any, NoReturn, Self

from devices.color import ColorSets
from devices.devices_misc import ButtonRef
from event import EventSystem
from task import Task, TaskSchedule
from .modes_misc import (
    ChangeMode, CreateModeInstance, ModeDefinition, ReplaceKwargValues,
)

log = logging.getLogger('marquee.' + __name__)


@dataclass()
class BaseMode(ABC):
    """Base for both foreground and background modes."""
    index: int
    name: str
    speed_factor: float
    create_mode_instance: CreateModeInstance
    replace_kwarg_values: ReplaceKwargValues
    events: EventSystem
    tasks: TaskSchedule
    modes: dict[int, ModeDefinition]
    mode_ids: dict[str, int]
    color_sets: ColorSets
    parent: Self | None = None

    @abstractmethod
    def button_action(self, button: ButtonRef) -> int | None:
        """Respond to button being pressed.
           Return index of new mode, if any."""

    @abstractmethod
    def execute(self) -> None:
        """Play the mode."""

    def interrupt_action(self, args: tuple[Any, ...]) -> None:
        """Respond to mode interrupt exception."""
        raise RuntimeError("Method must be overridden.")

    def __repr__(self) -> str:
        return f"<{self}>"
    
    def __str__(self) -> str:
        return f"Mode {self.index} {self.name}"

    def change_mode(self, mode_index: int) -> NoReturn:
        """Effects changing active mode to mode_index."""
        log.info(f"Changing to mode {mode_index}")
        raise ChangeMode(mode_index)

    def lookup_mode_index(self, name: str) -> int:
        """Return the index for the mode with name."""
        try:
            return self.mode_ids[name]
        except LookupError:
            raise ValueError(f"Mode {name} not defined.")

    def schedule(
        self, 
        due: float,
        action: Callable | None = None, 
        name: str | None = None,
        repeat: bool = False,
    ) -> None:
        """Schedule a new task for now + due.
           Adjust due by speed_factor.
           If repeat, schedule next task before calling action."""

        def push_event():
            """Push task onto queue."""
            assert _action is not None
            self.tasks.push(
                Task(
                    action=_action,
                    due=_due,
                    owner=_owner,
                    name=_name,
                )
            )

        def repeater():
            """Schedule next task. Call action."""
            nonlocal _due
            _due += due
            push_event()
            assert action is not None
            action()

        due = due * self.speed_factor
        _due = time.time() + due
        if action is None:
            action = getattr(self, 'execute')
        _action = repeater if repeat else action
        _owner = self.parent or self
        if name is None:
            caller = sys._getframe(1)
            _name = (
                type(caller.f_locals['self']).__name__ + "." + 
                caller.f_code.co_name
            )
        else:
            _name = name
        push_event()

    @staticmethod
    def wrap_value(
        lower: int,
        upper: int, 
        current: int, 
        delta: int,
    ) -> int:
        """Return current + delta, wrapping the value
           within the inclusive range lower..upper."""
        value = current + delta % (upper - lower + 1)
        if (dif := value - upper) > 0:
            value = lower + dif - 1
        elif (dif := value - lower) < 0:
            value = upper + dif + 1
        return value

