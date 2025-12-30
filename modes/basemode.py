"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass
import sys
import time
from typing import Callable, Protocol

from event import Event
from playerinterface import PlayerInterface
from .modeinterface import ModeInterface

class ScheduleCallback(Protocol):
    """Callback protocol for scheduling events."""
    def __call__(
        self, 
        action: Callable, 
        due_abs: float | None = None, 
        due_rel: float | None = None,
        name: str | None = None,
        repeat: bool = False,
    ) -> None:
        ...

@dataclass
class BaseMode(ModeInterface, ABC):
    """Base for both foreground and background modes."""
    player: PlayerInterface

    def schedule(
        self, 
        action: Callable, 
        due_abs: float | None = None, 
        due_rel: float | None = None,
        name: str | None = None,
        repeat: bool = False,
    ) -> None:
        """Schedule a new event, specifying either due_abs or due_rel.
           If repeat, schedule next before calling action."""

        def push_event():
            """Push event onto queue."""
            print(f"SCHEDULED {_due} {_name}")
            self.player.event_queue.push(
                Event(
                    action=_action,
                    due=_due,
                    owner=self,
                    name=_name,
                )
            )

        def repeater():
            """Schedule next event. Call action."""
            nonlocal _due
            assert due_rel is not None
            _due += due_rel
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

        _due = (
            due_abs if due_abs is not None 
            else time.time() + due_rel  # type: ignore None
        )
        _action = repeater if repeat else action
        push_event()

