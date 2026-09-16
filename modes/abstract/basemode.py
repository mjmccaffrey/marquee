"""Marquee Lighted Sign Project - basemode"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
import logging
import sys
import time
from typing import NoReturn, Self
from typing_extensions import override

from schemas import ChangeModeInterrupt, DeviceName, InterruptSource
from playerresources import PlayerResources
from task import SeqTask, Task


log = logging.getLogger('marquee.' + __name__)


@dataclass()
class BaseMode(ABC):
    """Base for (foreground and background) modes."""
    index: int
    name: str
    serial: int  # Unique ID for every instance.
    player: PlayerResources
    parent: Self | None = None
    children: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Initialize."""
        self._create_children()

    def _create_children(self) -> None:
        """Create child mode(s) specified."""
        for child in self.children:
            mode = self.player.create_mode_instance(
                mode_index=self.lookup_mode_index(child),
                parent=self,
            )
            print(f"Created mode {child} {mode.index} {mode.name}")

    @abstractmethod
    def control_action(self, control: DeviceName) -> None:
        """Respond to control action."""

    def close(self) -> None:
        """Clean up before instance is discarded."""
        print(f"BaseMode close called: {self.name}")

    def execute(self) -> None:
        """Play the mode."""

    @override
    def __repr__(self) -> str:
        return f"<{self}>"
    
    @override
    def __str__(self) -> str:
        return f"Mode {self.index} {self.name}"

    def change_mode(self, mode_index: int) -> None:
        """Effects changing (active) mode to mode_index."""
        def _change_mode() -> NoReturn:
            """Raise ChangeModeInterrupt."""
            log.info(f"Changing to mode {mode_index}")
            raise ChangeModeInterrupt(
                source=InterruptSource.MODE,
                mode_index=mode_index,
            )
        self.schedule(_change_mode)

    def lookup_mode_index(self, name: str) -> int:
        """Return the index for the mode with name."""
        try:
            return self.player.mode_ids[name]
        except LookupError:
            raise ValueError(f"Mode {name} not defined.")

    def next_entry(self) -> None:
        """Change to the next entry."""
        print("NEXT ENTRY")

    def previous_entry(self) -> None:
        """Change to the previous entry."""
        print("PREVIOUS ENTRY")
        
    def next_mode(self) -> None:
        """Change to the next mode."""
        print("NEXT MODE")
        
    def previous_mode(self) -> None:
        """Change to the previous mode."""
        print("PREVIOUS MODE")

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
            self.player.tasks.push(
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

        due = due * self.player.speed_factor
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

