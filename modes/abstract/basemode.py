"""Marquee Lighted Sign Project - basemode"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import logging
import sys
import time
from typing import Any, NoReturn, Protocol, Self
from typing_extensions import override

from devices.color import ColorSets
from devices.devices_misc import ButtonName
from event import EventSystem
from task import SeqTask, Task, TaskSchedule
from ..structural.modes_misc import ChangeMode, ModeDefinition

log = logging.getLogger('marquee.' + __name__)


@dataclass()
class BaseMode(ABC):
    """Base for (foreground and background) modes."""
    index: int
    name: str
    serial: int
    speed_factor: float
    create_mode_instance: 'CreateModeInstance'
    delete_mode_instance: 'DeleteModeInstance'
    replace_kwarg_values: 'ReplaceKwargValues'
    events: EventSystem
    tasks: TaskSchedule
    modes: dict[int, ModeDefinition]
    mode_ids: dict[str, int]
    color_sets: ColorSets
    parent: Self | None = None

    @abstractmethod
    def button_action(self, button: ButtonName) -> int | None:
        """Respond to button being pressed.
           Return index of new mode, if any."""

    def execute(self) -> None:
        """Play the mode."""
        raise RuntimeError("Method must be overridden.")

    @override
    def __repr__(self) -> str:
        return f"<{self}>"
    
    @override
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
        action: Callable | None = None,  # .execute
        due: float = 0.0,
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

    def schedule_sequence(self, *tasks: SeqTask, delay=0.0) -> None:
        """Schedule sequential tasks with an initial seconds delay, 
           and due seconds before each task."""
        for task in tasks:
            delay += task.due
            self.schedule(
                due=delay,
                action=task.action,
                name=task.name,
            )

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

class CreateModeInstance(Protocol):
    """"""
    def __call__(
        self,
        mode_index: int | None = None,
        mode_definition: ModeDefinition | None = None,
        kwargs: dict[str, Any] = {},
        parent: BaseMode | None = None,  # !!! BaseMode
    ) -> BaseMode:  # !!! BackgroundMode | Mode:
        ...

class DeleteModeInstance(Protocol):
    """"""
    def __call__(
        self,
        mode_index: int | None = None,
    ) -> None:
        ...

class ReplaceKwargValues(Protocol):
    """"""
    def __call__(
        self, 
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        ...

