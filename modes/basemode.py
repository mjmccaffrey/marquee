"""Marquee Lighted Sign Project - basemode"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
import time
from typing import Callable

from button_misc import ButtonInterface
from event import Event
from playerinterface import PlayerInterface
# from .modeinterface import ModeInterface

@dataclass()
class BaseMode(ABC):
    """Base for both foreground and background modes."""
    player: PlayerInterface
    index: int
    name: str
    parent: 'BaseMode| None' = None


    @abstractmethod
    def button_action(self, button: ButtonInterface) -> int | None:
        """Respond to button being pressed.
           Return index of new mode, if any."""

    @abstractmethod
    def execute(self) -> None:
        """Play the mode."""

    def lookup_mode_index(self, name: str) -> int:
        """Return the index for the mode with name."""
        try:
            return self.player.mode_ids[name]
        except LookupError:
            raise ValueError(f"Mode {name} not defined.")

    def schedule(
        self, 
        action: Callable, 
        due_abs: float | None = None, 
        due_rel: float | None = None,
        name: str | None = None,
        repeat: bool = False,
    ) -> None:
        """Schedule a new event, specifying either due_abs or due_rel.
           Adjust due_rel by speed_factor.
           If repeat, schedule next event before calling action."""

        def push_event():
            """Push event onto queue."""
            self.player.event_queue.push(
                Event(
                    action=_action,
                    due=_due,
                    owner=self.parent or self,
                    name=_name,
                )
            )
            # print(f"SCHEDULED {_due} {_name} {len(self.player.event_queue)}")

        def repeater():
            """Schedule next event. Call action."""
            nonlocal _due
            _due += _due_rel
            push_event()
            action()

        assert (due_abs is None) ^ (due_rel is None)
        assert not (due_rel is None and repeat)
        if name is None:
            caller = sys._getframe(1)
            _name = (
                type(caller.f_locals['self']).__name__ + "." + 
                caller.f_code.co_name
            )
        else:
            _name = name

        if due_abs is not None:
            _due = due_abs
        else:
            assert due_rel is not None
            _due_rel: float = due_rel * self.player.speed_factor
            _due = time.time() + _due_rel
        _action = repeater if repeat else action
        push_event()

